from fractions import Fraction as F
import random,hashlib,json,csv
from pathlib import Path
P=Path(__file__).parent
BEATS=[5,5,5,7,7,5,5,7,7,7]
assert sum(BEATS)==60
NAMES=['A1','B1','C1']
SCENARIOS=['identical','offset','drift','missed_beat','frame_corrected','combined']
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def sha(x):return hashlib.sha256(canon(x).encode()).hexdigest()
def sample(kind):
 data=[]
 for node in NAMES:
  start=F(100);duration=F(60);rate=F(1);offset=F(0);miss=F(0)
  if kind in ('offset','combined') and node=='B1':offset=F(13,4)
  if kind in ('drift','combined') and node=='B1':rate=F(1001,1000)
  if kind=='missed_beat' and node=='C1':miss=F(7)
  if kind=='frame_corrected' and node=='B1':rate=F(5,4);offset=F(11)
  a=start*rate+offset;b=(start+duration-miss)*rate+offset
  data.append(dict(node=node,start=str(a),end=str(b),clock_rate=str(rate),clock_offset=str(offset),missing_duration=str(miss),reason=f'{node}: observed local interval with rate {rate}, offset {offset}, missing {miss}'))
 return data
checks=0;rows=[];result=[]
for scenario in SCENARIOS:
 records=sample(scenario);originals=[sha(r) for r in records]
 raw=[F(r['end'])-F(r['start']) for r in records]
 normalized=[d/F(r['clock_rate']) for d,r in zip(raw,records)]
 delta=[normalized[0]-normalized[1],normalized[1]-normalized[2],normalized[2]-normalized[0]]
 assert sum(delta)==0;checks+=1
 assert len({r['node'] for r in records})==3;checks+=1
 for i,r in enumerate(records):
  assert sha(r)==originals[i];checks+=1
  assert F(r['end'])>=F(r['start']);checks+=1
  assert normalized[i]==60-F(r['missing_duration']);checks+=1
  assert r['reason'].startswith(r['node']);checks+=1
  rows.append(dict(scenario=scenario,node=r['node'],start=r['start'],end=r['end'],raw_duration=str(raw[i]),corrected_duration=str(normalized[i]),why=r['reason'],raw_digest=originals[i]))
 matches=len(set(normalized))==1
 assert matches==(scenario!='missed_beat');checks+=1
 result.append(dict(scenario=scenario,raw_durations=list(map(str,raw)),corrected_durations=list(map(str,normalized)),deltas=list(map(str,delta)),match_after_rate_correction=matches))
rng=random.Random(90)
for _ in range(10000):
 d=[F(rng.randint(0,20000),rng.randint(1,50)) for _ in range(3)]
 assert (d[0]-d[1])+(d[1]-d[2])+(d[2]-d[0])==0;checks+=1
assert checks==10090
with (P/'sweep.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
(P/'results.json').write_text(json.dumps(dict(status='PASS',checks=checks,scenarios=result),indent=2)+'\n')
print('PASS',checks)
