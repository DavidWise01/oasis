#!/usr/bin/env python3
"""AETHER-137 — synthetic physical-readiness gate. No hardware connected."""
import csv,hashlib,hmac,json
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent
K=b'AETHER137-fixture-only-not-physical-authority'; T=24; THRESH=.025
SC=('clean_fixture','expired_calibration','missing_traceability','wrong_device','broken_acquisition_path','excess_uncertainty','counter_replay','forged_physical_claim')
SEEDS=range(137001,137051)
def raw(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sign(p):return dict(p,mac=hmac.new(K,raw(p),hashlib.sha256).hexdigest())
def authentic(p):
 q={k:v for k,v in p.items() if k!='mac'}
 return hmac.compare_digest(p.get('mac',''),sign(q)['mac'])
def fixture(seed,sc,t):
 r=np.random.default_rng(seed+SC.index(sc)*104729+t*2309)
 hazard=sc!='clean_fixture' and 8<=t<18
 risk=.075 if hazard else .004
 p=dict(source='synthetic-fixture',device='INSTRUMENT-A',cal_device='INSTRUMENT-A',tick=t,
  counter=t,observed_at=t,route='MAIN',cal_route='MAIN',standard_id='STD-1',
  root_id='TRACEABLE-ROOT-ASSUMED',uncertainty=.0006,
  reference_risk=risk,risk_reported=round((.004 if hazard else risk)+float(r.uniform(-.00025,.00025)),9),
  expires=t+1,hardware_receipt=None,claimed_physical=False)
 if hazard:
  if sc=='expired_calibration':p['expires']=t-1
  elif sc=='missing_traceability':p['standard_id']=None
  elif sc=='wrong_device':p['cal_device']='INSTRUMENT-B'
  elif sc=='broken_acquisition_path':p['cal_route']='BYPASS'
  elif sc=='excess_uncertainty':p['uncertainty']=.05
  elif sc=='counter_replay':p['counter']=t-3
  elif sc=='forged_physical_claim':
   p['hardware_receipt']={'validator':'self-attested fixture'}
   p['claimed_physical']=True
 return risk,sign(p)
def fixture_ready(p,t):
 if not authentic(p) or p['source']!='synthetic-fixture':return False
 if p['tick']!=t or p['observed_at']!=t or p['counter']!=t:return False
 if p['device']!=p['cal_device'] or p['route']!=p['cal_route']:return False
 if not p['standard_id'] or not p['root_id'] or p['expires']<=t:return False
 if not 0<=p['uncertainty']<=.002:return False
 if p['hardware_receipt'] is not None or p['claimed_physical']:return False
 return True
def policy(p,t,which):
 if which=='naive_signed':return authentic(p) and p['risk_reported']<=THRESH
 ok=fixture_ready(p,t) and p['reference_risk']+p['uncertainty']<=THRESH
 if which=='dry_run':return ok
 # No authenticated physical evidence or external validator in this experiment.
 return False
def episode(seed,sc,which):
 rows=[];prev='0'*64
 for t in range(T):
  truth,p=fixture(seed,sc,t);act=policy(p,t,which)
  r=dict(scenario=sc,seed=seed,policy=which,tick=t,action='ACT' if act else 'HOLD',
   fixture_valid=int(fixture_ready(p,t)),physical_attested=0,
   unsafe=int(act and truth>THRESH),safe_act=int(act and truth<=THRESH),
   safe_hold=int(not act and truth<=THRESH))
  digest=hashlib.sha256(prev.encode()+raw(r)).hexdigest()
  r['prev_hash']=prev;r['hash']=digest;prev=digest;rows.append(r)
 return rows
def chain(rows):
 prev='0'*64
 for r in rows:
  a={k:v for k,v in r.items() if k not in ('prev_hash','hash')}
  h=hashlib.sha256(prev.encode()+raw(a)).hexdigest()
  if r['prev_hash']!=prev or r['hash']!=h:return False
  prev=h
 return True
def save(file,rows):
 with (D/file).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 seeds=[];checks=[];traces=[]
 for sc in SC:
  for seed in SEEDS:
   for pol in ('naive_signed','dry_run','physical'):
    a=episode(seed,sc,pol);b=episode(seed,sc,pol)
    flags=dict(replay=a==b,chain=chain(a),single=len(a)==T and all(r['action'] in ('ACT','HOLD') for r in a),
     ordered=all(r['tick']==t for t,r in enumerate(a)),
     physical_hold=pol!='physical' or all(r['action']=='HOLD' for r in a),
     invalid_hold=pol!='dry_run' or all(r['action']=='HOLD' for r in a if not r['fixture_valid']),
     no_real_unsafe=pol!='physical' or all(r['unsafe']==0 for r in a))
    checks.append(dict(scenario=sc,seed=seed,policy=pol,**{k:int(v) for k,v in flags.items()}))
    seeds.append(dict(scenario=sc,seed=seed,policy=pol,unsafe=sum(r['unsafe'] for r in a),
     safe_act=sum(r['safe_act'] for r in a),safe_hold=sum(r['safe_hold'] for r in a)))
    if seed==SEEDS.start:traces+=a
 save('checks.csv',checks);save('seed_results.csv',seeds);save('trace_samples.csv',traces)
 total=[]
 for sc in (*SC,'ALL'):
  for pol in ('naive_signed','dry_run','physical'):
   z=[r for r in seeds if r['policy']==pol and (sc=='ALL' or r['scenario']==sc)]
   total.append(dict(scenario=sc,policy=pol,cases=len(z),unsafe=sum(r['unsafe'] for r in z),
    safe_act=sum(r['safe_act'] for r in z),safe_hold=sum(r['safe_hold'] for r in z)))
 save('results.csv',total)
 x={(r['scenario'],r['policy']):r for r in total}
 gates=dict(no_physical_ACT=x['ALL','physical']['safe_act']==0 and x['ALL','physical']['unsafe']==0,
  comparator_failure=x['ALL','naive_signed']['unsafe']>0,
  clean_dry_run=x['clean_fixture','dry_run']['safe_act']==len(SEEDS)*T,
  no_dry_run_unsafe=x['ALL','dry_run']['unsafe']==0,
  all_checks=all(all(v==1 for k,v in r.items() if k not in ('scenario','seed','policy')) for r in checks))
 m=dict(bound='AETHER-137',phase='VIII',status='PASS' if all(gates.values()) else 'FAIL',
  episodes_per_policy=400,decisions_per_policy=9600,checks=len(checks)*7,gates=gates,
  physical_validation='NOT PERFORMED',
  limits=['Fixture HMAC is not a physical certificate','Real ACT remains HOLD',
   'No actual sensor or reference standard was tested'])
 (D/'checkout-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 print(json.dumps(dict(manifest=m,results=total),indent=2))
 if m['status']!='PASS':raise SystemExit(2)
if __name__=='__main__':main()
