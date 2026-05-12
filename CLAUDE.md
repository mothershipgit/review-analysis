# Reviews Analysis — Project Memory

> Living document. Update after every architecture change, new dashboard, or pattern discovered.

## Purpose

Per-product Amazon review analysis dashboards in a sidebar-navigated hub. Each product opens a 2-tab view:
1. **Reviews VOC** — sentiment split, customer profile (Who/When/Where/What), usage scenarios, neg/pos themes with English-translated quotes, buyers motivation, customer expectations, full review browser with originals.
2. **Marketing Deep-Dive** — competitor overview grid, claims matrix, claim-frequency bars, VOC↔claims gap analysis, whitespace opportunities, saturation, strategic recommendations.

## Deployment

- **Repo:** https://github.com/mothershipgit/review-analysis (public)
- **Live URL:** https://mothershipgit.github.io/review-analysis/
- **Hosting:** GitHub Pages (main branch root)
- **Auth:** Firebase + Google Sign-In with email allow-list. Reuses the **`cases-tracker-dc2f2`** Firebase project (same one as the Cases dashboard) — `mothershipgit.github.io` is already an authorised domain there. Allow-list is the same 12 `@themothership.ai` accounts used by Cases.
- **Auth code:** shared `js/auth.js` included by all 4 HTML files (root hub + 3 standalones). Detects mode automatically — full overlay UI on the hub, redirect-message on standalones if hit directly without sign-in.

## Tech stack

- Vanilla HTML + JS + CSS, no build tools, no framework
- Chart.js 4.4.4 + ChartDataLabels 2.2.0 (CDN)
- Firebase 10.12.0 compat SDK (auth-only — no Realtime DB usage)
- Static files — works on `file://` (limited) and via `python -m http.server` (full functionality)
- Hub renders each product as an iframe pointing to `dashboards/{id}/index.html`

## Architecture

| Layer | File(s) |
|-------|---------|
| Hub shell | root `index.html` + `js/hub.js` + `css/hub.css` |
| Auth | `js/auth.js` (loaded by all 4 HTMLs) |
| Sidebar registry | root `config.json` — one entry per product |
| Per-product standalone | `dashboards/{id}/index.html` (self-contained, fetches its own data) |
| Per-product analysis data | `dashboards/{id}/dashboard.json` (VOC + Marketing Deep-Dive) |
| Source review data | `reviews/{ASIN}-{MARKET}-Reviews.json` (one per dashboard, format: `[{title, date, author, review}]`) |
| Competitor master list | `data/DETOX + LAX TOP COMPETITORS.xlsx` (top-5 per market per product family — gitignored) |

Each standalone fetches **two** files at load:
1. Its own `dashboard.json` (VOC + MDD analysis: themes, customer profile, quotes, insights, competitor data)
2. The source reviews JSON at `../../reviews/{ASIN}-{MARKET}-Reviews.json` (raw reviews for the Browser tab)

The standalone runs a multilingual sentiment + theme classifier in JS at load time on each raw review (rule-based regex covering DE/ES/IT/FR/EN). No pre-tagging required.

## Products (live as of 2026-05-06)

| ID | Title | ASIN | Market | Reviews | Pos / Neg / Neu | VOC | MDD |
|----|-------|------|--------|---------|-----------------|-----|-----|
| `detox-de` | Detox DE | B0B6GHYP1V | DE | 304 | 42% / 48% / 10% | ✅ | ✅ (5 competitors, curated) |
| `lax-de` | Lax DE | B0BM1WPXC5 | DE | 326 | 47% / 44% / 10% | ✅ | ✅ (5 competitors) |
| `lax-fr` | Lax FR | B0BM1WPXC5 | FR | 327 | 48% / 43% / 10% | ✅ | ✅ (5 competitors) |
| `inositol-uk` | Inositol Caps UK | TBD | UK | 363 | 63% / 26% / 11% | ✅ | ⏸ |
| `inositol-de` | Inositol Caps DE | TBD | DE | 367 | 60% / 30% / 10% | ✅ | ⏸ |
| `inositol-fr` | Inositol Caps FR | TBD | FR | 341 | 52% / 37% / 10% | ✅ | ⏸ |
| `inositol-es` | Inositol Caps ES | TBD | ES | 455 | 51% / 36% / 13% | ✅ | ⏸ |
| `inositol-it` | Inositol Caps IT | TBD | IT | 376 | 65% / 26% / 9% | ✅ | ⏸ |
| `menositol-uk` | Menositol UK | TBD | UK | 261 | 60% / 27% / 12% | ✅ | ⏸ |
| `menositol-de` | Menositol DE | TBD | DE | 218 | 57% / 32% / 11% | ✅ | ⏸ |
| `menositol-fr` | Menositol FR | TBD | FR | 136 | 45% / 42% / 13% | ✅ | ⏸ |
| `menositol-es` | Menositol ES | TBD | ES | 252 | 69% / 20% / 11% | ✅ | ⏸ |
| `menositol-it` | Menositol IT | TBD | IT | 230 | 69% / 24% / 7% | ✅ | ⏸ |

**Menositol VOC complete (2026-05-12):** All 5 markets analyzed (1,097 reviews total). Sentiment: UK 60/27/12, DE 57/32/11, FR 45/42/13, ES 69/20/11, IT 69/24/7. ASINs still TBD — user to provide.

**Menositol language profile:** Same multilingual cross-pool pattern as Inositol — Spanish-led brand, so even UK file is only ~12-14% native English (~38-40% ES, ~22-24% IT, ~15-17% FR). ES is the home market (~70% native ES) and shows highest positive skew. FR is the most polarised market (44.9 pos / 41.9 neg — closest split of all 5 EU markets).

**Inositol VOC complete (2026-05-11):** All 5 markets analyzed. ASINs still TBD — user to provide. Reviews JSONs at project root with placeholder name `INOSITOL-{MARKET}-Reviews.json`. Once ASINs known, rename files + update fetch URLs in HTML.

**Inositol language profile:** All 5 files are heavily multilingual (cross-marketplace pooling from a Spanish-origin brand). Native-language share is typically 25-55% with heavy ES/IT/FR cross-pool. Even the UK file is only ~13% English — ~71% comes from ES/IT/FR cross-pool. Frame language in cpSummary honestly per market.

### Lax DE vs Lax FR — file overlap structure

**Same ASIN, separate dashboards** because competitor sets differ between markets — Marketing Deep-Dive analyses are legitimately separate. The two source JSONs share most reviews because Amazon EU pools cross-marketplace reviews on each product detail page.

| Component | Count | Language |
|---|---|---|
| Shared multilingual cross-marketplace pool (in BOTH files, byte-identical) | **263** | DE/ES/IT/FR/EN mix |
| Unique to Lax DE | 63 | All German |
| Unique to Lax FR | 64 | All French |

The shared pool dominates the analysis. Market-specific differences come from the 63/64 native-language tail. **Don't merge** — Marketing Deep-Dive needs to be per-market because competitors differ.

### Detox DE — language profile

The Spanish-led brand (CNC / QSTA Labs) means Amazon EU's cross-marketplace pooling brings in **heavy ES/IT/FR reviews alongside German ones**. The 304-review file is genuinely multilingual — not a single-language file with occasional cross-pool entries.

## Conventions

- **No star ratings.** Source scrape doesn't include them; user explicitly opted out. Sentiment is AI-classified (positive / negative / neutral) on text alone.
- **Output language: English.** All themes, summaries, customer profile labels, strategic insights are in English. Quotes are translated to English in the analysis sections. **Originals are preserved in the Review Browser** — no translation there.
- Dashboard IDs: `kebab-case`, match folder names.
- Sidebar entries grouped under `"detailed"` in `config.json` (the only group used by this project).
- Standalone HTML is self-contained — no external CSS/JS imports except CDN-hosted Chart.js, Firebase SDK, and `../../js/auth.js`.
- ASIN review JSON files live in the `reviews/` folder at project root (not inside per-dashboard folders) — the standalone fetches them via `../../reviews/`. **Refactored 2026-05-12** from previous flat-root layout.

## dashboard.json schema

```json
{
  "id": "detox-de",
  "title": "...", "subtitle": "...",
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
  "sentimentFilters": [{ "value", "label" }, ...],

  "marketingDeepDive": {
    "marketplace": "Amazon DE",
    "totalCompetitors": 9,
    "currency": "€",
    "intro": "...",
    "userProduct": { "asin", "brand", "title", "price", "bsr", "nicheBsr", "niche", "size", "image", "themes":[] },
    "competitors": [{ "asin", "brand", "title", "price", "bsr", "nicheBsr", "niche", "size", "image", "themes":[], "highlight" }, ...9],
    "claimsMatrix": {
      "themes": [{ "value", "label" }, ...15],
      "rows":   [{ "asin", "brand", "isUser?", "cells":[0/1, ...] }, ...10]
    },
    "claimsSummary": [{ "label", "count", "pct", "topBrands":[] }, ...15],
    "vocGap": [{ "vocTopic", "customerConcernPct", "addressedByCount", "addressedByBrands":[], "gapSeverity":"HIGH|MEDIUM|LOW", "whitespace" }, ...8],
    "whitespaceOpportunities": [{ "opportunity", "rationale", "evidence" }, ...4-5],
    "saturation": [{ "label", "saturationPct", "advice" }, ...3-5],
    "strategicRecommendations": [{ "type", "finding", "implication", "badgeBg", "badgeColor" }, ...4-6]
  }
}
```

- VOC percentages within `negativeTopics` should sum to ~100% (shares of the **negative** subset); same for `positiveTopics`.
- `usageScenarios`, `buyersMotivation`, `customerExpectations` percentages sum to ~100% across each section.
- `cpWho/When/Where/What` `pos[]` and `neg[]` are review counts, not percentages.
- MDD `claimsMatrix.rows` includes the user's own product as `isUser: true` so the renderer can highlight it.

## SP-API workflow for Marketing Deep-Dive

### Source of competitor ASINs

`data/DETOX + LAX TOP COMPETITORS.xlsx` is the single source of truth. Maintained manually by the user, **gitignored**, read locally with `openpyxl`. Layout:

```
DETOX block:
  Row 0 header: DETOX | Competitor 1..5
  Rows 1-5:    one row per market (ES, DE, IT, FR, UK) with 5 ASINs

(blank separator row)

LAX block:
  Row 7 header: LAX | Competitor 1..5
  Rows 8-12:   one row per market
```

The user will append new product-family blocks (separator + header + 5 market rows) as new dashboards are added. **Read this file first** when populating any MDD — only ask the user for ASINs if the relevant block is missing.

### Live SP-API lookups

- `mcp__amazon-sp-api__get_listing_by_asin` — full attributes (title, brand, bullets, images, BSR, niche category) per ASIN. Marketplace param: `DE` / `FR` / `IT` / `ES` / `UK` / `US`.
- `mcp__amazon-sp-api__get_competitive_pricing` — batched (up to 20 ASINs per call) for price + offer count.

**Caveat:** ASINs not listed on the requested marketplace return `not found in marketplace(s)` errors. Many EU competitor ASINs are listed on `ES` or `FR` only and visible on `DE` only via cross-marketplace pooling — they won't return data when querying DE. For Detox DE, 4/12 of an early list returned data on DE; the corrected list of 10 DE-listed ASINs returned 9/10. The xlsx is curated to avoid this — ASINs there should match the marketplace listed.

## Strategic findings (cross-product)

1. **Detox DE has a positioning mismatch.** ~32% of negative reviewers say "no effect" but most came specifically for weight loss — the product actually delivers bloating relief + transit regularity.
2. **Detox DE has a safety flag.** ~10% of negatives report severe systemic reactions (vertigo, panic, projectile vomiting, skin rash). Higher than typical for a supplement.
3. **"Natural alternative to chemical laxatives" is the strongest positive across both Lax markets.** Customers actively name Laxoberal, Movicol, magnesium citrate, suppositories. Lead with this in copy.
4. **Lax FR over-indexes on travel-constipation and post-bypass surgery use cases.** Lax DE over-indexes on medication-induced constipation and elderly-relative purchases. Localise messaging.
5. **Operational issues are repeated across all 3 products** — capsule count discrepancies, broken seals, half-empty bottles, tiny labelling.
6. **Review-for-freebie scheme is publicly called out** by 3-4% of Detox DE negatives. Risk to long-term rating credibility.
7. **Bloating relief + Regularity are unowned in the Detox DE competitive set.** 0/5 curated competitors lead with these — clean whitespace lead-claim opportunity (highest-leverage finding from the Detox DE MDD).
8. **Detox DE sits at the probiotic ↔ detox intersection.** 4/5 competitors are pure probiotics (Kijimea, Nature Love, OMNi BiOTiC, NATURTREU); 1/5 is pure liver-detox (natural elements). CNC Detox is the only product combining both.
9. **Lax DE: the 'natural alternative' angle is wide-open.** 0/5 DE competitors claim it. The DE top-5 splits into 2 chemical pharmacy laxatives (Dulcolax/Macrogol) + 3 bloating/enzyme products (STADA/LEFAX/sanotact). LAX+ is the only natural multi-herb laxative in the set.
10. **Lax FR is the inverse: 'natural alternative' is saturated (5/5 claim it).** Don't translate DE copy. Differentiate via capsule format (0/5 competitors offer it — they sell bars/tablets/tea) + 7-ingredient formulation depth + travel-ready use case.
11. **Natural Sprint (FR competitor B0D474GHRR) is the closest direct threat to LAX+.** 8 herbs vs LAX+'s 7, made in Italy, undercuts price (€7 vs €25). Differentiate on professional branding + QR support service.
12. **Inositol — silent reformulation is a brand-wide trust crisis (all 5 markets independently flag it).** Long-time buyers + MTHFR-aware customers caught two changes: D-chiro reduced from ~100mg→40mg (40:1 ratio broken, sometimes to 100:1), AND methylfolate replaced with folic acid. Spans UK/DE/FR/ES/IT — not a market-specific quirk. They're actively warning others ("Reddit threads", "not what I bought before"). Highest-leverage fix: either restore the original spec or transparently re-launch as "Reformulated" with clinical rationale.
13. **Inositol — cycle regulation + hormonal acne are the true repeat-purchase drivers (35-45% of positives across all 5 markets).** Current listing leads with "4100mg 9-in-1" — too generic, hides the emotional outcome. Lead instead with "Restore your cycle + clear hormonal acne". Bigger than fertility, bigger than insulin resistance, bigger than value.
14. **Inositol — "6 capsules = 4100mg daily" labeling is a cascading 1-star generator (~18% of negatives across markets).** Customers expect per-capsule dose, feel deceived, bottle lasts 30 days, value collapses. Copy fix, not product fix — disclose daily-dose math up front in the listing headline.
15. **Inositol — the QR-code WhatsApp dosing support is praised across all 5 markets as a real differentiator.** Currently buried in listing copy. Promote to top-3 bullet.
16. **Menositol — hot flushes + night sweats relief is the #1 positive driver in all 5 markets (28-36% of positives) AND the #1 unfulfilled expectation in all 5 (31-38% of negatives).** Product polarises sharply on the same outcome. The brand cannot lead with anything else without rebuilding the formula — but it can manage expectations (4-12 week curve) and offer an honoured 90-day refund to convert lukewarm one-bottle buyers.
17. **Menositol — capsule count shortage (59/58 vs labelled 60) is documented across all 5 markets including by 2-year subscribers.** Same operational defect as Inositol — brand-wide fill-line / QC issue at the contract manufacturer. Highest-leverage cleanup: fix the line + over-fill to 62.
18. **Menositol — review-for-freebie scheme exposed publicly in IT, ES, DE, FR.** Same pattern as Inositol — credibility decay risk + Amazon TOS exposure. Phase out coupon-for-review now.
19. **Menositol — '100% money-back guarantee on empty bottle' is called fraud/escroquerie across FR/IT/ES.** WhatsApp goes silent on refund requests. Either honour the guarantee or remove the claim — biggest single trust hit on the listing.
20. **Menositol — PCOS / hormonal-acne off-label use is a real second TAM (5-8% across all 5 markets).** Younger women (30-40) drawn by myo + D-chiro inositol content write the longest, most emotional 5-star reviews. Consider sister-SKU or split-listing — they're winning these buyers by accident.
21. **Menositol — FR is the outlier market (45 pos / 42 neg — closest split).** The other 4 markets are 57-69% positive. FR is more polarised, more sensitive to price, and the only market where "no effect" almost equals "real effect" in volume. Treat FR copy / pricing differently — likely needs a comparison vs Ménophytea + Sérélys built into the listing.
22. **Menositol — wrong-time-of-day dosing is fixable copy-only insight.** ~9-10% of negatives report insomnia because they take it in the evening. Vitamin C + ginseng + ashwagandha are stimulating. Single label change ('morning and lunch — avoid evening dosing') defuses these reviews and converts them into "good for daytime energy" praise.
23. **Menositol — silhouette/weight-loss messaging contradicts the data.** Several reviewers report weight gain on the product. The listing should reposition silhouette as "menopausal bloating relief" rather than weight loss — sets achievable expectations and removes a recurring 1-star generator.

## Workflow patterns

### Add a new product dashboard
Use the `review-analysis` skill (Action 1). Inputs: ASIN, marketplace, product name, path to a `*-Reviews.json` file. Skill creates the folder, clones the standalone HTML, registers in root `config.json`, optionally runs the VOC analysis.

### Refresh VOC for an existing dashboard
Re-run the analysis when the source JSON is updated. Skill reads the new reviews, re-synthesises themes / customer profile / quotes, overwrites `dashboard.json`. The HTML doesn't need to change.

### Populate the Marketing Deep-Dive tab
1. Read competitor ASINs from `data/DETOX + LAX TOP COMPETITORS.xlsx` (top-5 per market per product family). Only ask the user if the block is missing.
2. Use SP-API (`get_listing_by_asin` + `get_competitive_pricing`) to fetch live data.
3. Tag each competitor's claims across ~15 themes (multi-strain probiotic, bloating relief, gentle, weight loss, natural, made in DE/EU, lab tested, etc.).
4. Build the `marketingDeepDive` block in `dashboard.json` with: competitor cards, claims matrix (incl. user product), claim-frequency bars, VOC↔claims gap table, whitespace cards, saturation cards, strategic recommendations.
5. The standalone renderer (`renderMDD()` in each `dashboards/{id}/index.html`) auto-displays — no HTML edit needed.

### Publish updates
Each `dashboard.json` change → `git add . && git commit && git push`. GitHub Pages auto-rebuilds in ~60s.

## Local dev

```bash
cd "projects/Reviews Analysis"
python -m http.server 8765
# Open http://localhost:8765/
```

`fetch('config.json')` requires HTTP — opening `index.html` directly via `file://` will not work. Firebase auth also requires a real origin (works on `localhost` and `mothershipgit.github.io`).

## Known issues

- **Excel lock files (`~$*.xlsx`)** appear when the user has a review xlsx open. They block `rm` until Excel is closed. Excluded from git via `.gitignore`.
- **Competitor xlsx is gitignored.** `data/DETOX + LAX TOP COMPETITORS.xlsx` stays local — read with `openpyxl`, never commit.
- **Sentiment classifier is rule-based regex.** Multilingual but not perfect — long mixed reviews (some pos + some neg phrases) default to `neutral`. Good enough for the Browser filter; the analytical sections use AI-synthesised counts, not the regex output.
- **SP-API marketplace mismatch.** ASINs listed only on a different EU marketplace (e.g. ES) return errors when querying DE — even though Amazon shows the product on DE via cross-pooling.

## Self-update rule

Update this file when:
- A new product dashboard is added (extend the Products table)
- VOC data is refreshed (update sentiment %, note the date)
- Marketing Deep-Dive is populated for any product (mark ✅ in the table, append strategic findings)
- Architecture changes (e.g., sentiment classifier becomes ML-based, source data format changes, hosting moves)
- Auth allow-list changes (sync with `js/auth.js`)
