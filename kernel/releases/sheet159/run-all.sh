#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
temp="$(mktemp -d)"
trap 'rm -rf "$temp"' EXIT
cp -a "$here/baseline158" "$temp/sheet158"
(cd "$temp/sheet158" && bash run-all.sh)
(cd "$here" && node gate159.js)
