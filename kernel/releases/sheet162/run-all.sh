#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cp -a baseline161 "$TMP/sheet161"
(cd "$TMP/sheet161" && node gate161.js)
node unit162.js
node gate162.js
