# Reviews Analysis Tracker

**Last updated:** 2026-05-13

---

## Summary

| Metric | Value |
|--------|-------|
| **In Progress** | 1 |
| **Pending Decisions** | 0 |
| **Backlog** | 5 |
| **Recently Completed** | 9 |

---

## In Progress

- [ ] **Run VOC analysis for 5 Ashwagandha dashboards (UK/DE/FR/ES/IT)** @2026-05-13 #reviews-analysis #→action — Scaffolding complete (this session): folders, HTML, stubs, config.json, CLAUDE.md row done. Reviews at `reviews/Ashwagandha-{MARKET}-Reviews.json`. Next: spawn 5 parallel sub-agents per Action 0/Action 2 of the review-analysis skill — each reads its market's reviews and writes the full dashboard.json.

---

## Pending Decisions

-

---

## Backlog

- [ ] **Contact Arush — request top-5 competitors per marketplace for Inositol, Menositol, Ashwagandha (UK/DE/FR/ES/IT)** @2026-05-15 #reviews-analysis #→action — Upstream blocker for MDD population on all 3 product families. Once Arush replies, append INOSITOL, MENOSITOL, ASHWAGANDHA blocks (header row + 5 market rows: ES/DE/IT/FR/UK each) to `data/DETOX + LAX TOP COMPETITORS.xlsx`. Unblocks 3 downstream MDD tasks.
- [ ] **Populate Marketing Deep-Dive for 5 Ashwagandha dashboards** @2026-05-18 #reviews-analysis — Run after VOC complete (depends on @2026-05-13 task above). Blocked on: ASHWAGANDHA block (top-5 competitors per market) appended to `data/DETOX + LAX TOP COMPETITORS.xlsx`. Once xlsx updated, run Action 3 (SP-API + MDD synthesis) for all 5 markets.
- [ ] **Populate Marketing Deep-Dive for 5 Inositol dashboards** @TBD #reviews-analysis — VOC done 2026-05-11. Blocked on: user to add INOSITOL block (top-5 competitors per market) to `data/DETOX + LAX TOP COMPETITORS.xlsx`. Once xlsx updated, run Action 3 (SP-API + MDD synthesis) for all 5 markets.
- [ ] **Provide ASINs for 5 Inositol dashboards** @TBD #reviews-analysis — all 5 dashboard.json files have `asin: "TBD"`. User to supply real ASINs per market, then rename `INOSITOL-{MARKET}-Reviews.json` files to `{ASIN}-{MARKET}-Reviews.json` and update fetch URLs in HTML.
- [ ] **Refresh data/DETOX + LAX TOP COMPETITORS.xlsx** — user to append product-family blocks for Inositol, Menositol, Ashwagandha (top-5 per market per family). Depends on Arush reply (@2026-05-15 task above). Required before MDD tab can populate for any of the 15 new dashboards.

---

## Recently Completed (last 10)

| Date | Item |
|------|------|
| 2026-05-13 | **Scaffolded 5 Ashwagandha dashboards (UK/DE/FR/ES/IT)** — folders, cloned HTML templates with title/fetch URL swaps, stub JSONs, registered in `config.json`, CLAUDE.md table updated, tracker updated. SKILL.md gained new Action 0 (multi-market batch scaffold recipe) to make this reproducible. VOC pending. |
| 2026-05-12 | **VOC analysis complete for all 5 Menositol dashboards (UK/DE/FR/ES/IT)** — 1,097 reviews total. Sentiment: UK 60/27/12, DE 57/32/11, FR 45/42/13, ES 69/20/11, IT 69/24/7. Universal findings: hot flush relief polarises sharply (#1 positive AND #1 negative theme in all 5 markets), 59/60 capsule count shortage (same operational defect as Inositol), review-for-freebie scheme called out publicly across 4 markets, FR is the outlier (most polarised market). |
| 2026-05-12 | **Scaffolded 5 Menositol dashboards (UK/DE/FR/ES/IT)** — folders, cloned HTML templates with title/fetch URL swaps, stub JSONs, registered in `config.json`, CLAUDE.md table updated. |
| 2026-05-12 | **Refactored review files into `reviews/` folder** — moved 8 existing `*-Reviews.json` files from project root to `reviews/`. Updated fetch URLs in all 13 HTMLs + reviewsFile in all 13 dashboard.json. Updated CLAUDE.md + skill SKILL.md docs. Cleaner structure for the 13-dashboard hub. |
| 2026-05-11 | **VOC analysis complete for all 5 Inositol Caps dashboards (UK/DE/FR/ES/IT)** — 1,902 reviews total. Sentiment: UK 63/26/11, DE 60/30/10, FR 52/37/10, ES 51/36/13, IT 65/26/9. Universal finding: silent reformulation (40:1→100:1 ratio, folate→folic acid) caught in all 5 markets independently — brand-wide trust crisis. |
| 2026-05-11 | Scaffold 5 Inositol Caps dashboards (UK/DE/FR/ES/IT) — folders, stub JSONs, registered in hub, CLAUDE.md table updated. Commit `20269c5`. |
| 2026-05-11 | Fix MDD renderer — clone full template to Lax DE/FR (they were missing `renderMDD()` entirely), fix bar-width bug (missing `%` suffix), fix price NaN rendering, dynamic competitor count in headers. Commits `ac3dbea`, `21575c6`. |
| 2026-05-11 | Document `data/DETOX + LAX TOP COMPETITORS.xlsx` as canonical competitor source in CLAUDE.md + SKILL.md. Workflow updated: read xlsx before asking user for ASINs. |
| 2026-05-06 | Populate Marketing Deep-Dive for Detox DE, Lax DE, Lax FR (5 curated competitors each). Commit `3f608b4`. |
| 2026-05-06 | Initial deployment — hub + 3 standalone dashboards + Firebase Auth (reuses `cases-tracker-dc2f2`) + GitHub Pages live at https://mothershipgit.github.io/review-analysis/. |

---

## Conventions

- Aggregator skanuje `## In Progress` + `## Pending Decisions`. Format: `- [ ] **Tytuł** @YYYY-MM-DD #reviews-analysis — szczegóły`.
- **`@YYYY-MM-DD` jest WYMAGANE** na każdym tasku. Bez tego markera Dataview w daily note NIE wyłapie taska. Use `@today` only for same-day tasks; otherwise the literal target date.
- **Done items** przenosisz z In Progress → Recently Completed z datą. Po 10 - usuwasz najstarsze.

---

## Project context

Source of truth: [CLAUDE.md](CLAUDE.md). Voice of Customer / VOC analysis dashboards per produkt.

**Workflow for adding a new product-family across multiple markets** (codified in skill `review-analysis` Action 0 — proven for Inositol 2026-05-11, Menositol 2026-05-12, Ashwagandha 2026-05-13):
1. User specifies product name + says "all 5 markets" or "UK/DE/FR/ES/IT".
2. Claude runs the Action 0 Python script: creates `dashboards/{product}-{market}/` × 5, clones canonical `detox-de/index.html` with title + reviews fetch URL swapped, writes stub `dashboard.json`, registers all 5 in `config.json`, updates CLAUDE.md Products table.
3. Commit + push scaffolding. Sidebar entries appear in hub immediately (empty state). ~2 min total.
4. Reviews JSON files live at `reviews/{Product}-{MARKET}-Reviews.json`.
5. Claude runs VOC analysis (Action 2) → spawns 5 parallel sub-agents (one per market). ~3-5 min wall clock.
6. User adds competitor block to `data/DETOX + LAX TOP COMPETITORS.xlsx`.
7. Claude runs MDD population (Action 3) → SP-API lookups + claims matrix + whitespace analysis.

Steps 2-3 happen same day; steps 4-7 follow as data arrives. Total time for steps 2-5 with reviews already dropped: ~10 minutes.
