#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
node gate164.js | tee gate164.log
python make_docs164.py
python make_dashboard164.py
python browser-check164.py
