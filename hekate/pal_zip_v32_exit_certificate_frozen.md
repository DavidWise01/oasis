# PAL-ZIP v32 — EXIT CERTIFICATE / APPEND-ONLY AUTHORIZED EXIT — FROZEN

**Parent:** PAL-ZIP v31  
**State:** FROZEN / 0e  
**Scope:** formal certificate identity and permanent authorized-exit provenance.

## Target

v31 tells us whether one exact exit proposal satisfies one exact policy.

v32 binds that result into a certificate and then into append-only history.

## Frozen certificate

```text
EXIT-CERT
::
exact EXIT-POLICY
+
exact EXIT-PROPOSAL
+
canonical voter/decision set
```

## Frozen authorized exit

```text
AUTHORIZED-EXIT
::
halt_head
+
action
+
target
+
EXIT-CERT
```

Then:

```text
halt head
↓
AUTHORIZED-EXIT
↓
new append-only head
```

## Certification

- certificate vote-order tests: 2
- certificate order failures: 0
- policy-swap attacks: 2
- policy swaps preserving same cert: 0
- halt-head swap attacks: 2
- halt-head swaps preserving same cert: 0
- proposal-swap attacks: 3
- proposal swaps preserving same cert: 0
- foreign-cert event attacks: 1
- foreign-cert event rejections: 1
- append-prefix tests: 1
- append-prefix failures: 0
- stale-cert attacks: 2
- stale-cert false accepts: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
EXIT AUTHORITY
::
policy-specific
+
proposal-specific
+
halt-specific
```

A certificate cannot be transferred to:

```text
another policy
another halt head
another action
another target
```

and the successful exit becomes permanent provenance rather than transient runtime state.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
