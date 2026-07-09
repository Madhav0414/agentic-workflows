"""
Send an HTML newsletter email via the Gmail API using Google OAuth credentials.

Requires:
  - credentials.json (OAuth client secret — download from Google Cloud Console)
  - token.json will be auto-created on first run after OAuth browser flow
  - The Gmail API must be enabled in your Google Cloud project
  - Scope needed: https://www.googleapis.com/auth/gmail.send

If token.json exists but lacks the gmail.send scope, delete it and re-run to
trigger a fresh OAuth flow that includes the new scope.

Usage:
    python tools/send_email_gmail.py \
        --html-file .tmp/newsletter_20250430_demo.html \
        --to "recipient@example.com,another@example.com" \
        --subject "Issue #1: AI Regulation" \
        [--dry-run]

    # Recipients from a file (one email per line):
    python tools/send_email_gmail.py \
        --html-file .tmp/newsletter_20250430.html \
        --to subscribers.txt \
        --subject "Issue #1" \
        --from-name "Your Brand"

Output (stdout): JSON result — { "sent": N, "failed": 0, "recipients": [...] }
Exit codes: 0=ok, 1=missing credentials, 2=Gmail API error, 3=bad args
"""

import argparse
import base64
import json
import os
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
CREDENTIALS_PATH = Path(__file__).parent.parent / "credentials.json"
TOKEN_PATH = Path(__file__).parent.parent / "token.json"
DEFAULT_FROM_NAME = "Your Brand"


def get_gmail_service():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        print("Error: Google API libraries not installed. Run: pip install -r tools/requirements.txt", file=sys.stderr)
        sys.exit(1)

    # Check if credentials are in .env (as JSON string)
    creds_from_env = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if creds_from_env:
        try:
            creds_data = json.loads(creds_from_env)
            with open(CREDENTIALS_PATH, "w") as f:
                json.dump(creds_data, f)
            print(f"Created credentials.json from .env", file=sys.stderr)
        except json.JSONDecodeError:
            print("Error: GOOGLE_CREDENTIALS_JSON in .env is not valid JSON", file=sys.stderr)
            sys.exit(1)

    if not CREDENTIALS_PATH.exists():
        print(f"Error: credentials.json not found at {CREDENTIALS_PATH}", file=sys.stderr)
        print("Option 1: Download credentials.json from Google Cloud Console → APIs & Services → Credentials", file=sys.stderr)
        print("Option 2: Paste the full JSON content into .env as: GOOGLE_CREDENTIALS_JSON=<paste full JSON here>", file=sys.stderr)
        sys.exit(1)

    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def parse_recipients(to_arg: str) -> list[str]:
    to_path = Path(to_arg)
    if to_path.exists() and to_path.suffix == ".txt":
        emails = [line.strip() for line in to_path.read_text().splitlines() if line.strip()]
    else:
        emails = [e.strip() for e in to_arg.split(",") if e.strip()]

    if not emails:
        print("Error: No valid recipient email addresses found", file=sys.stderr)
        sys.exit(3)
    return emails


def build_message(html_content: str, subject: str, from_email: str, from_name: str, to_email: str) -> dict:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = to_email

    # Plain text fallback for email clients that block HTML
    plain_text = "This email contains HTML content. Please view it in an HTML-capable email client."
    msg.attach(MIMEText(plain_text, "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    return {"raw": raw}


def send_email(
    html_file: str,
    recipients: list[str],
    subject: str,
    from_name: str = DEFAULT_FROM_NAME,
    dry_run: bool = False,
) -> dict:
    html_path = Path(html_file)
    if not html_path.exists():
        print(f"Error: HTML file not found: {html_file}", file=sys.stderr)
        sys.exit(3)

    html_content = html_path.read_text(encoding="utf-8")

    if dry_run:
        print("=== DRY RUN — no email sent ===", file=sys.stderr)
        print(f"From:    {from_name}", file=sys.stderr)
        print(f"Subject: {subject}", file=sys.stderr)
        print(f"To:      {', '.join(recipients)}", file=sys.stderr)
        print(f"HTML file: {html_file} ({len(html_content):,} chars)", file=sys.stderr)
        return {"sent": 0, "failed": 0, "dry_run": True, "would_send_to": recipients}

    service = get_gmail_service()

    # Get sender email from authenticated account
    profile = service.users().getProfile(userId="me").execute()
    from_email = profile["emailAddress"]

    sent = []
    failed = []

    for recipient in recipients:
        try:
            message_body = build_message(html_content, subject, from_email, from_name, recipient)
            result = service.users().messages().send(userId="me", body=message_body).execute()
            sent.append({"email": recipient, "message_id": result.get("id")})
            print(f"Sent to {recipient} (id: {result.get('id')})", file=sys.stderr)
        except Exception as e:
            failed.append({"email": recipient, "error": str(e)})
            print(f"Failed to send to {recipient}: {e}", file=sys.stderr)

    return {
        "sent": len(sent),
        "failed": len(failed),
        "recipients": sent,
        "errors": failed,
    }


def main():
    parser = argparse.ArgumentParser(description="Send newsletter via Gmail API (OAuth)")
    parser.add_argument("--html-file", required=True, help="Path to rendered HTML newsletter")
    parser.add_argument("--to", required=True,
                        help="Recipient email(s) — comma-separated or path to .txt file (one per line)")
    parser.add_argument("--subject", required=True, help="Email subject line")
    parser.add_argument("--from-name", default=DEFAULT_FROM_NAME,
                        help=f"Sender display name (default: {DEFAULT_FROM_NAME})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview payload without sending")
    args = parser.parse_args()

    recipients = parse_recipients(args.to)
    result = send_email(
        html_file=args.html_file,
        recipients=recipients,
        subject=args.subject,
        from_name=args.from_name,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
