# B0BM1WPXC5 — DE vs FR JSON comparison

Generated: 2026-04-29

The two files **partially overlap**. Roughly **80% identical**, with marketplace-specific tails on each side.

## Counts

| File | Reviews |
|---|---|
| `B0BM1WPXC5-DE-Reviews.json` | 326 |
| `B0BM1WPXC5-FR-Reviews.json` | 327 |
| **In both files** (byte-identical) | **263** |
| Only in DE file | 63 |
| Only in FR file | 64 |

## What's shared

- 263 reviews are **byte-for-byte identical** in both files (same author, date, title, text)
- These are the "global / cross-marketplace" reviews Amazon surfaces on every country's review page

## What's unique to each

- **DE-only (63)** — all German-language reviews (e.g. "Hohe Wirksamkeit", "Geballte pflanzliche Naturkraft", "Abführmittel"). Reviews originally posted on amazon.de that don't get cross-listed on amazon.fr.
- **FR-only (64)** — all French-language reviews (e.g. "Bon produit", "Très efficace", "EFFICACITÉ 100/100"). Posted on amazon.fr only.

## Other shape stats

- Date range identical in both: **2023-01-10/17 → 2026-04-27**
- Average review length: DE 224 chars · FR 220 chars
- Same schema: `title`, `date`, `author`, `review`

## Bottom line

Not "totally different reviews" — they share a large global pool (263). The real DE↔FR delta is small: ~63 truly German + ~64 truly French reviews. If you want a deduplicated combined corpus for B0BM1WPXC5, you'd get **~390 unique reviews** (263 + 63 + 64), not 653.

## Method

Identity key: `(author, date, review_text[:120])`. Shared records were verified to be byte-identical across all four fields (`title`, `date`, `author`, `review`).
