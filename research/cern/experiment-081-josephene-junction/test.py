from math import sin,cos,pi
from fractions import Fraction as F
import csv,json
from pathlib import Path
P=Path(__file__).parent
BEATS=[5,5,5,7,7,5,5,7,7,7]
assert sum(BEATS)==60
dt=.0025; steps=24000
cases={'subcritical':.7,'threshold':1.0,'supercritical':1.3,'beat_modulated':1.1}
rows=[];checks=0;out={}
for name,bias in cases.items():
 phi=W=D=E=0.
 for k in range(steps):
  t=k*dt;unit=int(t)%60;cum=0;weight=5
  for b in BEATS:
   cum+=b
   if unit<cum:weight=b;break
  I=bias*(weight/6 if name=='beat_modulated' else 1)
  f=lambda q:I-sin(q)
  k1=f(phi);k2=f(phi+dt*k1/2);k3=f(phi+dt*k2/2);k4=f(phi+dt*k3)
  nxt=phi+dt*(k1+2*k2+2*k3+k4)/6
  delta=nxt-phi; dU=cos(phi)-cos(nxt); work=I*delta; diss=work-dU
  assert diss>=-1e-7
  W+=work;D+=diss;E+=dU
  assert abs(W-D-E)<1e-8
  assert abs(1-cos(nxt)-E)<1e-8
  checks+=2
  if k%40==0:rows.append(dict(case=name,time=(k+1)*dt,phase=nxt,current=sin(nxt),voltage_norm=delta/dt,bias=I,potential=1-cos(nxt),work=W,dissipation=D,slips=int(nxt/(2*pi))))
  phi=nxt
 out[name]=dict(phase_final_rad=phi,full_positive_slips=int(phi/(2*pi)),total_work=W,dissipated_energy=D,stored_energy_change=E,ledger_residual=W-D-E)
assert out['subcritical']['full_positive_slips']==0
assert out['supercritical']['full_positive_slips']>0
assert out['beat_modulated']['full_positive_slips']>0
assert checks==192000
with (P/'sweep.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
(P/'results.json').write_text(json.dumps(dict(status='PASS',assertions=checks+4,cases=out),indent=2)+'\n')
print(json.dumps(out,indent=2))
