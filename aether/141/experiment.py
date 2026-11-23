#!/usr/bin/env python3
"""AETHER-141 checkout reproducer: all ingress and reference roots are MOCKS."""
from pathlib import Path
import csv,hashlib,hmac,json
D=Path(__file__).resolve().parent
SC=('clean','valid_rotation','split_path','probe_bypass','replayed_receipt','issuer_swap','session_swap','latency_mismatch')
KEY=b'MOCK-TRANSPORT-141';ROOT=b'MOCK-PROTECTED-INGRESS-141'
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sign(k,x):return dict(x,mac=hmac.new(k,enc(x),hashlib.sha256).hexdigest())
def verify(k,x):
 if not isinstance(x,dict):return False
 return hmac.compare_digest(str(x.get('mac','')),hmac.new(k,enc({a:b for a,b in x.items() if a!='mac'}),hashlib.sha256).hexdigest())
def evidence(seed,sc,t):
 bad=sc not in ('clean','valid_rotation') and 8<=t<16
 true=.045 if bad else .005;g=2 if sc=='valid_rotation' and t>=12 else 1
 n=hashlib.sha256(enc([seed,sc,t])).hexdigest()[:24]
 p=sign(KEY,dict(device='A',generation=g,tick=t,counter=t,nonce=n,path='A',reading=.005))
 c=dict(device='A',generation=g,tick=t,counter=t,nonce=n,path='A',probe_path='A',session=f'{seed}:{t}',latency=1,reference='MOCK')
 if bad:
  if sc=='split_path':c['path']='B'
  elif sc=='probe_bypass':c['probe_path']='B'
  elif sc=='replayed_receipt':c['counter']=t-1
  elif sc=='issuer_swap':c['reference']='UNTRUSTED'
  elif sc=='session_swap':c['session']='WRONG'
  elif sc=='latency_mismatch':c['latency']=9
 r=sign(KEY if bad and sc=='issuer_swap' else ROOT,c)
 return true,p,r
def valid(p,r,seed,t):
 return (verify(KEY,p) and verify(ROOT,r) and
  all(p[k]==r[k] for k in ('device','generation','tick','counter','nonce','path'))
  and p['tick']==t and p['counter']==t and r['probe_path']=='A'
  and r['path']=='A' and r['session']==f'{seed}:{t}' and r['latency']==1
  and r['reference']=='MOCK')
def episode(seed,sc,policy):
 previous='0'*64;out=[]
 for t in range(24):
  truth,p,r=evidence(seed,sc,t);ok=valid(p,r,seed,t)
  act=(verify(KEY,p) and p['reading']<=.025) if policy=='signed_only' else (ok and p['reading']<=.025)
  rec=dict(seed=seed,scenario=sc,policy=policy,tick=t,action='ACT' if act else 'HOLD',unsafe=int(act and truth>.025),
   safe_act=int(act and truth<=.025),safe_hold=int(not act and truth<=.025),receipt_valid=int(ok),operational_act=0)
  h=hashlib.sha256(previous.encode()+enc(rec)).hexdigest()
  rec['prev_hash']=previous;rec['hash']=h;previous=h;out.append(rec)
 return out
def chain(rows):
 prev='0'*64
 for row in rows:
  x={k:v for k,v in row.items() if k not in ('prev_hash','hash')}
  h=hashlib.sha256(prev.encode()+enc(x)).hexdigest()
  if row['prev_hash']!=prev or row['hash']!=h:return False
  prev=h
 return True
def save(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 checks=[];seeds=[];samples=[]
 for sc in SC:
  for seed in range(141001,141041):
   for policy in ('signed_only','ingress_bound'):
    a=episode(seed,sc,policy)
    gates=dict(replay=a==episode(seed,sc,policy),chain=chain(a),single=len(a)==24,
     ticks=all(r['tick']==i for i,r in enumerate(a)),zero_unsafe=policy!='ingress_bound' or all(not r['unsafe'] for r in a),
     fail_closed=policy!='ingress_bound' or all(r['action']=='HOLD' for r in a if not r['receipt_valid']),
     availability=sc not in ('clean','valid_rotation') or all(r['safe_act']==1 for r in a),
     no_hardware=all(r['operational_act']==0 for r in a))
    checks.extend(dict(scenario=sc,seed=seed,policy=policy,gate=k,passed=int(v)) for k,v in gates.items())
    seeds.append(dict(scenario=sc,seed=seed,policy=policy,unsafe=sum(r['unsafe'] for r in a),
     safe_act=sum(r['safe_act'] for r in a),safe_hold=sum(r['safe_hold'] for r in a)))
    if seed==141001:samples+=a
 save('checkout_checks.csv',checks);save('checkout_seed_results.csv',seeds);save('checkout_trace_samples.csv',samples)
 res=[]
 for sc in (*SC,'ALL'):
  for policy in ('signed_only','ingress_bound'):
   z=[r for r in seeds if r['policy']==policy and (sc=='ALL' or sc==r['scenario'])]
   res.append(dict(scenario=sc,policy=policy,cases=len(z),unsafe=sum(r['unsafe'] for r in z),
    safe_act=sum(r['safe_act'] for r in z),safe_hold=sum(r['safe_hold'] for r in z)))
 save('checkout_results.csv',res)
 allr={r['policy']:r for r in res if r['scenario']=='ALL'}
 passed=all(x['passed'] for x in checks) and allr['signed_only']['unsafe']==1920 and allr['ingress_bound']['unsafe']==0
 (D/'checkout_manifest.json').write_text(json.dumps(dict(bound='AETHER-141',status='PASS' if passed else 'FAIL',
  checks=len(checks),physical_validation_percent=0,operational_ACT=0),indent=2)+'\n')
 print(json.dumps([r for r in res if r['scenario']=='ALL'],indent=2))
 if not passed:raise SystemExit(1)
if __name__=='__main__':main()
