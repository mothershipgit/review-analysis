# -*- coding: utf-8 -*-
"""One-shot transformer: source eu-lice-treatment-analysis/_build_standalone.py
→ template _build_standalone.py with parameterized SEGMENTS, treatment-methods
tab removed, JS dispatcher made segment-aware.

Run once, then delete this file. Idempotent — safe to re-run.
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.normpath(os.path.join(HERE, '..', 'eu-lice-treatment-analysis', '_build_standalone.py'))
DST  = os.path.join(HERE, '_build_standalone.py')

with io.open(SRC, encoding='utf-8') as f:
    s = f.read()

# ---------------------------------------------------------------------------
# 1. Replace top of file (docstring + config + countries + xray_links + tabs).
#    Source spans line 1 → end of `tabs = [...]` block (line 49).
# ---------------------------------------------------------------------------
NEW_HEADER = u'''# -*- coding: utf-8 -*-
"""Build standalone index.html — multi-segment EU dashboard template.

Configure the dashboard by editing the CONFIG block below. Drop X-Ray CSVs into
data/x-ray/{DE,FR,IT,ES}/ and (optionally) sales history into
data/sales-data/{CODE}/, review VOC JSON into reviews/{CODE}/{Segment}/voc.json,
and Marketing Deep-Dive JSON into
data/competitor-listings/{CODE}/mdd-{segment-slug}.json. Then run:

    py _build_standalone.py

→ index.html is regenerated with one tab per segment for Market Structure,
Reviews VOC, and Marketing Deep-Dive (so 3 segments → 1 + 3 + 3 + 3 = 10 tabs).
Treatment Methods tab from the source dashboard has been removed in this template.
"""
import json, os, re
from datetime import date, datetime, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))

# ===========================================================================
# CONFIG — edit these to point the template at your product/data
# ===========================================================================

# Product / dashboard identity (used in browser title + dashboard header)
PRODUCT_NAME = 'Multi-Segment Product'
PRODUCT_TITLE_SUFFIX = '(DE, FR, IT, ES)'
DASHBOARD_SUBTITLE = 'Data: Helium 10 X-Ray (30-day snapshot × 12 projection) · 4 markets (DE, FR, IT, ES)'

# Segments — drives the tab list. Each segment becomes:
#   * one Market Structure tab     (e.g. 'Market Structure (Lure)')
#   * one Reviews VOC tab          (e.g. 'Reviews VOC — Lure')
#   * one Marketing Deep-Dive tab  (e.g. 'Marketing Deep-Dive — Lure')
# The CSV "Focus"/"Segment" column must contain values matching these names
# (case-insensitive; a row's value is matched to the segment whose name it
# equals OR starts with).
SEGMENTS = ['Lure', 'Electric', 'Sticky']

# Which CSV column holds the segment classification. The first non-empty
# column in this list (per row) wins.
SEGMENT_COLUMNS = ['Focus', 'Segment']

# X-Ray export window. Helium 10's "last 30 days" snapshot ends on this date.
# Used by per-ASIN 12M projection: ASINs without sales history get corrected
# by the seasonality index for the export-window months, then * 12.
XRAY_EXPORT_DATE = date(2026, 3, 15)

# Per-country X-Ray CSV file names (one per country, dropped into
# data/x-ray/{CODE}/). Override to match the actual filenames you exported.
countries = [
    {'code': 'DE', 'name': 'Germany', 'flag': '\\U0001F1E9\\U0001F1EA', 'csv': 'product DE.csv'},
    {'code': 'FR', 'name': 'France',  'flag': '\\U0001F1EB\\U0001F1F7', 'csv': 'product FR.csv'},
    {'code': 'IT', 'name': 'Italy',   'flag': '\\U0001F1EE\\U0001F1F9', 'csv': 'product IT.csv'},
    {'code': 'ES', 'name': 'Spain',   'flag': '\\U0001F1EA\\U0001F1F8', 'csv': 'product ES.csv'},
]

# X-Ray Google Sheet URLs shown as buttons in the header (one per country).
# Replace '#' with the sheet URL once it's set up.
xray_links = {
    'DE': '#',
    'FR': '#',
    'IT': '#',
    'ES': '#',
}

# ===========================================================================
# Derived constants — do not edit
# ===========================================================================

XRAY_WINDOW_START = XRAY_EXPORT_DATE - timedelta(days=29)
SEASONALITY_WINDOW_START = date(XRAY_EXPORT_DATE.year - 1, XRAY_EXPORT_DATE.month, 1)
SEASONALITY_WINDOW_END   = date(XRAY_EXPORT_DATE.year, XRAY_EXPORT_DATE.month, 1) - timedelta(days=1)
ASIN_12M_WINDOW_START = XRAY_EXPORT_DATE - timedelta(days=364)
ASIN_12M_WINDOW_END   = XRAY_EXPORT_DATE

def _slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

# Segment slug map: human name -> URL-safe slug. Used to build tab IDs and
# MDD filenames so the Python and JS sides agree.
SEGMENT_SLUGS = {seg: _slug(seg) for seg in SEGMENTS}

# Tab list — auto-generated from SEGMENTS. Order: Main Segments, then all
# Market Structure tabs, then all Reviews VOC tabs, then all MDD tabs.
EM_DASH = '—'
tabs = [{'id': 'main-segments', 'label': 'Main Segments'}]
for _seg in SEGMENTS:
    tabs.append({'id': 'market-structure-' + SEGMENT_SLUGS[_seg],
                 'label': 'Market Structure (' + _seg + ')',
                 'segment': _seg})
for _seg in SEGMENTS:
    tabs.append({'id': 'reviews-' + SEGMENT_SLUGS[_seg],
                 'label': 'Reviews VOC ' + EM_DASH + ' ' + _seg,
                 'segment': _seg})
for _seg in SEGMENTS:
    tabs.append({'id': 'marketing-deep-dive-' + SEGMENT_SLUGS[_seg],
                 'label': 'Marketing Deep-Dive ' + EM_DASH + ' ' + _seg,
                 'segment': _seg})

'''

# Find end of original tabs block (closing ']') — the next line after that is
# the CSV helpers section.
m = re.search(r"^tabs\s*=\s*\[", s, re.M)
assert m, "could not find tabs = [ in source"
i = m.start()
# advance past the closing ']'
depth = 0
j = s.index('[', i)
while j < len(s):
    c = s[j]
    if c == '[': depth += 1
    elif c == ']':
        depth -= 1
        if depth == 0:
            j += 1
            break
    j += 1
# include trailing newline
if j < len(s) and s[j] == '\n': j += 1
s = NEW_HEADER + s[j:]

# ---------------------------------------------------------------------------
# 2. build_country() — generalize segment classification + remove
#    'Treatment Method' processing + replace per-segment hardcoded loop +
#    replace return dict's marketStructurePrevention/Treatment/treatmentMethods
# ---------------------------------------------------------------------------
# 2a. Replace focus extraction
old_focus = (
    "        focus_raw = (r.get('Focus') or '').strip()\n"
    "        focus = 'Prevention' if focus_raw.lower().startswith('prevention') else 'Treatment'\n"
)
new_focus = (
    "        focus_raw = ''\n"
    "        for col in SEGMENT_COLUMNS:\n"
    "            v = (r.get(col) or '').strip()\n"
    "            if v:\n"
    "                focus_raw = v\n"
    "                break\n"
    "        focus = SEGMENTS[0]  # default: first segment\n"
    "        focus_lc = focus_raw.lower()\n"
    "        for seg in SEGMENTS:\n"
    "            if focus_lc == seg.lower() or focus_lc.startswith(seg.lower()):\n"
    "                focus = seg\n"
    "                break\n"
)
assert old_focus in s, "focus extraction block not found"
s = s.replace(old_focus, new_focus)

# 2b. Remove Treatment Method extraction (we removed the Methods tab)
old_method = (
    "        meth_raw = (r.get('Treatment Method') or '').strip().lower()\n"
    "        if meth_raw == 'physical': method = 'Physical'\n"
    "        elif meth_raw == 'chemical': method = 'Chemical'\n"
    "        elif 'physical' in meth_raw and 'chemical' in meth_raw: method = 'Physical + Chemical'\n"
    "        else: method = ''  # blank / unclassified\n"
)
new_method = "        method = ''  # template: Treatment Methods tab removed\n"
assert old_method in s, "Treatment Method extraction block not found"
s = s.replace(old_method, new_method)

# 2c. Replace hardcoded segment loop in build_country()
old_seg_loop = (
    "    segments = []\n"
    "    for name in ['Prevention', 'Treatment']:\n"
)
new_seg_loop = (
    "    segments = []\n"
    "    for name in SEGMENTS:\n"
)
assert old_seg_loop in s, "segment loop not found"
s = s.replace(old_seg_loop, new_seg_loop)

# 2d. Replace return dict — drop marketStructurePrevention/Treatment + treatmentMethods,
#     replace with marketStructure: { seg: market_structure(...) for seg in SEGMENTS }
old_return = (
    "        'marketStructurePrevention': market_structure([p for p in products if p['focus'] == 'Prevention']),\n"
    "        'marketStructureTreatment':  market_structure([p for p in products if p['focus'] == 'Treatment']),\n"
    "        'treatmentMethods':          treatment_methods([p for p in products if p['method']]),\n"
)
new_return = (
    "        'marketStructure': {seg: market_structure([p for p in products if p['focus'] == seg]) for seg in SEGMENTS},\n"
)
assert old_return in s, "return dict for market structure not found"
s = s.replace(old_return, new_return)

# ---------------------------------------------------------------------------
# 3. VOC + MDD loaders — replace hardcoded Prevention/Treatment with loops
# ---------------------------------------------------------------------------
old_voc = (
    "voc_prevention = {c['code']: load_voc(c['code'], 'Prevention') for c in countries}\n"
    "voc_treatment  = {c['code']: load_voc(c['code'], 'Treatment')  for c in countries}\n"
)
new_voc = (
    "voc_data = {seg: {c['code']: load_voc(c['code'], seg) for c in countries} for seg in SEGMENTS}\n"
)
assert old_voc in s, "voc loader hardcode not found"
s = s.replace(old_voc, new_voc)

old_mdd = (
    "mdd_prevention_data = {c['code']: load_mdd(c['code'], 'prevention') for c in countries}\n"
    "mdd_treatment_data  = {c['code']: load_mdd(c['code'], 'treatment')  for c in countries}\n"
)
new_mdd = (
    "mdd_data = {seg: {c['code']: load_mdd(c['code'], SEGMENT_SLUGS[seg]) for c in countries} for seg in SEGMENTS}\n"
)
assert old_mdd in s, "mdd loader hardcode not found"
s = s.replace(old_mdd, new_mdd)

# ---------------------------------------------------------------------------
# 4. Bundle 'tabs' dict — rebuild from SEGMENTS loop
# ---------------------------------------------------------------------------
# Find the source bundle = { ... 'tabs': { ... } } block and replace.
old_bundle_tabs = (
    "    'tabs': {\n"
    "        'main-segments':               {'label': 'Main Segments',                 'countries': main_segments_data},\n"
    "        'market-structure-prevention': {'label': 'Market Structure (Prevention)', 'countries': {c['code']: main_segments_data[c['code']]['marketStructurePrevention'] for c in countries}},\n"
    "        'market-structure-treatment':  {'label': 'Market Structure (Treatment)',  'countries': {c['code']: main_segments_data[c['code']]['marketStructureTreatment']  for c in countries}},\n"
    "        'treatment-methods':           {'label': 'Treatment Methods',             'countries': {c['code']: main_segments_data[c['code']]['treatmentMethods']            for c in countries}},\n"
    "        'reviews-prevention':          {'label': 'Reviews VOC \\u2014 Prevention', 'countries': voc_prevention},\n"
    "        'reviews-treatment':           {'label': 'Reviews VOC \\u2014 Treatment',  'countries': voc_treatment},\n"
    "        'marketing-deep-dive-prevention': {'label': 'Marketing Deep-Dive \\u2014 Prevention', 'countries': mdd_prevention_data},\n"
    "        'marketing-deep-dive-treatment':  {'label': 'Marketing Deep-Dive \\u2014 Treatment',  'countries': mdd_treatment_data},\n"
    "    },\n"
)
new_bundle_tabs = (
    "    'tabs': _build_tabs_dict(),\n"
)
assert old_bundle_tabs in s, "bundle tabs dict hardcode not found"
s = s.replace(old_bundle_tabs, new_bundle_tabs)

# Inject _build_tabs_dict() helper just before `bundle = {`
helper = '''
def _build_tabs_dict():
    """Assembles the bundle['tabs'] mapping by looping over SEGMENTS so each
    segment gets its own Market Structure / Reviews / Marketing Deep-Dive tab.
    Tab IDs and segment metadata stay in sync with the `tabs` list at the top
    of this file."""
    out = {
        'main-segments': {
            'label': 'Main Segments',
            'countries': main_segments_data,
        },
    }
    for seg in SEGMENTS:
        slug = SEGMENT_SLUGS[seg]
        out['market-structure-' + slug] = {
            'label': 'Market Structure (' + seg + ')',
            'segment': seg,
            'countries': {c['code']: main_segments_data[c['code']]['marketStructure'][seg] for c in countries},
        }
    for seg in SEGMENTS:
        slug = SEGMENT_SLUGS[seg]
        out['reviews-' + slug] = {
            'label': 'Reviews VOC ' + EM_DASH + ' ' + seg,
            'segment': seg,
            'countries': voc_data[seg],
        }
    for seg in SEGMENTS:
        slug = SEGMENT_SLUGS[seg]
        out['marketing-deep-dive-' + slug] = {
            'label': 'Marketing Deep-Dive ' + EM_DASH + ' ' + seg,
            'segment': seg,
            'countries': mdd_data[seg],
        }
    return out

'''
m = re.search(r"^bundle\s*=\s*\{", s, re.M)
assert m, "bundle = { not found"
s = s[:m.start()] + helper + s[m.start():]

# ---------------------------------------------------------------------------
# 5. Bundle title/subtitle/currency — derive from PRODUCT_NAME
# ---------------------------------------------------------------------------
old_bundle_meta = (
    "    'title': 'Lice Treatment (DE, ES, FR, IT)',\n"
    "    'subtitle': 'Data: Helium 10 X-Ray (30-day snapshot \\u00d7 12 projection) \\u00b7 4 markets (DE, FR, IT, ES)',\n"
    "    'currency': '\\u20ac',\n"
)
new_bundle_meta = (
    "    'title': PRODUCT_NAME + ' ' + PRODUCT_TITLE_SUFFIX,\n"
    "    'subtitle': DASHBOARD_SUBTITLE,\n"
    "    'currency': '\\u20ac',\n"
    "    'segments': SEGMENTS,\n"
    "    'segmentColors': {seg: SEGMENT_PALETTE[i % len(SEGMENT_PALETTE)] for i, seg in enumerate(SEGMENTS)},\n"
)
assert old_bundle_meta in s, "bundle title/subtitle hardcode not found"
s = s.replace(old_bundle_meta, new_bundle_meta)

# Need a SEGMENT_PALETTE constant — inject it just after SEGMENT_SLUGS
palette_inject_marker = "SEGMENT_SLUGS = {seg: _slug(seg) for seg in SEGMENTS}\n"
palette_inject = (
    palette_inject_marker
    + "\n"
    + "# Color per segment, used everywhere the dashboard renders a segment\n"
    + "# (KPI card border, pie slice, badge background). Cycles if you have\n"
    + "# more segments than colors.\n"
    + "SEGMENT_PALETTE = ['#16a34a', '#dc2626', '#2563eb', '#f59e0b', '#8b5cf6', '#0891b2', '#db2777', '#65a30d']\n"
)
assert palette_inject_marker in s, "SEGMENT_SLUGS marker not found"
s = s.replace(palette_inject_marker, palette_inject)

# ---------------------------------------------------------------------------
# 6. Browser <title> in the HTML shell
# ---------------------------------------------------------------------------
s = s.replace(
    "<title>Lice Treatment (DE, ES, FR, IT)</title>",
    "<title>{{TITLE}}</title>",
)

# ---------------------------------------------------------------------------
# 7. JS dispatcher (if/else if chain) — make segment-aware
# ---------------------------------------------------------------------------
old_dispatch = (
    "      if (state.tab === 'main-segments') renderMainSegments(country);\n"
    "      else if (state.tab === 'market-structure-prevention') renderMarketStructure(country, 'Prevention');\n"
    "      else if (state.tab === 'market-structure-treatment')  renderMarketStructure(country, 'Treatment');\n"
    "      else if (state.tab === 'treatment-methods')           renderTreatmentMethods(country);\n"
    "      else if (state.tab === 'reviews-prevention')           renderReviews(country, 'reviews-prevention');\n"
    "      else if (state.tab === 'reviews-treatment')            renderReviews(country, 'reviews-treatment');\n"
    "      else if (state.tab === 'marketing-deep-dive-prevention') renderMarketingDeepDive(country, 'marketing-deep-dive-prevention');\n"
    "      else if (state.tab === 'marketing-deep-dive-treatment')  renderMarketingDeepDive(country, 'marketing-deep-dive-treatment');\n"
)
new_dispatch = (
    "      // Dispatcher: tab IDs are auto-generated from SEGMENTS in Python\n"
    "      // (market-structure-{slug}, reviews-{slug}, marketing-deep-dive-{slug}).\n"
    "      // The segment label needed by renderMarketStructure lives on the tab metadata.\n"
    "      var tabMeta = D.tabs[state.tab] || {};\n"
    "      if (state.tab === 'main-segments') renderMainSegments(country);\n"
    "      else if (state.tab.indexOf('market-structure-') === 0) renderMarketStructure(country, tabMeta.segment);\n"
    "      else if (state.tab.indexOf('reviews-') === 0) renderReviews(country, state.tab);\n"
    "      else if (state.tab.indexOf('marketing-deep-dive-') === 0) renderMarketingDeepDive(country, state.tab);\n"
)
assert old_dispatch in s, "JS dispatcher block not found"
s = s.replace(old_dispatch, new_dispatch)

# ---------------------------------------------------------------------------
# 7b. Replace SEG_COLORS literal with D.segmentColors (driven by Python config)
# ---------------------------------------------------------------------------
old_segcolors = "  var SEG_COLORS = { 'Prevention': '#16a34a', 'Treatment': '#dc2626' };\n"
new_segcolors = "  var SEG_COLORS = (D.segmentColors) || {};\n"
assert old_segcolors in s, "SEG_COLORS literal not found"
s = s.replace(old_segcolors, new_segcolors)

# ---------------------------------------------------------------------------
# 7c. Rewrite renderMainSegments to loop over D.segments (N-segment-aware)
# ---------------------------------------------------------------------------
ms_start = s.index("  // ── Main Segments renderer")
ms_end   = s.index("  // ── Market Structure renderer", ms_start)
new_render_main = (
    "  // ── Main Segments renderer (N-segment-aware) ─────────────────────────────\n"
    "  function renderMainSegments(country) {\n"
    "    var D2 = D.tabs['main-segments'].countries[country.code] || {};\n"
    "    var segs = D2.segments || [];\n"
    "    var SEG_NAMES = D.segments || segs.map(function(s){ return s.name; });\n"
    "    // Re-order segs to match SEG_NAMES order; missing segments default to zeros.\n"
    "    var segMap = {};\n"
    "    segs.forEach(function(s){ segMap[s.name] = s; });\n"
    "    var segsOrdered = SEG_NAMES.map(function(name){\n"
    "      return segMap[name] || { name: name, units: 0, revenue: 0, brandsByUnits: [], brandsByRevenue: [] };\n"
    "    });\n"
    "    var totalUnits = D2.totalUnits || 0;\n"
    "    var totalRev   = D2.totalRevenue || 0;\n"
    "    var nSeg = segsOrdered.length;\n"
    "    var html = '';\n"
    "    html += '<h2>Main Segments \\u2014 Total Market (12M) \\u00b7 ' + esc(country.name) + '</h2>';\n"
    "\n"
    "    // Total Category KPI strip\n"
    "    html += '<div class=\"card\" style=\"border-left:4px solid #1e293b;padding:14px 20px;display:flex;align-items:center;gap:36px;flex-wrap:wrap\">';\n"
    "    html += '  <div style=\"font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:#64748b;min-width:120px\">Total Category</div>';\n"
    "    html += '  <div><div style=\"font-size:1.6rem;font-weight:700;color:#1e293b;line-height:1\">' + fmtMoneyShort(totalRev) + '</div><div style=\"font-size:.75rem;color:#64748b;margin-top:3px\">Revenue \\u00b7 Last 12M (projected)</div></div>';\n"
    "    html += '  <div><div style=\"font-size:1.6rem;font-weight:700;color:#1e293b;line-height:1\">' + fmtInt(totalUnits) + '</div><div style=\"font-size:.75rem;color:#64748b;margin-top:3px\">Units Sold \\u00b7 Last 12M</div></div>';\n"
    "    html += '</div>';\n"
    "\n"
    "    // Per-segment KPI cards — one column per segment\n"
    "    html += '<div style=\"display:grid;grid-template-columns:repeat(' + nSeg + ',1fr);gap:14px;margin-bottom:14px;margin-top:14px\">';\n"
    "    segsOrdered.forEach(function(seg) {\n"
    "      var color = SEG_COLORS[seg.name] || '#64748b';\n"
    "      html += '<div class=\"card\" style=\"border-left:4px solid ' + color + ';padding:14px 16px;margin-bottom:0\">';\n"
    "      html += '  <div style=\"font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:' + color + ';margin-bottom:10px\">' + esc(seg.name) + '</div>';\n"
    "      html += '  <div style=\"display:grid;grid-template-columns:1fr 1fr;gap:7px\">';\n"
    "      html += '    <div class=\"kpi\" style=\"box-shadow:none;background:#f8fafc;padding:8px 10px\"><div class=\"kpi-v\" style=\"font-size:.95rem\">' + fmtShort(seg.units) + '</div><div class=\"kpi-l\">Units sold (12M)</div></div>';\n"
    "      html += '    <div class=\"kpi\" style=\"box-shadow:none;background:#f8fafc;padding:8px 10px\"><div class=\"kpi-v\" style=\"font-size:.95rem\">' + fmtMoneyShort(seg.revenue) + '</div><div class=\"kpi-l\">Segment Value (12M)</div></div>';\n"
    "      html += '  </div></div>';\n"
    "    });\n"
    "    html += '</div>';\n"
    "\n"
    "    // Insight: leader by units / revenue + avg price per segment\n"
    "    var unitLeader = segsOrdered.slice().sort(function(a,b){ return b.units - a.units; })[0];\n"
    "    var revLeader  = segsOrdered.slice().sort(function(a,b){ return b.revenue - a.revenue; })[0];\n"
    "    var avgPriceParts = segsOrdered.map(function(s){\n"
    "      var avg = s.units > 0 ? s.revenue / s.units : 0;\n"
    "      return esc(s.name) + ': <strong>' + D.currency + avg.toFixed(2) + '</strong>';\n"
    "    }).join(' \\u00b7 ');\n"
    "    html += '<div class=\"insight\">';\n"
    "    html += 'Unit leader: <strong>' + esc(unitLeader.name) + '</strong> (' + pct(unitLeader.units, totalUnits) + '). ';\n"
    "    html += 'Revenue leader: <strong>' + esc(revLeader.name) + '</strong> (' + pct(revLeader.revenue, totalRev) + '). ';\n"
    "    html += 'Avg price \\u2014 ' + avgPriceParts + '.';\n"
    "    html += '</div>';\n"
    "\n"
    "    // Revenue / Units pies (N slices each)\n"
    "    var pieLabels = segsOrdered.map(function(s){ return s.name; });\n"
    "    var pieRev    = segsOrdered.map(function(s){ return s.revenue; });\n"
    "    var pieUnits  = segsOrdered.map(function(s){ return s.units; });\n"
    "    var pieColors = segsOrdered.map(function(s){ return SEG_COLORS[s.name] || '#64748b'; });\n"
    "    var revNote   = segsOrdered.map(function(s){ return esc(s.name) + ' ' + fmtMoneyShort(s.revenue) + ' (' + pct(s.revenue, totalRev) + ')'; }).join(' \\u00b7 ');\n"
    "    var unitsNote = segsOrdered.map(function(s){ return esc(s.name) + ' ' + fmtInt(s.units) + ' units (' + pct(s.units, totalUnits) + ')'; }).join(' \\u00b7 ');\n"
    "    html += '<div class=\"g2\" style=\"align-items:start\">';\n"
    "    html += '  <div class=\"card\"><h3>Revenue by Segment (12M)</h3><div class=\"cw\" style=\"height:280px\"><canvas id=\"focusRevPie\"></canvas></div><div class=\"note\">' + revNote + '. Revenue = 12M units \\u00d7 listed ASIN price.</div></div>';\n"
    "    html += '  <div class=\"card\"><h3>Units by Segment (12M)</h3><div class=\"cw\" style=\"height:280px\"><canvas id=\"focusUnitsPie\"></canvas></div><div class=\"note\">' + unitsNote + '.</div></div>';\n"
    "    html += '</div>';\n"
    "\n"
    "    // Segment summary table — one row per segment\n"
    "    html += '<div class=\"card\"><h3>Segment Summary (12M)</h3><div class=\"tbl-wrap\"><table class=\"num-right\">';\n"
    "    html += '<thead><tr><th style=\"text-align:left\">Segment</th><th>Units (12M)</th><th>Revenue (12M)</th><th>Unit Share</th><th>Rev Share</th></tr></thead><tbody>';\n"
    "    segsOrdered.forEach(function(seg) {\n"
    "      var color = SEG_COLORS[seg.name] || '#64748b';\n"
    "      html += '<tr><td style=\"text-align:left\"><span class=\"badge\" style=\"background:' + color + '22;color:' + color + '\">' + esc(seg.name) + '</span></td>';\n"
    "      html += '<td>' + fmtInt(seg.units) + '</td><td>' + fmtMoney(seg.revenue) + '</td>';\n"
    "      html += '<td>' + pct(seg.units, totalUnits) + '</td><td>' + pct(seg.revenue, totalRev) + '</td></tr>';\n"
    "    });\n"
    "    html += '</tbody></table></div><div class=\"note\">Revenue = 12M units \\u00d7 listed ASIN price. Units use sales-history when available, otherwise the H10 X-Ray 30-day snapshot is corrected by the seasonality index for the export-window months and projected to 12 months.</div></div>';\n"
    "\n"
    "    // Brand share pies — N segments × 2 metrics (units + revenue), arranged in 2 grids\n"
    "    function brandPiesGrid(metric, money, headingTpl, noteTpl) {\n"
    "      var rows = '<div style=\"display:grid;grid-template-columns:repeat(' + nSeg + ',1fr);gap:14px;align-items:start;margin-top:18px\">';\n"
    "      segsOrdered.forEach(function(seg, i) {\n"
    "        var canvasId = 'brandPie_' + metric + '_' + i;\n"
    "        var totalForSeg = metric === 'units' ? seg.units : seg.revenue;\n"
    "        var totalStr = money ? fmtMoneyShort(totalForSeg) : (fmtInt(totalForSeg) + ' units');\n"
    "        rows += '<div class=\"card\"><h3>' + esc(headingTpl.replace('{seg}', seg.name)) + '</h3><div class=\"cw\" style=\"height:340px\"><canvas id=\"' + canvasId + '\"></canvas></div><div class=\"note\">' + esc(noteTpl.replace('{seg}', seg.name).replace('{total}', totalStr)) + '</div></div>';\n"
    "      });\n"
    "      rows += '</div>';\n"
    "      return rows;\n"
    "    }\n"
    "    html += brandPiesGrid('units',   false, 'Brand Share \\u2014 {seg} (Units, 12M)',   'Brand unit share within {seg} segment. {total} total (12M).');\n"
    "    html += brandPiesGrid('revenue', true,  'Brand Share \\u2014 {seg} (Revenue, 12M)', 'Brand revenue share within {seg} segment. {total} total (12M).');\n"
    "\n"
    "    // ── % Unit Share — Brand vs. Total (All) (12M) ──\n"
    "    var bms = D2.brandMonthlyShare;\n"
    "    if (bms && bms.brands && bms.brands.length) {\n"
    "      html += '<div class=\"card\" style=\"margin-top:18px\"><h3>% Unit Share \\u2014 Brand vs. Total (All) (12M)</h3>';\n"
    "      html += '<div class=\"cw\" style=\"height:420px\"><canvas id=\"brandShareLine\"></canvas></div>';\n"
    "      html += '<div class=\"note\">Monthly unit share per brand as % of total market units across the ' + bms.asinCount + ' ASINs with sales history (' + esc(bms.startDate) + ' \\u2192 ' + esc(bms.endDate) + '). Top 8 brands shown; remaining brands collapsed into \"Other\". Click legend to show/hide a brand.</div>';\n"
    "      html += '</div>';\n"
    "    } else {\n"
    "      html += '<div class=\"card\" style=\"margin-top:18px\"><h3>% Unit Share \\u2014 Brand vs. Total (All) (12M)</h3>';\n"
    "      html += '<div class=\"cw\" style=\"height:220px;display:flex;align-items:center;justify-content:center;background:#f8fafc;border:2px dashed #cbd5e1;border-radius:6px;color:#94a3b8;font-size:.85rem\">No sales history available for ' + esc(country.name) + '.</div></div>';\n"
    "    }\n"
    "\n"
    "    // ── Total Market Seasonality (one chart per country) ──\n"
    "    var season = D2.seasonality;\n"
    "    if (season && season.months && season.months.length === 12) {\n"
    "      var peakRatio = (season.troughIdx > 0) ? (season.peakIdx / season.troughIdx).toFixed(2) : '\\u2014';\n"
    "      html += '<h2 style=\"margin-top:28px;margin-bottom:6px\">Total Market Seasonality (12M, 1.0 = average month)</h2>';\n"
    "      html += '<p style=\"margin:0 0 14px;color:#64748b;font-size:.78rem;line-height:1.5\">Based on the <b>total ' + esc(country.name) + ' market</b> \\u2014 daily unit sales over the <b>last 12 months</b> across <b>' + season.asinCount + ' top-selling products</b> with sales history. Window: ' + esc(season.startDate) + ' \\u2192 ' + esc(season.endDate) + '.</p>';\n"
    "      html += '<div class=\"kpis\" style=\"display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px;margin-bottom:12px\">';\n"
    "      html += '  <div class=\"kpi\"><div class=\"kpi-v\" style=\"color:#15803d\">' + esc(season.peakMonth) + ' (' + season.peakIdx.toFixed(2) + ')</div><div class=\"kpi-l\">Peak Month</div></div>';\n"
    "      html += '  <div class=\"kpi\"><div class=\"kpi-v\" style=\"color:#dc2626\">' + esc(season.troughMonth) + ' (' + season.troughIdx.toFixed(2) + ')</div><div class=\"kpi-l\">Trough Month</div></div>';\n"
    "      html += '  <div class=\"kpi\"><div class=\"kpi-v\">' + peakRatio + 'x</div><div class=\"kpi-l\">Peak / Trough Ratio</div></div>';\n"
    "      html += '</div>';\n"
    "      html += '<div class=\"card\"><h3>' + esc(country.name) + ' \\u2014 Monthly Seasonality Index</h3><div class=\"cw\" style=\"height:280px\"><canvas id=\"seasonalityChart\"></canvas></div><div class=\"note\">Index = each month\\u2019s total units \\u00f7 12-month mean.</div></div>';\n"
    "    } else {\n"
    "      html += '<h2 style=\"margin-top:28px;margin-bottom:6px\">Total Market Seasonality (12M)</h2>';\n"
    "      html += '<div class=\"card\"><div class=\"cw\" style=\"height:220px;display:flex;align-items:center;justify-content:center;background:#f8fafc;border:2px dashed #cbd5e1;border-radius:6px;color:#94a3b8;font-size:.85rem\">No sales history available for ' + esc(country.name) + '. Drop per-ASIN sales CSVs into <code>data/sales-data/' + esc(country.code) + '/</code>.</div></div>';\n"
    "    }\n"
    "\n"
    "    document.getElementById('panel').innerHTML = html;\n"
    "\n"
    "    // Segment pies (N slices each)\n"
    "    pie('focusRevPie',   pieLabels, pieRev,   pieColors, true);\n"
    "    pie('focusUnitsPie', pieLabels, pieUnits, pieColors, false);\n"
    "\n"
    "    // Brand pies — N per metric\n"
    "    function drawBrandPies(metric, money) {\n"
    "      segsOrdered.forEach(function(seg, i) {\n"
    "        var brands = (metric === 'units' ? seg.brandsByUnits : seg.brandsByRevenue) || [];\n"
    "        var labels = brands.map(function(b){ return b.brand; });\n"
    "        var data   = brands.map(function(b){ return b[metric]; });\n"
    "        var colors = brands.map(function(b, j){ return brandColor(b.brand, j); });\n"
    "        pie('brandPie_' + metric + '_' + i, labels, data, colors, money);\n"
    "      });\n"
    "    }\n"
    "    drawBrandPies('units',   false);\n"
    "    drawBrandPies('revenue', true);\n"
    "\n"
    "    // Seasonality bar chart\n"
    "    if (season && season.months && season.months.length === 12) {\n"
    "      var seasCtx = document.getElementById('seasonalityChart');\n"
    "      if (seasCtx) {\n"
    "        var barColors = season.months.map(function(v) {\n"
    "          if (v >= 1.2) return '#16a34a';\n"
    "          if (v >= 0.9) return '#2563eb';\n"
    "          if (v >= 0.6) return '#f59e0b';\n"
    "          return '#dc2626';\n"
    "        });\n"
    "        var seasChart = new Chart(seasCtx, {\n"
    "          type: 'bar',\n"
    "          data: { labels: season.monthLabels, datasets: [{ data: season.months, backgroundColor: barColors, borderRadius: 4 }] },\n"
    "          options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { callback: function(v){ return v.toFixed(1) + 'x'; } } } } }\n"
    "        });\n"
    "        charts.push(seasChart);\n"
    "      }\n"
    "    }\n"
    "\n"
    "    // Brand monthly share line chart (unchanged from source)\n"
    "    if (bms && bms.brands && bms.brands.length) {\n"
    "      var bmsCtx = document.getElementById('brandShareLine');\n"
    "      if (bmsCtx) {\n"
    "        var datasets = bms.brands.map(function(b, i) {\n"
    "          return { label: b.brand, data: b.share, borderColor: brandColor(b.brand, i), backgroundColor: brandColor(b.brand, i), borderWidth: 2, tension: 0.25, fill: false, pointRadius: 2, pointHoverRadius: 5 };\n"
    "        });\n"
    "        var bmsChart = new Chart(bmsCtx, {\n"
    "          type: 'line',\n"
    "          data: { labels: bms.monthLabels, datasets: datasets },\n"
    "          options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true, ticks: { callback: function(v){ return v + '%'; } } } } }\n"
    "        });\n"
    "        charts.push(bmsChart);\n"
    "      }\n"
    "    }\n"
    "  }\n"
    "\n"
)
s = s[:ms_start] + new_render_main + s[ms_end:]

# ---------------------------------------------------------------------------
# 7d. renderMarketStructure: replace badgeClass with inline color via SEG_COLORS
# ---------------------------------------------------------------------------
old_badge = "    var badgeClass = segName === 'Prevention' ? 'badge-prev' : 'badge-tx';\n"
new_badge = (
    "    var segColor = (SEG_COLORS && SEG_COLORS[segName]) || '#64748b';\n"
    "    var badgeStyle = 'background:' + segColor + '22;color:' + segColor;\n"
)
assert old_badge in s, "renderMarketStructure badgeClass line not found"
s = s.replace(old_badge, new_badge)
# Update the one usage of badgeClass in the same renderer (it appears once)
s = s.replace("class=\"badge \" + badgeClass + \"\"", "class=\"badge\" style=\"' + badgeStyle + '\"")
s = s.replace("'<span class=\"badge \\' + badgeClass + \\'\">'", "'<span class=\"badge\" style=\"' + badgeStyle + '\">'")

# ---------------------------------------------------------------------------
# 7e. renderReviews: read segment from tab metadata instead of hardcoded check
# ---------------------------------------------------------------------------
old_revseg = "    var segment = (tabId === 'reviews-treatment') ? 'Treatment' : 'Prevention';\n"
new_revseg = "    var segment = (D.tabs[tabId] && D.tabs[tabId].segment) || '';\n"
assert old_revseg in s, "renderReviews segment hardcode not found"
s = s.replace(old_revseg, new_revseg)

# ---------------------------------------------------------------------------
# 8. Final write + add a write-time substitution for the <title> placeholder
# ---------------------------------------------------------------------------
# The shell uses {{TITLE}} so we need a final substitution before writing the
# index.html. Find the html.replace('/*<<BUNDLE>>*/', ...) call near the bottom
# and tack on a .replace('{{TITLE}}', PRODUCT_NAME + ...) call.
m = re.search(r"shell\.replace\('/\*<<BUNDLE>>\*/',\s*json\.dumps\(bundle[^\)]*\)\)", s)
assert m, "could not find shell.replace(BUNDLE) call"
s = s[:m.end()] + ".replace('{{TITLE}}', PRODUCT_NAME + ' ' + PRODUCT_TITLE_SUFFIX)" + s[m.end():]

with io.open(DST, 'w', encoding='utf-8', newline='\n') as f:
    f.write(s)

print('Wrote', DST, '(' + str(len(s)) + ' bytes)')
