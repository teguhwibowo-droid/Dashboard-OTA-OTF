#!/usr/bin/env python3
"""
fetch_sheets.py
Fetch data dari Google Sheets (public) via CSV URL → update dashboard_ota.html.

Dipakai oleh GitHub Actions (auto_update.yml).
Bisa juga dijalankan manual: python fetch_sheets.py

Tidak perlu API key atau service account — cukup sheet di-set "Anyone with the link can view".

GitHub Secrets yang dibutuhkan:
  SPREADSHEET_ID  ← ID spreadsheet (dari URL Google Sheets)
  SHEET_NAME      ← nama tab/sheet (default: Sheet1)
"""

import os, sys, csv, io, urllib.request
from update_dashboard import process, update_html

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "")
SHEET_NAME     = os.environ.get("SHEET_NAME", "Sheet1")

# ---------------------------------------------------------------------------
# FETCH CSV DARI GOOGLE SHEETS
# ---------------------------------------------------------------------------
def fetch_csv():
    url = (
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
        f"/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(SHEET_NAME)}"
    )
    print(f"📡 Fetching: {url}")
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except Exception as e:
        print(f"ERROR: Gagal fetch dari Google Sheets — {e}")
        sys.exit(1)

# ---------------------------------------------------------------------------
# PARSE CSV → list of dict (format sama seperti parse_markdown_table)
# ---------------------------------------------------------------------------
def parse_csv(raw_csv):
    reader = csv.DictReader(io.StringIO(raw_csv))
    rows = []
    for row in reader:
        # Strip whitespace dari semua key & value
        rows.append({k.strip(): v.strip() for k, v in row.items()})
    return rows

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    if not SPREADSHEET_ID:
        print("ERROR: SPREADSHEET_ID belum di-set.")
        print("  → Set GitHub Secret: SPREADSHEET_ID")
        print("  → Atau set environment variable: set SPREADSHEET_ID=xxx")
        sys.exit(1)

    import urllib.parse  # noqa: import di sini biar error lebih jelas kalau missing

    print(f"📊 Spreadsheet ID : {SPREADSHEET_ID}")
    print(f"📋 Sheet Name     : {SHEET_NAME}")

    raw_csv = fetch_csv()
    rows = parse_csv(raw_csv)

    if not rows:
        print("ERROR: Tidak ada baris data yang berhasil di-parse.")
        sys.exit(1)

    print(f"✅ Fetched {len(rows)} baris dari Google Sheets")

    D = process(rows)
    update_html(D)
    print("🚀 Dashboard berhasil diperbarui!")


if __name__ == "__main__":
    import urllib.parse
    main()
