# MORE GARBAGE algorithm v00

```text
candidate
  ↓
+verify   exact recovery still possible?
  ↓ YES
+sort     enumerate reversible encoding paths; rank strict badness reduction
  ↓ YES
+verify   inverse path reproduces original garbage exactly
  ↓ YES
compress  NFC → UTF-8 → lossless compression witness
  ↓ YES
expand    expansion returns recovered invariant exactly
  ↓ YES
ISOMORPHIC → eligible for AETHER | TEMPORAL

any NO → rm / A::xx → delete current → free space → advance
```

v00 searches cp1252, latin1, and mac_roman to depth 3. A repair is accepted only when its inverse path reproduces the exact source string.

Ag remains the symbolic compression stage. v00 uses zlib only as an executable lossless compression/expansion witness.

AETHER/TEMPORAL routing remains intentionally unspecified.

Local test record before publication:

```text
fixed corpus       11 / 11 PASS
synthetic sweep    60 / 60 PASS
Lean               pending user 0e
```
