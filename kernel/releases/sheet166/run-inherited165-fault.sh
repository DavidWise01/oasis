#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
tmp="$(mktemp -d -t oasis165-fault-XXXXXX)"
trap 'rm -rf "$tmp"' EXIT
cp -a baseline165/. "$tmp/"
(cd "$tmp" && S165_MODE=fault node gate165.js) 2>&1 | tee inherited165-fault.log
