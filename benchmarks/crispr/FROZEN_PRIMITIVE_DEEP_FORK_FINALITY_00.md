# Frozen Primitive Deep Fork Finality 00

Status: **PASS**

Finality depth: 3
Quorum: 3

Tested:
- equal-length / equal-quorum pre-finality ties
- equal-length / equal-quorum finalized ties
- longer pre-finality competing branch
- late longer branch after finality
- arrival-order independence
- loser descendants remain noncanonical
- immutable finality checkpoint

```text
before finality:
branch choice may resolve deterministically

after finality:
canonical ancestry may not be rewritten

finality checkpoint:
seq=4
hash=356aeec1eeb1a189ac968c66a3b30f4809d63b7fc82a7b5172493e968f4261d6

RESULT = 0e
```
