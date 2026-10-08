#!/usr/bin/env python3
"""OaSIs NEON ..|.. closure, symbolic five-step 3-close/2-open up to 184."""
import json
N=184
records=[]
for n in range(1,N+1):
    phase=(n-1)%5
    records.append({"n":n,"window":(n-1)//5,"phase":phase,"op":"close" if phase<3 else "open","lane":(n-1)%8})
a=sum(x["op"]=="close" for x in records); b=N-a
checks={"184_count":len(records)==184,"append_only":all(x["n"]==i+1 for i,x in enumerate(records)),"3_close_2_open":all(x["op"]==("close" if x["phase"]<3 else "open") for x in records),"window_36_remainder_4":divmod(N,5)==(36,4),"sum_preserved":a+b==184,"eight_lanes":set(x["lane"] for x in records)==set(range(8)),"workers_two":len([a,b])==2,"final_op_open":records[-1]["op"]=="open","all_addresses_unique":len({x["n"] for x in records})==184,"not_closed_at_184":records[-1]["phase"]!=2}
report={"limit":N,"complete_windows":N//5,"remainder":N%5,"close_events":a,"open_events":b,"last_window":records[-4:],"checks":checks,"passed":sum(checks.values()),"total":len(checks),"scope":"Symbolic register only, not nuclear shell calculations"}
print(json.dumps(report,indent=2))
assert all(checks.values())
