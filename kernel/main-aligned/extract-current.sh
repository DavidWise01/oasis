#!/usr/bin/env sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SRC="$HERE/v25/OASIS_Main_Kernel_FalloutAligned_v25_2026-10-07.lean.gz"
OUT="$HERE/CURRENT.lean"
gzip -dc "$SRC" > "$OUT"
echo "expected 846ff2bd464139506fdc0db1f16f1392d14e22eaf6d7e27c144008732082ab69"
sha256sum "$OUT"
