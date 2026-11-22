#!/usr/bin/env python3
"""AETHER-104: deterministic synthetic lineage-aware evidence deduplication."""
import csv,hashlib,json,random
from collections import Counter,defaultdict
from pathlib import Path
OUT=Path(__file__).resolve().parent
N=2000
SCENARIOS=('independent','cloned_corrupt','insufficient_roots')
SEEDS=range(104000,104000+N)
def rec(seed,scenario):
 rng=random.Random(seed+{'independent':0,'cloned_corrupt':1000000,'insufficient_roots':2000000}[scenario])
 truth=rng.randrange(2)
 if scenario=='independent':
  roots=[('root-A',truth if rng.random()<.88 else 1-truth),('root-B',truth if rng.random()<.88 else 1-truth),('root-C',truth if rng.random()<.88 else 1-truth)]
  reports=roots[:]+[roots[0],roots[1]]
 elif scenario=='cloned_corrupt':
  roots=[('root-corrupt',1-truth),('root-clean-B',truth),('root-clean-C',truth)]
  reports=[roots[0]]*4+[roots[1],roots[2]]
 else:
  v0=truth if rng.random()<.8 else 1-truth
  v1=truth if rng.random()<.8 else 1-truth
  roots=[('root-A',v0),('root-B',v1)]
  reports=[roots[0]]*4+[roots[1]]
 rng.shuffle(reports)
 return truth,[(f'report-{i}',root,v) for i,(root,v) in enumerate(reports)]
def choose_naive(reports):
 count=Counter(v for _,_,v in reports)
 return 'HOLD' if count[0]==count[1] else str(count.most_common(1)[0][0])
def choose_roots(reports):
 ancestry=defaultdict(set)
 for _,root,value in reports:ancestry[root].add(value)
 clean=[next(iter(v)) for v in ancestry.values() if len(v)==1]
 count=Counter(clean)
 return 'HOLD' if count[0]==count[1] or max(count.values(),default=0)<2 else str(count.most_common(1)[0][0])
def save(name,items):
 with (OUT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)
def main():
 cases=[];traces=[]
 for scenario in SCENARIOS:
  for seed in SEEDS:
   truth,reports=rec(seed,scenario)
   naive,root=choose_naive(reports),choose_roots(reports)
   record=dict(scenario=scenario,seed=seed,truth=truth,report_count=len(reports),distinct_ancestry_roots=len({r[1] for r in reports}),
      naive=naive,root_aware=root,naive_wrong=int(naive!='HOLD' and int(naive)!=truth),
      root_wrong=int(root!='HOLD' and int(root)!=truth),root_hold=int(root=='HOLD'))
   cases.append(record)
   if seed<104004:
    payload=json.dumps(dict(case=record,reports=reports),sort_keys=True,separators=(',',':'))
    traces.append(dict(scenario=scenario,seed=seed,trace_sha256=hashlib.sha256(payload.encode()).hexdigest(),reports_json=json.dumps(reports)))
 summary=[]
 for scenario in (*SCENARIOS,'ALL'):
  subset=[x for x in cases if scenario=='ALL' or x['scenario']==scenario]
  n=len(subset);nw=sum(x['naive_wrong'] for x in subset);rw=sum(x['root_wrong'] for x in subset);holds=sum(x['root_hold'] for x in subset)
  summary.append(dict(scenario=scenario,cases=n,naive_wrong=nw,root_wrong=rw,root_holds=holds,
   naive_wrong_pct=round(nw/n*100,3),root_wrong_pct=round(rw/n*100,3),root_coverage_pct=round((n-holds)/n*100,3)))
 save('results.csv',summary);save('seed_results.csv',cases);save('trace_samples.csv',traces)
 by={r['scenario']:r for r in summary};cloned=by['cloned_corrupt'];overall=by['ALL']
 checks=dict(rooted_not_worse_overall=overall['root_wrong']<=overall['naive_wrong'],
  cloned_bad_reduction_at_least_90pct=cloned['root_wrong']<=.1*cloned['naive_wrong'],
  no_single_root_authorization=all(not(x['root_aware']!='HOLD' and x['distinct_ancestry_roots']<2) for x in cases))
 manifest=dict(bound='AETHER-104',phase='III',status='PASS' if all(checks.values()) else 'FAIL',
  phase_pct=12.5 if all(checks.values()) else 0,cases=len(cases),scenarios=list(SCENARIOS),
  seed_range=[min(SEEDS),max(SEEDS)],tests=checks,
  scope='Trusted source-root metadata in synthetic evidence; no protection from forged ancestry IDs or coordinated corrupt roots',
  next='AETHER-105: forged provenance and shared upstream ancestry')
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(manifest=manifest,results=summary),indent=2))
if __name__=='__main__':main()
