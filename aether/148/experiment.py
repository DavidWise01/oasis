#!/usr/bin/env python3
"""AETHER-148: standalone synthetic coverage-contract demonstration.
Full 3840-check locally executed experiment is in the evidence ZIP.
Mock held-out samples are generated from known truth, NOT hardware data.
"""
import hashlib,hmac,json,math
SC=('clean','valid_rotation','missing_heldout','false_coverage_claim','shared_root',
    'underreported_uncertainty','stale_calibration','threshold_crossing')
ROOT=b'AETHER148-MOCK-REFERENCE'
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sign(x):return dict(x,mac=hmac.new(ROOT,canon(x),hashlib.sha256).hexdigest())
def verified(x):return hmac.compare_digest(x.get('mac',''),hmac.new(ROOT,canon({k:v for k,v in x.items() if k!='mac'}),hashlib.sha256).hexdigest())
def wilson_lower(success,n,z=1.6448536269514722):
 p=success/n;return (p+z*z/(2*n)-z*math.sqrt((p*(1-p)+z*z/(4*n))/n))/(1+z*z/n)
def event(seed,sc,t):
 faulty=sc not in SC[:2] and 6<=t<14
 risk=.045 if faulty else .005
 samples=[round(risk+((k*31+seed*7)%37-18)/18000,9) for k in range(120)]
 cert=dict(issuer='REFERENCE-SYNTHETIC',source='EXTERNAL-SYNTHETIC',
  tick=t,counter=t,expires=t+1,risk=risk,width=.002,
  method='heldout_wilson_90pct',coverage=.95,shared_ancestry=False,
  heldout=samples)
 if faulty:
  if sc=='missing_heldout':del cert['heldout']
  if sc=='false_coverage_claim':cert['coverage']=.9999
  if sc=='shared_root':cert['shared_ancestry']=True
  if sc=='underreported_uncertainty':cert['width']=.0001
  if sc=='stale_calibration':cert['expires']=t
  if sc=='threshold_crossing':cert['risk']=.024
 return risk,sign(cert)
def gate(c,t):
 if not verified(c) or c['issuer']!='REFERENCE-SYNTHETIC' or c['source']!='EXTERNAL-SYNTHETIC':return False
 if c['tick']!=t or c['counter']!=t or c['expires']!=t+1:return False
 if c['shared_ancestry'] or c['coverage']!=.95 or c['method']!='heldout_wilson_90pct':return False
 if not .002<=c['width']<=.004 or 'heldout' not in c or len(c['heldout'])!=120:return False
 coverage=sum(abs(x-c['risk'])<=c['width'] for x in c['heldout'])
 return wilson_lower(coverage,120)>=.95 and c['risk']+c['width']<=.025
def main():
 baseline=unsafe=safe=0
 for sc in SC:
  for seed in range(148001,148031):
   for t in range(20):
    truth,cert=event(seed,sc,t);approved=gate(cert,t)
    baseline+=int(truth>.025)
    unsafe+=int(approved and truth>.025)
    safe+=int(approved and truth<=.025)
 assert (baseline,unsafe,safe)==(1440,0,3360),(baseline,unsafe,safe)
 print(json.dumps(dict(bound='AETHER-148',result='SYNTHETIC PASS',
  baseline_unsafe=baseline,coverage_gate_unsafe=unsafe,coverage_gate_safe=safe,
  operational_ACT=0,physical_qualification='NOT PERFORMED'),indent=2))
if __name__=='__main__':main()
