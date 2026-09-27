# Frozen Primitive Observer Poisoning 00

Status: **PASS**

Truth observation hash:
`9f49b37b9ec7b76bc890005064b95d50f6800bc5732454f9275b5422d457cf7d`

Poisoned observation hash:
`c8381255409178c8f5285d40e7533ec38b00c2903455697db10225606bd3625b`

Results:

```text
2 truthful independent observers         -> ACCEPT TRUTH
1 truth / 1 poison                       -> NO CONSENSUS
2 truth / 1 poison                       -> ACCEPT TRUTH
2 poison IDs / 1 shared root             -> COUNT AS 1
2 independent poison roots at threshold2 -> FALSE OBSERVER CONSENSUS boundary
2 poison / 2 truth with threshold3       -> NO CONSENSUS
3 truth / 1 poison with threshold3       -> ACCEPT TRUTH
resolved truth shared DNS root            -> DETECT
```

Key invariant:

```text
observer_id != independent observer

observer consensus must count
independent provenance roots
and must itself have a threshold
```

Residual boundary:

```text
if threshold-many genuinely independent observers
coordinate on the same false dependency graph,
the observer layer can still be fooled.
```

RESULT = 0e
