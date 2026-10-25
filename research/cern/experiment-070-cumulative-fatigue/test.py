from fractions import Fraction as F
from pathlib import Path
import json,csv
BASE=Path(__file__).parent
PULSE=F(1,20);CAP=F(1,10);DAMAGE_LIMIT=F(1,20)
RELEASES=[F(0),F(1,200),F(1,100),F(1,50),F(3,100),F(1,20)]
rows=[];summary=[];checks=0
for release in RELEASES:
 held=vented=overflow=F(0);damage=[F(0),F(0)];first=None
 for tick in range(1,21):
  vent=min(release,held);held-=vent;vented+=vent
  captured=min(PULSE,CAP-held);leaked=PULSE-captured
  held+=captured;overflow+=leaked
  damage=[d+leaked/2 for d in damage]
  if first is None and any(d>=DAMAGE_LIMIT for d in damage):first=tick
  assert held+vented+overflow==tick*PULSE;checks+=1
  assert 0<=held<=CAP;checks+=1
  assert damage[0]==damage[1]==overflow/2;checks+=1
  assert leaked>=0;checks+=1
  rows.append(dict(release_J=str(release),tick=tick,held_J=str(held),vented_J=str(vented),overflow_total_J=str(overflow),neighbor_damage_J=str(damage[0])))
 assert held+vented+overflow==20*PULSE;checks+=1
 summary.append(dict(release_J=str(release),first_failure=first,total_overflow_J=str(overflow)))
assert checks==486 and [s['first_failure'] for s in summary]==[4,5,5,6,9,None]
with (BASE/'sweep.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
(BASE/'results.json').write_text(json.dumps({'status':'PASS','checks':checks,'scenarios':summary},indent=2)+'\n')
print(json.dumps(summary,indent=2))
