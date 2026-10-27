#!/bin/sh
# Jalankan dari root repo: pipeline analisis lalu Report v2.
set -e
python3 -I scripts/01_analysis.py
python3 -I scripts/02_load_duckdb.py
python3 -I scripts/03_crosscheck.py
python3 -I scripts/04_one_sheet.py
python3 -I design-and-report/src/build_report.py
