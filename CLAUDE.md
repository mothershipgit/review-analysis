# Reviews Analysis — Project Memory

> Living document. Update after every architecture change, new dashboard, or pattern discovered.

## Purpose

Per-product Amazon review analysis dashboards in a sidebar-navigated hub. Each product opens a 2-tab view:
1. **Reviews VOC** — sentiment split, customer profile (Who/When/Where/What), usage scenarios, neg/pos themes with English-translated quotes, buyers motivation, customer expectations, full review browser with originals.
2. **Marketing Deep-Dive** — competitor claims breakdown, claims matrix, VOC↔claims gap analysis, whitespace opportunities, strategic recommendations. **Skeleton until competitor data is provided.**

## Tech stack

- Vanilla HTML + JS + CSS, no build tools, no framework
- Chart.js 4.4.4 + ChartDataLabels 2.2.0 (CDN)
- Static files — works on `file://` (limited) and via `python -m http.server` (full functionality)
- Hub renders each product as an iframe pointing to `dashboards/{id}/index.html`

## Architecture

| Layer | File(s) |
|-------|---------|
| Hub shell | root `index.html` + `js/hub.js` + `css/hub.css` |
| Sidebar registry | root `config.json` — one entry per product |
| Per-product standalone | `dashboards/{id}/index.html` (self-contained, fetches its own data) |
| Per-product VOC data | `dashboards/{id}/dashboard.json` (analysis output) |
| Source review data | root `{ASIN}-{MARKET}-Reviews.json` (one per product, format: `[{title, date, author, review}]`) |

Each standalone fetches **two** files at load:
1. Its own `dashboard.json` (analysis: themes, customer profile, quotes, insights)
2. The source reviews JSON at `../../{ASIN}-{MARKET}-Reviews.json` (raw reviews for the Browser tab)

The standalone runs a multilingual sentiment + theme classifier in JS at load time on each raw review (rule-based regex covering DE/ES/IT/FR/EN). No pre-tagging required.

## Products (live as of 2026-04-29)

| ID | Title | ASIN | Market | Reviews | Pos / Neg / Neu | Source JSON |
|----|-------|------|--------|---------|-----------------|-------------|
| `detox-de` | Detox DE | B0B6GHYP1V | DE | 304 | 42% / 48% / 10% | `B0B6GHYP1V-DE-Reviews.json` |
| `lax-de` | Lax DE | B0BM1WPXC5 | DE | 326 | 47% / 44% / 10% | `B0BM1WPXC5-DE-Reviews.json` |
| `lax-fr` | Lax FR | B0BM1WPXC5 | FR | 327 | 48% / 43% / 10% | `B0BM1WPXC5-FR-Reviews.json` |

**Same ASIN, separate dashboards for Lax DE and Lax FR** — the two files share ~80% of reviews due to Amazon EU cross-marketplace pooling, but **competitor sets differ between markets**, so the Marketing Deep-Dive tab makes them legitimately separate analyses. Don't merge.

Reviews are **multilingual within each marketplace file** — Detox DE for example contains DE / ES / IT / FR / EN / CA. Amazon shows reviews from across the EU on each marketplace.

## Conventions

- **No star ratings.** The source scrape doesn't include them, and the user explicitly opted out of star distribution. Sentiment is AI-classified (positive / negative / neutral) on text alone.
- **Output language: English.** All themes, summaries, customer profile labels, strategic insights are in English. Quotes are translated to English in the analysis sections. **Originals are preserved in the Review Browser** — no translation there.
- Dashboard IDs: `kebab-case`, match folder names.
- Sidebar entries grouped under `"detailed"` in `config.json` (the only group used by this project).
- Standalone HTML is self-contained — no external CSS/JS imports except CDN-hosted Chart.js.
- ASIN review JSON files live at the project root (not inside per-dashboard folders) — the standalone fetches them via `../../`.

## VOC structure (dashboard.json schema)

```json
{
  "id": "detox-de",
  "title": "...",
  "subtitle": "...",
  "asin": "...", "marketplace": "DE",
  "reviewsFile": "../../...-Reviews.json",

  "totalReviews": 304,
  "posCount": 128, "negCount": 145, "neuCount": 31,
  "posPct": "42.1", "negPct": "47.7", "neuPct": "10.2",

  "cpSummary": "...HTML allowed for <strong>...</strong>...",
  "cpWho":   { "labels": [...6 segments], "pos": [...], "neg": [...] },
  "cpWhen":  { "labels": [...], "pos": [...], "neg": [...] },
  "cpWhere": { "labels": [...], "pos": [...], "neg": [...] },
  "cpWhat":  { "labels": [...], "pos": [...], "neg": [...] },

  "usageScenarios": [{ "label", "reason", "pct" }, ...8-10],
  "csSummary": "...",
  "negativeTopics": [{ "label", "reason", "pct", "bullets":[], "quotes":[] }, ...6-9],
  "negativeInsights": [{ "type", "finding", "implication", "badgeBg", "badgeColor" }, ...3-5],
  "positiveTopics": [...same shape, 6-8],
  "positiveInsights": [...same shape, 3-4],
  "buyersMotivation": [{ "label", "reason", "pct" }, ...7-8],
  "customerExpectations": [{ "label", "reason", "pct" }, ...7-8],

  "themeFilters": [{ "value", "label" }, ...],
  "sentimentFilters": [{ "value", "label" }, ...]
}
```

- Percentages within `negativeTopics` should sum to ~100% (they describe shares of the **negative** review subset), same for `positiveTopics`.
- `usageScenarios`, `buyersMotivation`, `customerExpectations` percentages should sum to ~100% across each section.
- `cpWho/When/Where/What` `pos[]` and `neg[]` are review counts (not percentages), one per label.

## Strategic findings (cross-product)

1. **Detox DE has a positioning mismatch.** ~32% of negative reviewers say "no effect" but most of them came specifically for weight loss — the product actually delivers bloating relief + transit regularity. Reposition to fix.
2. **Detox DE has a safety flag.** ~10% of negatives report severe systemic reactions (vertigo, panic, projectile vomiting, skin rash). Higher than typical for a supplement.
3. **"Natural alternative to chemical laxatives" is the strongest positive across both Lax markets.** Customers actively name Laxoberal, Movicol, magnesium citrate, suppositories — the alternatives they wanted to escape. Lead with this in copy.
4. **Lax FR over-indexes on travel-constipation and post-bypass surgery use cases.** Lax DE over-indexes on medication-induced constipation and elderly-relative purchases. Localise messaging.
5. **Operational issues are repeated across all 3 products** — capsule count discrepancies, broken seals, half-empty bottles, tiny labelling. Cheap to fix; lost reviews are not.
6. **Review-for-freebie scheme is publicly called out** by 3-4% of Detox DE negatives. Risk to long-term rating credibility.

## Workflow patterns

### Add a new product dashboard
Use the `review-analysis` skill. Inputs: ASIN, marketplace, product name, path to a `*-Reviews.json` file. Skill creates the folder, clones the standalone HTML, registers in root `config.json`, optionally runs the VOC analysis.

### Refresh VOC for an existing dashboard
Re-run the analysis when the source JSON is updated. Skill reads the new reviews, re-synthesises themes / customer profile / quotes, overwrites `dashboard.json`. The HTML doesn't need to change.

### Populate the Marketing Deep-Dive tab
Requires competitor data (top ASINs per market with scraped titles, bullets, images). When the user provides competitor JSON / CSV, the MDD analysis tags claims by theme, cross-references with VOC findings, and emits a populated MDD section. Currently all 3 products show the MDD skeleton.

### Publish to GitHub
Public repo named `review-analysis`, hub gated by client-side JS password prompt before `index.html` content loads (option B chosen by user — code is visible but dashboard requires password). `.gitignore` excludes `~$*.xlsx` Excel lock files.

## Files NOT used by this project (left over from Console copy)

- `templates/` — used by `hub.js` for non-standalone dashboards. Empty for now, harmless.
- `scripts/build_voc.py` — original Console VOC builder (English regex + assumes star ratings). NOT used here. Phase B analysis is done in-conversation.
- `dashboards/_template-multisegment-eu/` — Console's multi-country template, not used. Safe to delete.
- `js/data-engine.js` — CSV parser used by Console for X-Ray data. Loaded by hub.js but not exercised; harmless.

## Local dev

```bash
cd "projects/Reviews Analysis"
python -m http.server 8765
# Open http://localhost:8765/
```

`fetch('config.json')` requires HTTP — opening `index.html` directly via `file://` will not work.

## Known issues

- **Excel lock files (`~$*.xlsx`)** appear when the user has a review xlsx open. They block `rm` until Excel is closed. Excluded from git via `.gitignore`.
- **Sentiment classifier is rule-based regex.** Multilingual but not perfect — long mixed reviews (some pos + some neg phrases) default to `neutral`. Good enough for the Browser filter; the analytical sections use AI-synthesised counts not the regex output.

## Self-update rule

Update this file when:
- A new product dashboard is added
- VOC data is refreshed (note the date)
- Architecture changes (e.g., the sentiment classifier becomes ML-based, or the source data format changes)
- Marketing Deep-Dive is populated for any product
