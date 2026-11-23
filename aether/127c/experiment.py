#!/usr/bin/env python3
"""AETHER-127C: bounded, opaque microprobe coverage over the risk range.
Frozen AETHER-126 action logic; AETHER-127 sensor fault generator. Synthetic only.
Requires NumPy and SciPy, with aether/126 and aether/127 alongside this folder.
"""
import csv,hashlib,importlib.util,json
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent
def load(p,name):
 spec=importlib.util.spec_from_file_location(name,p)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
SOURCE=D.parent/'126'/'experiment.py'
STRESS=D.parent/'127'/'experiment.py'
base=load(SOURCE,'frozen126');stress=load(STRESS,'stress127')
SHA=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
SC=stress.SCENARIOS;SEEDS=range(127201,127261);T=base.T;N=base.N
DOMAIN=tuple(range(101));NP=88
def response(sc,t,x):
 g,b=1.,0.
 if sc=='fast_drift':g=1.-.018*t
 if sc=='abrupt_gain' and t>=13:g=.34
 if sc=='abrupt_offset' and t>=13:b=-36.
 if sc=='replacement_spoof' and t>=15:g=.45
 z=g*x+b
 if sc=='monitor_blindspot' and t>=13 and 35<=x<90:z=x-45
 if sc=='nonlinear_midrange' and t>=13 and 35<=x<80:z=x-40
 return z
def probe_positions(seed,sc,t):
 rng=np.random.default_rng(seed+100003*SC.index(sc)+701*t+127829)
 parity=int(rng.integers(0,2))
 # Guaranteed 1-net, with additional hidden randomly selected interior points.
 guarantee=set(range(parity,101,2))|{0,100}
 others=tuple(sorted(set(DOMAIN)-guarantee))
 added=tuple(int(x) for x in rng.choice(others,size=NP-len(guarantee),replace=False))
 return tuple(sorted(guarantee.union(added)))
def coverage(seed,sc,t,p):
 if not base.verify(p) or p['tick']!=t or p['counter']!=t or p['independent'] is not True:
  return False,'invalid'
 if p['noise_bound'] is None:return False,'noise_certificate_missing'
 if p['noise_bound']>4:return False,'noise_out_of_bound'
 pts=probe_positions(seed,sc,t)
 if max(min(abs(x-v) for v in pts) for x in DOMAIN)>1:
  return False,'uncovered_domain'
 fit=base.full_fit(p)
 if fit is None:return False,'invalid_affine'
 eps=float(p['noise_bound'])
 # Assumed physical same-path response and protected sentinel ground truth.
 # Sensor ability to recognize probes invalidates this synthetic demonstration.
 for x in pts:
  y=response(sc,t,x)
  lo=fit['gl']*x+fit['bl']-1-eps
  hi=fit['gh']*x+fit['bh']+1+eps
  if not lo<=y<=hi:return False,'microprobe_mismatch'
 return True,'microprobe_covered'
def guarded(seed,sc):
 records=stress.packet_stream(seed,sc)
 anchor=None;rows=[];prev='0'*64
 for t,(risk,p) in enumerate(records):
  action,n,anchor,reason=base.decide(p,t,'adaptive',anchor)
  covered,why=coverage(seed,sc,t,p)
  if not covered:action='HOLD';reason=why
  act=action=='ACT'
  count=n+(NP if base.verify(p) and p['noise_bound'] is not None else 0)
  row=dict(seed=seed,scenario=sc,policy='guarded',tick=t,action=action,
    reason=reason,unsafe=int(act and risk>base.LIMIT),
    safe_act=int(act and risk<=base.LIMIT),safe_hold=int(not act and risk<=base.LIMIT),
    probes=count,microprobe_authorized=int(covered),
    cost=round((10*N*risk if act else .05*N)+(n+NP)*2.,3))
  raw=json.dumps(row,sort_keys=True,separators=(',',':'))
  row['prev_hash']=prev;prev=hashlib.sha256((prev+raw).encode()).hexdigest()
  row['hash']=prev;rows.append(row)
 return rows
def save(path,rows):
 fields=list(dict.fromkeys(k for r in rows for k in r))
 with (D/path).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def main():
 stress.base.environment=stress.packet_stream
 summaries=[];checks=[];traces=[]
 for sc in SC:
  for seed in SEEDS:
   for policy in ('adaptive_frozen','guarded'):
    a=stress.base.run(seed,sc,'adaptive') if policy=='adaptive_frozen' else guarded(seed,sc)
    b=stress.base.run(seed,sc,'adaptive') if policy=='adaptive_frozen' else guarded(seed,sc)
    rules=dict(replay=a==b,chain=base.chain(a),
      unique_tick=len(a)==T and all(r['tick']==t for t,r in enumerate(a)),
      no_unsafe=policy!='guarded' or all(r['unsafe']==0 for r in a),
      fresh_coverage=policy!='guarded' or all(r['action']=='HOLD' for r in a if not r['microprobe_authorized']),
      frozen_base=hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA,
      bounded_resources=all(r['probes'] in ((0,2,4) if policy=='adaptive_frozen' else (NP,NP+2,NP+4)) for r in a))
    checks.append(dict(scenario=sc,seed=seed,policy=policy,**{k:int(v) for k,v in rules.items()}))
    summaries.append(dict(scenario=sc,seed=seed,policy=policy,
      unsafe=sum(r['unsafe'] for r in a),safe_act=sum(r['safe_act'] for r in a),
      safe_hold=sum(r['safe_hold'] for r in a),probes=sum(r['probes'] for r in a),
      cost=round(sum(r['cost'] for r in a),2)))
    if seed==SEEDS.start:traces.extend(a)
 save('checks.csv',checks);save('seed_results.csv',summaries);save('trace_samples.csv',traces)
 totals=[]
 for sc in (*SC,'ALL'):
  for policy in ('adaptive_frozen','guarded'):
   z=[r for r in summaries if r['policy']==policy and (sc=='ALL' or r['scenario']==sc)]
   totals.append(dict(scenario=sc,policy=policy,cases=len(z),
     unsafe=sum(r['unsafe'] for r in z),safe_act=sum(r['safe_act'] for r in z),
     safe_hold=sum(r['safe_hold'] for r in z),probes=sum(r['probes'] for r in z),
     cost=round(sum(r['cost'] for r in z),2)))
 save('results.csv',totals)
 lookup={(r['scenario'],r['policy']):r for r in totals}
 gates=dict(no_unsafe=lookup['ALL','guarded']['unsafe']==0,
   nonlinear_zero=all(lookup[s,'guarded']['unsafe']==0 for s in ('monitor_blindspot','nonlinear_midrange')),
   clean_availability=lookup['clean','guarded']['safe_act']==lookup['clean','adaptive_frozen']['safe_act'],
   baseline_failed=lookup['ALL','adaptive_frozen']['unsafe']>0,
   reproducible=all(all(v==1 for k,v in r.items() if k not in ('scenario','seed','policy')) for r in checks))
 manifest=dict(bound='AETHER-127C',phase='VI',status='PASS' if all(gates.values()) else 'FAIL',
   episodes_per_policy=480,decisions_per_policy=15360,checks=len(checks)*7,
   base_sha256=SHA,gates=gates,seed_range=[SEEDS.start,SEEDS.stop-1],
   probes_per_tick=NP,input_domain=[0,100],coverage_radius=1,
   assumptions=['Trusted opaque challenge insertion and ground truth',
     'Same-path response and an externally trusted regularity constraint',
     'Attacker recognizing probe inputs breaks claimed coverage protection',
     'Synthetic model, no guarantee against arbitrary nonlinear deception'])
 (D/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(manifest=manifest,results=totals),indent=2))
 if manifest['status']!='PASS':raise SystemExit(2)
if __name__=='__main__':main()
