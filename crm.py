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
    In production: integrate with SendGrid / Mailchimp / internal SMTP.
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

    print(f"  [CRM] Email simulated → saved to {filename}")


def get_record(record_id: str) -> dict:
    """Retrieve a CRM record by ID."""
    for rec in _load_records():
        if rec["record_id"] == record_id:
            return rec
    return None
