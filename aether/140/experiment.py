#!/usr/bin/env python3
"""AETHER-140 GitHub-checkout synthetic uncertainty coverage regression.
Separately authored reproducer; local recorded run has its own source SHA.
No physical instrumentation or empirical statistical coverage.
"""
import csv,hashlib,hmac,json
from pathlib import Path
D=Path(__file__).resolve().parent
SC=('clean','valid_rotation','missing_budget','unsupported_coverage','common_root_ignored','threshold_crossing','stale_budget','understated_uncertainty')
KEY=b'AETHER140-REFERENCE-MOCK';THRESHOLD=.025
def raw(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sig(x):return dict(x,signature=hmac.new(KEY,raw(x),hashlib.sha256).hexdigest())
def ver(x):
 return hmac.compare_digest(str(x.get('signature','')),hmac.new(KEY,raw({k:v for k,v in x.items() if k!='signature'}),hashlib.sha256).hexdigest())
def obs(seed,scenario,t):
 fault=scenario not in ('clean','valid_rotation') and 8<=t<16
 risk=.035 if fault else .005;generation=2 if scenario=='valid_rotation' and t>=12 else 1
 pkt=sig(dict(device='DUT-A',generation=generation,tick=t,counter=t,session=f'{seed}:{t}',reported=.005))
 c=dict(device='DUT-A',generation=generation,tick=t,session=pkt['session'],expiry=t+1,
  root='ASSUMED-TRACEABLE',coverage='deterministic-model',correlation='shared',
  random=.001,reference=.001,shared=.002,systematic=.003,reference_value=risk)
 if fault:
  if scenario=='missing_budget':del c['reference']
  if scenario=='unsupported_coverage':c['coverage']='99.999%-guaranteed'
  if scenario=='common_root_ignored':c['correlation']='independent'
  if scenario=='threshold_crossing':c['reference_value']=.024
  if scenario=='stale_budget':c['expiry']=t
  if scenario=='understated_uncertainty':c['systematic']=-.01
 return risk,pkt,sig(c)
def admit(pkt,c,t):
 if not ver(pkt) or not ver(c):return False
 if any(pkt[k]!=c[k] for k in ('device','generation','tick','session')):return False
 if pkt['tick']!=t or pkt['counter']!=t or c['expiry']!=t+1:return False
 if c['root']!='ASSUMED-TRACEABLE' or c['coverage']!='deterministic-model' or c['correlation']!='shared':return False
 terms=('random','reference','shared','systematic')
 if any(k not in c for k in terms):return False
 if any(c[k]<v for k,v in zip(terms,(.001,.001,.002,.003))):return False
 return c['reference_value']+sum(c[k] for k in terms)<=THRESHOLD
def episode(seed,sc,policy):
 a=[];prev='0'*64
 for t in range(24):
  risk,p,c=obs(seed,sc,t);bound=admit(p,c,t)
  act=(p['reported']<=THRESHOLD and ver(p)) if policy=='signed_only' else bound
  r=dict(seed=seed,scenario=sc,policy=policy,tick=t,action='ACT' if act else 'HOLD',
   unsafe=int(act and risk>THRESHOLD),safe_act=int(act and risk<=THRESHOLD),
   safe_hold=int(not act and risk<=THRESHOLD),admissible=int(bound),physical_act=0)
  h=hashlib.sha256(prev.encode()+raw(r)).hexdigest();r['prev']=prev;r['hash']=h;prev=h;a.append(r)
 return a
def chain(a):
 prev='0'*64
 for r in a:
  b={k:v for k,v in r.items() if k not in ('prev','hash')}
  digest=hashlib.sha256(prev.encode()+raw(b)).hexdigest()
  if r['prev']!=prev or r['hash']!=digest:return False
  prev=digest
 return True
def save(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 cases=[];checks=[];samples=[]
 for sc in SC:
  for seed in range(140001,140041):
   for policy in ('signed_only','budget_gated'):
    rows=episode(seed,sc,policy)
    gates=dict(repeat=rows==episode(seed,sc,policy),chain=chain(rows),ticks=len(rows)==24 and all(r['tick']==i for i,r in enumerate(rows)),
     safe=policy!='budget_gated' or all(r['unsafe']==0 for r in rows),
     fail_closed=policy!='budget_gated' or all(r['action']=='HOLD' for r in rows if not r['admissible']),
     clean=sc not in ('clean','valid_rotation') or all(r['safe_act']==1 for r in rows),
     physical_hold=all(r['physical_act']==0 for r in rows),single_action=all(r['action'] in ('ACT','HOLD') for r in rows))
    checks.extend(dict(scenario=sc,seed=seed,policy=policy,test=k,passed=int(v)) for k,v in gates.items())
    cases.append(dict(scenario=sc,seed=seed,policy=policy,unsafe=sum(r['unsafe'] for r in rows),safe_act=sum(r['safe_act'] for r in rows),safe_hold=sum(r['safe_hold'] for r in rows)))
    if seed==140001:samples+=rows
 save('checkout_checks.csv',checks);save('checkout_seed_results.csv',cases);save('checkout_traces.csv',samples)
 aggregate=[]
 for sc in (*SC,'ALL'):
  for policy in ('signed_only','budget_gated'):
   a=[r for r in cases if r['policy']==policy and (sc=='ALL' or r['scenario']==sc)]
   aggregate.append(dict(scenario=sc,policy=policy,episodes=len(a),unsafe=sum(r['unsafe'] for r in a),
    safe_act=sum(r['safe_act'] for r in a),safe_hold=sum(r['safe_hold'] for r in a)))
 save('checkout_results.csv',aggregate)
 finals={(r['scenario'],r['policy']):r for r in aggregate}
 pass_gate=all(r['passed'] for r in checks) and finals['ALL','signed_only']['unsafe']==1920 and finals['ALL','budget_gated']['unsafe']==0
 m=dict(bound='AETHER-140',repo_checkout_status='PASS' if pass_gate else 'FAIL',episodes_per_policy=320,checks=len(checks),
  physical_validation='NOT PERFORMED',operational_act=0)
 (D/'checkout_manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 print(json.dumps(dict(manifest=m,aggregate=[r for r in aggregate if r['scenario']=='ALL']),indent=2))
 if not pass_gate:raise SystemExit(1)
if __name__=='__main__':main()
