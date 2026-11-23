#!/usr/bin/env python3
"""AETHER-131 — covariance-aware reference gate; synthetic experiment.
Signed ancestry/covariance are model assumptions, not physical evidence.
Requires NumPy; run: python aether/131/experiment.py
"""
import csv,hashlib,hmac,json,math
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent
SC=('clean','shared_drift','common_root','high_covariance','unknown_covariance','stale_covariance','valid_rotation','split_root')
SEEDS=range(131001,131051);T=24;CAP=.025;KEY=b'AETHER131-synthetic-signer'
def encode(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sign(x):return dict(x,mac=hmac.new(KEY,encode(x),hashlib.sha256).hexdigest())
def verify(x):return hmac.compare_digest(str(x.get('mac','')),sign({k:v for k,v in x.items() if k!='mac'})['mac'])
def measurement(seed,sc,t):
 rng=np.random.default_rng(seed*3719+SC.index(sc)*900011+t)
 bad=8<=t<18 and sc not in ('clean','valid_rotation','split_root')
 risk=.030 if bad else .003
 obs=(.018 if bad else .004)+float(rng.uniform(-.00015,.00015))
 root='shared-A' if sc in ('shared_drift','common_root','high_covariance','unknown_covariance','stale_covariance') else 'separate'
 rho=None if sc=='unknown_covariance' else (.95 if sc=='high_covariance' else (1.0 if root=='shared-A' else 0.0))
 epoch=2 if sc=='valid_rotation' and t>=12 else 1
 cert=dict(device='REF-1',epoch=epoch,seq=t,valid_until=t+1,rho=rho,root=root,u_sensor=.004,u_reference=.004,
  provenance='shared-laboratory-standard' if root=='shared-A' else 'separate-calibration-sources')
 if sc=='stale_covariance' and bad:cert.update(seq=t-3,valid_until=t-2)
 return risk,sign(dict(device='REF-1',epoch=epoch,tick=t,counter=t,observed=obs)),sign(cert)
def gate(t,r,c,policy):
 fresh=verify(r) and verify(c) and r['tick']==t and r['counter']==t and r['device']==c['device'] and r['epoch']==c['epoch']
 if not fresh:return False,'identity_or_signature'
 a,b=c['u_sensor'],c['u_reference']
 if policy=='naive':
  return r['observed']+math.sqrt(a*a+b*b)<=CAP,'independent_assumption'
 rho=c['rho']
 if c['seq']!=t or c['valid_until']!=t+1:return False,'stale'
 if rho is None or not isinstance(rho,(float,int)) or not -1<=rho<=1:return False,'unknown'
 if c['root']=='shared-A' and rho<.95:return False,'ancestry_mismatch'
 if c['root']=='separate' and c['provenance']!='separate-calibration-sources':return False,'provenance_mismatch'
 v=a*a+b*b+2*rho*a*b
 if v<0:return False,'variance_invalid'
 return r['observed']+math.sqrt(v)<=CAP,'covariance_bound'
def episode(seed,sc,policy):
 rows=[];prev='0'*64
 for t in range(T):
  truth,r,c=measurement(seed,sc,t);act,why=gate(t,r,c,policy)
  row=dict(seed=seed,scenario=sc,policy=policy,tick=t,truth=truth,observed=round(r['observed'],9),
   action='ACT' if act else 'HOLD',unsafe=int(act and truth>CAP),safe_act=int(act and truth<=CAP),
   safe_hold=int(not act and truth<=CAP),reason=why,epoch=r['epoch'],covariance_root=c['root'],rho=c['rho'])
  h=hashlib.sha256(prev.encode()+encode(row)).hexdigest()
  row['prev_hash']=prev;row['hash']=h;prev=h;rows.append(row)
 return rows
def chain(rows):
 prev='0'*64
 for row in rows:
  fields={k:v for k,v in row.items() if k not in ('prev_hash','hash')}
  digest=hashlib.sha256(prev.encode()+encode(fields)).hexdigest()
  if row['prev_hash']!=prev or row['hash']!=digest:return False
  prev=digest
 return True
def save(path,rows):
 with (D/path).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 per=[];checks=[];trace=[]
 for sc in SC:
  for seed in SEEDS:
   for policy in ('naive','covariance'):
    a=episode(seed,sc,policy);b=episode(seed,sc,policy)
    rules=dict(replay=a==b,hash_chain=chain(a),one_action=len(a)==T and all(r['action'] in ('ACT','HOLD') for r in a),
      time_order=all(r['tick']==i for i,r in enumerate(a)),
      fail_closed=(policy!='covariance' or all(r['action']=='HOLD' for r in a if r['reason'] in ('unknown','stale','ancestry_mismatch'))),
      no_unsafe=policy!='covariance' or all(r['unsafe']==0 for r in a),
      signatures=all(verify(measurement(seed,sc,t)[1]) and verify(measurement(seed,sc,t)[2]) for t in range(T)))
    checks.append(dict(scenario=sc,seed=seed,policy=policy,**{k:int(v) for k,v in rules.items()}))
    per.append(dict(scenario=sc,seed=seed,policy=policy,unsafe=sum(r['unsafe'] for r in a),
     safe_act=sum(r['safe_act'] for r in a),safe_hold=sum(r['safe_hold'] for r in a),act=sum(r['action']=='ACT' for r in a)))
    if seed==SEEDS.start:trace.extend(a)
 save('checks.csv',checks);save('seed_results.csv',per);save('trace_samples.csv',trace)
 total=[]
 for sc in (*SC,'ALL'):
  for policy in ('naive','covariance'):
   z=[r for r in per if r['policy']==policy and (r['scenario']==sc or sc=='ALL')]
   total.append(dict(scenario=sc,policy=policy,cases=len(z),unsafe=sum(r['unsafe'] for r in z),
     safe_act=sum(r['safe_act'] for r in z),safe_hold=sum(r['safe_hold'] for r in z),act=sum(r['act'] for r in z)))
 save('results.csv',total);lookup={(r['scenario'],r['policy']):r for r in total}
 gates=dict(zero_unsafe=lookup['ALL','covariance']['unsafe']==0,counterexample=lookup['ALL','naive']['unsafe']>0,
  clean_nonregression=lookup['clean','covariance']['safe_act']==lookup['clean','naive']['safe_act'],
  rotation_nonregression=lookup['valid_rotation','covariance']['safe_act']==lookup['valid_rotation','naive']['safe_act'],
  missing_fails_closed=lookup['unknown_covariance','covariance']['unsafe']==0,
  checks=all(all(v==1 for k,v in c.items() if k not in ('scenario','seed','policy')) for c in checks))
 manifest=dict(bound='AETHER-131',phase='VII',status='PASS' if all(gates.values()) else 'FAIL',
   paired_episodes=len(SEEDS)*len(SC),ticks_per_policy=T*len(SEEDS)*len(SC),
   checks=len(checks)*7,gates=gates,assumptions=['Synthetic declared covariance and ancestry, not physically verified',
   'One standard deviation modeled as bound; not calibrated confidence guarantee',
   'Common-mode sensor errors may still be wrong despite signed ancestry'])
 (D/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(manifest=manifest,results=total),indent=2))
 if manifest['status']!='PASS':raise SystemExit(2)
if __name__=='__main__':main()
