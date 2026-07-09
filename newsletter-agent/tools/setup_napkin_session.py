"""
One-time setup: log in to Napkin.ai manually and save the browser session.

Run this ONCE. A browser window will open — log in with Google as you normally would.
Once you're inside Napkin.ai, come back here and press Enter.
The session (cookies + storage) is saved to .tmp/napkin_session.json and reused
automatically by generate_infographic.py on every future run.

Usage:
    python tools/setup_napkin_session.py
"""

import sys
from pathlib import Path

SESSION_PATH = Path(__file__).parent.parent / ".tmp" / "napkin_session.json"


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Error: playwright not installed. Run: pip install playwright && playwright install chromium")
        sys.exit(1)

    SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("Opening Napkin.ai in a browser window...")
    print("Log in with your Google account as you normally would.")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        page.goto("https://app.napkin.ai", wait_until="domcontentloaded")

        print("=" * 60)
        print("ACTION REQUIRED:")
        print("  1. Log in with Google in the browser window that opened")
        print("  2. Wait until you can see the Napkin.ai dashboard")
        print("  3. Come back here and press Enter")
        print("=" * 60)
        input("\nPress Enter once you are logged in and see the dashboard... ")

        context.storage_state(path=str(SESSION_PATH))
        browser.close()

    print()
    print(f"Session saved to: {SESSION_PATH}")
    print("You're all set — generate_infographic.py will use this session automatically.")


if __name__ == "__main__":
    main()
