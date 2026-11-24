#!/usr/bin/env python3
"""AETHER-149 standalone synthetic same-path reproducibility demonstration.
The complete locally executed 3840-check script is in the evidence ZIP.
No actual calibration challenge or physical path was observed.
"""
import hashlib,hmac,json
SC=('clean','valid_rotation','probe_bypass','route_swap','probe_replay','time_gap','missing_probe','false_path')
K1=b'DUT-149-SIM';K2=b'BENCH-149-SIM'
def b(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sign(x,key):return dict(x,mac=hmac.new(key,b(x),hashlib.sha256).hexdigest())
def ok(x,key):
 return bool(x) and hmac.compare_digest(x.get('mac',''),hmac.new(key,b({k:v for k,v in x.items() if k!='mac'}),hashlib.sha256).hexdigest())
def fixture(seed,scenario,t):
 fault=scenario not in SC[:2] and 6<=t<14
 risk=.045 if fault else .005;generation=2 if scenario=='valid_rotation' and t>=10 else 1
 nonce=hashlib.sha256(b([seed,scenario,t])).hexdigest()[:24]
 common=dict(device='DUT-A',generation=generation,tick=t,counter=t,nonce=nonce,path='INGRESS-A')
 d=sign(dict(common,reported=.005),K1)
 p=dict(common,pulse=.012,observed=.012,completed=t*1000+120,source='SIM-BENCH')
 o=dict(common,risk=risk,acquired=t*1000+145)
 if fault:
  if scenario=='probe_bypass':p['observed']=0
  if scenario=='route_swap':o['path']='BYPASS-B'
  if scenario=='probe_replay':p['counter']=t-1
  if scenario=='time_gap':o['acquired']=t*1000+450
  if scenario=='missing_probe':p=None
  if scenario=='false_path':p['path']='DECLARED-PATH'
 return risk,d,sign(p,K2) if p else None,sign(o,K2)
def gate(d,p,o,t):
 if not (ok(d,K1) and ok(p,K2) and ok(o,K2)):return False
 if not all(d[k]==p[k]==o[k] for k in ('device','generation','tick','counter','nonce','path')):return False
 if d['tick']!=t or d['path']!='INGRESS-A' or p['source']!='SIM-BENCH':return False
 if abs(p['observed']-p['pulse'])>.0001 or not 0<o['acquired']-p['completed']<=50:return False
 return o['risk']+.0005<=.025
def main():
 signed=unsafe=safe=0
 for sc in SC:
  for seed in range(149001,149031):
   for t in range(20):
    truth,d,p,o=fixture(seed,sc,t);allowed=gate(d,p,o,t)
    signed+=int(truth>.025)
    unsafe+=int(allowed and truth>.025)
    safe+=int(allowed and truth<=.025)
 assert (signed,unsafe,safe)==(1440,0,3360)
 print(json.dumps(dict(bound='AETHER-149',status='SYNTHETIC PASS',
  signed_only_unsafe=signed,same_path_unsafe=unsafe,safe_dry_run=safe,
  operational_act=0,physical_qualification_percent=0),indent=2))
if __name__=='__main__':main()
