"""
main.py
One-command entry point: scrape leads then run outreach.

Usage:
    python main.py --query "coffee shops" --location "Austin, TX"
    python main.py --email-only          # skip scraping, use existing leads.csv
    python main.py --scrape-only         # only scrape, don't send emails
"""

import argparse
from places_scraper import scrape_leads
from emailer import run_outreach


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automated outreach system")
    parser.add_argument("--query",       default="digital marketing agencies", help="Business type to search for")
    parser.add_argument("--location",    default="Los Angeles, CA",            help="City / region to search in")
    parser.add_argument("--leads-file",  default="Northern Beaches, Sydney, Australia",                  help="Path to leads CSV")
    parser.add_argument("--template",    default="templates/outreach.html",    help="HTML email template")
    parser.add_argument("--subject",     default="Quick question about {{name}}", help="Email subject line")
    parser.add_argument("--scrape-only", action="store_true",  help="Only scrape — skip sending emails")
    parser.add_argument("--email-only",  action="store_true",  help="Only send emails — skip scraping")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.email_only:
        scrape_leads(
            query=args.query,
            location=args.location,
            output_file=args.leads_file,
        )

    if not args.scrape_only:
        run_outreach(
            leads_file=args.leads_file,
            template_file=args.template,
            subject=args.subject,
        )


if __name__ == "__main__":
    main()
