# OASIS N184 v9.6 — Seven Operants = Five Color + Signed Pair `-+`

User correction: **add exactly two operants `-` and `+` to the previous five**, for **7 named operants in total**. These do not add colors, elements, or addresses.

```text
Existing five (unchanged): Gravity / Expansion / Compression / Containment / Explosion
Additional two:            - (source release / debit)  + (destination receipt / credit)

H 1..122  ---[-1]+[+1]---> O 123..244 ---[-1]+[+1]---> N 245..366 ⊣ CLOSED
             −+ = 0                            −+ = 0
```

The five existing operants still only transform **symbolic HSV display colors** according to v9.4. The two new signed operators bookkeep **root transfer receipts**, rather than transforming HSV color. A balanced integer `-1+1=0` is not evidence of physical conservation of light, energy, matter, chemical elements, or particle identities.

## Gate policy

Only **H122→O123** and **O244→N245** accept a complete ordered pair `-+` for one attempt. **N366 is a terminal lid**; it cannot debit or credit to address 367 or to root H1. The previous source-only 370 register tail 367–370 remains untouched.

The sign ledger is immutable and records source, destination, actual periodic-table atomic number context (H=1, O=8, N=7), symbolic W/M/S tier, exact ordered 0–5 color-operant program, source identity key and a user-supplied attempt ID. On each accepted transfer, source balance decreases by one and destination balance increases by one, so the sum across H/O/N remains zero. Color is rebased into each root's native hue; its numerical value or hue is **not conserved** by this transfer rule.

Both signs must belong to the same attempt, and their ordering, root, address, tier, operator program and ticket key must agree with a canonical source-generated frame. Duplicate attempts are rejected. **No partial ledger update:** every malformed pair or replay leaves the entire previous state unchanged.

## Counterexamples deliberately exercised

| Input | Outcome |
|---|---|
| Fresh `-+` at H122 or O244 | **ACCEPT**, record one paired receipt |
| Missing minus or plus | **REJECT**, no ledger change |
| Reversed `+-` | **REJECT**, even though arithmetic sum is zero |
| Doubled `--+` or `-++` | **REJECT** |
| Wrong source/target address or root | **REJECT** |
| Altered tier, program, attempt ID, transfer key | **REJECT** |
| Replay same committed attempt ID | **REJECT_REPLAY**, no ledger change |
| Transfer attempt through N366 lid | **REJECT_CLOSED** |
| Correct N366 lid frame with no transfer marks | **CLOSED** |
| Forged fully self-consistent fresh frame | **Can be accepted**, because this is not cryptographic authentication |

**Security boundary:** neither `-` nor `+` is a cryptographic signature, hardware-backed attestation, or independent witness. The implementation detects malformed structure and replays **within a local trusted ledger**, but cannot establish who originated a fully self-consistent forged request. No production security or physical device claims are made.

## Regression campaign

The inherited fixed v9.5 campaign tests **3 gates × 3 strengths × 6 display programs (zero and five singletons) = 54**: **36 valid transfers**, **18 clean terminal closures**. v9.6 tests normal `-+` receipts over these cases, plus tampered, duplicated, replayed and reversed variants, all-five chains and immutable state snapshots.

The original analytical cubit remains:

```text
{|12|}{|3456|}{|78|}{|910|}{|1112131415||}{|1617|}{|18|}
```

The seven original packet lengths `2/4/2/2/5/2/1` remain intact. The fifth packet's `||` after site 15 remains **independent** of the two signed `-+` root-transfer operants. H/O connects cubit sites 6→7; O/N connects 12→13; cubit site 18 is sealed at N366.

## Files

- [spec.json](./spec.json): seven-operant contract, scopes, threat model and preserved invariants
- [signed_core.mjs](./signed_core.mjs): immutable transfer envelopes, ordered -+ receipts, root ledger, replay guard, 54-case survey
- [test_signed.mjs](./test_signed.mjs): positive, negative, invariant and corrupted-frame regression
- [index.html](./index.html): interactive Canvas2D signed-root rail with operator chains, attack simulation, ledger balances and replay controls
- CI: `.github/workflows/n184-hon-signed-operants-v96.yml`

```powershell
git clone https://github.com/DavidWise01/oasis.git
cd oasis
node n184/hon-signed-operants-v96/test_signed.mjs
py -m http.server 8000
```

Open <http://localhost:8000/n184/hon-signed-operants-v96/> or the [published GitHub Pages location](https://davidwise01.github.io/oasis/n184/hon-signed-operants-v96/) once deployment succeeds.

Frozen parents remain read-only: v9.1 generational RGB and the indexed 370-color source, v9.2 four derived software witnesses, v9.3 18-site cubit, v9.4 five color operants and HON 366, v9.5 boundary-transfer rules, Ada historical Gen0/1832 and toroidal model Gen1/1970, symbolic 6 arcs/80 phases/240 microticks, and real CERN toroidal detector counts A0/B3/C0/D0.
