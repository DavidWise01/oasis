#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cp -a "$ROOT/baseline151" "$TMP/baseline151"
(cd "$TMP/baseline151" && bash run-all.sh)
(cd "$ROOT" && node gate152.js)
