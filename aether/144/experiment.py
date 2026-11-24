#!/usr/bin/env python3
"""AETHER-144 checkout replay. Synthetic readiness only, NOT hardware validation.
Runs GitHub checkout's AETHER-143 controller with 25 new seeds.
No real physical root, reference standard or operational ACT.
"""
import csv,hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'143'/'experiment.py'
spec=importlib.util.spec_from_file_location('frozen143',SOURCE)
model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,rows):
 with (HERE/p).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 frozen=digest(SOURCE);results=[];checks=[];traces=[]
 for sc in model.SC:
  for seed in range(144001,144026):
   a=model.episode(seed,sc,'bench_gated')
   b=model.episode(seed,sc,'bench_gated')
   gates=dict(replay=a==b,chain=model.chain(a),
    single_action=len(a)==24 and all(x['action'] in ('ACT','HOLD') for x in a),
    ordered=all(x['tick']==i for i,x in enumerate(a)),
    zero_model_unsafe=all(x['unsafe']==0 for x in a),
    reference_before_act=all(x['action']=='HOLD' for x in a if not x['reference_ok']),
    physical_hold=all(x['operational_action']=='HOLD' for x in a),
    source_unchanged=digest(SOURCE)==frozen)
   checks.extend(dict(scenario=sc,seed=seed,gate=k,passed=int(v)) for k,v in gates.items())
   results.append(dict(scenario=sc,seed=seed,decisions=len(a),unsafe=sum(x['unsafe'] for x in a),
    safe_act=sum(x['safe_act'] for x in a),safe_hold=sum(x['safe_hold'] for x in a),last_hash=a[-1]['hash']))
   if seed==144001:traces.extend(a)
 save('checkout_checks.csv',checks);save('checkout_cases.csv',results);save('checkout_traces.csv',traces)
 agg=[]
 for sc in (*model.SC,'ALL'):
  z=[x for x in results if x['scenario']==sc or sc=='ALL']
  agg.append(dict(scenario=sc,cases=len(z),decisions=sum(x['decisions'] for x in z),
   unsafe=sum(x['unsafe'] for x in z),safe_act=sum(x['safe_act'] for x in z),safe_hold=sum(x['safe_hold'] for x in z)))
 save('checkout_results.csv',agg)
 gates=dict(checks=all(x['passed']==1 for x in checks),zero_unsafe=agg[-1]['unsafe']==0,
  clean=next(x for x in agg if x['scenario']=='clean')['safe_act']==600,
  valid_rotation=next(x for x in agg if x['scenario']=='valid_rotation')['safe_act']==600)
 manifest=dict(bound='AETHER-144',source='repository_checkout',status='PASS' if all(gates.values()) else 'FAIL',
  tests=len(checks),cases=len(results),source_sha256=frozen,gates=gates,physical_validation=0,
  qualification='Synthetic only, mock bench knows ground truth; all operational actions HOLD.')
 (HERE/'checkout_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(manifest,indent=2))
 if manifest['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
