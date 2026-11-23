#!/usr/bin/env python3
"""AETHER-112: Phase IV deterministic closure integration.
Run: python aether/112/experiment.py --source-root /mnt/data
Requires numpy, scipy, and preserved Phase IV aetherNNN directories.
"""
import argparse,csv,hashlib,importlib.util,json
from pathlib import Path
import numpy as np
BOUNDS=('105','106','107','108','109b','110','111b')
FAILED=('109','111')
KINDS=('price_shock','sensor_dropout','hidden_correlation','abrupt_spike','moving_oscillation')
def digest(b):return hashlib.sha256(b).hexdigest()
def save(p,rows):
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def load(p):
 s=importlib.util.spec_from_file_location('aether111b_frozen',p)
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 a=argparse.ArgumentParser();a.add_argument('--source-root',default='/mnt/data');args=a.parse_args()
 root=Path(args.source_root);out=Path(__file__).resolve().parent
 archive=[];missing=[]
 for b in (*BOUNDS,*FAILED):
  for f in ('experiment.py','results.csv','manifest.json'):
   p=root/('aether'+b)/f
   if not p.is_file():missing.append(str(p));continue
   archive.append(dict(bound=b,record='accepted' if b in BOUNDS else 'failed-preserved',file=f,bytes=p.stat().st_size,sha256=digest(p.read_bytes())))
 if missing:raise RuntimeError('Missing archived evidence: '+', '.join(missing))
 save(out/'inventory.csv',archive)
 m=load(root/'aether111b'/'experiment.py)
 checks=('replay','causal_prefix','hash_chain','packet_fail_closed','admissibility','resource_budget')
 rows=[]
 for kind in KINDS:
  for seed in range(112001,112013):
   data=m.episode(seed,kind)
   for policy in ('fixed','adaptive'):
    result,trace=m.run(seed,kind,policy,data,trace=True)
    replay,rtrace=m.run(seed,kind,policy,data,trace=True)
    future=[dict(p) for p in data]
    for t in range(12,len(future)):
     future[t].update(status='missing',values=np.array([],dtype=np.int8),reported_count=0,certified_unique_count=0)
    _,ftrace=m.run(seed,kind,policy,future,trace=True)
    chain='0'*64;hash_ok=True
    for event in trace:
     payload={k:v for k,v in event.items() if k!='hash'}
     chain=digest((chain+json.dumps(payload,sort_keys=True,separators=(',',':'))).encode())
     if chain!=event['hash']:hash_ok=False;break
    tests=dict(replay=result==replay and trace==rtrace,
      causal_prefix=trace[:12]==ftrace[:12],hash_chain=hash_ok,
      packet_fail_closed=all(x['action']=='HOLD' for x in trace if x['packet_status']!='valid'),
      admissibility=all(x['action']=='HOLD' or (x['packet_status']=='valid' and x['upper']<=m.LIMIT+1e-8) for x in trace),
      resource_budget=result['roots']<=m.BUDGET and all(x['remaining_budget']>=0 for x in trace))
    rows.append(dict(seed=seed,scenario=kind,policy=policy,acts=result['acts'],holds=result['holds'],
     wrong=result['wrong'],unsafe_authorized=result['unsafe_authorized'],roots=result['roots'],cost=result['cost'],**tests))
 save(out/'integration_cases.csv',rows)
 scores={k:sum(int(x[k]) for x in rows) for k in checks}
 passed=all(v==len(rows) for v in scores.values())
 manifest=dict(bound='AETHER-112',phase='IV',status='PASS' if passed else 'FAIL',completion_percent=100 if passed else 87.5,
  accepted_bounds=list(BOUNDS),preserved_failed_bounds=list(FAILED),
  archived_source_files=len(archive),integration_cases=len(rows),check_categories=scores,
  check_total=sum(scores.values()),checks_possible=len(rows)*len(checks),
  simulated_inspections=sum(x['acts']+x['holds'] for x in rows),
  acts=sum(x['acts'] for x in rows),holds=sum(x['holds'] for x in rows),
  unsafe_authorized_ticks=sum(x['unsafe_authorized'] for x in rows),
  gate='All archive items present, six deterministic checks per case pass; no universal risk guarantee',
  caveats=['Packet status and certified root counts assumed truthful at acquisition boundary',
   'Fixed-time bounds do not imply distribution-free protection after drift',
   'Integrated 111B frozen controller tested; previous bounds inventoried and hashed, not reexecuted',
   'No witness consensus or Byzantine fault tolerance attempted'])
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(manifest,indent=2));return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
