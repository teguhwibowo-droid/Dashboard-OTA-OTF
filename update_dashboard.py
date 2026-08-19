#!/usr/bin/env python3
"""
update_dashboard.py
Auto-update Dashboard OTA dari data Google Sheets.
Input : data markdown table via stdin (format output Google Drive MCP)
Output: update dashboard_ota.html di folder yang sama
"""

import sys, json, re, os
from datetime import datetime

DASHBOARD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard_ota.html")

# ---------------------------------------------------------------------------
# 1. PARSE MARKDOWN TABLE
# ---------------------------------------------------------------------------
def parse_markdown_table(text):
    """Parse tabel markdown menjadi list of dict."""
    rows = []
    lines = [l for l in text.splitlines() if l.strip().startswith("|")]
    if not lines:
        return rows
    # Baris pertama = header
    headers = [h.strip() for h in lines[0].split("|") if h.strip()]
    for line in lines[2:]:          # skip separator
        vals = [v.strip() for v in line.split("|")]
        vals = [v for i, v in enumerate(vals) if i > 0 and i <= len(headers)]
        if len(vals) == len(headers):
            rows.append(dict(zip(headers, vals)))
    return rows

# ---------------------------------------------------------------------------
# 2. PARSE DATETIME
# ---------------------------------------------------------------------------
def parse_dt(s):
    s = s.strip()
    for fmt in ["%d %b %y %H:%M", "%-d %b %y %H:%M", "%d %b %Y %H:%M"]:
        try:
            return datetime.strptime(s, fmt)
        except:
            pass
    # Coba tanpa leading zero via replace
    parts = s.split()
    if len(parts) >= 4:
        s2 = f"{int(parts[0]):02d} {parts[1]} {parts[2]} {parts[3]}"
        try:
            return datetime.strptime(s2, "%d %b %y %H:%M")
        except:
            pass
    return None

# ---------------------------------------------------------------------------
# 3. PROSES DATA → STRUKTUR D
# ---------------------------------------------------------------------------
MONTH_ORDER = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

def process(rows):
    sites, months, modas, batches = set(), set(), set(), set()
    summary, daily, vendor_d, detail = {}, {}, {}, {}

    for row in rows:
        site    = row.get("Supply site", "").strip()
        moda    = row.get("Moda", "").strip()
        batch   = row.get("Batch", "").strip()
        month   = row.get("Month", "").strip()
        vdr     = row.get("Vendor", "").strip()
        no_si   = row.get("No SI", "").strip()
        tujuan  = row.get("Tujuan", "").strip()
        area    = row.get("Area", "").strip()
        req_s   = row.get("Req Stuffing", "").strip()
        cin_s   = row.get("Checkin", "").strip()
        cout_s  = row.get("Checkout", "").strip()

        if not (site and moda and batch and month and req_s and cin_s):
            continue

        req_dt  = parse_dt(req_s)
        cin_dt = parse_dt(cin_s)
        if not req_dt or not cin_dt:
            continue

        ota  = cin_dt <= req_dt
        day  = req_dt.day          # pakai hari dari Req Stuffing

        sites.add(site); months.add(month); modas.add(moda); batches.add(batch)

        def inc(d, key):
            if key not in d:
                d[key] = {"total":0,"ot":0,"late":0}
            d[key]["total"] += 1
            if ota: d[key]["ot"] += 1
            else:   d[key]["late"] += 1

        sk = f"{site}|{month}|{moda}|{batch}"
        inc(summary, sk)
        inc(daily,   f"{sk}|{day}")
        inc(vendor_d,f"{sk}|{vdr}")

        if sk not in detail:
            detail[sk] = []
        detail[sk].append({
            "noSI":no_si, "vendor":vdr, "tujuan":tujuan, "area":area,
            "req":req_s, "checkin":cin_s, "ota":ota, "day":day
        })

    return {
        "sites":   sorted(sites),
        "months":  sorted(months, key=lambda m: MONTH_ORDER.index(m) if m in MONTH_ORDER else 99),
        "modas":   sorted(modas),
        "batches": sorted(batches),
        "summary": summary,
        "daily":   daily,
        "vendor":  vendor_d,
        "detail":  detail,
    }

# ---------------------------------------------------------------------------
# 4. UPDATE HTML
# ---------------------------------------------------------------------------
def update_html(D):
    with open(DASHBOARD, encoding="utf-8") as f:
        html = f.read()

    # Cari blok: const D = {...};
    m = re.search(r'const D = \{', html)
    if not m:
        print("ERROR: Tidak menemukan 'const D = {' di dashboard HTML")
        sys.exit(1)

    start = m.start()
    # Cari closing brace yang cocok
    depth, i = 0, start + len("const D = ")
    for j, ch in enumerate(html[i:], i):
        if ch == '{': depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                end = j + 1
                break

    new_block = "const D = " + json.dumps(D, ensure_ascii=False, separators=(',', ':'))
    updated = html[:start] + new_block + html[end:]

    with open(DASHBOARD, "w", encoding="utf-8") as f:
        f.write(updated)

    total_trips = sum(v["total"] for v in D["summary"].values())
    print(f"✅ Dashboard diperbarui: {total_trips} trip, {len(D['sites'])} site, "
          f"bulan {', '.join(D['months'])}")
    print(f"   File: {DASHBOARD}")

# ---------------------------------------------------------------------------
# 5. MAIN
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    raw = sys.stdin.read()
    if not raw.strip():
        print("ERROR: Tidak ada data di stdin.")
        sys.exit(1)

    rows = parse_markdown_table(raw)
    if not rows:
        print(f"ERROR: Tidak ada baris data yang berhasil di-parse (panjang input: {len(raw)} chars)")
        sys.exit(1)

    print(f"📋 Parsed {len(rows)} baris data dari Google Sheets")
    D = process(rows)
    print(f"📊 Processed: {len(D['summary'])} summary entries, "
          f"{len(D['daily'])} daily entries, {len(D['vendor'])} vendor entries")
    update_html(D)
