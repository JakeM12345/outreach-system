"""
enrich.py
Automatically finds email addresses for leads in leads.csv using the Hunter.io API.
"""

import os
import csv
import time
import requests
from dotenv import load_dotenv

load_dotenv()

HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")
HUNTER_BASE    = "https://api.hunter.io/v2"


def extract_domain(url: str) -> str:
    if not url:
        return ""
    url = url.lower().replace("https://", "").replace("http://", "").replace("www.", "")
    return url.split("/")[0].strip()


def find_email(domain: str) -> str:
    if not domain:
        return ""
    url = f"{HUNTER_BASE}/domain-search"
    params = {"domain": domain, "api_key": HUNTER_API_KEY, "limit": 1}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", {})
        emails = data.get("emails", [])
        if emails:
            return emails[0].get("value", "")
    except Exception as exc:
        print(f"    [ERROR] Hunter.io lookup failed for {domain}: {exc}")
    return ""


def enrich_leads(leads_file: str = "leads.csv") -> None:
    if not HUNTER_API_KEY:
        raise ValueError("HUNTER_API_KEY must be set in secrets")

    try:
        with open(leads_file, "r", encoding="utf-8") as f:
            leads = list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"[!] {leads_file} not found — skipping enrichment")
        return

    if not leads:
        print("[!] No leads found")
        return

    fieldnames = list(leads[0].keys())
    if "email" not in fieldnames:
        fieldnames.append("email")

    found = 0
    skipped = 0

    print(f"[+] Enriching {len(leads)} leads with Hunter.io ...")

    for i, lead in enumerate(leads, 1):
        if lead.get("email", "").strip():
            skipped += 1
            continue

        domain = extract_domain(lead.get("website", ""))
        if not domain:
            print(f"    [{i}/{len(leads)}] {lead.get('name', '')} — no website, skipping")
            continue

        email = find_email(domain)
        lead["email"] = email

        if email:
            found += 1
            print(f"    [{i}/{len(leads)}] {lead.get('name', '')} → {email}")
        else:
            print(f"    [{i}/{len(leads)}] {lead.get('name', '')} → no email found")

        time.sleep(1)

    with open(leads_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leads)

    print(f"\n[✓] Done — {found} emails found, {skipped} already had emails.")


if __name__ == "__main__":
    enrich_leads()
