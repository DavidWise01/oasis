#!/usr/bin/env python3
"""AETHER-152 GitHub checkout companion, synthetic only.
For the EXACT locally executed frozen 151 controller integration, see evidence ZIP
shipped with this milestone. This script checks the GitHub 151 source under
25 new seeds. Its output is not interchangeable with local evidence results.
"""
import ast,importlib.util,json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent
SOURCE=D.parent/'151'/'experiment.py'
def load():
 tree=ast.parse(SOURCE.read_text())
 eligible=[]
 for node in tree.body:
  if isinstance(node,(ast.Import,ast.ImportFrom,ast.FunctionDef)):eligible.append(node)
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('SCENARIOS','TICKS','LIMIT','DUT_KEY','REF_KEY','BENCH_KEY') for t in node.targets):eligible.append(node)
 context={'__file__':str(SOURCE)}
 exec(compile(ast.fix_missing_locations(ast.Module(body=eligible,type_ignores=[])),str(SOURCE),'exec'),context)
 return context
def main():
 m=load();SC=m['SCENARIOS'];assert len(SC)==8
 checks=cases=safe=baseline=unsafe=real_actions=0
 for case in SC:
  for seed in range(152001,152026):
   for policy in ('signed_only','blind_intake'):
    a=m['episode'](seed,case,policy)
    b=m['episode'](seed,case,policy)
    predicates=[a==b,m['chain'](a),len(a)==20,
      all(r['tick']==i for i,r in enumerate(a)),
      policy!='blind_intake' or not any(r['unsafe'] for r in a),
      all(r['operational_action']=='HOLD' for r in a),
      case not in SC[:2] or all(r['safe_act'] for r in a),
      all(r['action'] in ('HOLD','ACT') for r in a)]
    checks+=len(predicates);assert all(predicates),(case,seed,policy)
    cases+=1
    if policy=='signed_only':baseline+=sum(r['unsafe'] for r in a)
    else:
     safe+=sum(r['safe_act'] for r in a)
     unsafe+=sum(r['unsafe'] for r in a)
 assert (checks,cases,baseline,unsafe,safe,real_actions)==(3200,400,1200,0,2800,0)
 print(json.dumps(dict(bound='AETHER-152',checkout_comparator='distinct inherited 151 GitHub source',
  checks=checks,episodes=cases,baseline_unsafe=baseline,guard_unsafe=unsafe,
  guard_safe=safe,operational_act=real_actions,physical_validation_percent=0),indent=2))
if __name__=='__main__':main()
