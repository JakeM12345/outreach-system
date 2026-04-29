"""
emailer.py
Sends personalized outreach emails via Gmail SMTP using leads from leads.csv.
"""

import os
import csv
import time
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS    = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASS   = os.getenv("GMAIL_APP_PASSWORD")
SENDER_NAME      = os.getenv("SENDER_NAME", "Your Name")
DAILY_LIMIT      = int(os.getenv("DAILY_EMAIL_LIMIT", 50))
DELAY_SECONDS    = int(os.getenv("DELAY_BETWEEN_EMAILS", 10))

logging.basicConfig(
    filename="outreach_log.txt",
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
)


def load_template(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def personalize(template: str, lead: dict) -> str:
    """
    Replace {{placeholders}} in the template with lead data.
    Available keys: name, address, phone, website, rating
    """
    for key, value in lead.items():
        template = template.replace(f"{{{{{key}}}}}", str(value))
    return template


def send_email(to_address: str, subject: str, body_html: str, body_text: str = "") -> bool:
    """
    Send a single email via Gmail SMTP (TLS on port 587).

    Returns True on success, False on failure.
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{SENDER_NAME} <{GMAIL_ADDRESS}>"
    msg["To"]      = to_address

    if body_text:
        msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASS)
            server.sendmail(GMAIL_ADDRESS, to_address, msg.as_string())
        return True
    except smtplib.SMTPException as exc:
        logging.error("SMTP error sending to %s: %s", to_address, exc)
        return False
    except Exception as exc:
        logging.error("Unexpected error sending to %s: %s", to_address, exc)
        return False


def run_outreach(
    leads_file: str = "leads.csv",
    template_file: str = "templates/outreach.html",
    subject: str = "Quick question about {{name}}",
    contact_email_field: str = "website",   # swap for a real email field once you have one
) -> None:
    """
    Main loop: read leads → personalise template → send → log result.
    """
    if not GMAIL_ADDRESS or not GMAIL_APP_PASS:
        raise ValueError("GMAIL_ADDRESS and GMAIL_APP_PASSWORD must be set in .env")

    template_html = load_template(template_file)
    sent_count    = 0
    skipped       = 0

    with open(leads_file, "r", encoding="utf-8") as f:
        leads = list(csv.DictReader(f))

    print(f"[+] Loaded {len(leads)} leads. Daily limit: {DAILY_LIMIT}")

    for lead in leads:
        if sent_count >= DAILY_LIMIT:
            print(f"[!] Daily limit of {DAILY_LIMIT} reached. Stopping.")
            break

        # In a real campaign this field would be a dedicated 'email' column.
        # Here we fall back to website as a placeholder.
        recipient = lead.get("email") or lead.get(contact_email_field, "").strip()
        if not recipient or "@" not in recipient:
            skipped += 1
            continue

        html_body    = personalize(template_html, lead)
        email_subject = personalize(subject, lead)

        success = send_email(
            to_address=recipient,
            subject=email_subject,
            body_html=html_body,
        )

        status = "SENT" if success else "FAILED"
        logging.info("%s  →  %s  |  %s", status, recipient, lead.get("name", ""))
        print(f"  [{status}] {lead.get('name', '')}  →  {recipient}")

        sent_count += 1
        time.sleep(DELAY_SECONDS)

    print(f"\n[✓] Done — {sent_count} sent, {skipped} skipped (no email address).")
    print(    "    Full log saved to outreach_log.txt")


if __name__ == "__main__":
    run_outreach()
