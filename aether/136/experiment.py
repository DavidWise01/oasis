#!/usr/bin/env python3
"""AETHER-136 Phase VII closure — GitHub-checkout synthetic replay.

This runs the repository-authored frozen AETHER-135B policy. Local executed
AETHER-136 script has a separate source hash and may produce different hashes.
No real hardware or reference-standard validation is claimed.
"""
from pathlib import Path
import csv,hashlib,importlib.util,json
D=Path(__file__).resolve().parent;P=D.parent
def load(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
base=load(P/'135b'/'experiment.py','frozen135b')
ARCHIVE=[('129','PASS'),('130','FAIL'),('130b','PASS'),('131','PASS'),
 ('132','PASS'),('133','FAIL'),('133b','PASS'),('134','PASS'),('135','FAIL'),('135b','PASS')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,rs):
 with (D/n).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
def main():
 inventory=[]
 for name,expected in ARCHIVE:
  folder=P/name;source=folder/'experiment.py';manifest=folder/'manifest.json'
  actual=json.loads(manifest.read_text()).get('status') if manifest.exists() else 'MISSING'
  inventory.append(dict(bound=name,expected=expected,observed=actual,
   source_present=int(source.exists()),manifest_present=int(manifest.exists()),
   status_matches=int(actual==expected),source_sha256=sha(source) if source.exists() else '',
   manifest_sha256=sha(manifest) if manifest.exists() else ''))
 save('archive_inventory.csv',inventory)
 frozen={name:sha(P/name/'experiment.py') for name,_ in ARCHIVE}
 cases=[];checks=[];traces=[]
 for scenario in base.SC:
  for seed in range(136001,136026):
   a=base.episode(seed,scenario);b=base.episode(seed,scenario)
   tested=dict(replay=a==b,chain=base.chain(a),
    one_action=len(a)==base.T and all(r['action'] in ('ACT','HOLD') for r in a),
    ordered=all(r['tick']==t for t,r in enumerate(a)),
    no_unsafe=all(r['unsafe']==0 for r in a),
    reference_gate=all(r['action']=='HOLD' for r in a if not r['reference_ok']),
    signed_permission=all(r['action']!='ACT' or r['reference_ok'] for r in a),
    frozen_source=all(sha(P/name/'experiment.py')==v for name,v in frozen.items()))
   checks.extend(dict(scenario=scenario,seed=seed,check=k,passed=int(v)) for k,v in tested.items())
   cases.append(dict(scenario=scenario,seed=seed,decisions=len(a),
    unsafe=sum(r['unsafe'] for r in a),safe_act=sum(r['safe_act'] for r in a),
    safe_hold=sum(r['safe_hold'] for r in a),
    reference_cost=sum(r['reference_cost'] for r in a),last_hash=a[-1]['hash']))
   if seed==136001:traces.extend(a)
 save('checks.csv',checks);save('integration_cases.csv',cases);save('trace_samples.csv',traces)
 results=[]
 for scenario in (*base.SC,'ALL'):
  z=[r for r in cases if scenario=='ALL' or r['scenario']==scenario]
  results.append(dict(scenario=scenario,cases=len(z),decisions=sum(r['decisions'] for r in z),
   unsafe=sum(r['unsafe'] for r in z),safe_act=sum(r['safe_act'] for r in z),
   safe_hold=sum(r['safe_hold'] for r in z),reference_cost=sum(r['reference_cost'] for r in z)))
 save('results.csv',results)
 d={r['scenario']:r for r in results}
 gates=dict(all_checks=all(c['passed'] for c in checks),no_unsafe=d['ALL']['unsafe']==0,
  clean_availability=d['clean']['safe_act']==25*base.T,
  replacement_availability=d['valid_replacement']['safe_act']==25*base.T,
  historical_failures_preserved=all(r['status_matches'] and r['source_present'] and r['manifest_present']
    for r in inventory if r['expected']=='FAIL'),
  all_archives_present=len(inventory)==10 and all(r['source_present'] and r['manifest_present'] for r in inventory))
 manifest=dict(bound='AETHER-136',status='PASS' if all(gates.values()) else 'FAIL',phase='VII',
  cases=200,decisions=results[-1]['decisions'],checks=len(checks),gates=gates,
  checkout_source_sha256=sha(P/'135b'/'experiment.py'),
  physical_validation='NOT PERFORMED')
 (D/'checkout-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(manifest=manifest,results=results),indent=2))
 if manifest['status']!='PASS':raise SystemExit(2)
if __name__=='__main__':main()
