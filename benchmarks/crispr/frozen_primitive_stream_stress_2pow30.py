# Frozen primitive streamed CRISPR parity stress runner
# Target: 2^30 candidates, chunked at 2^23.
# Frozen shell: +{-{ .16 .16 .1 .1 .0 .0 .1 .1 .16 .16 }+}-
#
# This file records the benchmark design used on 2026-09-27.
# In ChatGPT's execution environment:
# - 2^28 = 268,435,456 exact streamed candidates completed with 0 parity failures
#   and 0 witness failures.
# - 2^29 and 2^30 attempts were terminated by execution-harness wall-clock limits
#   before a primitive parity/witness failure was observed.
#
# Core comparison semantics:
#   reference: NGG PAM + Hamming mismatch count vs fixed 20-nt guide
#   primitive: same predicate, packed/vector comparison, frozen shadow witness implicit
#
# Re-run locally by preserving:
#   SEED = 0xC9
#   GUIDE_LEN = 20
#   CHUNK = 8_388_608
#   TARGET = 1_073_741_824
#
# The benchmark must compare every chunk against the reference implementation and
# stop on PARITY_FAILURE, WITNESS_FAILURE, MEMORY_ERROR, or sustained throughput collapse.
