#!/usr/bin/env python3
"""AETHER-123(B): deterministic synthetic interior pilot calibration; not field assurance."""
from pathlib import Path
import csv,hashlib,hmac,json
import numpy as np
from scipy.stats import beta
D=Path(__file__).resolve().parent
T=24;N=560;LIMIT=.025;KEY=b'aether123-demo-only';PROBES=(32,96,160,224)
SC=('clean','negative_offset','positive_offset','low_gain','high_gain','drift','nonlinear','hard_saturation','hazard_shift')
SEEDS=range(123001,123061)
def signed(b):return dict(b,mac=hmac.new(KEY,json.dumps(b,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest())
def authentic(p):
 b={k:v for k,v in p.items() if k!='mac'}
 return hmac.compare_digest(p.get('mac',''),signed(b)['mac'])
def upper(e):return 1.0 if e>=N else float(beta.ppf(.95,e+1,N-e))
def truth_risk(sc,t):return .09 if (8<=t<18 or (sc=='hazard_shift' and 5<=t<21)) else .003
def parameters(sc,t):
 if sc=='negative_offset':return 1.0,-9.0,0.0
 if sc=='positive_offset':return 1.0,9.0,0.0
 if sc=='low_gain':return .86,-2.0,0.0
 if sc=='high_gain':return 1.13,5.0,0.0
 if sc=='drift':return 1-.005*t,-.2*t,0.0
 if sc=='nonlinear':return 1.,0.,0.00048
 if sc=='hard_saturation':return 1.5,18.,0.
 return 1.,0.,0.
def sensor(sc,t,x):
 g,b,c=parameters(sc,t)
 return max(0.,min(235. if sc=='hard_saturation' else N,g*x+b+c*(x-128.)**2))
def packet(seed,sc,t):
 rng=np.random.default_rng(seed+SC.index(sc)*100003+t*7927)
 q=truth_risk(sc,t);x=int(rng.binomial(N,q));y=sensor(sc,t,x)
 v=tuple(sensor(sc,t,k) for k in PROBES)
 b=dict(source='risk-audit',seq=t,observed_t=t,counter=t,valid_until=t+1,epoch=1,independent=True,n=N,
        measured=round(y,6),probe_commit=t,probes=[round(z,6) for z in v])
 return q,x,signed(b)
def calibrate(p):
 ys=p['probes'];xs=PROBES
 if len(ys)!=4:return False,None,None,None
 g=(ys[2]-ys[0])/(xs[2]-xs[0]);b=ys[0]-g*xs[0]
 residual=max(abs(ys[i]-(g*xs[i]+b)) for i in (1,3))
 okay=(.8<=g<=1.2 and -16<=b<=16 and residual<=1.0 and
       all(.001<y<N-1 for y in ys) and all(ys[i]<ys[i+1] for i in range(3)))
 return okay,g,b,residual
def run(seed,sc,policy):
 out=[];h='0'*64
 for t in range(T):
  risk,x,p=packet(seed,sc,t)
  signed_ok=(authentic(p) and p['source']=='risk-audit' and p['seq']==t and p['observed_t']==t
   and p['counter']==t and p['valid_until']==t+1 and p['epoch']==1 and p['independent'] is True
   and p['n']==N and p['probe_commit']==t)
  good,g,b,res=calibrate(p)
  if policy=='frozen_122':
   accepted=signed_ok and abs(sensor(sc,t,0))<=.001 and abs(sensor(sc,t,128)-128)<=.001
   corrected=p['measured']
  else:
   accepted=signed_ok and good
   margin=0.0 if abs(g-1)<1e-9 and abs(b)<1e-9 and res<1e-9 else 3.0
   corrected=max(0,min(N,(p['measured']-b)/g+margin)) if accepted else N
  act=accepted and upper(int(np.ceil(corrected)))<=LIMIT
  cost=(10*N*risk if act else .05*N)+(.01*(4*224) if policy=='bounded' else .01*128)
  r=dict(scenario=sc,seed=seed,tick=t,policy=policy,risk=risk,true_errors=x,
   sensor_errors=p['measured'],correction_upper_errors=round(corrected,4),gain=round(g or 0,5),
   offset=round(b or 0,5),validation_residual=round(res or 0,5),signed_ok=int(signed_ok),
   calibration_ok=int(good),accepted=int(accepted),action='ACT' if act else 'HOLD',
   unsafe=int(act and risk>LIMIT),safe_act=int(act and risk<=LIMIT),
   safe_hold=int(not act and risk<=LIMIT),cost=round(cost,3))
  payload=json.dumps(r,sort_keys=True,separators=(',',':'))
  r['previous_hash']=h;h=hashlib.sha256((h+payload).encode()).hexdigest();r['hash']=h;out.append(r)
 return out
def chain(rows):
 h='0'*64
 for r in rows:
  b={k:v for k,v in r.items() if k not in ('previous_hash','hash')}
  hh=hashlib.sha256((h+json.dumps(b,sort_keys=True,separators=(',',':'))).encode()).hexdigest()
  if r['previous_hash']!=h or r['hash']!=hh:return False
  h=hh
 return True
def save(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 per=[];checks=[];traces=[]
 for sc in SC:
  for seed in SEEDS:
   for policy in ('frozen_122','bounded'):
    a=run(seed,sc,policy);again=run(seed,sc,policy)
    cv=dict(replay=a==again,hash_chain=chain(a),one_action=len(a)==T and all(r['action'] in ('ACT','HOLD') for r in a),
     signed_packet=all(r['signed_ok'] for r in a),fail_closed=(policy!='bounded' or all(r['action']=='HOLD' for r in a if not r['calibration_ok'])),
     no_unsafe=(policy!='bounded' or not any(r['unsafe'] for r in a)),no_future=all(0<=r['tick']<T for r in a))
    checks.append(dict(scenario=sc,seed=seed,policy=policy,**{k:int(v) for k,v in cv.items()}))
    per.append(dict(scenario=sc,seed=seed,policy=policy,unsafe=sum(r['unsafe'] for r in a),
     safe_act=sum(r['safe_act'] for r in a),safe_hold=sum(r['safe_hold'] for r in a),
     accepted=sum(r['accepted'] for r in a),cost=round(sum(r['cost'] for r in a),2)))
    if seed==SEEDS.start:traces.extend(a)
 save('checks.csv',checks);save('seed_results.csv',per);save('trace_samples.csv',traces)
 totals=[]
 for sc in (*SC,'ALL'):
  for policy in ('frozen_122','bounded'):
   a=[r for r in per if r['policy']==policy and (sc=='ALL' or r['scenario']==sc)]
   totals.append(dict(scenario=sc,policy=policy,cases=len(a),unsafe=sum(r['unsafe'] for r in a),
    safe_act=sum(r['safe_act'] for r in a),safe_hold=sum(r['safe_hold'] for r in a),
    accepted=sum(r['accepted'] for r in a),cost=round(sum(r['cost'] for r in a),2)))
 save('results.csv',totals);at={(r['scenario'],r['policy']):r for r in totals}
 gates=dict(zero_unsafe=at['ALL','bounded']['unsafe']==0,
   clean_nonregression=at['clean','bounded']['safe_act']==at['clean','frozen_122']['safe_act'],
   hazard_nonregression=at['hazard_shift','bounded']['safe_act']==at['hazard_shift','frozen_122']['safe_act'],
   moderate_recovery=sum(at[s,'bounded']['safe_act']>at[s,'frozen_122']['safe_act'] for s in ('negative_offset','positive_offset','low_gain','high_gain','drift'))>=3,
   rejects_nonlinearity=at['nonlinear','bounded']['accepted']==0,
   rejects_saturation=at['hard_saturation','bounded']['accepted']==0,
   deterministic=all(all(v==1 for k,v in r.items() if k not in ('scenario','seed','policy')) for r in checks))
 manifest=dict(bound='AETHER-123B',phase='VI',status='PASS' if all(gates.values()) else 'FAIL',
  episodes_per_policy=len(SEEDS)*len(SC),ticks_per_policy=len(SEEDS)*len(SC)*T,checks=len(checks)*7,gates=gates,
  seeds=[SEEDS.start,SEEDS.stop-1],pilots=PROBES,correction_margin_count=3,identity_pass_through=True,
  limits=['synthetic only','opaque same-path calibration and trustworthy probe truth assumed',
  'affine gain/offset correction can fail under unmodeled nonlinear response at risk counts',
  'fourth probe validates affine fit, not an independent witness'])
 (D/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(manifest=manifest,results=totals),indent=2))
 if manifest['status']!='PASS':raise SystemExit(2)
if __name__=='__main__':main()
