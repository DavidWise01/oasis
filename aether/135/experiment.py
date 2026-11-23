#!/usr/bin/env python3
"""AETHER-135 failed stress: frozen AETHER-134 against false physical assumptions.
Synthetic experiment. Requires numpy and ../134/experiment.py; fails zero-unsafe.
"""
import csv,hashlib,importlib.util,json
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent
P=D.parent/'134'/'experiment.py'
sp=importlib.util.spec_from_file_location('frozen134',P)
base=importlib.util.module_from_spec(sp);sp.loader.exec_module(base)
SHA=hashlib.sha256(P.read_bytes()).hexdigest()
SC=('clean','hidden_jump','false_drift_rate','false_calibration_bias','forged_ingress_receipt','joint_spoof','honest_anomaly','valid_replacement')
SEEDS=range(135001,135051)
def environment(seed,sc):
 rng=np.random.default_rng(seed+SC.index(sc)*100019);out=[]
 for t in range(base.TICKS):
  dangerous=12<=t<20 and sc not in ('clean','valid_replacement')
  truth=.075 if dangerous else .005
  drift=.00005
  bad=sc in ('hidden_jump','false_drift_rate','false_calibration_bias','forged_ingress_receipt','joint_spoof','honest_anomaly') and t>=12
  physical_bias=drift*t+(.06 if bad else 0)
  cert_rate=.000005 if sc in ('false_drift_rate','joint_spoof') else drift
  cert_bias=drift*t if sc in ('false_calibration_bias','joint_spoof') else physical_bias
  observed=max(0.,truth-physical_bias+float(rng.uniform(-.00004,.00004)))
  pkt=base.sign(dict(tick=t,counter=t,path='ingress-A',generation=2 if sc=='valid_replacement' and t>=16 else 1,
   risk_observed=round(observed,10),independent_anomaly=sc=='honest_anomaly' and dangerous,
   reference_valid=True,noise_envelope=.00004,certified_drift_rate=cert_rate,
   true_reference_bias=round(cert_bias,10)))
  out.append((truth,pkt))
 return out
def write(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 base.environment=environment
 checks=[];per=[];traces=[]
 for sc in SC:
  for seed in SEEDS:
   for pol in ('fixed','adaptive'):
    a=base.run(seed,sc,pol);b=base.run(seed,sc,pol)
    gates=dict(replay=a==b,chain=base.chain_ok(a),one_action=len(a)==base.TICKS,
     order=all(r['tick']==i for i,r in enumerate(a)),
     fail_closed=all(r['action']=='HOLD' for r in a if not r['trusted']),
     packets=all(base.verified(p) for _,p in environment(seed,sc)),
     frozen=hashlib.sha256(P.read_bytes()).hexdigest()==SHA)
    checks.append(dict(scenario=sc,seed=seed,policy=pol,**{k:int(v) for k,v in gates.items()}))
    per.append(dict(scenario=sc,seed=seed,policy=pol,unsafe=sum(r['unsafe_act'] for r in a),
     safe_act=sum(r['safe_act'] for r in a),safe_hold=sum(r['safe_hold'] for r in a),
     calibrations=sum(r['calibration'] for r in a)))
    if seed==SEEDS.start:traces.extend(a)
 write('checks.csv',checks);write('seed_results.csv',per);write('trace_samples.csv',traces)
 results=[]
 for sc in (*SC,'ALL'):
  for pol in ('fixed','adaptive'):
   z=[r for r in per if r['policy']==pol and (sc=='ALL' or r['scenario']==sc)]
   results.append(dict(scenario=sc,policy=pol,cases=len(z),unsafe=sum(r['unsafe'] for r in z),
     safe_act=sum(r['safe_act'] for r in z),safe_hold=sum(r['safe_hold'] for r in z),
     calibrations=sum(r['calibrations'] for r in z)))
 write('results.csv',results)
 gate=dict(zero_unsafe=not any(r['unsafe'] for r in results if r['scenario']=='ALL'),
  integrity=all(all(v==1 for k,v in r.items() if k not in ('scenario','seed','policy')) for r in checks),
  frozen=hashlib.sha256(P.read_bytes()).hexdigest()==SHA)
 m=dict(bound='AETHER-135',phase='VII',status='PASS' if all(gate.values()) else 'FAIL',
  cases_per_policy=400,decisions_per_policy=12800,checks=len(checks)*7,gates=gate,
  note='A valid digital signature cannot certify hidden physical correctness')
 (D/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 print(json.dumps(dict(manifest=m,results=results),indent=2))
if __name__=='__main__':main()
