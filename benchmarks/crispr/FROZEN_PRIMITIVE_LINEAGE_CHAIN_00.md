# Frozen Primitive Lineage Chain 00

Status: **PASS**

Canonical chain length: 9
Canonical head: `28f564aa74fc27394c033a1b2fa2533ea06b92ab96836dad2af3006ce9a384a9`

Checks enforced:
- content hash integrity
- exact parent linkage
- append-only sequence increments
- monotonic time
- expected canonical head / anti-replay

Results:

```text
clean control             -> ACCEPT
fork ancestry             -> DETECT
rewrite parent             -> DETECT
truncate lineage          -> DETECT
replay old valid lineage  -> DETECT
duplicate record          -> DETECT
time rollback             -> DETECT
sequence skip             -> DETECT

RESULT = 0e
```

Key invariant:

```text
record[n].parent == hash(record[n-1])
record[n].seq    == record[n-1].seq + 1
record[n].time   >  record[n-1].time
head             == canonical expected head
```
