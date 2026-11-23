#!/usr/bin/env python3
"""AETHER-127: frozen AETHER-126 stress on unseen nonlinear sensor response.

Run from the repository with NumPy, SciPy and sibling aether/126/experiment.py.
A failing safety gate is intentional and preserved.
"""
import csv,hashlib,importlib.util,json
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent
SOURCE=D.parent/'126'/'experiment.py'
spec=importlib.util.spec_from_file_location('aether126_frozen',SOURCE)
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
HASH=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
SCENARIOS=('clean','fast_drift','abrupt_gain','abrupt_offset','monitor_blindspot',
           'nonlinear_midrange','intermittent_noise','replacement_spoof')
SEEDS=range(127001,127061)
T=base.T;N=base.N
def packet_stream(seed,scenario):
 rng=np.random.default_rng(seed+SCENARIOS.index(scenario)*100019)
 packets=[]
 for t in range(T):
  g,b,noise=1.,0.,0.
  if scenario=='fast_drift':g=1.-.018*t
  if scenario=='abrupt_gain' and t>=13:g=.34
  if scenario=='abrupt_offset' and t>=13:b=-36.
  if scenario=='intermittent_noise' and 12<=t<=25:noise=4.
  if scenario=='replacement_spoof' and t>=15:g=.45
  risk=.084 if (13<=t<=21 and scenario!='clean') else .003
  errors=int(rng.binomial(N,risk))
  def response(x):
   z=g*x+b
   # Malformed response in ordinary risk range, while calibration
   # probe values 32,96,160,224 are untouched.
   if scenario=='monitor_blindspot' and t>=13:
    z=x-45 if 35<=x<90 else x
   if scenario=='nonlinear_midrange' and t>=13:
    z=x-40 if 35<=x<80 else x
   return z
  m=response(errors)+(float(rng.uniform(-noise,noise)) if noise else 0.)
  vals=[response(x)+(float(rng.uniform(-noise,noise)) if noise else 0.)
        for x in base.PROBES]
  p=base.sign(dict(source='risk',tick=t,counter=t,generation=1,
    identity='A',noise_bound=noise,count=round(m,6),
    probes=[round(v,6) for v in vals],independent=True))
  packets.append((risk,p))
 return packets
def save(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 # Frozen policy implementation: only environment generator replaced.
 base.environment=packet_stream
 cases=[];checks=[];traces=[]
 for sc in SCENARIOS:
  for seed in SEEDS:
   for policy in ('fixed','adaptive'):
    rows=base.run(seed,sc,policy);again=base.run(seed,sc,policy)
    tests=dict(replay=rows==again,chain=base.chain(rows),
      unique=len(rows)==T and all(r['tick']==t for t,r in enumerate(rows)),
      fail_closed=all(r['action']=='HOLD' for r in rows
                      if r['reason'] in ('invalid','failed_full')),
      budget=all(r['probes'] in (0,2,4) for r in rows),
      source_frozen=hashlib.sha256(SOURCE.read_bytes()).hexdigest()==HASH)
    checks.append(dict(scenario=sc,seed=seed,policy=policy,
          **{k:int(v) for k,v in tests.items()}))
    cases.append(dict(scenario=sc,seed=seed,policy=policy,
      unsafe=sum(r['unsafe'] for r in rows),
      safe_act=sum(r['safe_act'] for r in rows),
      safe_hold=sum(r['safe_hold'] for r in rows),
      monitor_act=sum(r['action']=='ACT' and r['reason']=='monitor' for r in rows),
      probes=sum(r['probes'] for r in rows),
      cost=round(sum(r['cost'] for r in rows),2)))
    if seed==SEEDS.start:traces.extend(rows)
 save('checks.csv',checks);save('seed_results.csv',cases);save('trace_samples.csv',traces)
 total=[]
 for sc in (*SCENARIOS,'ALL'):
  for policy in ('fixed','adaptive'):
   a=[r for r in cases if r['policy']==policy and
       (sc=='ALL' or r['scenario']==sc)]
   total.append(dict(scenario=sc,policy=policy,cases=len(a),
     unsafe=sum(r['unsafe'] for r in a),
     safe_act=sum(r['safe_act'] for r in a),
     safe_hold=sum(r['safe_hold'] for r in a),
     monitor_act=sum(r['monitor_act'] for r in a),
     probes=sum(r['probes'] for r in a),
     cost=round(sum(r['cost'] for r in a),2)))
 save('results.csv',total)
 lookup={(r['scenario'],r['policy']):r for r in total}
 gates=dict(zero_unsafe=lookup['ALL','adaptive']['unsafe']==0,
   no_added_unsafe=lookup['ALL','adaptive']['unsafe']<=lookup['ALL','fixed']['unsafe'],
   cost_reduction=lookup['ALL','adaptive']['cost']<lookup['ALL','fixed']['cost'],
   clean_cost_reduction=lookup['clean','adaptive']['cost']<lookup['clean','fixed']['cost'],
   checks=all(all(v==1 for k,v in x.items()
        if k not in ('scenario','seed','policy')) for x in checks))
 m=dict(bound='AETHER-127',phase='VI',status='PASS' if all(gates.values()) else 'FAIL',
  frozen_126_source_sha256=HASH,paired_episodes=len(SCENARIOS)*len(SEEDS),
  decisions_per_policy=T*len(SCENARIOS)*len(SEEDS),checks=len(checks)*6,
  gates=gates,scenarios=SCENARIOS,seeds=[SEEDS.start,SEEDS.stop-1],
  limitations=['Synthetic sensor and packet physics',
    'Frozen AETHER-126 policy imported unchanged',
    'Trusted signing and noise declaration assumed',
    'Finite calibration samples cannot certify arbitrary nonlinear response'])
 (D/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 print(json.dumps(dict(manifest=m,results=total),indent=2))
if __name__=='__main__':main()
