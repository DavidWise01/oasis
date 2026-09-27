# Frozen Primitive Provenance Spoof 00

Status: **PASS**

Quorum rule:

```text
YES votes >= 3
AND unique provenance chains >= 3
AND independent ancestry roots >= 3
```

Tests:
- clean independent control
- duplicated ancestry under different witness names
- forged source ID with shared root
- three nominal votes from one root
- five nominal votes from only two roots
- valid three-vote / three-root quorum
- replayed witness record with deduplication

Result:

```text
duplicate ancestry       -> REJECT
forged source ID         -> REJECT
3 votes / 1 root         -> REJECT
5 votes / 2 roots        -> REJECT
3 votes / 3 roots        -> ACCEPT
replayed record          -> DEDUPE, then valid 3-root quorum

RESULT = 0e
```

The test demonstrates a validator property only. It does not establish biological accuracy.
