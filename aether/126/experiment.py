#!/usr/bin/env python3
"""AETHER-126: sequential calibration-resource scheduler, synthetic deterministic test.
Assumes truthful same-path probes and bound on drift between full audits.
"""
import csv,hashlib,hmac,json
from pathlib import Path
import numpy as np
from scipy.stats import beta
D=Path(__file__).resolve().parent
SEEDS=range(126001,126061); T=32; N=560; LIMIT=.025
SCENARIOS=('stable','slow_drift','noise_burst','instrument_swap','hazard_step','broken_calibration','missing_certificate')
PROBES=(32.,96.,160.,224.); KEY=b'aether126-synthetic'

def auth(body):return hmac.new(KEY,json.dumps(body,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest()
def sign(body):return dict(body,mac=auth(body))
def verify(p):return hmac.compare_digest(p.get('mac',''),auth({k:v for k,v in p.items() if k!='mac'}))
def upper(e):return 1. if e>=N else float(beta.ppf(.95,int(e)+1,N-int(e)))
def environment(seed,scenario):
 rng=np.random.default_rng(seed+SCENARIOS.index(scenario)*100019)
 records=[]
 for t in range(T):
  generation=2 if scenario=='instrument_swap' and t>=15 else 1
  g=1.;b=0.;noise=0.
  if scenario=='slow_drift':g=1.-.003*t
  if scenario=='noise_burst' and 12<=t<22:noise=3.
  if scenario=='instrument_swap' and t>=15:g=1.09;b=3.
  if scenario=='broken_calibration' and 13<=t<21:g=.45
  if scenario=='missing_certificate' and 10<=t<22:noise=0.
  hazard=(scenario=='hazard_step' and 14<=t<23) or (scenario in ('slow_drift','noise_burst','instrument_swap','broken_calibration','missing_certificate') and 13<=t<20)
  risk=.085 if hazard else .003
  e=int(rng.binomial(N,risk))
  m=g*e+b+(float(rng.uniform(-noise,noise)) if noise else 0.)
  vals=[g*x+b+(float(rng.uniform(-noise,noise)) if noise else 0.) for x in PROBES]
  p=sign(dict(source='risk',tick=t,counter=t,generation=generation,identity='B' if generation==2 else 'A',
     noise_bound=noise if scenario!='missing_certificate' or not (10<=t<22) else None,
     count=round(m,6),probes=[round(v,6) for v in vals],independent=True))
  records.append((risk,p))
 return records

def certificate(p,t,last_full):
 if not verify(p) or p['tick']!=t or p['counter']!=t or p['independent'] is not True:return False
 if p['noise_bound'] is None:return False
 if last_full is not None and p['generation']!=last_full['generation']:return False
 return True

def full_fit(p):
 eps=p['noise_bound'];ys=p['probes']
 if eps is None or len(ys)!=4:return None
 gl=.75;gh=1.25
 for i in range(4):
  for j in range(i+1,4):
   dy=ys[j]-ys[i];dx=PROBES[j]-PROBES[i]
   gl=max(gl,(dy-2*eps)/dx);gh=min(gh,(dy+2*eps)/dx)
 if gl<=0 or gl>gh:return None
 bl=max(-20.,max(ys[i]-eps-gh*PROBES[i] for i in range(4)))
 bh=min(20.,min(ys[i]+eps-gl*PROBES[i] for i in range(4)))
 if bl>bh or any(y<=0 or y>=N for y in ys):return None
 return dict(gl=gl,gh=gh,bl=bl,bh=bh,generation=p['generation'],tick=p['tick'],identity=p['identity'])

def two_probe_ok(p,anchor):
 if anchor is None or p['generation']!=anchor['generation'] or p['identity']!=anchor['identity']:return False
 if p['tick']-anchor['tick']>3:return False
 eps=p['noise_bound']
 if eps is None or eps>1:return False
 for i in (0,2):
  x=PROBES[i];y=p['probes'][i]
  lo=anchor['gl']*x+anchor['bl']-1.0-eps
  hi=anchor['gh']*x+anchor['bh']+1.0+eps
  if not lo<=y<=hi:return False
 return True

def decide(p,t,policy,anchor):
 trusted=(verify(p) and p['tick']==t and p['counter']==t and p['independent'] is True and
          p['source']=='risk' and p['noise_bound'] is not None)
 if not trusted:return 'HOLD',0,anchor,'invalid'
 need_full=(policy=='fixed' or anchor is None or t-anchor['tick']>=4 or
            p['generation']!=anchor['generation'] or p['identity']!=anchor['identity'] or
            p['noise_bound']>1)
 if not need_full and not two_probe_ok(p,anchor):need_full=True
 purchased=4 if need_full else 2
 if need_full:
  fitted=full_fit(p)
  if fitted is None:return 'HOLD',purchased,None,'failed_full'
  anchor=fitted
  margin=0. if abs(fitted['gl']-1)<1e-7 and abs(fitted['gh']-1)<1e-7 and abs(fitted['bl'])<1e-7 and abs(fitted['bh'])<1e-7 else 1.
 else:
  margin=1.
 error=max(0.,min(N,(p['count']+p['noise_bound']-anchor['bl'])/anchor['gl']+margin))
 action='ACT' if upper(int(np.ceil(error)))<=LIMIT else 'HOLD'
 return action,purchased,anchor,'full' if need_full else 'monitor'

def run(seed,scenario,policy):
 packets=environment(seed,scenario);rows=[];anchor=None;prev='0'*64
 for t,(risk,p) in enumerate(packets):
  action,n,anchor,reason=decide(p,t,policy,anchor)
  act=action=='ACT'
  row=dict(seed=seed,scenario=scenario,policy=policy,tick=t,action=action,
     unsafe=int(act and risk>LIMIT),safe_act=int(act and risk<=LIMIT),safe_hold=int(not act and risk<=LIMIT),
     probes=n,reason=reason,generation=p['generation'],noise=p['noise_bound'],
     cost=round((10*N*risk if act else .05*N)+n*2.,3))
  raw=json.dumps(row,sort_keys=True,separators=(',',':'))
  row['prev_hash']=prev;prev=hashlib.sha256((prev+raw).encode()).hexdigest();row['hash']=prev
  rows.append(row)
 return rows

def chain(rows):
 prev='0'*64
 for r in rows:
  d={k:v for k,v in r.items() if k not in ('prev_hash','hash')}
  h=hashlib.sha256((prev+json.dumps(d,sort_keys=True,separators=(',',':'))).encode()).hexdigest()
  if r['prev_hash']!=prev or r['hash']!=h:return False
  prev=h
 return True

def save(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
 summary=[];checks=[];traces=[]
 for sc in SCENARIOS:
  for seed in SEEDS:
   for policy in ('fixed','adaptive'):
    a=run(seed,sc,policy);b=run(seed,sc,policy)
    cond=dict(replay=a==b,hash_chain=chain(a),unique=len(a)==T and all(r['tick']==i for i,r in enumerate(a)),
     no_unauthorized=all(r['action']=='HOLD' for r in a if r['reason'] in ('invalid','failed_full')),
     no_unsafe=(policy!='adaptive' or all(r['unsafe']==0 for r in a)),
     budget=all(r['probes'] in (0,2,4) for r in a),
     no_inherited_calibration=all(r['reason']!='monitor' for r in a if r['tick']==15 and sc=='instrument_swap'))
    checks.append(dict(scenario=sc,seed=seed,policy=policy,**{k:int(v) for k,v in cond.items()}))
    summary.append(dict(scenario=sc,seed=seed,policy=policy,unsafe=sum(r['unsafe'] for r in a),
      safe_act=sum(r['safe_act'] for r in a),safe_hold=sum(r['safe_hold'] for r in a),
      probes=sum(r['probes'] for r in a),cost=round(sum(r['cost'] for r in a),2)))
    if seed==SEEDS.start:traces.extend(a)
 save('checks.csv',checks);save('seed_results.csv',summary);save('trace_samples.csv',traces)
 total=[]
 for sc in (*SCENARIOS,'ALL'):
  for policy in ('fixed','adaptive'):
   z=[r for r in summary if r['policy']==policy and (r['scenario']==sc or sc=='ALL')]
   total.append(dict(scenario=sc,policy=policy,cases=len(z),unsafe=sum(r['unsafe'] for r in z),
     safe_act=sum(r['safe_act'] for r in z),safe_hold=sum(r['safe_hold'] for r in z),
     probes=sum(r['probes'] for r in z),cost=round(sum(r['cost'] for r in z),2)))
 save('results.csv',total);d={(r['scenario'],r['policy']):r for r in total}
 gates=dict(no_added_unsafe=d['ALL','adaptive']['unsafe']<=d['ALL','fixed']['unsafe'],
  zero_unsafe=d['ALL','adaptive']['unsafe']==0,
  cost_reduction=d['ALL','adaptive']['cost']<d['ALL','fixed']['cost'],
  probe_reduction=d['ALL','adaptive']['probes']<d['ALL','fixed']['probes'],
  clean_availability=d['stable','adaptive']['safe_act']>=d['stable','fixed']['safe_act'],
  checks=all(all(v==1 for k,v in c.items() if k not in ('scenario','seed','policy')) for c in checks))
 m=dict(bound='AETHER-126',phase='VI',status='PASS' if all(gates.values()) else 'FAIL',
   paired_episodes=len(SEEDS)*len(SCENARIOS),ticks_per_policy=len(SEEDS)*len(SCENARIOS)*T,
   checks=len(checks)*7,gates=gates,assumptions=['trusted signer and current protected counter',
   'sensors behave affine between full audits, bounded monitor drift; no adversarial selective nonlinear steps',
   'truthful noise bound and same-path calibrated probes',
   'each decision 95% binomial bound not a familywise guarantee'])
 (D/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 print(json.dumps(dict(manifest=m,results=total),indent=2))
 if m['status']!='PASS':raise SystemExit(2)
if __name__=='__main__':main()
