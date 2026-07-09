"""
Render a newsletter HTML file from a content JSON file using the Jinja2 template.

Usage:
    python tools/render_newsletter_html.py --content .tmp/content_20250430.json

Output (stdout): absolute path to the rendered HTML file
Exit codes: 0=ok, 1=missing/invalid content file, 2=template error, 3=bad args
"""

import argparse
import base64
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

TEMPLATE_DIR = Path(__file__).parent / "templates"
TEMPLATE_FILE = "newsletter.html.j2"
LOGO_PATH = Path(__file__).parent.parent / "brand_asset" / "logo.png"

REQUIRED_META_FIELDS = ["newsletter_name", "issue_number", "date", "topic",
                        "preview_text", "sender_name", "sender_email"]
REQUIRED_FOOTER_FIELDS = ["unsubscribe_url", "physical_address", "copyright_year"]


def validate_content(content: dict) -> list[str]:
    errors = []

    meta = content.get("meta", {})
    for field in REQUIRED_META_FIELDS:
        if not meta.get(field):
            errors.append(f"meta.{field} is required and cannot be empty")

    footer = content.get("footer", {})
    for field in REQUIRED_FOOTER_FIELDS:
        if not footer.get(field):
            errors.append(f"footer.{field} is required (CAN-SPAM compliance)")

    if not content.get("sections"):
        errors.append("sections array is required and cannot be empty")

    return errors


def make_slug(topic: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "", topic.lower().replace(" ", ""))
    return slug[:8] if slug else "newsletter"


def load_logo_base64() -> str | None:
    if LOGO_PATH.exists():
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    print(f"Warning: Logo not found at {LOGO_PATH} — header will render without logo", file=sys.stderr)
    return None


def render(content: dict, output_dir: str = ".tmp") -> str:
    errors = validate_content(content)
    if errors:
        for e in errors:
            print(f"Validation error: {e}", file=sys.stderr)
        sys.exit(1)

    # Inject brand logo as base64 so it embeds inline (no external hosting needed)
    content.setdefault("meta", {})["logo_base64"] = load_logo_base64()

    try:
        env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=False)
        template = env.get_template(TEMPLATE_FILE)
    except TemplateNotFound:
        print(f"Error: Template not found at {TEMPLATE_DIR / TEMPLATE_FILE}", file=sys.stderr)
        sys.exit(2)

    try:
        rendered_html = template.render(**content)
    except Exception as e:
        print(f"Error: Template rendering failed — {e}", file=sys.stderr)
        sys.exit(2)

    date_str = datetime.now().strftime("%Y%m%d")
    slug = make_slug(content["meta"].get("topic", ""))
    filename = f"newsletter_{date_str}_{slug}.html"

    output_path = Path(output_dir) / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    return str(output_path.resolve())


def main():
    parser = argparse.ArgumentParser(description="Render newsletter HTML from content JSON")
    parser.add_argument("--content", required=True, help="Path to content JSON file")
    parser.add_argument("--output-dir", default=".tmp", help="Output directory (default: .tmp)")
    args = parser.parse_args()

    content_path = Path(args.content)
    if not content_path.exists():
        print(f"Error: Content file not found: {args.content}", file=sys.stderr)
        sys.exit(3)

    try:
        with open(content_path, "r", encoding="utf-8") as f:
            content = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in content file — {e}", file=sys.stderr)
        sys.exit(1)

    output_path = render(content, args.output_dir)
    print(output_path)


if __name__ == "__main__":
    main()
