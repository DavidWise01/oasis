#!/usr/bin/env python3
"""129 proton insertion positions in the OaSIs v02 8+2 register fixture.
Requires oasis_quantum_dot_16_proton_v02.py on PYTHONPATH.
"""
import json,hashlib,time
from oasis_quantum_dot_16_proton_v02 import run,undo,PROTON,base
DOTS=tuple(range(128))
def order(i): return DOTS[:i]+(PROTON,)+DOTS[i:]
def changed(a,b):return sum(x!=y for x,y in zip(a,b))
def circ(a,b):return max(min((x-y)&base.MASK,(y-x)&base.MASK) for x,y in zip(a,b))
t=time.perf_counter()
seqs=[order(i) for i in range(129)]
outs=[run(seq) for seq in seqs]
delta=[changed(outs[i],outs[i+1]) for i in range(128)]
jump=[circ(outs[i],outs[i+1]) for i in range(128)]
checks={
 "129_positions":len(outs)==129,
 "dot_order_fixed":all(tuple(x for x in s if x!=PROTON)==DOTS for s in seqs),
 "exact_reverse":all(undo(s,o)==base.INIT for s,o in zip(seqs,outs)),
 "distinct_outputs":len(set(outs))==129,
 "repeatability":all(run(s)==o for s,o in zip(seqs,outs)),
 "different_endpoints":outs[0]!=outs[-1],
 "adjacent_sensitive":all(d>0 for d in delta),
 "one_proton_per_sequence":all(s.count(PROTON)==1 for s in seqs),
 "ten_components":all(len(o)==10 for o in outs),
 "all_dot_events_once":all(len(s)==129 and len(set(s))==129 for s in seqs)
}
result={"schema":"oasis/8cube-16slots-proton-2workers/insertion-v03","checks":checks,"passed":sum(checks.values()),"total":len(checks),"unique_final_states":len(set(outs)),"positions":129,"reverse_passes":sum(undo(s,o)==base.INIT for s,o in zip(seqs,outs)),"adjacent_changed":{"min":min(delta),"mean":sum(delta)/128,"max":max(delta)},"top_jumps":[{"positions":[i,i+1],"modular_max_jump":jump[i],"changed_lanes":delta[i]} for i in sorted(range(128),key=lambda i:jump[i],reverse=True)[:5]],"seconds":time.perf_counter()-t,"scope":"Symbolic 32-bit modular state machine; not a nuclear simulation."}
print(json.dumps(result,indent=2))
if result["passed"]!=result["total"]:raise SystemExit(1)
