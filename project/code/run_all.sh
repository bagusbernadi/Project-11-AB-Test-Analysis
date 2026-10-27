#!/bin/sh
# Jalankan dari root repo: sh project/code/run_all.sh
# Urutan = urutan eksekusi (ketergantungan data). Hapus project/abtest.duckdb dan project/results/* untuk uji dari nol.
set -e
PY="python3 -I"
$PY project/code/1-data-preparation/python/01_clean_load.py
$PY project/code/2-analysis/python/02_tests.py
$PY project/code/2-analysis/python/03_crosscheck.py
$PY project/code/3-presentation/python/04_one_sheet.py
python3 project/code/3-presentation/python/05_build_notebook.py
(cd project/results/3-presentation && python3 -m nbconvert --to notebook --execute --inplace analysis.ipynb --ExecutePreprocessor.timeout=900 >/dev/null 2>&1)
$PY project/code/3-presentation/python/06_slides.py
$PY project/code/3-presentation/python/07_build_readme.py
$PY design-and-report/src/build_report.py
