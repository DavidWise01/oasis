#!/usr/bin/env python3
"""AETHER-147: small standalone synthetic provenance reproducer.

The full 3840-check executed source is packaged in aether147-evidence.zip.
This source is independently authored; no physical reference was tested.
"""
import hashlib,hmac,json
SC=('clean','valid_rotation','raw_missing','raw_mutated',
    'samples_reordered','sample_dropped','forged_transform','source_untraceable')
KEY=b'AETHER147-MOCK-REFERENCE-ACQUISITION-KEY'
def enc(a):return json.dumps(a,sort_keys=True,separators=(',',':')).encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def sign(a):return dict(a,mac=hmac.new(KEY,enc(a),hashlib.sha256).hexdigest())
def verify(a):
 return hmac.compare_digest(a.get('mac',''),hmac.new(KEY,enc({k:v for k,v in a.items() if k!='mac'}),hashlib.sha256).hexdigest())
def acquire(seed,sc,t):
 bad=sc not in SC[:2] and 6<=t<14
 truth=.045 if bad else .005
 gen=2 if sc=='valid_rotation' and t>=10 else 1
 nonce=sha(enc([seed,sc,t]))[:24]
 samples=[dict(index=i,value=round(truth+.0001*(i-1),8)) for i in range(3)]
 obj=dict(reference='REF-147',generation=gen,tick=t,nonce=nonce,samples=samples)
 raw=enc(obj)
 proof=dict(device='DUT-147',generation=gen,tick=t,nonce=nonce,path='INGRESS-A',
  source='MOCK-EXTERNAL',raw_sha256=sha(raw),claimed=truth,uncertainty=.0004)
 if bad:
  if sc=='raw_missing':raw=b''
  elif sc=='raw_mutated':raw=raw.replace(b'REF-147',b'REF-148')
  elif sc=='samples_reordered':raw=enc(dict(obj,samples=samples[::-1]))
  elif sc=='sample_dropped':raw=enc(dict(obj,samples=samples[:-1]))
  elif sc=='forged_transform':proof['claimed']=.005
  elif sc=='source_untraceable':proof['source']='DUT-OWNED'
 return truth,raw,sign(proof),nonce
def permitted(raw,r,t,nonce):
 if not verify(r) or r['source']!='MOCK-EXTERNAL' or r['device']!='DUT-147' or r['path']!='INGRESS-A':return False
 if not raw or sha(raw)!=r['raw_sha256'] or r['tick']!=t or r['nonce']!=nonce:return False
 try:
  d=json.loads(raw)
  a=d['samples']
  if d['reference']!='REF-147' or d['generation']!=r['generation'] or d['tick']!=t:return False
  if d['nonce']!=nonce or len(a)!=3 or [x['index'] for x in a]!=[0,1,2]:return False
  if enc(d)!=raw:return False
  mean=sum(x['value'] for x in a)/3
  if abs(mean-r['claimed'])>1e-9:return False
  return mean+r['uncertainty']<=.025
 except (KeyError,ValueError,TypeError):return False
def main():
 signed_unsafe=guard_unsafe=guard_safe=0
 for sc in SC:
  for seed in range(147001,147031):
   for t in range(20):
    truth,raw,r,nonce=acquire(seed,sc,t)
    gate=permitted(raw,r,t,nonce)
    signed_unsafe+=int(truth>.025)
    guard_unsafe+=int(gate and truth>.025)
    guard_safe+=int(gate and truth<=.025)
 assert (signed_unsafe,guard_unsafe,guard_safe)==(1440,0,3360)
 print(json.dumps(dict(bound='AETHER-147',status='PASS',mode='SYNTHETIC ONLY',
  signed_only_unsafe=signed_unsafe,lineage_gated_unsafe=guard_unsafe,
  lineage_gated_safe=guard_safe,operational_ACT=0),indent=2))
if __name__=='__main__':main()
