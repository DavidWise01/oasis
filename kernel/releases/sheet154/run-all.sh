#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cp -a "$ROOT/baseline153" "$TMP/baseline153"
(cd "$TMP/baseline153" && bash run-all.sh)
(cd "$ROOT" && node gate154.js)
