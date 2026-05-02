"""
followup.py
Sends follow-up emails to leads who were contacted 2 days ago and haven't replied.

Usage:
    python followup.py
"""

import os
import csv
import time
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS  = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASS = os.getenv("GMAIL_APP_PASSWORD")
SENDER_NAME    = os.getenv("SENDER_NAME", "Your Name")
DELAY_SECONDS  = int(os.getenv("DELAY_BETWEEN_EMAILS", 10))
FOLLOWUP_DAYS  = 2   # days after initial email to send follow-up

logging.basicConfig(
    filename="followup_log.txt",
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
)


def load_template(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def personalize(template: str, lead: dict) -> str:
    for key, value in lead.items():
        template = template.replace(f"{{{{{key}}}}}", str(value))
    return template


def send_email(to_address: str, subject: str, body_html: str) -> bool:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{SENDER_NAME} <{GMAIL_ADDRESS}>"
    msg["To"]      = to_address

    msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASS)
            server.sendmail(GMAIL_ADDRESS, to_address, msg.as_string())
        return True
    except Exception as exc:
        logging.error("Error sending to %s: %s", to_address, exc)
        return False


def run_followups(
    sent_log_file: str  = "sent_log.csv",
    template_file: str  = "templates/followup.html",
    subject: str        = "Following up — {{name}}",
) -> None:
    """
    Read sent_log.csv, find leads emailed exactly FOLLOWUP_DAYS ago,
    and send them a follow-up if they haven't had one yet.
    """
    if not GMAIL_ADDRESS or not GMAIL_APP_PASS:
        raise ValueError("Gmail credentials not set")

    try:
        with open(sent_log_file, "r", encoding="utf-8") as f:
            log = list(csv.DictReader(f))
    except FileNotFoundError:
        print("[!] sent_log.csv not found — run emailer.py first.")
        return

    template_html = load_template(template_file)
    today         = datetime.now().date()
    target_date   = today - timedelta(days=FOLLOWUP_DAYS)
    sent_count    = 0

    print(f"[+] Looking for leads emailed on {target_date} (i.e. {FOLLOWUP_DAYS} days ago) ...")

    for lead in log:
        # Skip if already followed up
        if lead.get("followup_sent", "").strip().lower() == "yes":
            continue

        # Check if initial email was sent on the target date
        sent_date_str = lead.get("sent_date", "").strip()
        if not sent_date_str:
            continue

        try:
            sent_date = datetime.strptime(sent_date_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        if sent_date != target_date:
            continue

        recipient = lead.get("email", "").strip()
        if not recipient or "@" not in recipient:
            continue

        html_body     = personalize(template_html, lead)
        email_subject = personalize(subject, lead)

        success = send_email(recipient, email_subject, html_body)
        status  = "SENT" if success else "FAILED"
        logging.info("FOLLOWUP %s → %s | %s", status, recipient, lead.get("name", ""))
        print(f"  [FOLLOWUP {status}] {lead.get('name', '')} → {recipient}")

        # Mark as followed up in the log
        lead["followup_sent"] = "yes" if success else "no"
        sent_count += 1
        time.sleep(DELAY_SECONDS)

    # Write updated log back
    if log:
        with open(sent_log_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=log[0].keys())
            writer.writeheader()
            writer.writerows(log)

    print(f"\n[✓] Follow-ups done — {sent_count} sent.")
    print(    "    Log saved to followup_log.txt")


if __name__ == "__main__":
    run_followups()
