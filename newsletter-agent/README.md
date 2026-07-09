# newsletter-agent

Autonomous newsletter pipeline built on the WAT framework. One instruction — *"generate a newsletter about X"* — triggers the full chain: live research → structured content → branded HTML render → infographic generation → Gmail delivery.

## How it works

The agent (Claude Code) reads the 8-phase SOP in [`workflows/generate_newsletter.md`](workflows/generate_newsletter.md) and calls these tools in sequence:

| Phase | Tool | What it does |
|-------|------|--------------|
| Research | `tools/research_topic.py` | Perplexity `sonar-pro` live web research → structured JSON |
| Infographics | `tools/generate_infographic.py` | Playwright drives Napkin.ai (session-based auth) to generate visuals |
| Render | `tools/render_newsletter_html.py` | Jinja2 template, brand logo base64-inlined, email-client-safe table layout |
| Deliver | `tools/send_email_gmail.py` | Gmail API via OAuth 2.0 (`credentials.json` + `token.json`) |

A real rendered output is in [`examples/sample_newsletter_evolution_of_ai.html`](examples/) — open it in a browser.

The `tools/` folder also contains other WAT-pattern automations reusing the same skeleton (stock-report and education-report PDF generators).

## Setup

```bash
pip install -r tools/requirements.txt
playwright install chromium
cp .env.example .env          # fill in your keys
python tools/setup_napkin_session.py   # one-time Napkin.ai login
```

Gmail delivery needs a Google Cloud OAuth client (Desktop app) — download `credentials.json`, and `token.json` is created on first authorized send.

## Credentials

Everything secret is gitignored: `.env`, `credentials.json`, `token.json`, Napkin session files. See `.env.example`.
