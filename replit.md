# Automated Outreach System

## Overview
A **command-line Python tool** that finds business leads via the Google Places API
and sends personalized cold emails via Gmail SMTP. This project has **no web
frontend and no backend server** — it is a one-shot CLI script invoked manually.

## Project Structure
```
.
├── main.py               # CLI entry point (argparse)
├── places_scraper.py     # Google Places API → leads.csv
├── emailer.py            # Gmail SMTP sender
├── templates/
│   └── outreach.html     # Personalisable HTML email template
├── env.example           # Template for required env vars
├── requirements.txt      # Original pip requirements (kept for reference)
├── pyproject.toml        # uv-managed dependency manifest (source of truth)
└── README.md
```

## Tech Stack
- **Language**: Python 3.12
- **Package manager**: `uv` (project uses `pyproject.toml` + `uv.lock`)
- **Runtime deps**: `requests`, `python-dotenv`
  - `pandas` was listed in the original `requirements.txt` but is never imported
    anywhere in the code, so it was removed to keep the install lean.

## Running
```bash
uv run python main.py --query "coffee shops" --location "Austin, TX"
uv run python main.py --scrape-only
uv run python main.py --email-only
uv run python main.py --help
```

## Environment Variables
Copy `env.example` to `.env` and fill in:
- `GOOGLE_PLACES_API_KEY`
- `GMAIL_ADDRESS`
- `GMAIL_APP_PASSWORD` (16-char Gmail App Password, not your normal password)
- `SENDER_NAME`
- `DAILY_EMAIL_LIMIT` (default 50)
- `DELAY_BETWEEN_EMAILS` (default 10 seconds)

## Replit Setup Notes
- **No workflow is configured.** This is intentional — the project is a CLI
  script, not a long-running server. There is nothing to host on a port.
- **No deployment is configured.** Deployment is for web apps; this script
  is run on-demand from the shell.
- Dependencies are managed by `uv`. Run `uv sync` to install.

## Recent Changes
- 2026-04-30: Initial Replit import. Switched dependency management to `uv`,
  removed unused `pandas` dependency, verified the CLI runs.
