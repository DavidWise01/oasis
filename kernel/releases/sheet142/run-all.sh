#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMP="$(mktemp -d)"
trap 'rm -rf "$TEMP"' EXIT
cp -a "$HERE/baseline141" "$TEMP/baseline141"
(cd "$TEMP/baseline141" && bash run-all.sh)
(cd "$HERE" && node gate142.js)
