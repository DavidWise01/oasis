#!/usr/bin/env python3
"""AETHER-167 compact GitHub demo. Exact executed 3200-check source is in
AETHER-167 local evidence ZIP (SHA-256:
60401569f875a87de629b7233155288e3f0c1fdbad74a33b5f63d314d5a41b17).
This is not byte-identical to the executed local program, and does not
authenticate independent physical witnesses.
"""
import json,hashlib,hmac
CASES=('clean_mock','legitimate_rotation','shared_ancestry','duplicate_witness',
       'self_issued_root','contradictory_capture','missing_independent_root','replayed_provenance')
KEYS={'dut':b'SIM167-DUT','ref':b'SIM167-REF','bench':b'SIM167-BENCH'}
ROOTS={'dut':'SIM-DUT-ANCESTRY','ref':'SIM-REFERENCE-ANCESTRY','bench':'SIM-BENCH-ANCESTRY'}
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def sign(x,k):return dict(x,mac=hmac.new(KEYS[k],enc(x),hashlib.sha256).hexdigest())
def valid(x,k):return hmac.compare_digest(x.get('mac',''),hmac.new(KEYS[k],enc({a:b for a,b in x.items() if a!='mac'}),hashlib.sha256).hexdigest())
def fixture(seed,scenario,t):
 bad=scenario not in CASES[:2] and 6<=t<14
 truth=.045 if bad else .005;gen=2 if scenario=='legitimate_rotation' and t>=10 else 1
 nonce=sha(enc([seed,scenario,t]))[:24]
 cap=sha(enc([seed,scenario,t,truth]))
 d={role:dict(role=role,ancestor=ROOTS[role],issuer='SIM-'+role.upper()+'-ISSUER',
 serial='SIM-'+role.upper()+'-167',tick=t,generation=gen,nonce=nonce,
 capture_sha=cap,reading=truth,uncertainty=.0005,expires=t+1) for role in KEYS}
 if bad:
  if scenario=='shared_ancestry':d['bench']['ancestor']=ROOTS['ref']
  elif scenario=='duplicate_witness':d['bench']=dict(d['ref'])
  elif scenario=='self_issued_root':d['ref']['issuer']=d['dut']['issuer']
  elif scenario=='contradictory_capture':d['bench']['reading']=.005
  elif scenario=='missing_independent_root':d['ref']['ancestor']=''
  elif scenario=='replayed_provenance':d['bench']['nonce']='REPLAYED'
 return truth,{k:sign(d[k],k) for k in KEYS}
def admit(d):
 if set(d)!=set(KEYS) or not all(valid(d[k],k) for k in KEYS):return False
 if any(d[k]['role']!=k or d[k]['serial']!='SIM-'+k.upper()+'-167' for k in KEYS):return False
 if any(d[k]['ancestor']!=ROOTS[k] or d[k]['issuer']!='SIM-'+k.upper()+'-ISSUER' for k in KEYS):return False
 if any(len({d[k][field] for k in KEYS})!=1 for field in ('tick','generation','nonce','capture_sha')):return False
 if any(d[k]['expires']!=d[k]['tick']+1 or d[k]['uncertainty']!=.0005 for k in KEYS):return False
 values=[d[k]['reading'] for k in KEYS]
 return max(values)-min(values)<=.001 and max(values)+.0005<=.025
def main():
 baseline=gated_bad=gated_safe=0
 for case in CASES:
  for seed in range(167001,167026):
   for t in range(20):
    truth,evidence=fixture(seed,case,t)
    action=admit(evidence)
    baseline+=int(truth>.025)
    gated_bad+=int(action and truth>.025)
    gated_safe+=int(action and truth<=.025)
 assert (baseline,gated_bad,gated_safe)==(1200,0,2800)
 print(json.dumps(dict(bound='AETHER-167',mode='SYNTHETIC',signed_only_unsafe=baseline,
  gated_unsafe=gated_bad,gated_safe=gated_safe,
  physical_qualification_percent=0,operational_act='HOLD'),indent=2))
if __name__=='__main__':main()
