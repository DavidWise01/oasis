#!/usr/bin/env python3
"""AETHER-156 standalone synthetic uncertainty-budget reproduction.
Full executed 3200-check source and audit are in the conversation evidence ZIP.
No real reference instrument, accredited certificate or physical samples exist.
"""
import json,math,hashlib,hmac
CASES=['clean','legitimate_rotation','missing_contributor','shared_calibration_root',
 'understated_resolution','expired_calibration','unsupported_coverage','false_reference']
REF=b'SIM-REFERENCE-156';BENCH=b'SIM-BENCH-156'
MIN={'calibration':.001,'repeatability':.0005,'resolution':.0004,'drift':.0006}
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sign(x,key):return dict(x,mac=hmac.new(key,enc(x),hashlib.sha256).hexdigest())
def valid(x,key):return hmac.compare_digest(x.get('mac',''),
 hmac.new(key,enc({k:v for k,v in x.items() if k!='mac'}),hashlib.sha256).hexdigest())
def lower(hit,n,z=1.6448536269514722):
 p=hit/n;q=z*z
 return (p+q/(2*n)-z*math.sqrt(p*(1-p)/n+q/(4*n*n)))/(1+q/n)
def specimen(seed,case,t):
 bad=case not in CASES[:2] and 6<=t<14
 truth=.045 if bad else .005
 g=2 if case=='legitimate_rotation' and t>=10 else 1
 nonce=hashlib.sha256(enc([seed,case,t])).hexdigest()[:24]
 c=dict(serial='REF-156',generation=g,tick=t,nonce=nonce,
   issuer='MOCK-LAB',ancestry='MOCK-TRACE',shared=False,expires=t+1,
   contributors=dict(MIN),k=2,coverage=.95,n=120,hits=120,measured=truth)
 b=dict(generation=g,tick=t,nonce=nonce,observed=truth,uncertainty=.0003)
 if bad:
  if case=='missing_contributor':del c['contributors']['drift']
  elif case=='shared_calibration_root':c['shared']=True
  elif case=='understated_resolution':c['contributors']['resolution']=.00001
  elif case=='expired_calibration':c['expires']=t
  elif case=='unsupported_coverage':c['hits']=100
  elif case=='false_reference':c['measured']=.005
 return truth,sign(c,REF),sign(b,BENCH)
def admit(c,b):
 if not(valid(c,REF) and valid(b,BENCH)):return False
 if c['issuer']!='MOCK-LAB' or c['ancestry']!='MOCK-TRACE' or c['shared']:return False
 if c['generation']!=b['generation'] or c['tick']!=b['tick'] or c['nonce']!=b['nonce']:return False
 if c['expires']!=c['tick']+1 or set(c['contributors'])!=set(MIN):return False
 if any(c['contributors'][k]<v for k,v in MIN.items()):return False
 if c['k']!=2 or c['coverage']!=.95 or c['n']!=120 or lower(c['hits'],120)<.95:return False
 u=math.sqrt(sum(v*v for v in c['contributors'].values()))
 return abs(c['measured']-b['observed'])<=2*u+b['uncertainty'] and c['measured']+2*u+b['uncertainty']<=.025
def main():
 totals=dict(baseline_unsafe=0,guarded_unsafe=0,safe_dry_run=0,operational_act=0)
 for case in CASES:
  for seed in range(156001,156026):
   for tick in range(20):
    truth,c,b=specimen(seed,case,tick);decision=admit(c,b)
    totals['baseline_unsafe']+=int(truth>.025)
    totals['guarded_unsafe']+=int(decision and truth>.025)
    totals['safe_dry_run']+=int(decision and truth<=.025)
 assert totals==dict(baseline_unsafe=1200,guarded_unsafe=0,safe_dry_run=2800,operational_act=0),totals
 print(json.dumps(dict(bound='AETHER-156',status='SYNTHETIC PASS',**totals),indent=2))
if __name__=='__main__':main()
