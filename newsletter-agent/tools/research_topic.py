"""
Research a topic using Perplexity's sonar-pro model (live web search + synthesis).

Usage:
    python tools/research_topic.py --topic "AI regulation 2025" [--depth deep|standard]

Output (stdout): JSON research brief
Exit codes: 0=ok, 1=missing key, 2=API error, 3=bad args
"""

import argparse
import json
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

RESEARCH_PROMPT = """You are a research assistant preparing a briefing for a newsletter writer.
Research the following topic thoroughly using current sources and return a structured JSON response.

Topic: {topic}

Return ONLY valid JSON matching this exact schema (no markdown, no explanation, just the JSON object):
{{
  "topic": "{topic}",
  "summary": "2-3 sentence executive summary of the current state of this topic",
  "key_stats": [
    {{"value": "XX%", "label": "concise label under 10 words", "source": "publication or org name"}}
  ],
  "findings": [
    "paragraph 1 — detailed finding with specific facts",
    "paragraph 2 — another detailed finding",
    "paragraph 3 — third finding",
    "paragraph 4 — fourth finding (optional)"
  ],
  "signals": [
    "Specific upcoming event or development — Organization Name, Month Year",
    "Another signal with date and org"
  ],
  "resources": [
    {{"name": "Resource Name", "url": "https://...", "description": "one sentence on what it is and who it's for"}}
  ],
  "citations": [
    {{"title": "Article or Source Title", "url": "https://..."}}
  ]
}}

Requirements:
- key_stats: exactly 3 items with real numbers (%, $, counts, dates)
- findings: 3-4 paragraphs, each 60-120 words, grounded in specific facts
- signals: 4-5 items, each naming a specific org, event, and approximate date
- resources: 2-4 items with real, working URLs
- citations: 3-6 sources used in your research"""


def research(topic: str, depth: str = "deep") -> dict:
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("Error: PERPLEXITY_API_KEY not set in .env", file=sys.stderr)
        sys.exit(1)

    model = "sonar-pro" if depth == "deep" else "sonar"

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a precise research assistant. Always respond with valid JSON only. No markdown, no code blocks, no explanation — just the raw JSON object.",
            },
            {
                "role": "user",
                "content": RESEARCH_PROMPT.format(topic=topic),
            },
        ],
        "temperature": 0.2,
        "max_tokens": 3000,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(PERPLEXITY_API_URL, json=payload, headers=headers, timeout=60)
    except requests.exceptions.RequestException as e:
        print(f"Error: Network request failed — {e}", file=sys.stderr)
        sys.exit(2)

    if response.status_code != 200:
        print(f"Error: Perplexity API returned {response.status_code}: {response.text}", file=sys.stderr)
        sys.exit(2)

    try:
        content = response.json()["choices"][0]["message"]["content"].strip()
        # Strip any accidental markdown fences
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        result = json.loads(content)
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error: Failed to parse Perplexity response as JSON — {e}", file=sys.stderr)
        print(f"Raw response: {response.text[:500]}", file=sys.stderr)
        sys.exit(2)

    return result


def main():
    parser = argparse.ArgumentParser(description="Research a topic via Perplexity sonar-pro")
    parser.add_argument("--topic", required=True, help="Topic to research")
    parser.add_argument("--depth", choices=["deep", "standard"], default="deep",
                        help="Research depth: deep=sonar-pro, standard=sonar")
    args = parser.parse_args()

    if not args.topic.strip():
        print("Error: --topic cannot be empty", file=sys.stderr)
        sys.exit(3)

    result = research(args.topic.strip(), args.depth)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
