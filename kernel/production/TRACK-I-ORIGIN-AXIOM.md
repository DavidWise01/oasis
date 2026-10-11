# Track i — Universal Origin Axiom (symbolic)

Status: SPECIFICATION-ONLY / UNVERIFIED PHYSICAL INTERPRETATION. Extends THREE-TRACK-CONTROL-MODEL.md; does not modify frozen RC0 code or release-gate acceptance.

## Source notation
```text
{{ i [ universal constant :: from nothing 0 comes something :: quantum dot :: `.` ] }}
```

## Deterministic framework interpretation
- `0` = uninstantiated/empty *local state register* (NOT proven metaphysical nothingness, physical vacuum, or literal energy-free origin).
- `.` = first addressable discrete event or state in Track i, called a **quantum dot** in the user's symbolic language (NOT necessarily a semiconductor quantum dot or physical Planck-scale object).
- `i` = identity context assigning an immutable ID and provenance to the transition.
- Transition: `(i, state=0, event=create) -> (i, state=., sequence=1)`, only when authorization and append-only storage succeed.
- If preconditions fail, the register stays `0` or the pending event is quarantined; no asserted successful creation.
- Every subsequent state uses a **new** append-only event/sequence; no rewrite of the first dot.

## Proof obligations before executable adoption
1. Define canonical serialization/ID and genesis event hash.
2. Demonstrate exactly-once identity issuance or documented idempotent retries.
3. Reject duplicate genesis, forged origin and replay of retired identity.
4. Verify zero-state remains unchanged on interrupted prepare.
5. Produce one independently readable signed/hashed audit lineage.

## Three-track propagation
```text
T1 i    : 0 --authorized genesis--> .   (identity and intent)
T2 u    : . --verified consequence--> accepted / quarantined
T3 u.s. : created --> live --> retired --> successor (new dot)
```

The expression `0 -> .` is **symbolic**, and does not establish that something physically arises from absolute nothing. Terms “universal constant” and “quantum” remain nomenclature until defined dimensionally and supported by independent physical evidence.

P0 source freeze remains unchanged. P0 blockers B01-B03 remain open. Formal acceptance: 0/6 gates.
