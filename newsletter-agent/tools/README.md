# Tools

Python scripts that handle deterministic execution. Each script:
- Does one thing well
- Reads config/inputs from arguments or stdin
- Writes outputs to `.tmp/` or a cloud service
- Prints a clear success/error message

## Scripts

| Script | Purpose |
|--------|---------|
| `research_topic.py` | Research a topic via Perplexity sonar-pro (live web search + synthesis) → JSON |
| `generate_infographic.py` | Automate Napkin.ai via Playwright — paste text, export SVG infographic |
| `render_newsletter_html.py` | Render Jinja2 template with content JSON → branded HTML file in `.tmp/` |
| `send_email_gmail.py` | Send HTML newsletter via Gmail API using Google OAuth credentials |

## Setup

```bash
pip install -r tools/requirements.txt
playwright install chromium   # required for generate_infographic.py
```
