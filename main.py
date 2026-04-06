"""
Zap Group – AI-Powered Client Onboarding Automation
=====================================================
Usage:
  # Demo mode (uses realistic mock data, no live scraping needed):
  python main.py --demo

  # Live mode (scrape real URLs):
  python main.py --website https://client-website.co.il \
                 --dapei-zahav https://www.d.co.il/...

  # Skip scraping, load previously saved scraped content:
  python main.py --from-file scraped_content.txt

Environment:
  ANTHROPIC_API_KEY  – required
"""

import argparse
import json
import os
import sys
from datetime import datetime

# Add src/ and data/ to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "data"))

import results_viewer

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.rule import Rule

import ai_processor
import crm
import scraper
from demo_data import MOCK_DAPEI_ZAHAV_CONTENT, MOCK_WEBSITE_CONTENT

load_dotenv()
console = Console()


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def save_output(filename: str, content: str) -> None:
    os.makedirs("output", exist_ok=True)
    path = f"output/{filename}"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    console.print(f"  [dim]Saved → {path}[/dim]")


def build_onboarding_email(client_data: dict, script: str) -> tuple[str, str]:
    """Build the email subject and body that gets sent to the client."""
    name = client_data.get("owner_name") or client_data.get("business_name", "לקוח יקר")
    business = client_data.get("business_name", "העסק שלך")
    subject = f"ברוכים הבאים לזאפ! הכל מוכן לתחילת הקמת {business} 🚀"

    body = f"""שלום {name},

ברוכים הבאים למשפחת זאפ! אנחנו שמחים שבחרתם בנו לניהול הנוכחות הדיגיטלית של {business}.

החבילה שרכשתם כוללת:
✓ אתר אינטרנט מקצועי בן 5 עמודים
✓ מיניסייט מוביל בדפי זהב באזור הקריות

מה הלאה?
אחד מנציגינו ייצור איתכם קשר בקרוב לשיחת היכרות קצרה שבה נתאם את כל הפרטים.

לשאלות ותיאום מהיר: info@zapgroup.co.il | 1-700-XXX-XXX

בברכה,
צוות זאפ גרופ
"""
    return subject, body


# ---------------------------------------------------------------------------
# Pipeline steps
# ---------------------------------------------------------------------------

def step_scrape(args) -> str:
    """Step 1: Scrape (or load) content."""
    if args.demo:
        console.print(Panel("[bold cyan]Demo Mode[/bold cyan] – using realistic mock data", expand=False))
        website_data = MOCK_WEBSITE_CONTENT
        dz_data = MOCK_DAPEI_ZAHAV_CONTENT
        raw = scraper.combine_scraped_content(website_data, dz_data)
        save_output("scraped_content.txt", raw)
        return raw

    if args.from_file:
        console.print(f"[cyan]Loading scraped content from {args.from_file}[/cyan]")
        with open(args.from_file, encoding="utf-8") as f:
            return f.read()

    # Live scraping
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as p:
        t = p.add_task("Scraping client website…", total=None)
        website_data = scraper.scrape_website(args.website, max_pages=5)
        p.update(t, description=f"  Scraped {len(website_data['pages'])} pages from {args.website}")

        t2 = p.add_task("Scraping Dapei Zahav listing…", total=None)
        dz_data = scraper.scrape_dapei_zahav(args.dapei_zahav)
        p.update(t2, description="  Dapei Zahav listing scraped")

    raw = scraper.combine_scraped_content(website_data, dz_data)
    save_output("scraped_content.txt", raw)
    return raw


def step_extract(raw_content: str) -> dict:
    """Step 2: AI extraction of structured client data."""
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as p:
        p.add_task("Extracting client data with Claude…", total=None)
        data = ai_processor.extract_client_data(raw_content)

    save_output("client_data.json", json.dumps(data, ensure_ascii=False, indent=2))
    return data


def step_generate_card(client_data: dict) -> str:
    """Step 3: Generate the client card."""
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as p:
        p.add_task("Generating client card…", total=None)
        card = ai_processor.generate_client_card(client_data)

    save_output("client_card.md", card)
    return card


def step_generate_script(client_data: dict) -> str:
    """Step 4: Generate the onboarding call script."""
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as p:
        p.add_task("Generating onboarding script…", total=None)
        script = ai_processor.generate_onboarding_script(client_data)

    save_output("onboarding_script.md", script)
    return script


def step_crm_and_email(client_data: dict, card: str, script: str) -> str:
    """Step 5: Log to CRM and simulate sending onboarding email."""
    record_id = crm.log_onboarding(client_data, card, script)

    subject, body = build_onboarding_email(client_data, script)
    email_recipient = client_data.get("email") or "client@example.com"

    crm.simulate_send_email(email_recipient, subject, body)
    crm.log_email_sent(record_id, email_recipient, subject, body)

    return record_id


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Zap Group AI Onboarding Automation")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--demo", action="store_true", help="Run with realistic mock data")
    group.add_argument("--website", metavar="URL", help="Client website base URL")
    group.add_argument("--from-file", metavar="FILE", help="Load pre-scraped content from file")

    parser.add_argument("--dapei-zahav", metavar="URL", help="Dapei Zahav listing URL (required with --website)")
    args = parser.parse_args()

    if args.website and not args.dapei_zahav:
        parser.error("--dapei-zahav is required when using --website")

    if not os.getenv("GROQ_API_KEY"):
        console.print("[red]Error: GROQ_API_KEY environment variable not set.[/red]")
        console.print("[yellow]Get a free key at: https://console.groq.com[/yellow]")
        sys.exit(1)

    console.print(Rule("[bold green]Zap Group – AI Onboarding Automation[/bold green]"))
    console.print()

    # --- Step 1: Scrape ---
    console.print("[bold]Step 1:[/bold] Collecting digital assets…")
    raw_content = step_scrape(args)
    console.print(f"  [green]✓[/green] Content collected ({len(raw_content):,} chars)\n")

    # --- Step 2: Extract ---
    console.print("[bold]Step 2:[/bold] AI-powered data extraction…")
    client_data = step_extract(raw_content)
    console.print(f"  [green]✓[/green] Extracted data for: [bold]{client_data.get('business_name', 'Unknown')}[/bold]\n")

    # --- Step 3: Client Card ---
    console.print("[bold]Step 3:[/bold] Generating client card…")
    client_card = step_generate_card(client_data)
    console.print("  [green]✓[/green] Client card generated\n")

    # --- Step 4: Onboarding Script ---
    console.print("[bold]Step 4:[/bold] Generating onboarding call script…")
    onboarding_script = step_generate_script(client_data)
    console.print("  [green]✓[/green] Onboarding script generated\n")

    # --- Step 5: CRM + Email ---
    console.print("[bold]Step 5:[/bold] Logging to CRM & sending onboarding email…")
    record_id = step_crm_and_email(client_data, client_card, onboarding_script)
    console.print(f"  [green]✓[/green] CRM record created: [bold]{record_id}[/bold]\n")

    # --- Display results ---
    console.print(Rule("[bold blue]CLIENT CARD[/bold blue]"))
    console.print(Markdown(client_card))

    console.print()
    console.print(Rule("[bold blue]ONBOARDING SCRIPT[/bold blue]"))
    console.print(Markdown(onboarding_script))

    console.print()
    console.print(Rule("[bold green]Done[/bold green]"))
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  CRM Record ID : [cyan]{record_id}[/cyan]")
    console.print(f"  Output files  : [dim]output/[/dim]")
    console.print(f"    • client_data.json")
    console.print(f"    • client_card.md")
    console.print(f"    • onboarding_script.md")
    console.print(f"    • email_*.txt")
    console.print(f"    • scraped_content.txt")
    console.print(f"  CRM DB        : [dim]crm_records.json[/dim]")

    # Open results viewer in browser
    console.print(f"\n[bold green]Opening results viewer in browser...[/bold green]")
    results_viewer.generate_and_open(client_data, client_card, onboarding_script, record_id)


if __name__ == "__main__":
    main()
