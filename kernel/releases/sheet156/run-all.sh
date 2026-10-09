#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
temp="$(mktemp -d)"
trap 'rm -rf "$temp"' EXIT
cp -a "$here/baseline155" "$temp/sheet155"
(cd "$temp/sheet155" && bash run-all.sh)
(cd "$here" && node gate156.js)
