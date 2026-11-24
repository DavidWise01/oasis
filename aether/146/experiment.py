#!/usr/bin/env python3
"""AETHER-146 checkout-oriented synthetic quarantine intake reproducer.
The complete locally tested 3840-check experiment is in the evidence ZIP.
Mock HMAC keys and generated raw records ARE NOT physical qualification.
"""
import hashlib,hmac,json
KEY=b'SIMULATED-REFERENCE-ROOT-146'
def data(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sign(x):return dict(x,mac=hmac.new(KEY,data(x),hashlib.sha256).hexdigest())
def valid(x):
 if not isinstance(x,dict):return False
 return hmac.compare_digest(x.get('mac',''),hmac.new(KEY,data({k:v for k,v in x.items() if k!='mac'}),hashlib.sha256).hexdigest())
def acquire(seed,scenario,t):
 bad=scenario not in ('clean','valid_rotation') and 6<=t<14
 true=.045 if bad else .005
 gen=2 if scenario=='valid_rotation' and t>=10 else 1
 nonce=hashlib.sha256(data([seed,scenario,t])).hexdigest()[:24]
 raw=data(dict(seed=seed,scenario=scenario,t=t,risk=true))
 c=dict(issuer='EXTERNAL-CALIBRATION-ROOT-MOCK',serial='REF-146',generation=gen,
   start=t,end=t+1,uncertainty=.0004,calibration='CERT-146')
 r=dict(serial='REF-146',generation=gen,nonce=nonce,tick=t,device='DUT-146',
   path='PATH-A',calibration='CERT-146',raw_sha256=hashlib.sha256(raw).hexdigest(),
   reference_risk=true,uncertainty=.0004)
 if bad:
  if scenario=='missing_certificate':c=None
  elif scenario=='expired_certificate':c['end']=t
  elif scenario=='wrong_serial':c['serial']='UNKNOWN'
  elif scenario=='raw_hash_mismatch':r['raw_sha256']='0'*64
  elif scenario=='self_issued_reference':c['issuer']='DUT-146'
  elif scenario=='unbound_acquisition':r['nonce']='WRONG'
 return true,sign(c) if c else None,sign(r),raw,nonce
def permitted(cert,receipt,raw,nonce,t):
 if not (valid(cert) and valid(receipt)):return False
 if cert['issuer']!='EXTERNAL-CALIBRATION-ROOT-MOCK':return False
 if cert['serial']!='REF-146' or cert['serial']!=receipt['serial']:return False
 if cert['calibration']!=receipt['calibration'] or cert['generation']!=receipt['generation']:return False
 if cert['start']!=t or cert['end']!=t+1 or receipt['tick']!=t:return False
 if receipt['device']!='DUT-146' or receipt['path']!='PATH-A' or receipt['nonce']!=nonce:return False
 if receipt['raw_sha256']!=hashlib.sha256(raw).hexdigest():return False
 if not .0003<=cert['uncertainty']<=.001:return False
 if receipt['uncertainty']!=cert['uncertainty']:return False
 return receipt['reference_risk']+receipt['uncertainty']<=.025
def main():
 scenarios=['clean','valid_rotation','missing_certificate','expired_certificate','wrong_serial',
  'raw_hash_mismatch','self_issued_reference','unbound_acquisition']
 summary=dict(cases=0,decisions=0,signed_only_unsafe=0,intake_unsafe=0,intake_safe=0,physical_ACT=0)
 for sc in scenarios:
  for seed in range(146001,146031):
   summary['cases']+=1
   for t in range(20):
    truth,c,r,raw,nonce=acquire(seed,sc,t)
    signed_only=True
    act=permitted(c,r,raw,nonce,t)
    summary['decisions']+=1
    summary['signed_only_unsafe']+=int(signed_only and truth>.025)
    summary['intake_unsafe']+=int(act and truth>.025)
    summary['intake_safe']+=int(act and truth<=.025)
 assert summary==dict(cases=240,decisions=4800,signed_only_unsafe=1440,
   intake_unsafe=0,intake_safe=3360,physical_ACT=0),summary
 print(json.dumps(dict(bound='AETHER-146',status='SYNTHETIC_ONLY',**summary),indent=2))
if __name__=='__main__':main()
