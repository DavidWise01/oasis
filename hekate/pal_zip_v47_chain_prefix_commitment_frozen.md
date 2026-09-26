# PAL-ZIP v47 — CHAIN-PREFIX COMMITMENT — FROZEN

**Parent:** PAL-ZIP v46  
**State:** FROZEN / 0e  
**Scope:** bind the complete witness prefix into every new chain identity.

## Target

v46 proves adjacent witness continuity.

v47 freezes a stronger prefix commitment so an attacker cannot:

```text
truncate a valid chain
replace its prefix with a different valid ancestry
graft an older prefix under a newer tail
splice a valid tail from another branch
```

and obtain the same chain identity.

## Frozen prefix head

```text
PREFIX-HEAD
::
depth
+
previous_prefix_head
+
exact RANK-WITNESS
```

Genesis is:

```text
PREFIX-ROOT
```

Then:

```text
H1 := PREFIX-HEAD(1, PREFIX-ROOT, W1)

H2 := PREFIX-HEAD(2, H1, W2)
```

So `H2` commits recursively to the complete ordered prefix.

## Important control

Two sibling histories may legitimately share the **same** `H1`.

That is not a prefix-replacement attack.

The attack requires:

```text
replacement_H1 != authentic_H1
```

The first test pass caught this distinction and was **not frozen**.
The corrected test separates same-prefix sibling controls from genuine different-prefix attacks.

## Frozen continuity

Both are required:

```text
previous.post_head = current.pre_head
previous.eligible_after = current.eligible_before
```

and:

```text
current PREFIX-HEAD
binds
exact previous PREFIX-HEAD
```

## Certification

- complete histories: 12
- valid prefix links checked: 24
- valid prefix failures: 0
- legitimate final-head collisions: 0
- truncation tests: 12
- truncations preserving final head: 0
- genuine prefix-replacement attacks: 96
- prefix-replacement false accepts: 0
- same-prefix sibling controls: 36
- same-prefix control failures: 0
- older-prefix graft attacks: 132
- older-prefix graft false accepts: 0
- wrong-depth attacks: 12
- wrong-depth false accepts: 0
- witness-tamper attacks: 12
- witness-tamper false accepts: 0
- cross-branch tail-splice attacks: 96
- cross-branch tail-splice false accepts: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
FINAL CHAIN HEAD
::
commitment to
the entire ordered witness prefix
```

Therefore:

```text
truncate(prefix)
!=
original final head
```

```text
replace(prefix with different valid ancestry)
!=
original final head
```

```text
graft(old prefix, new tail)
!=
original final head
```

and a tail from another valid branch cannot pass exact state continuity.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
