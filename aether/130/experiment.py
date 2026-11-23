#!/usr/bin/env python3
"""AETHER-130: synthetic calibration provenance and uncertainty ancestry.
One controller; no physical instrument. Ancestry signatures are DEMO secrets,
not evidence of independent physical truth.
"""
import csv,hashlib,hmac,json
from pathlib import Path
import numpy as np
from scipy.stats import beta
D=Path(__file__).resolve().parent
N=560;T=28;CAP=.025;SEEDS=range(130001,130041)
SC=('clean','broken_parent','shared_root','expired_calibration','wrong_device','unknown_uncertainty','tampered_certificate','cyclic_parent','valid_rotation','missing_calibration')
KEYS={x:('synthetic-130-'+x).encode() for x in ('risk','ref','root-A','root-B','lab','sensor')}
def encode(b):return json.dumps(b,sort_keys=True,separators=(',',':')).encode()
def sign(b,issuer):return dict(b,signature=hmac.new(KEYS[issuer],encode(b),hashlib.sha256).hexdigest())
def valid(b,issuer):
 if not isinstance(b,dict):return False
 v={k:x for k,x in b.items() if k!='signature'}
 return hmac.compare_digest(str(b.get('signature','')),hmac.new(KEYS[issuer],encode(v),hashlib.sha256).hexdigest())
def ub(x):return 1. if x>=N else float(beta.ppf(.95,int(x)+1,N-int(x)))
def truth(sc,t):return .085 if 8<=t<18 and sc!='clean' else .003
def packet(seed,sc,t):
 rng=np.random.default_rng(seed+100003*SC.index(sc)+t*7919)
 q=truth(sc,t);errors=int(rng.binomial(N,q));faulty=(8<=t<18 and sc not in ('clean','valid_rotation'))
 # Untrustworthy instrument with a still-valid risk and reference signature.
 measured=0 if faulty else errors
 rp=sign(dict(kind='sensor_risk',device='S1',tick=t,counter=t,n=N,errors=measured,generation=1),'risk')
 ref=sign(dict(kind='reference_risk',device='S1',tick=t,counter=t,
  declared_upper=min(1.,(.004 if faulty else q+.002)),reference_serial='REF-1',generation=1),'ref')
 root=sign(dict(kind='root',serial='ROOT-B',issuer='root-B',independent_from='ROOT-A',valid_from=0,valid_until=T+1),'root-B')
 lab=sign(dict(kind='lab_certificate',serial='LAB-1',parent='ROOT-B',issuer='lab',valid_from=0,valid_until=T+1,
  reference_serial='REF-1',device='S1',systematic_uncertainty=.001),'lab')
 cert=sign(dict(kind='instrument_certificate',serial='CAL-1',parent='LAB-1',issuer='sensor',
  valid_from=0,valid_until=T+1,reference_serial='REF-1',device='S1',
  random_uncertainty=.001,systematic_uncertainty=.001),'sensor')
 if sc=='valid_rotation' and t>=14:
  lab=sign(dict(lab,serial='LAB-2',valid_from=14,parent='ROOT-B',issuer='lab'),'lab')
  cert=sign(dict(cert,serial='CAL-2',parent='LAB-2',valid_from=14),'sensor')
 if faulty:
  if sc=='broken_parent':cert=sign(dict({k:v for k,v in cert.items() if k!='signature'},parent='MISSING-LAB'),'sensor')
  if sc=='shared_root':root=sign(dict({k:v for k,v in root.items() if k!='signature'},serial='ROOT-A',independent_from='ROOT-A'),'root-B')
  if sc=='expired_calibration':cert=sign(dict({k:v for k,v in cert.items() if k!='signature'},valid_until=8),'sensor')
  if sc=='wrong_device':lab=sign(dict({k:v for k,v in lab.items() if k!='signature'},device='S2'),'lab')
  if sc=='unknown_uncertainty':cert=sign(dict({k:v for k,v in cert.items() if k!='signature'},random_uncertainty=None),'sensor')
  if sc=='tampered_certificate':cert['device']='S2'
  if sc=='cyclic_parent':lab=sign(dict({k:v for k,v in lab.items() if k!='signature'},parent='CAL-1'),'lab')
  if sc=='missing_calibration':cert=None
 return q,rp,ref,(root,lab,cert)
def baseline(t,rp,ref):
 return (valid(rp,'risk') and valid(ref,'ref') and rp.get('tick')==t and rp.get('counter')==t and
  ref.get('tick')==t and ref.get('counter')==t and rp.get('device')==ref.get('device') and
  rp.get('n')==N and 0<=ref.get('declared_upper',2.)<=CAP and ub(rp.get('errors',N))<=CAP)
def lineage(t,rp,ref,chain):
 root,lab,cal=chain
 if not all((valid(root,'root-B'),valid(lab,'lab'),valid(cal,'sensor'))):return False,'certificate_signature'
 if root['serial']!='ROOT-B' or root.get('independent_from')!='ROOT-A':return False,'shared_root'
 if lab['parent']!=root['serial'] or cal['parent']!=lab['serial'] or len({root['serial'],lab['serial'],cal['serial']})!=3:return False,'ancestry'
 if lab['reference_serial']!=ref['reference_serial'] or cal['reference_serial']!=ref['reference_serial']:return False,'reference_binding'
 if not (lab['device']==cal['device']==ref['device']==rp['device']):return False,'device_binding'
 if not all(c['valid_from']<=t<c['valid_until'] for c in chain):return False,'calibration_lease'
 vals=(lab.get('systematic_uncertainty'),cal.get('systematic_uncertainty'),cal.get('random_uncertainty'))
 if any(not isinstance(v,(int,float)) or isinstance(v,bool) or not np.isfinite(v) or v<0 for v in vals):return False,'uncertainty_missing'
 if sum(vals)>.006:return False,'uncertainty_budget'
 if not baseline(t,rp,ref):return False,'risk_bound'
 # Since declared_upper already includes base reference error, require budget headroom
 if ref['declared_upper']+sum(vals)>CAP:return False,'combined_uncertainty'
 return True,'qualified'
def episode(seed,sc,policy):
 rows=[];prior='0'*64
 for t in range(T):
  q,rp,ref,chain=packet(seed,sc,t)
  b=baseline(t,rp,ref);qualified,reason=lineage(t,rp,ref,chain)
  act=b if policy=='signed_only' else qualified
  r=dict(seed=seed,scenario=sc,tick=t,policy=policy,truth_risk=q,act=int(act),unsafe=int(act and q>CAP),
   safe_act=int(act and q<=CAP),safe_hold=int(not act and q<=CAP),qualified=int(qualified),
   reason=reason if policy=='lineage' else ('signed' if b else 'risk_bound'),
   cost=round((10*N*q if act else .05*N)+(6. if policy=='lineage' else 0.),3))
  raw=encode(r);r['prev_hash']=prior;prior=hashlib.sha256(prior.encode()+raw).hexdigest();r['hash']=prior
  rows.append(r)
 return rows
def replay_chain(rows):
 prev='0'*64
 for r in rows:
  obj={k:v for k,v in r.items() if k not in ('hash','prev_hash')};digest=hashlib.sha256(prev.encode()+encode(obj)).hexdigest()
  if r['prev_hash']!=prev or r['hash']!=digest:return False
  prev=digest
 return True
def csv_write(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 cases=[];checks=[];traces=[]
 for sc in SC:
  for seed in SEEDS:
   for p in ('signed_only','lineage'):
    a=episode(seed,sc,p);b=episode(seed,sc,p)
    gates=dict(replay=a==b,hash_chain=replay_chain(a),one_action=len(a)==T and all(r['act'] in (0,1) for r in a),
      gate_binding=p!='lineage' or all(not r['act'] or r['qualified'] for r in a),
      zero_unsafe=p!='lineage' or all(not r['unsafe'] for r in a),
      proper_ticks=all(r['tick']==i for i,r in enumerate(a)),
      no_false_recovery=p!='lineage' or all(not r['act'] for r in a if r['reason']!='qualified'))
    checks.append(dict(seed=seed,scenario=sc,policy=p,**{k:int(v) for k,v in gates.items()}))
    cases.append(dict(scenario=sc,seed=seed,policy=p,unsafe=sum(r['unsafe'] for r in a),
     safe_act=sum(r['safe_act'] for r in a),safe_hold=sum(r['safe_hold'] for r in a),cost=round(sum(r['cost'] for r in a),2)))
    if seed==SEEDS.start:traces.extend(a)
 csv_write('checks.csv',checks);csv_write('seed_results.csv',cases);csv_write('trace_samples.csv',traces)
 totals=[]
 for sc in (*SC,'ALL'):
  for policy in ('signed_only','lineage'):
   z=[r for r in cases if r['policy']==policy and (sc=='ALL' or sc==r['scenario'])]
   totals.append(dict(scenario=sc,policy=policy,cases=len(z),unsafe=sum(x['unsafe'] for x in z),
    safe_act=sum(x['safe_act'] for x in z),safe_hold=sum(x['safe_hold'] for x in z),
    cost=round(sum(x['cost'] for x in z),2)))
 csv_write('results.csv',totals)
 look={(r['scenario'],r['policy']):r for r in totals}
 gates=dict(unsafe_zero=look['ALL','lineage']['unsafe']==0,
  baseline_counterexample=look['ALL','signed_only']['unsafe']>0,
  clean_nonregression=look['clean','lineage']['safe_act']==look['clean','signed_only']['safe_act'],
  rotation_nonregression=look['valid_rotation','lineage']['safe_act']==look['valid_rotation','signed_only']['safe_act'],
  replay_checks=all(all(v==1 for k,v in r.items() if k not in ('seed','scenario','policy')) for r in checks))
 manifest=dict(bound='AETHER-130',phase='VII',status='PASS' if all(gates.values()) else 'FAIL',
  episodes_per_policy=len(SEEDS)*len(SC),decision_ticks_per_policy=T*len(SEEDS)*len(SC),
  checks=7*len(checks),seeds=[SEEDS.start,SEEDS.stop-1],gates=gates,
  caveats=['No physical reference instrument was connected','Root-B independence from Root-A is a signed declaration, not independently established',
  'HMAC demo signatures and simulated reference risk','Additive systematic uncertainty may understate correlated real-world sources'])
 (D/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(manifest=manifest,results=totals),indent=2))
 if manifest['status']!='PASS':raise SystemExit(2)
if __name__=='__main__':main()
