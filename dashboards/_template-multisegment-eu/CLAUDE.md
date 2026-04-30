> Living document — update after every structural change or new pattern.

# Multi-Segment EU Dashboard Template

## What this is

A configurable copy of [eu-lice-treatment-analysis](../eu-lice-treatment-analysis/) with:

- **Treatment Methods tab removed** (was lice-specific, kept the source dashboard at 8 tabs but every other dashboard built from this template will skip it)
- **Segments parameterized** — change one Python list and the dashboard regenerates with one Market Structure + one Reviews VOC + one Marketing Deep-Dive tab per segment
- **All real data stripped** — placeholder X-Ray rows in `data/x-ray/{DE,FR,IT,ES}/product {CODE}.csv` so the build runs out of the box

Default config: 3 segments (`Lure`, `Electric`, `Sticky`) → **10 tabs**:

| Tab | How it's generated |
|-----|--------------------|
| Main Segments | Always present. Loops `D.segments` to render N-segment KPI cards, pies, brand share grids. |
| Market Structure (Lure / Electric / Sticky) | One tab per segment. Reads X-Ray rows whose `Focus`/`Segment` column matches the segment name. |
| Reviews VOC — Lure / Electric / Sticky | One tab per segment. Reads `reviews/{CODE}/{Segment}/voc.json`. Empty state if missing. |
| Marketing Deep-Dive — Lure / Electric / Sticky | One tab per segment. Reads `data/competitor-listings/{CODE}/mdd-{segment-slug}.json`. Empty state if missing. |

## Spinning up a new product dashboard from this template

1. Copy this folder: `cp -r _template-multisegment-eu/ my-new-product-eu/`
2. Open `_build_standalone.py` and edit the **CONFIG block** at the top:
   - `PRODUCT_NAME` → e.g. `'Wasp Traps'`
   - `SEGMENTS` → e.g. `['Lure', 'Electric', 'Sticky']` (or whatever the new product needs — order matters; first segment becomes the default tab)
   - `XRAY_EXPORT_DATE` → date the H10 X-Ray export was taken
   - `xray_links` → real Google Sheet URLs (replace `'#'`)
   - `countries[*].csv` → actual filenames you exported from H10
3. Drop the per-country X-Ray CSVs into `data/x-ray/{CODE}/`
4. (Optional) drop sales-history CSVs into `data/sales-data/{CODE}/` for accurate 12M projection + seasonality
5. (Optional) drop `voc.json` into `reviews/{CODE}/{Segment}/` (segment name = exact case from `SEGMENTS`)
6. (Optional) drop `mdd-{segment-slug}.json` into `data/competitor-listings/{CODE}/` (slug = lowercase, hyphenated)
7. Update `config.json` (`name`, `isTemplate: false`, remove `templateOf`)
8. Delete this CLAUDE.md and write a fresh one for the new dashboard
9. Run: `py _build_standalone.py` → `index.html` regenerates

## CSV schema (from H10 X-Ray)

Columns the build script reads (case-sensitive):

```
Product Details, ASIN, Type, Focus, Treatment Method, URL, Image URL, Brand,
Price €, Parent Level Sales, ASIN Sales, Recent Purchases,
Parent Level Revenue, ASIN Revenue, Title Char. Count, BSR,
Active Sellers, Ratings, Review Count, Seller Age (mo)
```

Required for the dashboard to be useful:

- `ASIN` — product ID
- `Focus` (or `Segment` — see `SEGMENT_COLUMNS`) — segment name matching the `SEGMENTS` list (case-insensitive prefix match)
- `Brand`, `Type`, `Price €`, `ASIN Sales`, `ASIN Revenue`, `Ratings`, `Review Count`, `Seller Age (mo)`

`Treatment Method` is no longer used (Treatment Methods tab was removed) — leave the column blank or drop it from the CSV.

## How the segment count flows through the code

| Layer | Where |
|---|---|
| Config | `SEGMENTS = [...]` near the top of `_build_standalone.py` |
| Tab list | `tabs = [...]` auto-built by looping `SEGMENTS` |
| Per-country aggregation | `build_country()` computes `marketStructure[seg]` for every seg in `SEGMENTS` |
| Bundle | `_build_tabs_dict()` assembles the bundle with one entry per segment per renderer |
| JS dispatcher | Prefix-based: `'market-structure-*' → renderMarketStructure`, `'reviews-*' → renderReviews`, `'marketing-deep-dive-*' → renderMarketingDeepDive`. Segment name comes from `D.tabs[tabId].segment`. |
| Colors | Auto-assigned from `SEGMENT_PALETTE` and exposed as `D.segmentColors` |

## What's still in the build script but unused

- `treatment_methods()` Python function — not called anywhere; safe to delete if you want to slim down `_build_standalone.py`
- `renderTreatmentMethods` JS function inside the shell — not in the dispatcher; safe to delete

Both are left in place to make it easy to diff against the source `eu-lice-treatment-analysis` if needed.

## Tech stack

- Python 3 stdlib only (no deps) — `_build_standalone.py`
- Chart.js 4.4.4 + chartjs-plugin-datalabels 2.2.0 (CDN)
- Self-contained `index.html` — opens via `file://`, no fetch calls

## Folder layout

```
_template-multisegment-eu/
├── CLAUDE.md                  ← this file
├── config.json                ← dashboard metadata (isTemplate: true)
├── _build_standalone.py       ← build script (CONFIG block at top)
├── _make_template.py          ← one-shot transformer used to create this template from the source dashboard. Safe to delete.
├── index.html                 ← built output (regenerate after data changes)
├── data/
│   ├── x-ray/{DE,FR,IT,ES}/   ← drop H10 X-Ray CSVs here
│   ├── sales-data/{DE,FR,IT,ES}/   ← optional — per-ASIN sales history
│   └── competitor-listings/{DE,FR,IT,ES}/   ← optional — mdd-{slug}.json per segment
├── reviews/{DE,FR,IT,ES}/{Segment}/   ← optional — voc.json per segment
└── scripts/
    ├── build_mdd.py           ← MDD builder (copied from source — adapt for new product)
    └── fetch_competitor_listings.py
```

## Self-Update Rule

Update this file after any structural change to the template, new config knob, or change to how segments flow through the build.
