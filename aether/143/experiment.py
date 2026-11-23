#!/usr/bin/env python3
"""AETHER-143 repository-oriented adversarial hardware-readiness experiment.
Synthetic only; signed reference truth and 'external bench' are modeled.
Run python aether/143/experiment.py. Do not treat as physical qualification.
"""
from pathlib import Path
import csv,hashlib,hmac,json
D=Path(__file__).resolve().parent
SC=['clean','valid_rotation','compromised_reference_root','replayed_attestation',
 'tampered_calibration','false_same_path','suppressed_alarm','dual_compromise']
KEYS=dict(dut=b'mock-dut-root',ref=b'mock-reference-root',bench=b'mock-bench-root')
def pack(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def seal(x,key):return dict(x,mac=hmac.new(KEYS[key],pack(x),hashlib.sha256).hexdigest())
def valid(x,key):
 return bool(x) and hmac.compare_digest(x.get('mac',''),
  hmac.new(KEYS[key],pack({k:v for k,v in x.items() if k!='mac'}),hashlib.sha256).hexdigest())
def fixture(seed,scenario,t):
 bad=scenario not in ('clean','valid_rotation') and 8<=t<16
 real=.045 if bad else .005
 gen=2 if scenario=='valid_rotation' and t>=12 else 1
 nonce=hashlib.sha256(pack([seed,scenario,t])).hexdigest()[:20]
 common=dict(generation=gen,tick=t,counter=t,path='MEASURE',nonce=nonce)
 dut=seal(dict(common,id='DUT',reported=.005,alarm=False),'dut')
 r=dict(common,id='REF',estimate=real,uncertainty=.001,expires=t+1)
 bench=seal(dict(common,id='BENCH',observed_truth=real,uncertainty=.001,
  origin='SIMULATED-BENCH'),'bench')
 if bad:
  if scenario in ('compromised_reference_root','suppressed_alarm','dual_compromise'):r['estimate']=.005
  if scenario=='replayed_attestation':r['tick']=t-1
  if scenario=='tampered_calibration':r['uncertainty']=-.001
  if scenario=='false_same_path':r['path']='CALIBRATE'
 return real,dut,seal(r,'ref'),bench
def permit(dut,ref,bench,t):
 if not all((valid(dut,'dut'),valid(ref,'ref'),valid(bench,'bench'))):return False
 if any(not(dut[k]==ref[k]==bench[k]) for k in ('generation','tick','counter','path','nonce')):return False
 if dut['tick']!=t or dut['counter']!=t or ref['expires']!=t+1 or dut['path']!='MEASURE':return False
 if not 0<=ref['uncertainty']<=.002 or bench['uncertainty']>.002:return False
 if abs(ref['estimate']-bench['observed_truth'])>ref['uncertainty']+bench['uncertainty']:return False
 return bench['observed_truth']+bench['uncertainty']<=.025
def episode(seed,sc,policy):
 rows=[];prev='0'*64
 for t in range(24):
  truth,d,r,b=fixture(seed,sc,t)
  ok=permit(d,r,b,t)
  act=(valid(d,'dut') and d['reported']<=.025) if policy=='signed_only' else ok
  rec=dict(scenario=sc,seed=seed,policy=policy,tick=t,action='ACT' if act else 'HOLD',
   safe_act=int(act and truth<=.025),unsafe=int(act and truth>.025),
   safe_hold=int(not act and truth<=.025),reference_ok=int(ok),operational_action='HOLD')
  checksum=hashlib.sha256(prev.encode()+pack(rec)).hexdigest()
  rec['prev_hash']=prev;rec['hash']=checksum;prev=checksum;rows.append(rec)
 return rows
def chain(rows):
 previous='0'*64
 for r in rows:
  bare={k:v for k,v in r.items() if k not in ('prev_hash','hash')}
  chk=hashlib.sha256(previous.encode()+pack(bare)).hexdigest()
  if r['prev_hash']!=previous or r['hash']!=chk:return False
  previous=chk
 return True
def save(name,records):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
def main():
 checks=[];cases=[];traces=[]
 for sc in SC:
  for seed in range(143001,143041):
   for policy in ('signed_only','bench_gated'):
    r=episode(seed,sc,policy)
    tests=dict(replay=r==episode(seed,sc,policy),hash_chain=chain(r),
      one_action=len(r)==24 and all(x['action'] in ('ACT','HOLD') for x in r),
      ordered=all(x['tick']==i for i,x in enumerate(r)),
      no_unsafe=policy!='bench_gated' or not any(x['unsafe'] for x in r),
      fail_closed=policy!='bench_gated' or all(x['action']=='HOLD' for x in r if not x['reference_ok']),
      clean_preserved=sc not in ('clean','valid_rotation') or all(x['safe_act'] for x in r),
      operational_hold=all(x['operational_action']=='HOLD' for x in r))
    checks.extend(dict(scenario=sc,seed=seed,policy=policy,gate=k,passed=int(v)) for k,v in tests.items())
    cases.append(dict(scenario=sc,seed=seed,policy=policy,unsafe=sum(x['unsafe'] for x in r),
      safe_act=sum(x['safe_act'] for x in r),safe_hold=sum(x['safe_hold'] for x in r)))
    if seed==143001:traces+=r
 save('checkout_checks.csv',checks);save('checkout_cases.csv',cases);save('checkout_traces.csv',traces)
 totals=[]
 for sc in (*SC,'ALL'):
  for pol in ('signed_only','bench_gated'):
   z=[r for r in cases if r['policy']==pol and (sc=='ALL' or r['scenario']==sc)]
   totals.append(dict(scenario=sc,policy=pol,cases=len(z),unsafe=sum(r['unsafe'] for r in z),
    safe_act=sum(r['safe_act'] for r in z),safe_hold=sum(r['safe_hold'] for r in z)))
 save('checkout_results.csv',totals)
 allrows={r['policy']:r for r in totals if r['scenario']=='ALL'}
 status='PASS' if all(r['passed'] for r in checks) and allrows['signed_only']['unsafe']==1920 and allrows['bench_gated']['unsafe']==0 else 'FAIL'
 m=dict(bound='AETHER-143',status=status,checks=len(checks),physical_validation=0,
  warning='No real standard, all simulated bench truth is oracle-provided')
 (D/'checkout_manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 print(json.dumps(dict(manifest=m,totals=allrows),indent=2))
 if status!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
