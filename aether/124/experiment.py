#!/usr/bin/env python3
"""AETHER-124 failed independently reproducible bounded-noise calibration evaluation.

Synthetic assumptions: trusted signing, probe truth, affine sensor, bounded noise,
same acquisition path. No general proof about sensor deception.
"""
import csv,hashlib,hmac,json
from pathlib import Path
import numpy as np
from scipy.stats import beta
D=Path(__file__).resolve().parent;T=24;N=560;LIMIT=.025
PROBES=(32.,96.,160.,224.);KEY=b'AETHER-124-synthetic-only'
SC=('clean','noise_1','noise_3','noise_6','gain_shift','offset_shift','drifting_gain','hazard_transition','uncertified_noise')
SEEDS=range(124001,124051)
EPS={'clean':0.,'noise_1':1.,'noise_3':3.,'noise_6':6.,'gain_shift':2.,'offset_shift':2.,'drifting_gain':3.,'hazard_transition':3.,'uncertified_noise':6.}
def sign(b):
 return dict(b,mac=hmac.new(KEY,json.dumps(b,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest())
def authentic(p):
 b={k:v for k,v in p.items() if k!='mac'}
 return hmac.compare_digest(p.get('mac',''),sign(b)['mac'])
def upper(e):return 1. if e>=N else float(beta.ppf(.95,e+1,N-e))
def settings(s,t):
 if s=='gain_shift':return .89,-1.
 if s=='offset_shift':return 1.,9.
 if s=='drifting_gain':return 1-.004*t,-.08*t
 return 1.,0.
def packet(seed,s,t):
 rng=np.random.default_rng(seed+100003*SC.index(s)+t*7907)
 q=.077 if (7<=t<19 if s=='hazard_transition' else 9<=t<17) else .003
 k=int(rng.binomial(N,q));g,b=settings(s,t);eps=EPS[s]
 ys=np.array([g*x+b for x in PROBES],float)
 if eps:ys+=rng.uniform(-eps,eps,size=4)
 measured=g*k+b+(float(rng.uniform(-eps,eps)) if eps else 0.)
 p=dict(source='risk-audit',seq=t,counter=t,observed_t=t,valid_until=t+1,epoch=1,
  independent=True,n=N,measured=round(measured,10),probes=[round(float(y),10) for y in ys],
  noise_bound=eps if s!='uncertified_noise' else None,
  noise_certificate=(s!='uncertified_noise'),probe_commit=t)
 return q,k,sign(p)
def interval(p):
 eps=p['noise_bound'];ys=p['probes']
 if eps is None or eps<0 or len(ys)!=4 or any(not np.isfinite(y) for y in ys):return None
 gl=.75;gh=1.25
 for i in range(4):
  for j in range(i+1,4):
   dx=PROBES[j]-PROBES[i];dy=ys[j]-ys[i]
   gl=max(gl,(dy-2*eps)/dx);gh=min(gh,(dy+2*eps)/dx)
 if gl<=0 or gl>gh:return None
 bl=max(-20.,max(ys[i]-eps-gh*PROBES[i] for i in range(4)))
 bh=min(20.,min(ys[i]+eps-gl*PROBES[i] for i in range(4)))
 if bl>bh or any(y<=0 or y>=N for y in ys):return None
 return gl,gh,bl,bh
def decision(p,t,policy):
 signed=(authentic(p) and p.get('source')=='risk-audit' and p.get('seq')==t
  and p.get('counter')==t and p.get('observed_t')==t and p.get('valid_until')==t+1
  and p.get('epoch')==1 and p.get('independent') is True and p.get('n')==N
  and p.get('probe_commit')==t)
 if not signed:return False,'HOLD',N,None
 if policy=='point_fit':
  ys=p['probes'];g=(ys[2]-ys[0])/(PROBES[2]-PROBES[0]);b=ys[0]-g*PROBES[0]
  residual=max(abs(ys[i]-(g*PROBES[i]+b)) for i in (1,3))
  accepted=.75<=g<=1.25 and -20<=b<=20 and residual<=15
  count=max(0.,min(N,(p['measured']-b)/g)) if accepted else N
  return accepted,('ACT' if accepted and upper(int(np.floor(count)))<=LIMIT else 'HOLD'),count,None
 if p['noise_certificate'] is not True:return False,'HOLD',N,None
 iv=interval(p)
 if iv is None:return False,'HOLD',N,None
 gl,gh,bl,bh=iv
 # Real error count <= (reported + measurement noise limit - minimum offset)
 # / minimum gain under the complete compatible affine parameter rectangle.
 # Certification MUST use MINIMUM plausible count (KNOWN UNSAFE, preserved failure).
 count=max(0.,min(N,(p['measured']-p['noise_bound']-bh)/gh))
 return True,('ACT' if upper(int(np.ceil(count)))<=LIMIT else 'HOLD'),count,iv
def episode(seed,s,policy):
 rows=[];prev='0'*64
 for t in range(T):
  risk,k,p=packet(seed,s,t);accepted,action,count,iv=decision(p,t,policy)
  act=action=='ACT'
  cost=(10*N*risk if act else .05*N)+(.01*(4*224) if policy=='interval' else .01*128)
  r=dict(seed=seed,scenario=s,policy=policy,tick=t,risk=risk,true_count=k,
    observed=p['measured'],noise_bound=p['noise_bound'],accepted=int(accepted),
    conservative_count=round(count,5),action=action,unsafe=int(act and risk>LIMIT),
    safe_act=int(act and risk<=LIMIT),safe_hold=int(not act and risk<=LIMIT),
    cost=round(cost,3),gain_min=round(iv[0],5) if iv else '',
    gain_max=round(iv[1],5) if iv else '')
  raw=json.dumps(r,sort_keys=True,separators=(',',':'))
  r['prev_hash']=prev;prev=hashlib.sha256((prev+raw).encode()).hexdigest();r['hash']=prev
  rows.append(r)
 return rows
def chain(rows):
 prev='0'*64
 for r in rows:
  b={k:v for k,v in r.items() if k not in ('prev_hash','hash')}
  h=hashlib.sha256((prev+json.dumps(b,sort_keys=True,separators=(',',':'))).encode()).hexdigest()
  if r['prev_hash']!=prev or r['hash']!=h:return False
  prev=h
 return True
def write(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 per=[];checks=[];traces=[]
 for s in SC:
  for seed in SEEDS:
   for policy in ('point_fit','interval'):
    rows=episode(seed,s,policy);again=episode(seed,s,policy)
    chk=dict(replay=rows==again,hash_chain=chain(rows),
      one_decision=len(rows)==T and all(r['action'] in ('ACT','HOLD') for r in rows),
      fail_closed=(policy!='interval' or all(r['action']=='HOLD' for r in rows if not r['accepted'])),
      no_unsafe=(policy!='interval' or all(r['unsafe']==0 for r in rows)),
      counter_order=all(r['tick']==i for i,r in enumerate(rows)),
      no_unbounded_act=(policy!='interval' or s!='uncertified_noise' or all(r['action']=='HOLD' for r in rows)))
    checks.append(dict(seed=seed,scenario=s,policy=policy,**{k:int(v) for k,v in chk.items()}))
    per.append(dict(seed=seed,scenario=s,policy=policy,unsafe=sum(r['unsafe'] for r in rows),
      safe_act=sum(r['safe_act'] for r in rows),safe_hold=sum(r['safe_hold'] for r in rows),
      total_act=sum(r['action']=='ACT' for r in rows),cost=round(sum(r['cost'] for r in rows),2)))
    if seed==SEEDS.start:traces.extend(rows)
 write('checks.csv',checks);write('seed_results.csv',per);write('trace_samples.csv',traces)
 totals=[]
 for s in (*SC,'ALL'):
  for policy in ('point_fit','interval'):
   z=[r for r in per if r['policy']==policy and (s=='ALL' or r['scenario']==s)]
   totals.append(dict(scenario=s,policy=policy,cases=len(z),unsafe=sum(r['unsafe'] for r in z),
    safe_act=sum(r['safe_act'] for r in z),safe_hold=sum(r['safe_hold'] for r in z),
    total_act=sum(r['total_act'] for r in z),cost=round(sum(r['cost'] for r in z),2)))
 write('results.csv',totals);look={(r['scenario'],r['policy']):r for r in totals}
 gates=dict(no_unsafe=look['ALL','interval']['unsafe']==0,
  clean_nonregression=look['clean','interval']['safe_act']==look['clean','point_fit']['safe_act'],
  certified_noise_usable=look['noise_1','interval']['safe_act']>0,
  noise_uncertainty_monotonic=look['noise_1','interval']['safe_act']>=look['noise_3','interval']['safe_act']>=look['noise_6','interval']['safe_act'],
  uncertified_fail_closed=look['uncertified_noise','interval']['total_act']==0,
  checks=all(all(v==1 for k,v in c.items() if k not in ('seed','scenario','policy')) for c in checks))
 m=dict(bound='AETHER-124',phase='VI',status='PASS' if all(gates.values()) else 'FAIL',
  cases_per_policy=450,decisions_per_policy=10800,checks=len(checks)*7,gates=gates,
  seeds=[SEEDS.start,SEEDS.stop-1],noise_model='bounded uniform additive with truthful per-packet bound',
  limitations=['Trusted sensor, HMAC, bounded noise certificates, probes and counters assumed',
   'Affine model and bounded noise limits essential','Per-look 95% Clopper-Pearson does not establish familywise control across 24 looks',
   'Extra HOLDs significantly reduce availability and increase cost'])
 (D/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 print(json.dumps(dict(manifest=m,results=totals),indent=2))
 if m['status']!='PASS':raise SystemExit(2)
if __name__=='__main__':main()
