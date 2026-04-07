"""
Mock CRM logger.
In production this would integrate with a real CRM (Salesforce, HubSpot, etc.).
Here we persist records to a local JSON file and simulate email dispatch.
"""

import json
import os
from datetime import datetime


CRM_FILE = "crm_records.json"


def _load_records() -> list:
    if os.path.exists(CRM_FILE):
        with open(CRM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_records(records: list) -> None:
    with open(CRM_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def log_onboarding(
    client_data: dict,
    client_card: str,
    onboarding_script: str,
) -> str:
    """
    Create a CRM record for the new client and return the record ID.
    """
    records = _load_records()
    record_id = f"ZAP-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{len(records) + 1:04d}"

    record = {
        "record_id": record_id,
        "created_at": datetime.now().isoformat(),
        "status": "pending_onboarding",
        "client_data": client_data,
        "client_card": client_card,
        "onboarding_script": onboarding_script,
        "communications": [],
    }

    records.append(record)
    _save_records(records)
    return record_id


def log_email_sent(record_id: str, recipient: str, subject: str, body: str) -> None:
    """Append an outbound email event to the CRM record."""
    records = _load_records()
    for rec in records:
        if rec["record_id"] == record_id:
            rec["communications"].append(
                {
                    "type": "email",
                    "direction": "outbound",
                    "timestamp": datetime.now().isoformat(),
                    "recipient": recipient,
                    "subject": subject,
                    "body_preview": body[:200] + "..." if len(body) > 200 else body,
                    "status": "sent",
                }
            )
            rec["status"] = "onboarding_email_sent"
            break
    _save_records(records)


def simulate_send_email(recipient: str, subject: str, body: str) -> None:
    """
    Simulate sending an onboarding email.
    Currently: saves the email to output/email_*.txt (no real sending).

    To connect a real email provider in production, replace this function body
    with one of the following integrations:

    ── Option A: SendGrid ──────────────────────────────────────────────────────
    pip install sendgrid
    Set env var: SENDGRID_API_KEY

        import sendgrid
        from sendgrid.helpers.mail import Mail

        sg = sendgrid.SendGridAPIClient(api_key=os.environ["SENDGRID_API_KEY"])
        message = Mail(
            from_email="onboarding@zapgroup.co.il",
            to_emails=recipient,
            subject=subject,
            plain_text_content=body,
        )
        sg.send(message)

    ── Option B: SMTP (Gmail / Outlook / corporate) ────────────────────────────
    Set env vars: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

        import smtplib
        from email.mime.text import MIMEText

        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = os.environ["SMTP_USER"]
        msg["To"] = recipient

        with smtplib.SMTP_SSL(os.environ["SMTP_HOST"], int(os.environ["SMTP_PORT"])) as s:
            s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
            s.send_message(msg)

    ── Option C: Mailchimp Transactional (Mandrill) ─────────────────────────────
    pip install mailchimp-transactional
    Set env var: MANDRILL_API_KEY

        import mailchimp_transactional as MailchimpTransactional

        client = MailchimpTransactional.Client(os.environ["MANDRILL_API_KEY"])
        client.messages.send({"message": {
            "from_email": "onboarding@zapgroup.co.il",
            "to": [{"email": recipient}],
            "subject": subject,
            "text": body,
        }})

    ── CRM integration note ─────────────────────────────────────────────────────
    The log_email_sent() function already records the outbound event.
    In a real CRM (HubSpot / Salesforce), replace _save_records() calls with
    the respective REST API calls to keep the timeline in sync.
    ────────────────────────────────────────────────────────────────────────────
    """
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/email_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"TO: {recipient}\n")
        f.write(f"SUBJECT: {subject}\n")
        f.write(f"DATE: {datetime.now().isoformat()}\n")
        f.write("-" * 60 + "\n")
        f.write(body)

    print(f"  [CRM] Email saved → {filename}")

    # Send via Gmail SMTP if credentials are set in .env
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    if smtp_user and smtp_password:
        try:
            import smtplib
            from email.mime.text import MIMEText
            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = smtp_user
            msg["To"] = recipient
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
                s.login(smtp_user, smtp_password)
                s.send_message(msg)
            print(f"  [CRM] Email sent via Gmail → {recipient}")
        except Exception as e:
            print(f"  [CRM] Gmail send failed: {e}")


def get_record(record_id: str) -> dict:
    """Retrieve a CRM record by ID."""
    for rec in _load_records():
        if rec["record_id"] == record_id:
            return rec
    return None
