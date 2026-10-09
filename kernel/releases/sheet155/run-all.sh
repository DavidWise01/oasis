#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cp -a "$ROOT/baseline154" "$TMP/baseline154"
(cd "$TMP/baseline154" && bash run-all.sh)
(cd "$ROOT" && node gate155.js)
