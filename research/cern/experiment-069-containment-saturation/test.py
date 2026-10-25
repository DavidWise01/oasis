from fractions import Fraction as F
from pathlib import Path
import json,csv
P=Path(__file__).parent
PULSE=F(1,20);CAPACITY=F(1,10);FAIL=F(1,50)
RELEASES=[F(0),F(1,200),F(1,100),F(1,50),F(3,100),F(1,20)]
rows=[]
for release in RELEASES:
 held=F(0);released=F(0);overflow_total=F(0)
 for tick in range(1,11):
  vent=min(held,release);held-=vent;released+=vent
  captured=min(PULSE,CAPACITY-held);leaked=PULSE-captured
  held+=captured;overflow_total+=leaked
  assert 0<=held<=CAPACITY
  assert tick*PULSE==held+released+overflow_total
  rows.append({'release_per_tick_J':float(release),'tick':tick,'held_J':float(held),'safe_released_J':float(released),'overflow_J':float(overflow_total),'pulse_overflow_J':float(leaked),'neighbor_J':float(leaked/2),'failed_this_tick':leaked/2>=FAIL})
 assert 10*PULSE==held+released+overflow_total
with (P/'sweep.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
summ=[]
for release in RELEASES:
 s=[r for r in rows if r['release_per_tick_J']==float(release)]
 summ.append({'release_per_tick_J':float(release),'first_saturation_tick':next((r['tick'] for r in s if r['held_J']==float(CAPACITY)),None),'first_neighbor_failure_tick':next((r['tick'] for r in s if r['failed_this_tick']),None),'total_overflow_J':s[-1]['overflow_J']})
result={'status':'PASS','cases':60,'assertions':126,'scenarios':summ}
(P/'results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
