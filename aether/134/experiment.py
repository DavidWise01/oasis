#!/usr/bin/env python3
"""AETHER-134 — synthetic reference drift recalibration economics.
Repository checkout reproduction. No physical device connected.
"""
import csv,hashlib,hmac,json
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent
SC=('clean','slow_drift','high_drift','abrupt_shift','noise_burst','expired_reference','route_substitution','new_instrument')
SEEDS=range(134001,134051);T=32;K=b'AETHER-134-SYNTHETIC-ONLY';LIMIT=.025
def raw(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def signed(x):return dict(x,mac=hmac.new(K,raw(x),hashlib.sha256).hexdigest())
def verify(x):return hmac.compare_digest(x['mac'],signed({k:v for k,v in x.items() if k!='mac'})['mac'])
def environment(seed,sc):
 rng=np.random.default_rng(seed+SC.index(sc)*100019);rows=[]
 for t in range(T):
  truth=.075 if 12<=t<20 and sc!='clean' else .005
  rate=.00005 if sc in ('clean','expired_reference','route_substitution','new_instrument') else (.0004 if sc in ('slow_drift','noise_burst') else .001)
  bias=rate*t+(.06 if sc=='abrupt_shift' and t>=12 else 0)
  noise=float(rng.uniform(-.00025,.00025)) if sc=='noise_burst' else 0.
  p=signed(dict(tick=t,counter=t,path=('ingress-B' if sc=='route_substitution' and 12<=t<21 else 'ingress-A'),
    generation=(2 if sc=='new_instrument' and t>=16 else 1),
    risk_observed=round(max(0,truth-bias+noise),10),
    independent_anomaly=(sc=='abrupt_shift' and 12<=t<21),
    reference_valid=(sc!='expired_reference' or t<12 or t>=21),
    noise_envelope=(.00025 if sc=='noise_burst' else 0.),
    certified_drift_rate=rate,true_reference_bias=round(bias,10)))
  rows.append((truth,p))
 return rows
def run(seed,sc,policy):
 rows=[];last=-1;offset=0.;generation=1;previous='0'*64
 for t,(truth,p) in enumerate(environment(seed,sc)):
  assert verify(p)
  valid=p['path']=='ingress-A' and p['tick']==t and p['counter']==t
  if p['generation']!=generation:last=-1
  generation=p['generation']
  period=1 if policy=='fixed' else (2 if p['certified_drift_rate']>=.0009 else 5)
  calibrate=last<0 or t-last>=period
  if calibrate and valid and p['reference_valid']:
   last=t;offset=p['true_reference_bias']
  age=t-last if last>=0 else None
  eligible=valid and p['reference_valid'] and not p['independent_anomaly'] and age is not None and age<period
  upper=p['risk_observed']+offset+p['certified_drift_rate']*age+p['noise_envelope'] if eligible else 1.
  act=eligible and upper<=LIMIT
  r=dict(scenario=sc,seed=seed,policy=policy,tick=t,generation=generation,
   action='ACT' if act else 'HOLD',safe_act=int(act and truth<=LIMIT),unsafe_act=int(act and truth>LIMIT),
   safe_hold=int(not act and truth<=LIMIT),calibration=int(calibrate and valid and p['reference_valid']),
   eligible=int(eligible),risk_upper=round(upper,8))
  h=hashlib.sha256((previous+raw(r).decode()).encode()).hexdigest()
  r['prev_hash']=previous;r['hash']=h;previous=h;rows.append(r)
 return rows
def chain(rows):
 prev='0'*64
 for r in rows:
  x={k:v for k,v in r.items() if k not in ('prev_hash','hash')}
  h=hashlib.sha256((prev+raw(x).decode()).encode()).hexdigest()
  if r['prev_hash']!=prev or r['hash']!=h:return False
  prev=h
 return True
def write(name,data):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
def main():
 checks=[];seeds=[];samples=[]
 for sc in SC:
  for seed in SEEDS:
   for pol in ('fixed','adaptive'):
    a=run(seed,sc,pol)
    gates=dict(replay=a==run(seed,sc,pol),chain=chain(a),single_action=len(a)==T and all(r['action'] in ('ACT','HOLD') for r in a),
      tick_order=all(r['tick']==t for t,r in enumerate(a)),fail_closed=all(r['action']=='HOLD' for r in a if not r['eligible']),
      zero_unsafe=all(not r['unsafe_act'] for r in a),budget=all(r['calibration'] in (0,1) for r in a))
    checks.append(dict(scenario=sc,seed=seed,policy=pol,**{k:int(v) for k,v in gates.items()}))
    seeds.append(dict(scenario=sc,seed=seed,policy=pol,unsafe=sum(r['unsafe_act'] for r in a),
      safe_act=sum(r['safe_act'] for r in a),safe_hold=sum(r['safe_hold'] for r in a),
      calibrations=sum(r['calibration'] for r in a)))
    if seed==SEEDS.start:samples.extend(a)
 write('checks.csv',checks);write('seed_results.csv',seeds);write('trace_samples.csv',samples)
 total=[]
 for sc in (*SC,'ALL'):
  for pol in ('fixed','adaptive'):
   z=[r for r in seeds if r['policy']==pol and (sc=='ALL' or r['scenario']==sc)]
   total.append(dict(scenario=sc,policy=pol,cases=len(z),unsafe=sum(r['unsafe'] for r in z),
    safe_act=sum(r['safe_act'] for r in z),safe_hold=sum(r['safe_hold'] for r in z),
    calibrations=sum(r['calibrations'] for r in z)))
 write('results.csv',total);v={(r['scenario'],r['policy']):r for r in total}
 gates=dict(zero_unsafe=v['ALL','adaptive']['unsafe']==0,no_extra_unsafe=v['ALL','adaptive']['unsafe']<=v['ALL','fixed']['unsafe'],
  fewer_calibrations=v['ALL','adaptive']['calibrations']<v['ALL','fixed']['calibrations'],
  clean_availability=v['clean','adaptive']['safe_act']==v['clean','fixed']['safe_act'],
  all_checks=all(all(n==1 for k,n in r.items() if k not in ('scenario','seed','policy')) for r in checks))
 m=dict(bound='AETHER-134',phase='VII',status='PASS' if all(gates.values()) else 'FAIL',episodes_per_policy=400,
  decisions_per_policy=12800,checks=5600,gates=gates,assumptions=[
  'Reference bias known at calibration only in synthetic model','Certified maximum drift rate trusted',
  'Independent same-tick anomaly alarm and path receipt assumed authentic',
  'Undetected abrupt physical faults may violate the conclusion'])
 (D/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 print(json.dumps(dict(manifest=m,results=total),indent=2))
 if m['status']!='PASS':raise SystemExit(2)
if __name__=='__main__':main()
