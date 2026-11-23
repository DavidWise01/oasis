#!/usr/bin/env python3
"""AETHER-135B: constrained synthetic independent physical-reference ingress.
Physical reference trust is ASSUMED. No live physical device was tested.
Run from an oasis checkout: python aether/135b/experiment.py
"""
import csv,hashlib,hmac,importlib.util,json
from pathlib import Path
D=Path(__file__).resolve().parent
P=D.parent/'135'/'experiment.py'
sp=importlib.util.spec_from_file_location('stress135',P)
stress=importlib.util.module_from_spec(sp);sp.loader.exec_module(stress)
base=stress.base
KEY=b'EXTERNAL-REFERENCE-TRUST-ROOT-AETHER-135B-SYNTHETIC'
SC=stress.SC;SEEDS=stress.SEEDS;T=base.TICKS
def raw(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sign(x):return dict(x,certificate=hmac.new(KEY,raw(x),hashlib.sha256).hexdigest())
def verify(x):
 y={k:v for k,v in x.items() if k!='certificate'}
 return hmac.compare_digest(str(x.get('certificate','')),hmac.new(KEY,raw(y),hashlib.sha256).hexdigest())
def ref(seed,sc,t,truth,p):
 if sc in ('clean','valid_replacement','honest_anomaly'):
  return sign(dict(device='REF-STD-2',root='PHYSICAL-ROOT-ASSUMED',generation=p['generation'],
   tick=t,path='REFERENCE-INDEPENDENT',reference_risk=round(truth,10),
   uncertainty=.0002,valid_until=t+1))
 if sc=='joint_spoof':
  return sign(dict(device='REF-STD-2',root='UNTRUSTED-ROOT',generation=p['generation'],
   tick=t,path='REFERENCE-INDEPENDENT',reference_risk=.001,uncertainty=0,valid_until=t+1))
 return None
def episode(seed,sc):
 prev='0'*64;out=[]
 for t,(truth,p) in enumerate(stress.environment(seed,sc)):
  r=ref(seed,sc,t,truth,p)
  ok=bool(r and verify(r) and r['device']=='REF-STD-2' and
   r['root']=='PHYSICAL-ROOT-ASSUMED' and r['path']=='REFERENCE-INDEPENDENT' and
   r['generation']==p['generation'] and r['tick']==t and r['valid_until']==t+1 and
   r['uncertainty']<=.001)
  act=ok and base.verified(p) and r['reference_risk']+r['uncertainty']<=base.THRESHOLD
  row=dict(scenario=sc,seed=seed,policy='reference_gated',tick=t,
   action='ACT' if act else 'HOLD',reference_ok=int(ok),
   unsafe=int(act and truth>base.THRESHOLD),safe_act=int(act and truth<=base.THRESHOLD),
   safe_hold=int(not act and truth<=base.THRESHOLD),reference_cost=int(r is not None))
  h=hashlib.sha256(prev.encode()+raw(row)).hexdigest()
  row['prev_hash']=prev;row['hash']=h;prev=h;out.append(row)
 return out
def chain(xs):
 prev='0'*64
 for r in xs:
  a={k:v for k,v in r.items() if k not in ('prev_hash','hash')}
  h=hashlib.sha256(prev.encode()+raw(a)).hexdigest()
  if r['prev_hash']!=prev or r['hash']!=h:return False
  prev=h
 return True
def save(n,rs):
 with (D/n).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
def main():
 records=[];checks=[];samples=[]
 for sc in SC:
  for seed in SEEDS:
   a=episode(seed,sc);b=episode(seed,sc)
   gates=dict(replay=a==b,chain=chain(a),one_action=len(a)==T,
    tick_order=all(r['tick']==t for t,r in enumerate(a)),
    no_unsafe=all(r['unsafe']==0 for r in a),
    fail_closed=all(r['action']=='HOLD' for r in a if not r['reference_ok']),
    signed_ref=all(r['action']=='HOLD' or r['reference_ok'] for r in a),
    no_forged_act=all(r['action']=='HOLD' for r in a if sc not in ('clean','valid_replacement','honest_anomaly')))
   checks.append(dict(scenario=sc,seed=seed,**{k:int(v) for k,v in gates.items()}))
   records.append(dict(scenario=sc,seed=seed,policy='reference_gated',unsafe=sum(r['unsafe'] for r in a),
    safe_act=sum(r['safe_act'] for r in a),safe_hold=sum(r['safe_hold'] for r in a),
    reference_cost=sum(r['reference_cost'] for r in a)))
   if seed==SEEDS.start:samples.extend(a)
 save('checks.csv',checks);save('seed_results.csv',records);save('trace_samples.csv',samples)
 res=[]
 for sc in (*SC,'ALL'):
  z=[r for r in records if sc=='ALL' or r['scenario']==sc]
  res.append(dict(scenario=sc,policy='reference_gated',cases=len(z),unsafe=sum(r['unsafe'] for r in z),
   safe_act=sum(r['safe_act'] for r in z),safe_hold=sum(r['safe_hold'] for r in z),
   reference_cost=sum(r['reference_cost'] for r in z)))
 save('results.csv',res);v={r['scenario']:r for r in res}
 g=dict(no_unsafe=v['ALL']['unsafe']==0,clean_retained=v['clean']['safe_act']==1600,
  replacement_retained=v['valid_replacement']['safe_act']==1600,
  failed_135_preserved=(D.parent/'135'/'manifest.json').exists() and json.loads((D.parent/'135'/'manifest.json').read_text())['status']=='FAIL',
  checks=all(all(n==1 for k,n in x.items() if k not in ('scenario','seed')) for x in checks))
 m=dict(bound='AETHER-135B',phase='VII',status='PASS' if all(g.values()) else 'FAIL',
  cases=400,decisions=12800,checks=len(checks)*8,gates=g,
  limitations=['Independent reference physical truth and root are assumed',
   'Missing corroborating reference forces HOLD, not repaired measurement',
   'Actual hardware path independence and accuracy not established'])
 (D/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 print(json.dumps(dict(manifest=m,results=res),indent=2))
 if m['status']!='PASS':raise SystemExit(2)
if __name__=='__main__':main()
