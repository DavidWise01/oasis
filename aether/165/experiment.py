#!/usr/bin/env python3
"""AETHER-165 compact checkout companion (synthetic only).
Exact locally tested program SHA256:
26f539f9e238d6dfcfd28e6b0f212571e25bf1e3ded71b77d7a4afc2b2e873fb.
Local full checks and chains are in the evidence ZIP.
"""
import hashlib,hmac,json
CASES=('clean','legitimate_rotation','missing_probe','bypass_route','replayed_challenge','late_propagation','substituted_injection_port','false_response')
KEY=b'SYNTHETIC-165'
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sha(x):return hashlib.sha256(x).hexdigest()
def signed(x):return dict(x,mac=hmac.new(KEY,enc(x),hashlib.sha256).hexdigest())
def good(x):return bool(x) and hmac.compare_digest(x.get('mac',''),hmac.new(KEY,enc({a:b for a,b in x.items() if a!='mac'}),hashlib.sha256).hexdigest())
def fixture(seed,case,t):
 bad=case not in CASES[:2] and 6<=t<14;truth=.045 if bad else .005
 gen=2 if case=='legitimate_rotation' and t>=10 else 1;nonce=sha(enc([seed,case,t]))[:24]
 p=dict(tick=t,generation=gen,nonce=nonce,route='ACQ-A',port='IN-A',counter=t,response=.012,start=1000*t+100)
 r=dict(tick=t,generation=gen,nonce=nonce,route='ACQ-A',port='IN-A',counter=t,raw_time=1000*t+125,observed=truth,uncertainty=.0005)
 raw=enc(dict(tick=t,generation=gen,nonce=nonce,route='ACQ-A',reading=truth,raw_time=r['raw_time']))
 r['raw_sha']=sha(raw)
 if bad:
  if case=='missing_probe':p=None
  elif case=='bypass_route':r['route']='BYPASS'
  elif case=='replayed_challenge':p['counter']-=1
  elif case=='late_propagation':r['raw_time']+=250
  elif case=='substituted_injection_port':p['port']='OTHER'
  elif case=='false_response':p['response']=.001
 return truth,raw,signed(p) if p else None,signed(r)
def admit(raw,p,r):
 if not good(p) or not good(r) or sha(raw)!=r['raw_sha']:return False
 if any(p[k]!=r[k] for k in ('tick','generation','nonce','route','port','counter')):return False
 if p['route']!='ACQ-A' or p['port']!='IN-A' or p['counter']!=p['tick']:return False
 if abs(p['response']-.012)>.0001 or p['start']!=1000*p['tick']+100:return False
 if not 0<r['raw_time']-p['start']<=50:return False
 try:
  x=json.loads(raw)
  return enc(x)==raw and x['raw_time']==r['raw_time'] and x['tick']==r['tick'] and x['generation']==r['generation'] and x['nonce']==r['nonce'] and abs(x['reading']-r['observed'])<=r['uncertainty'] and x['reading']+r['uncertainty']<=.025
 except (TypeError,ValueError,KeyError):return False
def main():
 base=unsafe=safe=0
 for case in CASES:
  for seed in range(165001,165026):
   for t in range(20):
    truth,raw,p,r=fixture(seed,case,t);allow=admit(raw,p,r)
    base+=int(truth>.025);unsafe+=int(allow and truth>.025);safe+=int(allow and truth<=.025)
 assert (base,unsafe,safe)==(1200,0,2800),(base,unsafe,safe)
 print(json.dumps(dict(bound='AETHER-165',synthetic=True,baseline_unsafe=base,gated_unsafe=unsafe,safe_dry_run=safe,physical_qualification_percent=0,operational_act=0),indent=2))
if __name__=='__main__':main()
