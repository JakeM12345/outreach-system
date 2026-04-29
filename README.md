# 🚀 Automated Outreach System

A Python tool that finds business leads via the **Google Places API** and sends personalized cold emails via **Gmail SMTP**.

---

## 📁 Project Structure

```
outreach-system/
├── main.py               # One-command entry point
├── places_scraper.py     # Google Places API → leads.csv
├── emailer.py            # Gmail SMTP sender
├── templates/
│   └── outreach.html     # Personalizable HTML email template
├── leads.csv             # Generated after scraping (git-ignored)
├── outreach_log.txt      # Per-send log (git-ignored)
├── .env                  # Your secrets (git-ignored)
├── .env.example          # Template — copy this to .env
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

### 1. Clone & install dependencies

```bash
git clone https://github.com/YOUR_USERNAME/outreach-system.git
cd outreach-system
pip install -r requirements.txt
```

### 2. Configure your `.env`

```bash
cp .env.example .env
```

Then edit `.env`:

| Variable | Description |
|---|---|
| `GOOGLE_PLACES_API_KEY` | From [Google Cloud Console](https://console.cloud.google.com/) — enable **Places API** |
| `GMAIL_ADDRESS` | Your Gmail address |
| `GMAIL_APP_PASSWORD` | A 16-char [App Password](https://myaccount.google.com/apppasswords) (not your regular password) |
| `SENDER_NAME` | Your full name shown in the From field |
| `DAILY_EMAIL_LIMIT` | Max emails per run (default: 50) |
| `DELAY_BETWEEN_EMAILS` | Seconds between sends (default: 10) |

> **Gmail App Password**: Go to Google Account → Security → 2-Step Verification → App passwords. Generate one for "Mail".

### 3. Customise your email template

Edit `templates/outreach.html`. Use `{{placeholders}}` for personalisation:

| Placeholder | Source |
|---|---|
| `{{name}}` | Business name |
| `{{address}}` | Business address |
| `{{rating}}` | Google rating |
| `{{phone}}` | Phone number |
| `{{website}}` | Website URL |

---

## 🏃 Usage

### Full pipeline (scrape + send)
```bash
python main.py --query "coffee shops" --location "Austin, TX"
```

### Scrape only (no emails)
```bash
python main.py --query "dentists" --location "Chicago, IL" --scrape-only
```

### Send only (uses existing `leads.csv`)
```bash
python main.py --email-only
```

### All options
```bash
python main.py --help
```

---

## 📌 Important Notes

- **Email field**: Google Places doesn't provide email addresses directly. You'll need to enrich `leads.csv` with a tool like Hunter.io or Apollo.io before sending. The `emailer.py` looks for an `email` column in your CSV.
- **Rate limits**: The scraper adds a 0.3s delay per result to stay within Google's quotas.
- **Spam compliance**: The template includes an unsubscribe notice. Always honor opt-out requests.
- **Gmail limits**: Free Gmail accounts allow ~500 emails/day. Use `DAILY_EMAIL_LIMIT` to stay safe.

---

## 🔒 .gitignore

Make sure your `.gitignore` includes:

```
.env
leads.csv
outreach_log.txt
__pycache__/
*.pyc
```

---

## 📄 License

MIT
