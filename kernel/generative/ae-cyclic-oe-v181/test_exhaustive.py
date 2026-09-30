#!/usr/bin/env python3
import json
import kernel

r=kernel.exhaustive_report()
assert r["status"]=="0e / v181 EXHAUSTIVE FINITE CONTROL PASS"
assert r["sealed"] is True
assert r["state_space"]["control_states"]==24
assert r["state_space"]["ring_cells"]==720
assert r["state_space"]["cells_per_control_state"]==30
assert len(r["states"])==24
assert sum(s["cells"] for s in r["states"])==720
assert len({(s["cell_start"],s["cell_end"]) for s in r["states"]})==24
assert r["closures"]["O3"]=="oeoeoe"
print(json.dumps({
  "status":"0e / v181 TEST HARNESS PASS",
  "control_states":24,
  "ring_cells":720,
  "cells_per_state":30,
  "literal_configuration_digits":r["state_space"]["literal_configuration_digits"]
},indent=2))
