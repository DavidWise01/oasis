# Frozen Primitive Common-Root Dependency 00

Status: **PASS**

Canonical wrapper:
`f25e14fb07112891fcd16529ba9c52d4e164d1e3f5adcf90001a6fc6700aa02b`

This test traces anchor dependencies transitively rather than trusting only direct configuration.

Results:

```text
EXT0 + EXT1 hidden shared DNS root      -> DETECT
multi-hop common parent                 -> DETECT
EXT0 + EXT2 independent                 -> CONFIRM
3 anchor IDs                            -> 2 effective domains
3-of-3 graph-domain quorum              -> REJECT
2-domain quorum                         -> VALID
chained shared dependency               -> COLLAPSE TO 1 COMPONENT
shared-root evidence                    -> RETAIN
```

Dependency rule:

```text
independent(A,B)
iff
upstream_closure(A) ∩ upstream_closure(B) = ∅
```

Graph result:

```text
EXT0 ----- DNS_A ----- DNS_ROOT_X ---+
                                     |
EXT1 ----- DNS_B ----- DNS_ROOT_X ---+

EXT2 ----- DNS_C ----- DNS_ROOT_Z

therefore:
EXT0 + EXT1 = correlated domain
EXT2        = independent domain

3 IDs -> 2 effective failure domains
```

RESULT = 0e
