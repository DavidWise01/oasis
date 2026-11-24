#!/usr/bin/env python3
"""AETHER-154 GitHub standalone certificate-intake reproduction.
Full corrected and original failed local experiments are in evidence ZIP.
All records are mock credentials, never physical qualification.
"""
import hashlib,hmac,json
ROOT=b'AETHER154-TEST-REFERENCE-ROOT';BENCH=b'AETHER154-TEST-INDEPENDENT-BENCH'
SC=('clean','valid_reference_rotation','missing_issuer_identity','issuer_key_mismatch',
 'serial_mismatch','expired_certificate','broken_traceability','tampered_certificate')
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def seal(x,key):return dict(x,mac=hmac.new(key,enc(x),hashlib.sha256).hexdigest())
def verify(x,key):
 return hmac.compare_digest(x.get('mac',''),hmac.new(key,enc({k:v for k,v in x.items() if k!='mac'}),hashlib.sha256).hexdigest())
def specimen(seed,sc,t):
 hazard=sc not in SC[:2] and 6<=t<14
 risk=.045 if hazard else .005
 gen=2 if sc=='valid_reference_rotation' and t>=10 else 1
 nonce=hashlib.sha256(enc([seed,sc,t])).hexdigest()[:24]
 cert=dict(issuer='LAB-ROOT-154',lab='EXTERNAL-LAB-MOCK',parent='MOCK-INDEPENDENT-ROOT',
  serial='REF-154',calibration='CAL-154',generation=gen,from_tick=t,to_tick=t+1,uncertainty=.0005)
 acquisition=dict(serial='REF-154',calibration='CAL-154',generation=gen,tick=t,counter=t,
  nonce=nonce,measured=risk,raw_sha=hashlib.sha256(enc([seed,sc,t,risk])).hexdigest())
 bench=dict(generation=gen,tick=t,nonce=nonce,observed=risk,uncertainty=.0005)
 if hazard:
  if sc=='missing_issuer_identity':cert['issuer']=''
  if sc=='issuer_key_mismatch':cert['issuer']='UNKNOWN'
  if sc=='serial_mismatch':acquisition['serial']='OTHER'
  if sc=='expired_certificate':cert['to_tick']=t
  if sc=='broken_traceability':cert['parent']='DUT-SELF'
  if sc=='tampered_certificate':cert['uncertainty']=.00001
 c=seal(cert,ROOT)
 if hazard and sc=='tampered_certificate':c['uncertainty']=.00002
 return risk,c,seal(acquisition,ROOT),seal(bench,BENCH)
def admit(c,a,b):
 if not (verify(c,ROOT) and verify(a,ROOT) and verify(b,BENCH)):return False
 if c['issuer']!='LAB-ROOT-154' or c['lab']!='EXTERNAL-LAB-MOCK' or c['parent']!='MOCK-INDEPENDENT-ROOT':return False
 if c['serial']!='REF-154' or a['serial']!=c['serial'] or c['calibration']!=a['calibration']:return False
 if c['generation']!=a['generation'] or a['generation']!=b['generation']:return False
 if c['from_tick']!=a['tick'] or c['to_tick']!=a['tick']+1 or a['tick']!=a['counter'] or a['tick']!=b['tick']:return False
 if a['nonce']!=b['nonce'] or not .0004<=c['uncertainty']<=.001:return False
 if abs(a['measured']-b['observed'])>c['uncertainty']+b['uncertainty']:return False
 return max(a['measured']+c['uncertainty'],b['observed']+b['uncertainty'])<=.025
def main():
 signed=unsafe=safe=0
 for sc in SC:
  for seed in range(154001,154026):
   for t in range(20):
    truth,c,a,b=specimen(seed,sc,t)
    permitted=admit(c,a,b)
    signed+=int(truth>.025)
    unsafe+=int(permitted and truth>.025)
    safe+=int(permitted and truth<=.025)
 assert (signed,unsafe,safe)==(1200,0,2800)
 print(json.dumps(dict(bound='AETHER-154',status='SYNTHETIC PASS',
  baseline_unsafe=signed,cert_gate_unsafe=unsafe,cert_gate_safe=safe,
  physical_measurements=0,operational_act=0),indent=2))
if __name__=='__main__':main()
