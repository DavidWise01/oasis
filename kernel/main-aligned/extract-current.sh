#!/usr/bin/env sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SRC="$HERE/v32/OASIS_Main_Kernel_AZ1Aligned_v32_2026-10-07.lean.gz"
OUT="$HERE/CURRENT.lean"
gzip -dc "$SRC" > "$OUT"
echo "expected df133032c570edefeca29efa48f2e21a21f1c5edf75ae480cbc6e3c89aecefd3"
sha256sum "$OUT"
