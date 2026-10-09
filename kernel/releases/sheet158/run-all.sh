#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
temp="$(mktemp -d)"
trap 'rm -rf "$temp"' EXIT
cp -a "$here/baseline157" "$temp/sheet157"
(cd "$temp/sheet157" && bash run-all.sh)
(cd "$here" && node gate158.js)
