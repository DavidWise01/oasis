#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
node unit162.js
node gate162.js
