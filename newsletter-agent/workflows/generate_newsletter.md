# Workflow: Generate Newsletter — Your Brand

## Objective
Research a topic, write a polished newsletter, generate infographics via Napkin.ai,
render it as a branded HTML email, and optionally send it via Gmail.

## Brand
- **Name**: Your Brand
- **Logo**: `brand_asset/logo.png` (auto-embedded as base64 by the renderer)
- **Palette**: Deep indigo `#0F0C29` / `#1E1B4B`, Periwinkle `#818CF8`, Amber `#F59E0B`
- **Voice**: Smart, direct, no hype — for tech-literate professionals

---

## Required Inputs

| Input | Required | Default |
|-------|----------|---------|
| `topic` | Yes | — |
| `audience` | No | tech-literate professionals |
| `tone` | No | smart, direct, no hype |
| `send_to` | No | (omit to render HTML only) |
| `issue_number` | No | 1 |

---

## Tools

| Tool | Script | Purpose |
|------|--------|---------|
| Research | `tools/research_topic.py` | Perplexity sonar-pro live web research |
| Infographics | `tools/generate_infographic.py` | Napkin.ai → SVG via Playwright |
| Renderer | `tools/render_newsletter_html.py` | Jinja2 → branded HTML file |
| Email | `tools/send_email_gmail.py` | Gmail API via Google OAuth |

---

## Phase 1: Intake & Planning

1. Confirm the topic. If ambiguous (e.g. "AI stuff"), ask for clarification.
2. Note any user-specified constraints: audience, tone, sections to include/exclude.
3. Determine the issue number (ask the user, or default to 1).
4. If `send_to` is provided, note the recipient list now.

---

## Phase 2: Research

Run the research tool with the confirmed topic:

```bash
python tools/research_topic.py --topic "EXACT TOPIC HERE" --depth deep
```

Parse the returned JSON. Verify it contains:
- `key_stats`: 3 items with real numeric values
- `findings`: 3-4 paragraphs
- `signals`: 4-5 items
- `resources`: 2-4 items with real URLs

If the JSON is malformed or missing fields, re-run once. If it fails again,
note which fields are missing and supplement from your own knowledge.

---

## Phase 3: Content Outline (Claude — no tools)

Read the research JSON and decide:

1. **Core narrative** — what is the single most important insight? This becomes the `big_idea` headline.
2. **Which 3 stats** go in `key_stats` — pick the most striking numbers.
3. **Deep dive focus** — which 1-2 findings have the most depth and nuance?
4. **What to watch** — select 4-5 signals that are specific and dated.
5. **Resources** — pick 2-4 that are genuinely useful (skip generic homepages).
6. **Infographic targets** — identify 1-2 data points that benefit from visualization:
   - Timelines (stages, deadlines, rollout dates)
   - Comparisons (before/after, A vs B, country vs country)
   - Distributions or breakdowns (market share, tier breakdown)
   - Trends with specific numbers

---

## Phase 4: Write Newsletter Content (Claude — no tools)

Write each section as valid HTML fragments (no `<html>`, `<head>`, or `<body>` tags).
Allowed tags: `<p>`, `<strong>`, `<em>`, `<a href="...">`, `<h3>`, `<ul>`, `<li>`.
All `<a>` tags must include: `style="color:#1E1B4B; font-weight:600;"`.

### big_idea (150-250 words)
- Open with a specific fact, event, or data point — NOT a vague statement like "AI is changing..."
- Make the "so what" explicit in the final 1-2 sentences
- `accent_color`: use `#4F46E5`

### key_stats (exactly 3)
- Each `value` must be a number: %, $, count, or date
- Each `label` must be under 10 words

### deep_dive (400-600 words)
- Use `<h3>` for 2-3 subheadings within the body_html
- Include at least one concrete example, case study, or named organization
- End with an implication or forward-looking statement

### what_to_watch (4-5 items)
- Each item must name a specific org, event, and approximate date
- Format: `[What] — [Organization], [Month Year]`
- Bad: "AI regulation will increase"
- Good: "EU AI Act Tier 1 compliance deadline — European Commission, August 2026"

### tools_resources (2-4 items)
- Only include real, verifiable URLs
- Description: one sentence on what it does and who it's for

---

## Phase 5: Generate Infographics

For each infographic identified in Phase 3, run:

```bash
python tools/generate_infographic.py \
  --text "DESCRIPTION OF WHAT TO VISUALIZE (2-4 sentences with specific data)" \
  --title "Infographic Title" \
  --output ".tmp/infographic_N.svg"
```

The tool logs in to Napkin.ai, pastes the text, waits for the AI visual to generate,
and exports the SVG. It prints the output path to stdout.

If the tool errors (timeout or UI change), fall back to writing a simple inline SVG
directly. The SVG must:
- Use `viewBox="0 0 520 280"` (fits the 520px email column)
- Use only: `#0F0C29`, `#1E1B4B`, `#818CF8`, `#A5B4FC`, `#F59E0B`, `#E5E7EB`, `#FFFFFF`
- Include no JavaScript and no external image references
- Include a title, axis labels, and a legend where relevant

Read the exported SVG file and include its content in the `infographics` section JSON.

---

## Phase 6: Subject Lines & Preview Text (Claude — no tools)

Generate 5 subject line options using these distinct hooks:
1. **Data-driven**: leads with a specific number or fact
2. **Urgency/deadline**: something happening soon
3. **Contrarian**: challenges the conventional take
4. **Curiosity gap**: withhold one key piece of information
5. **Reader benefit**: what the reader gains from reading

Rules:
- Max 60 characters (Gmail truncates beyond this on mobile)
- No ALL CAPS, no excessive punctuation
- No emoji unless the topic is light/consumer-facing

Generate 1 preview text (50-80 chars): a single sentence completing the subject line's thought.

Present the 5 options to the user and ask which to use.
If the user said "just send it" or similar, select the best-performing hook (usually #1 or #4).

---

## Phase 7: Assemble Content JSON

Assemble the complete content JSON matching this schema:

```json
{
  "meta": {
    "newsletter_name": "Your Brand",
    "issue_number": <number>,
    "date": "<Month DD, YYYY>",
    "topic": "<topic string>",
    "subject_lines": ["option 1", "option 2", "option 3", "option 4", "option 5"],
    "preview_text": "<50-80 char preview>",
    "sender_name": "Your Brand",
    "sender_email": "<auto-detected from Gmail OAuth>"
  },
  "sections": [
    {
      "id": "big_idea",
      "label": "This Week's Big Idea",
      "headline": "<headline>",
      "body_html": "<p>...</p>",
      "accent_color": "#4F46E5"
    },
    {
      "id": "key_stats",
      "label": "Key Stats",
      "headline": "By The Numbers",
      "stats": [
        {"value": "XX%", "label": "under 10 words"}
      ]
    },
    {
      "id": "deep_dive",
      "label": "Deep Dive",
      "headline": "<headline>",
      "body_html": "<p>...</p><h3>Subheading</h3><p>...</p>"
    },
    {
      "id": "infographics",
      "label": "Visualized",
      "items": [
        {
          "title": "<title>",
          "svg_code": "<svg ...>...</svg>",
          "caption": "Source: <publication>, <year>"
        }
      ]
    },
    {
      "id": "what_to_watch",
      "label": "What To Watch",
      "items": [{"text": "Event — Org, Month Year"}]
    },
    {
      "id": "tools_resources",
      "label": "Tools & Resources",
      "items": [{"name": "...", "url": "https://...", "description": "..."}]
    }
  ],
  "footer": {
    "unsubscribe_url": "https://yourbrand.example.com/unsubscribe",
    "physical_address": "Your Brand, [Address]",
    "copyright_year": <current year>
  }
}
```

Save this JSON to `.tmp/content_YYYYMMDD.json`.

---

## Phase 8: Render HTML

```bash
python tools/render_newsletter_html.py --content .tmp/content_YYYYMMDD.json
```

The tool prints the output HTML path to stdout. Confirm the file exists.

**If the tool errors:**
- `Validation error: meta.<field>` → add the missing field to the JSON
- `Validation error: footer.<field>` → CAN-SPAM required — fill in the footer fields
- `Template not found` → verify `tools/templates/newsletter.html.j2` exists
- `JSON parse error` → check for unescaped quotes or special characters in `body_html`

Tell the user the output path so they can open it in a browser to review.

---

## Phase 9: Email Delivery (conditional — only if `send_to` was provided)

### Step 9a — Confirm before sending
Tell the user:
- The subject line that will be used
- The recipient list (or count if long)
- The HTML file path

Ask: "Ready to send? Reply yes to proceed."

### Step 9b — Send

```bash
python tools/send_email_gmail.py \
  --html-file ".tmp/newsletter_YYYYMMDD_SLUG.html" \
  --to "email1@example.com,email2@example.com" \
  --subject "Chosen subject line" \
  --from-name "Your Brand"
```

On first run, a browser window will open for Google OAuth — authenticate and approve
the `gmail.send` scope. The token is saved to `token.json` for future runs.

Check stdout: `{"sent": N, "failed": 0, ...}`.
If `failed > 0`, read the `errors` array and report which addresses failed.

### Step 9c — Test send (recommended before list send)

Always send to yourself first with `--to "your-own-email@example.com"` and verify
the email renders correctly in Gmail before sending to a broader list.

---

## Edge Cases

| Situation | Handling |
|-----------|----------|
| Perplexity returns malformed JSON | Re-run once; if it fails again, supplement from Claude's knowledge |
| Napkin.ai login fails | Check NAPKIN_EMAIL/NAPKIN_PASSWORD in .env; a debug screenshot is saved to .tmp/ |
| Napkin.ai UI has changed | Fall back to writing inline SVG directly (see Phase 5) |
| Gmail OAuth scope missing | Delete token.json and re-run send_email_gmail.py to trigger fresh auth flow |
| Logo file not found | Renderer warns but continues; add logo.png to brand_asset/ |
| Paywalled source in research | Ignore that URL; rely on Perplexity's excerpt or Claude's knowledge |
| User wants different subject | Re-run Phase 9 only — no need to re-render HTML |
| HTML looks wrong in email | Check for unescaped special chars in body_html; validate at https://htmlemail.io/inline |

---

## Output Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| Research JSON | `.tmp/content_YYYYMMDD.json` | Full content object |
| Infographic SVGs | `.tmp/infographic_N.svg` | Source SVGs from Napkin.ai |
| Newsletter HTML | `.tmp/newsletter_YYYYMMDD_SLUG.html` | Final rendered output |
| Gmail token | `token.json` | OAuth credentials (gitignored) |
