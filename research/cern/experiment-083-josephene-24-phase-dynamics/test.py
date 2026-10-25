import math,csv,json
from pathlib import Path
P=Path(__file__).parent
B=[5,5,5,7,7,5,5,7,7,7]
def beat(t):
 s=0
 for b in B:
  s+=b
  if t<s:return b
 raise ValueError(t)
rows=[];summary=[];checks=0
for address in range(24):
 phase=math.pi*address/12;start=phase;work=diss=0.
 for unit in range(60):
  current=1.18*beat(unit)/6
  for substep in range(100):
   next_phase=phase+.01*(current-math.sin(phase))
   dtheta=next_phase-phase
   dw=current*dtheta
   du=math.cos(phase)-math.cos(next_phase)
   work+=dw;diss+=dw-du;phase=next_phase
   assert abs(work-diss-(math.cos(start)-math.cos(phase)))<1e-9
   assert math.isfinite(phase)
   checks+=2
  winding=math.floor(phase/(2*math.pi))
  remainder=phase-winding*2*math.pi
  assert 0<=remainder<2*math.pi+1e-12
  assert abs(phase-(winding*2*math.pi+remainder))<1e-11
  R=2+.5*math.cos(remainder)
  assert R>=1.5-1e-12
  checks+=3
  rows.append(dict(address=address,unit=unit,beat=beat(unit),winding=winding,phase=phase,remainder=remainder,work=work,dissipation=diss))
 summary.append(dict(address=address,final_winding=math.floor(phase/(2*math.pi)),work=work,dissipation=diss,energy_change=math.cos(start)-math.cos(phase)))
assert checks==292320 and len(rows)==1440
with (P/'timeline.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
result=dict(status='PASS',checks=checks,winding_values=sorted(set(x['final_winding'] for x in summary)),max_ledger_residual=max(abs(x['work']-x['dissipation']-x['energy_change']) for x in summary),summary=summary)
(P/'results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='summary'},indent=2))
