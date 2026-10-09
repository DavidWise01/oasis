#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
temp="$(mktemp -d)"
trap 'rm -rf "$temp"' EXIT
cp -a "$here/baseline156" "$temp/sheet156"
(cd "$temp/sheet156" && bash run-all.sh)
(cd "$here" && node gate157.js)
