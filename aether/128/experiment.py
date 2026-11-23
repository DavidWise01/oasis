#!/usr/bin/env python3
"""AETHER-128 — Phase VI constrained synthetic integration closure.

Requires numpy/scipy; run in GitHub repository checkout:
    python aether/128/experiment.py
Check local-result differences against archived local hashes. This script
is not a claim of real-world sensor trust or physical verification.
"""
from pathlib import Path
import csv,hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parent;UP=ROOT.parent
def load(path,name):
 sp=importlib.util.spec_from_file_location(name,path)
 mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);return mod
model=load(UP/'127c'/'experiment.py','model127c')
archive=('121','122','123','123b','124','124b','125','125b','126','127','127b','127c')
failed={'123','124','125','127','127b'}
seeds=range(128001,128026);faults=model.SC
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
frozen={str(p.relative_to(UP)):digest(p) for p in (UP/'126'/'experiment.py',UP/'127'/'experiment.py',UP/'127c'/'experiment.py')}
def save(name,rows):
 with (ROOT/name).open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
def main():
 source_audit=[]
 for b in archive:
  p=UP/b/'experiment.py';m=UP/b/'manifest.json'
  observed=json.loads(m.read_text()).get('status','UNKNOWN') if m.exists() else 'MISSING'
  expected='FAIL' if b in failed else 'PASS'
  source_audit.append(dict(bound=b,expected=expected,observed=observed,
   source_present=int(p.exists()),manifest_present=int(m.exists()),status_matches=int(expected==observed),
   source_sha256=digest(p) if p.exists() else '',manifest_sha256=digest(m) if m.exists() else ''))
 save('archive_inventory.csv',source_audit)
 # All 128 cases reuse a frozen single governing controller. Fresh seeds
 # are not used to select policy parameters.
 model.stress.base.environment=model.stress.packet_stream
 summaries=[];checks=[];traces=[]
 for sc in faults:
  for seed in seeds:
   a=model.guarded(seed,sc);b=model.guarded(seed,sc)
   packets=model.stress.packet_stream(seed,sc)
   tests=dict(replay=a==b,hash_chain=model.base.chain(a),
    one_action=len(a)==model.T and all(r['tick']==i and r['action'] in ('ACT','HOLD') for i,r in enumerate(a)),
    zero_unsafe=all(r['unsafe']==0 for r in a),
    signed_packet=all(r['action']=='HOLD' or (model.base.verify(packets[i][1]) and packets[i][1]['tick']==i and packets[i][1]['counter']==i) for i,r in enumerate(a)),
    coverage_before_act=all(r['action']=='HOLD' or model.coverage(seed,sc,i,packets[i][1])[0] for i,r in enumerate(a)),
    frozen_hash=all(digest(UP/k/'experiment.py')==v for k,v in ((k.split('/')[0],v) for k,v in frozen.items())),
    resource_bound=all(r['probes'] in (88,90,92) for r in a))
   checks.extend(dict(scenario=sc,seed=seed,gate=k,passed=int(v)) for k,v in tests.items())
   summaries.append(dict(scenario=sc,seed=seed,decisions=len(a),unsafe=sum(r['unsafe'] for r in a),
    safe_act=sum(r['safe_act'] for r in a),safe_hold=sum(r['safe_hold'] for r in a),
    probes=sum(r['probes'] for r in a),cost=round(sum(r['cost'] for r in a),2),trace_head=a[-1]['hash']))
   if seed==seeds.start:traces.extend(a)
 save('checks.csv',checks);save('integration_cases.csv',summaries);save('trace_samples.csv',traces)
 total=[]
 for sc in (*faults,'ALL'):
  z=[r for r in summaries if r['scenario']==sc or sc=='ALL']
  total.append(dict(scenario=sc,cases=len(z),decisions=sum(r['decisions'] for r in z),
   unsafe=sum(r['unsafe'] for r in z),safe_act=sum(r['safe_act'] for r in z),
   safe_hold=sum(r['safe_hold'] for r in z),probes=sum(r['probes'] for r in z),
   cost=round(sum(r['cost'] for r in z),2)))
 save('results.csv',total)
 gates=dict(all_checks=all(r['passed'] for r in checks),zero_unsafe=total[-1]['unsafe']==0,
    failures_preserved=all(r['source_present'] and r['manifest_present'] for r in source_audit if r['expected']=='FAIL'),
    archive_complete=len(source_audit)==12 and all(r['source_present'] and r['manifest_present'] for r in source_audit),
    statuses_match=all(r['status_matches'] for r in source_audit))
 manifest=dict(bound='AETHER-128',phase='VI',status='PASS' if all(gates.values()) else 'FAIL',
  cases=len(summaries),decisions=total[-1]['decisions'],checks=len(checks),gates=gates,source_hashes=frozen,
  warnings=['synthetic only, trusted probe response and sensor regularity assumed',
  'repository-checkout numerical reproduction must be compared with local exported data',
  'accepted historical sources inventoried not all rerun'])
 (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(manifest=manifest,summary=total),indent=2))
 if manifest['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
