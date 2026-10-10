#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cp -a baseline163/. "$TMP/"
(cd "$TMP" && node gate163.js) | tee audit/inherited163.log
