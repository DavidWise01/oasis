#!/usr/bin/env python3
import json
import kernel

r=kernel.exhaustive_report()
assert r["status"]=="0e / v183 ZERO-I TRANSFORM PASS"
assert r["canon"]=="{{0::{i::}}}"
assert r["bijective"] is True
assert r["source_states"]==3
assert r["image_states"]==3
assert [x["source"] for x in r["mapping"]]==["-1","0","+1"]
assert [x["image"] for x in r["mapping"]]==["0","-1","0&1"]
print(json.dumps(r,indent=2))
