"""
enrich.py
Automatically finds email addresses for leads in leads.csv using the Hunter.io API.
Saves enriched results back to leads.csv.

Usage:
    python enrich.py
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
    """Strip protocol and path from a URL to get the bare domain."""
    if not url:
        return ""
    url = url.lower().replace("https://", "").replace("http://", "").replace("www.", "")
    return url.split("/")[0].strip()


def find_email(domain: str) -> str:
    """
    Search Hunter.io for the most common email address for a domain.
    Returns the best email found, or empty string if none.
    """
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
    """
    Read leads.csv, look up emails via Hunter.io, write results back.
    Skips leads that already have an email address.
    """
    if not HUNTER_API_KEY:
        raise ValueError("HUNTER_API_KEY must be set in .env or GitHub Secrets")

    with open(leads_file, "r", encoding="utf-8") as f:
        leads = list(csv.DictReader(f))

    if not leads:
        print("[!] No leads found in", leads_file)
        return

    # Make sure the email column exists
    fieldnames = list(leads[0].keys())
    if "email" not in fieldnames:
        fieldnames.append("email")

    found = 0
    skipped = 0

    print(f"[+] Enriching {len(leads)} leads with Hunter.io ...")

    for i, lead in enumerate(leads, 1):
        # Skip if already has an email
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

        # Stay within Hunter.io rate limits
        time.sleep(1)

    # Write enriched data back
    with open(leads_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leads)

    print(f"\n[✓] Done — {found} emails found, {skipped} already had emails.")
    print(f"    Results saved to '{leads_file}'")


if __name__ == "__main__":
    enrich_leads()
