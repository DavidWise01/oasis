#!/usr/bin/env python3
"""AETHER-103: reproducible Phase II closure; synthetic integration audit."""
from pathlib import Path
import csv,hashlib,importlib.util,json
import numpy as np
ROOT=Path(__file__).resolve().parent;PARENT=ROOT.parent
ACCEPTED=[('096b',12.5),('097',25),('098',37.5),('099b',50),('100b',62.5),('101',75),('102b',87.5)]
FAILED=['096','099','100','102']
SEEDS=range(103001,103013)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csvwrite(name,rows):
 with (ROOT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def load(p):
 spec=importlib.util.spec_from_file_location('aether103_monitor',p)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 archive=[];errors=[]
 for v,pct in ACCEPTED+[(x,None) for x in FAILED]:
  folder=PARENT/('aether'+v)
  for file in ('experiment.py','results.csv','manifest.json'):
   if not (folder/file).is_file():errors.append(v+'/'+file)
  data=json.loads((folder/'manifest.json').read_text())
  status=data.get('status',data.get('accepted','unspecified'))
  if pct is not None and not (status in ('ACCEPTED','PASS',True) or (v=='099b' and data.get('phase_percent')==50)):errors.append(v+' not marked accepted')
  archive.append(dict(bound='AETHER-'+v.upper(),classification='accepted' if pct else 'failed-retained',phase_pct=pct or '',manifest_status=str(status),experiment_sha256=digest(folder/'experiment.py'),results_sha256=digest(folder/'results.csv'),manifest_sha256=digest(folder/'manifest.json')))
 csvwrite('inventory.csv',archive)
 m=load(PARENT/'aether102b'/'experiment.py');checks=dict(replay=0,causal_future=0,hash_integrity=0,policy_admissibility=0,unrequested_sensor=0)
 cases=[];acts={'direct':0,'guarded':0,'hold':0};count=0
 def verify(rows):
  prev='0'*64;keys=('tick','errors','sampled','upper','stress','diagnostic','action','prev_hash')
  for r in rows:
   v={k:r[k] for k in keys}
   h=hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
   if r['prev_hash']!=prev or r['hash']!=h:return False
   prev=h
  return True
 for regime in m.REGIMES:
  for seed in SEEDS:
   first=m.simulate(seed,regime,'monitor',1.15)
   again=m.simulate(seed,regime,'monitor',1.15)
   replay=(first==again)
   integrity=verify(first)
   admissible=all(r['action']=='hold' or r['upper']<=m.frozen.LIMIT+1e-9 for r in first)
   observe=m.observe
   def alter_future(s,g):
    risk,n,audit,direct,guarded,eff,health=observe(s,g)
    audit=audit.copy();audit[48:]=np.random.default_rng(s+31337).integers(0,int(max(n)),size=len(audit)-48)
    health=health.copy();health[48:]+=50
    return risk,n,audit,direct,guarded,eff,health
   m.observe=alter_future
   try:after=m.simulate(seed,regime,'monitor',1.15)
   finally:m.observe=observe
   causal=([r['hash'] for r in first[:48]]==[r['hash'] for r in after[:48]])
   def alter_unrequested(s,g):
    risk,n,audit,direct,guarded,eff,health=observe(s,g)
    health=health.copy();hist=[]
    for t in range(len(audit)):
     hist=(hist+[(int(audit[t]),int(n[t]))])[-5:]
     b=m.frozen.ub(sum(x[0] for x in hist),sum(x[1] for x in hist))
     if m.frozen.choose(b,bool(audit[t]>=3))!='guarded':health[t]+=1000.
    return risk,n,audit,direct,guarded,eff,health
   m.observe=alter_unrequested
   try:hidden=m.simulate(seed,regime,'monitor',1.15)
   finally:m.observe=observe
   independent=([r['hash'] for r in first]==[r['hash'] for r in hidden])
   for k,ok in [('replay',replay),('causal_future',causal),('hash_integrity',integrity),('policy_admissibility',admissible),('unrequested_sensor',independent)]:checks[k]+=int(ok)
   count+=1
   for r in first:acts[r['action']]+=1
   cases.append(dict(seed=seed,regime=regime,replay=int(replay),causal_future=int(causal),hash_integrity=int(integrity),admissible=int(admissible),unrequested_sensor=int(independent),cost=round(sum(r['cost'] for r in first),2)))
 csvwrite('integration_cases.csv',cases)
 passed=(len(archive)==11 and not errors and all(v==count for v in checks.values()) and all(acts.values()))
 obj=dict(bound='AETHER-103',phase='II',status='PASS' if passed else 'FAIL',closure='CLOSED' if passed else 'OPEN',completed_turns=8 if passed else 7,total_turns=8,phase_pct=100 if passed else 87.5,retained_failed_variants=FAILED,accepted_variants=[v for v,_ in ACCEPTED],inventory_errors=errors,integrated=dict(cases=count,ticks=count*m.T,checks=checks,actions=acts,all_pass=all(v==count for v in checks.values())),scope='Synthetic integration and reproducibility; no general safety guarantee or live deployment certification',notes='No witness quorum or Byzantine architecture introduced. Future work starts a separate phase.')
 (ROOT/'manifest.json').write_text(json.dumps(obj,indent=2)+'\n')
 print(json.dumps(obj,indent=2))
 if not passed:raise SystemExit(1)
if __name__=='__main__':main()
