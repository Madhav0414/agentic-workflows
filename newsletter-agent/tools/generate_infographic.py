"""
Generate an infographic via Napkin.ai using Playwright browser automation.

Napkin.ai takes a text description and auto-generates a visual diagram/infographic.
This tool logs in, creates a new napkin, pastes the text, waits for AI generation,
and exports the result as an SVG file.

Usage:
    python tools/generate_infographic.py \
        --text "Text describing what to visualize" \
        --title "Infographic Title" \
        --output .tmp/infographic_1.svg

Output (stdout): path to the exported SVG file
Exit codes: 0=ok, 1=missing credentials, 2=browser/Napkin error, 3=bad args

Setup:
    pip install playwright
    playwright install chromium
"""

import argparse
import sys
import time
from pathlib import Path

NAPKIN_URL = "https://app.napkin.ai"
SESSION_PATH = Path(__file__).parent.parent / ".tmp" / "napkin_session.json"


def generate_infographic(text: str, title: str, output_path: str) -> str:
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    except ImportError:
        print("Error: playwright not installed. Run: pip install playwright && playwright install chromium", file=sys.stderr)
        sys.exit(2)

    if not SESSION_PATH.exists():
        print("Error: Napkin.ai session not found.", file=sys.stderr)
        print("Run this once to save your session:", file=sys.stderr)
        print("  python tools/setup_napkin_session.py", file=sys.stderr)
        sys.exit(1)

    output_path = str(Path(output_path).resolve())
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Load saved session — no login needed
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            storage_state=str(SESSION_PATH),
        )
        page = context.new_page()

        try:
            print("Opening Napkin.ai with saved session...", file=sys.stderr)
            page.goto(NAPKIN_URL, wait_until="networkidle", timeout=30000)

            # If session expired, we'll land on the login page
            if "login" in page.url or "signin" in page.url:
                print("Error: Napkin.ai session has expired. Re-run setup:", file=sys.stderr)
                print("  python tools/setup_napkin_session.py", file=sys.stderr)
                sys.exit(1)

            print("Session loaded — on dashboard.", file=sys.stderr)

            # --- Handle onboarding screen: "How would you like to add text?" ---
            # Napkin shows this card picker when creating a new napkin.
            # We always want "By pasting my text".
            try:
                paste_card = page.locator('text="By pasting my text"').first
                paste_card.wait_for(timeout=5000)
                paste_card.click()
                print("Selected 'By pasting my text'.", file=sys.stderr)
                page.wait_for_load_state("networkidle", timeout=10000)
            except PlaywrightTimeout:
                pass  # Already in editor or different flow

            # --- Create new napkin if on dashboard ---
            try:
                new_btn = page.locator(
                    'button:has-text("New"), a:has-text("New"), '
                    'button[aria-label*="new" i], button[aria-label*="create" i]'
                ).first
                if new_btn.is_visible(timeout=4000):
                    new_btn.click()
                    page.wait_for_load_state("networkidle", timeout=15000)
                    # Handle "By pasting my text" card again after New
                    try:
                        paste_card2 = page.locator('text="By pasting my text"').first
                        paste_card2.wait_for(timeout=6000)
                        paste_card2.click()
                        page.wait_for_load_state("networkidle", timeout=10000)
                    except PlaywrightTimeout:
                        pass
            except PlaywrightTimeout:
                pass

            # --- Paste the text content ---
            editor = page.locator('[contenteditable="true"], textarea, [role="textbox"]').first
            editor.wait_for(timeout=15000)
            editor.click()
            editor.fill(f"{title}\n\n{text}")

            # Wait for Napkin's AI to process and suggest visuals
            print("Waiting for Napkin AI to generate visuals...", file=sys.stderr)
            time.sleep(5)

            # Look for generated visual/diagram elements and click to select
            try:
                visual = page.locator('[data-testid*="visual"], [class*="visual"], [class*="diagram"], [class*="infographic"]').first
                visual.wait_for(timeout=30000)
                visual.click()
            except PlaywrightTimeout:
                print("Warning: Could not detect generated visual element. Attempting export anyway.", file=sys.stderr)

            # --- Export as SVG ---
            # Look for export/download button
            try:
                export_btn = page.locator('button:has-text("Export"), button:has-text("Download"), button[aria-label*="export" i], button[aria-label*="download" i]').first
                export_btn.click(timeout=10000)

                # Wait for format selection (SVG option)
                svg_option = page.locator('button:has-text("SVG"), [role="option"]:has-text("SVG"), li:has-text("SVG")').first
                svg_option.click(timeout=8000)

                # Handle file download
                with page.expect_download(timeout=15000) as download_info:
                    confirm_btn = page.locator('button:has-text("Download"), button:has-text("Confirm"), button:has-text("Export")').last
                    confirm_btn.click(timeout=8000)

                download = download_info.value
                download.save_as(output_path)
                print(f"SVG exported to: {output_path}", file=sys.stderr)

            except PlaywrightTimeout:
                # Fallback: try to grab the SVG directly from the DOM
                print("Download UI not found — attempting to extract SVG from DOM...", file=sys.stderr)
                svg_element = page.locator("svg").first
                svg_content = svg_element.evaluate("el => el.outerHTML")

                if not svg_content or len(svg_content) < 100:
                    print("Error: Could not extract SVG from Napkin.ai. The UI may have changed.", file=sys.stderr)
                    sys.exit(2)

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(svg_content)
                print(f"SVG extracted from DOM and saved to: {output_path}", file=sys.stderr)

        except PlaywrightTimeout as e:
            print(f"Error: Browser timeout — {e}", file=sys.stderr)
            # Save a screenshot for debugging
            debug_path = output_path.replace(".svg", "_debug.png")
            page.screenshot(path=debug_path)
            print(f"Debug screenshot saved to: {debug_path}", file=sys.stderr)
            sys.exit(2)
        finally:
            browser.close()

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate infographic via Napkin.ai")
    parser.add_argument("--text", required=True, help="Text content describing what to visualize")
    parser.add_argument("--title", required=True, help="Title for the infographic")
    parser.add_argument("--output", required=True, help="Output path for the SVG file (e.g. .tmp/infographic_1.svg)")
    args = parser.parse_args()

    if not args.text.strip():
        print("Error: --text cannot be empty", file=sys.stderr)
        sys.exit(3)

    result_path = generate_infographic(args.text.strip(), args.title.strip(), args.output)
    print(result_path)


if __name__ == "__main__":
    main()
