from fractions import Fraction as F
import csv,json
from pathlib import Path
P=Path(__file__).parent
CAP=F('0.100'); VENT=F('0.020'); TH=F('0.050'); HEAL=F('0.005')
rows=[]; summary=[]; assertions=0
for drive in [F('0.000'),F('0.010'),F('0.020'),F('0.030'),F('0.050'),F('0.080')]:
    held=F(0); vented=F(0); overflow=F(0); total=F(0); damage=F('0.015'); state=0; first=None
    for tick in range(1,41):
        v=min(VENT,held); held-=v;vented+=v
        incoming=drive;total+=incoming
        captured=min(incoming,CAP-held) if state==0 else F(0)
        held+=captured; leaked=incoming-captured;overflow+=leaked
        if state==0:
            if incoming:damage+=incoming/4
            else:damage=max(F(0),damage-HEAL)
            if damage>=TH:state=-1;first=tick
        assert held+vented+overflow==total;assert F(0)<=held<=CAP;assert state in (-1,0)
        assertions+=3
        rows.append(dict(drive_J=str(drive),tick=tick,state=state,held_J=str(held),vented_J=str(vented),overflow_J=str(overflow),damage_index=str(damage)))
    summary.append(dict(drive_J=str(drive),first_failure_tick=first,final_state=state,total_in_J=str(total),vented_J=str(vented),held_J=str(held),overflow_J=str(overflow)))
assert assertions==720
with (P/'sweep.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
(P/'results.json').write_text(json.dumps(dict(experiment='PRIM-073',assertions=assertions,status='PASS',assumptions='symbolic cyclic fatigue',scenarios=summary),indent=2)+'\n')
print(json.dumps(summary,indent=2));print('PASS',assertions)
