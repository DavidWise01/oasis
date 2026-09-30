#!/usr/bin/env python3
import json
import kernel
r=kernel.two_boundary_test()
assert r["status"]=="0e / v182 TWO BOUNDARIES PASS"
assert r["total_boundary_transitions_tested"]==1440
assert r["unique_buckets"]==720 and r["unique_receipts"]==720
assert r["boundaries"]["ingress"]["tests"]==720
assert r["boundaries"]["egress"]["tests"]==720
assert r["boundaries"]["ingress"]["parent_preserved"] is True
assert r["boundaries"]["egress"]["parent_preserved"] is True
assert r["boundaries"]["egress"]["u_disposed"] is True
assert r["boundaries"]["egress"]["payload_exposed_bytes"]==0
assert r["canon"]["i"]=="{{i = inf + 1{{B{{u}}cket}}}}"
assert r["canon"]["referent"]=="0011 = plank 0"
print(json.dumps(r,indent=2))
