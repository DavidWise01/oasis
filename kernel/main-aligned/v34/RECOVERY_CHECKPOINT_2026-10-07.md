# OaSIs v34 recovery reconciliation — 2026-10-07

## Authority and scope

**Canonical repository:** `DavidWise01/oasis`.

**Current aligned source identity:** `OASIS_Main_Kernel_RegisterUnloadAligned_v34_2026-10-07.lean`

**Required source SHA-256:** `822153ca94170a82e34b99905bd94b10bd2065c6f80ac8420b47a3c121353e2c`

This is a recovery record, **not** a monolithic Lean compiler certification. v35 is a candidate extension and does not supersede this manifest-pinned v34 source. The frozen canonical ancestors stay immutable.

## Recovered exact artifacts

The user-supplied copies were independently checked against `kernel/main-aligned/v34/manifest.json`:

| Item | Manifest SHA-256 | Actual verification |
|---|---|---|
| Register_Unload_Audit_v34.py | `ac1f81ba59027c06beb5fc27ec8ded4b33304243f0585b90d2079ca7ccbe96cd` | MATCH |
| OASIS_RegisterUnload_Alignment_Report_v34.md | `03954105dba1dbb626eb490ed52d658d526d936fe2f7e96c83b824e2d68ba2b3` | MATCH |

Uploaded artifacts are archive-equivalent to the manifest's originals. The manifest alone does not supply the bytes of the monolithic source.

## Audit execution

Running the uploaded audit using Python returned exit code 0:

```text
orthogonality max error 2.220446049250313e-16
unload max error 2.220446049250313e-16
endpoint norm error 0.0
max component movement 0.8564316234445897
animation max norm deviation (0.11579339090220553, 0.5, 1.3498122859426953)
mean collision 50.0 50.0
```

The result supports 8D double-precision reversible load/unload, not byte-exact recovery of an arbitrary adapter. The interpolated *animation* is not norm-preserving between endpoints.

## Architecture placement (scope labels are essential)

```text
FROZEN PARENT (untouched)
    |
    +-- -+- lane [INTENDED / not established by these 3 artifacts]
    +-- +-+ lane [INTENDED / not established by these 3 artifacts]
    |
    +-- v34 reversible adapter [AUDIT PASS]
    |      load R / unload R^T
    |      orthogonal endpoint round trip
    |
    +-- durable truth authority [HOLD — not promoted]
    |
    +-- v35 independent integration candidate [NOT v34 canon]
```

The RingyBoxy WASM v5 snapshot-fencing/commit gate is a **separate** implementation family, not proof that the divided lanes are already compiled into the monolith.

## Fail-closed next gate

1. Search checked-out repository for all `.lean` / `.lean.gz` candidates.
2. Require exact decompressed source SHA-256 match with the pinned v34 digest.
3. Compile the exact matching source under the designated Lean toolchain.
4. Resolve import paths and dependency failures without mutating frozen ancestors.
5. Only then mark `0e` for this monolith, with separate cross-engine equivalence tests required for the full OaSIs system.

**Current checkpoint:** numerically validated + artifact hash matches; exact monolithic source/compiler PASS not yet established.
