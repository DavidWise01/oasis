#!/usr/bin/env python3
"""SHEET 42 v06 five-ring synchronization test. Run from this directory."""
import importlib.util,json,time
from sheet42 import START,digest
spec=importlib.util.spec_from_file_location("toroid_v05","sheet42-toroid-v05.py")
v05=importlib.util.module_from_spec(spec);spec.loader.exec_module(v05)
TURNS=10;TOTAL=TURNS*v05.TICKS;counts=[0]*v05.RINGS
checkpoints=[];s=START;seen={s};repeat=0;start=time.perf_counter()
for t in range(TOTAL):
    counts[t%v05.RINGS]+=1
    s=v05.tick(s,t)
    repeat+=(s in seen);seen.add(s)
    if (t+1)%v05.TICKS==0:
        checkpoints.append({"turn":(t+1)//v05.TICKS,"address":(t+1)%v05.TICKS,
          "next_ring":(t+1)%v05.RINGS,"counts":counts.copy(),
          "digest":digest(s),"same_as_initial":s==START})
final=digest(s)
for t in range(TOTAL-1,-1,-1):s=v05.tick(s,t,True)
checks={
"ten_turns":len(checkpoints)==10,
"five_rings":v05.RINGS==5,
"same_visits_each_turn":all(len(set(c["counts"]))==1 for c in checkpoints),
"zero_address_each_turn":all(c["address"]==0 for c in checkpoints),
"zero_next_ring_each_turn":all(c["next_ring"]==0 for c in checkpoints),
"720_visits_per_ring":counts==[720]*5,
"period_360_mod_5":360%5==0,
"ten_distinct_turn_states":len({c["digest"] for c in checkpoints})==10,
"no_repeated_full_states":repeat==0,
"reverse_exact":s==START,
"100800_updates":TOTAL*28==100800,
"symbolic_time_retained":"1^-1/360" in v05.LITERAL}
result={"schema":"oasis/sheet42/phase-sync-v06","checks":checks,
"passed":sum(checks.values()),"total":len(checks),"turns":TURNS,
"ticks":TOTAL,"node_updates":TOTAL*28,"ring_counts":counts,
"unique_full_states":len(seen),"full_state_repetitions":repeat,
"reverse_exact":s==START,"final_state_sha256":final,
"checkpoints":checkpoints,"seconds":time.perf_counter()-start,
"limitation":"Address/visit alignment, not physical phase-locking or full-state return."}
print(json.dumps(result,indent=2))
assert all(checks.values())
