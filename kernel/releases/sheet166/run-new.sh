#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
node gate166.js 2>&1 | tee gate166.log
