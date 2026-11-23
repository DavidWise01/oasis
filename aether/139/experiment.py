#!/usr/bin/env python3
"""AETHER-139: synthetic independent calibration-reference evidence.

Software fixture, NOT instrument validation. No real reference measurements,
hardware attestation or independent physical standard are present.
Run: python aether/139/experiment.py
"""
from pathlib import Path
import csv, hashlib, hmac, json
D=Path(__file__).resolve().parent
SEEDS=range(139001,139041)
SC=('clean','valid_rotation','shared_calibration_root','forged_reference_chain',
    'expired_calibration','swapped_reference','uncertainty_understated','measurement_unbound')
TICKS=24
LIMIT=.025
TRANSPORT=b'AETHER139-MOCK-TRANSPORT'
REFERENCE=b'AETHER139-MOCK-REFERENCE-ROOT'
UNTRUSTED=b'AETHER139-UNTRUSTED-ROOT'
def encoded(a):return json.dumps(a,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def mac(key,a):return hmac.new(key,encoded(a),hashlib.sha256).hexdigest()
def sign(key,a):return dict(a,mac=mac(key,a))
def verify(key,a):
 if not isinstance(a,dict):return False
 m=a.get('mac','')
 return isinstance(m,str) and hmac.compare_digest(m,mac(key,{k:v for k,v in a.items() if k!='mac'}))
def nonce(seed,sc,t):return hashlib.sha256(encoded([seed,sc,t])).hexdigest()[:24]
def evidence(seed,sc,t):
 defective=sc not in ('clean','valid_rotation') and 8<=t<16
 truth=.045 if defective else .005
 epoch=2 if sc=='valid_rotation' and t>=12 else 1
 n=nonce(seed,sc,t)
 packet=sign(TRANSPORT,dict(device='DUT-A',generation=epoch,tick=t,counter=t,
     ingress='PATH-A',nonce=n,measured_risk=.005,calibration_session='S-139'))
 refvalue=truth
 rid='REF-139-1'
 root='EXTERNAL-REFERENCE-ROOT'
 uncertainty=.0004
 cert=sign(REFERENCE,dict(reference_device=rid,reference_root=root,
     reference_generation=epoch,valid_from=t,valid_until=t+1,
     uncertainty=uncertainty,measured_value=refvalue,
     calibration_session='S-139',dut='DUT-A',dut_generation=epoch,
     acquisition_tick=t,nonce=n,ingress='PATH-A',source_root='NATIONAL-TRACEABILITY-ASSUMED',
     serial='LAB-139',continuity_counter=t))
 if defective:
  x={k:v for k,v in cert.items() if k!='mac'}
  if sc=='shared_calibration_root':x['source_root']='DUT-A-OWNED-CALIBRATION'
  if sc=='forged_reference_chain':cert=sign(UNTRUSTED,x)
  if sc=='expired_calibration':x['valid_until']=t
  if sc=='swapped_reference':x['reference_device']='OTHER-REFERENCE'
  if sc=='uncertainty_understated':x['uncertainty']=-.00001
  if sc=='measurement_unbound':x['nonce']='CHALLENGE-NOT-OBSERVED'
  if sc!='forged_reference_chain':cert=sign(REFERENCE,x)
 return truth,packet,cert
def contract(p,c,t):
 if not verify(TRANSPORT,p):return False,'invalid_transport'
 if not verify(REFERENCE,c):return False,'reference_signature_invalid'
 for key,other in [('dut','device'),('dut_generation','generation'),('acquisition_tick','tick'),
                   ('nonce','nonce'),('ingress','ingress'),('calibration_session','calibration_session'),
                   ('continuity_counter','counter')]:
  if c[key]!=p[other]:return False,'acquisition_binding'
 if p['tick']!=t or p['counter']!=t:return False,'wrong_tick'
 if c['valid_from']!=t or c['valid_until']!=t+1:return False,'expired_or_future'
 if c['reference_device']!='REF-139-1' or c['reference_root']!='EXTERNAL-REFERENCE-ROOT':
  return False,'unrecognized_reference'
 if c['source_root']!='NATIONAL-TRACEABILITY-ASSUMED':return False,'shared_or_unknown_origin'
 if c['serial']!='LAB-139' or c['reference_generation']!=p['generation']:
  return False,'calibration_ancestry'
 if not isinstance(c['uncertainty'],(int,float)) or not .0003<=c['uncertainty']<=.001:
  return False,'uncertainty_not_certified'
 if not 0<=c['measured_value']<=1:return False,'measured_value_out_of_range'
 return True,'mock_chain_bound'
def episode(seed,sc,policy):
 out=[];prev='0'*64
 for t in range(TICKS):
  truth,p,c=evidence(seed,sc,t);good,why=contract(p,c,t)
  if policy=='transport_only':
   act=verify(TRANSPORT,p) and p['measured_risk']<=LIMIT
  else:
   act=good and c['measured_value']+c['uncertainty']<=LIMIT
  row=dict(scenario=sc,seed=seed,policy=policy,tick=t,
    action='ACT' if act else 'HOLD',unsafe=int(act and truth>LIMIT),
    safe_act=int(act and truth<=LIMIT),safe_hold=int(not act and truth<=LIMIT),
    reference_contract=int(good),reason=why,operational_action='HOLD')
  digest=hashlib.sha256(prev.encode()+encoded(row)).hexdigest()
  row['prev_hash']=prev;row['hash']=digest;prev=digest;out.append(row)
 return out
def chain(rows):
 prev='0'*64
 for r in rows:
  bare={k:v for k,v in r.items() if k not in ('prev_hash','hash')}
  digest=hashlib.sha256(prev.encode()+encoded(bare)).hexdigest()
  if r['prev_hash']!=prev or r['hash']!=digest:return False
  prev=digest
 return True
def save(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 seeds=[];checks=[];samples=[]
 for sc in SC:
  for seed in SEEDS:
   for pol in ('transport_only','reference_contract'):
    a=episode(seed,sc,pol);b=episode(seed,sc,pol)
    tests=dict(replay=a==b,chain=chain(a),one_action=len(a)==TICKS,
       counter_order=all(r['tick']==i for i,r in enumerate(a)),
       zero_unsafe=pol!='reference_contract' or all(r['unsafe']==0 for r in a),
       fail_closed=pol!='reference_contract' or all(r['action']=='HOLD' for r in a if not r['reference_contract']),
       clean_availability=sc not in ('clean','valid_rotation') or all(r['safe_act']==1 for r in a),
       physical_hold=all(r['operational_action']=='HOLD' for r in a))
    checks.extend(dict(scenario=sc,seed=seed,policy=pol,gate=k,passed=int(v)) for k,v in tests.items())
    seeds.append(dict(scenario=sc,seed=seed,policy=pol,
      unsafe=sum(r['unsafe'] for r in a),safe_act=sum(r['safe_act'] for r in a),
      safe_hold=sum(r['safe_hold'] for r in a),contract_pass=sum(r['reference_contract'] for r in a)))
    if seed==SEEDS.start:samples+=a
 save('checks.csv',checks);save('seed_results.csv',seeds);save('trace_samples.csv',samples)
 totals=[]
 for sc in (*SC,'ALL'):
  for pol in ('transport_only','reference_contract'):
   z=[r for r in seeds if r['policy']==pol and (sc=='ALL' or sc==r['scenario'])]
   totals.append(dict(scenario=sc,policy=pol,cases=len(z),
      unsafe=sum(r['unsafe'] for r in z),safe_act=sum(r['safe_act'] for r in z),
      safe_hold=sum(r['safe_hold'] for r in z),contract_pass=sum(r['contract_pass'] for r in z),
      operational_ACT=0))
 save('results.csv',totals)
 z={(r['scenario'],r['policy']):r for r in totals}
 gates=dict(all_checks=all(x['passed'] for x in checks),
  baseline_counterexample=z['ALL','transport_only']['unsafe']>0,
  zero_unsafe=z['ALL','reference_contract']['unsafe']==0,
  clean_available=z['clean','reference_contract']['safe_act']==40*TICKS,
  rotation_available=z['valid_rotation','reference_contract']['safe_act']==40*TICKS,
  no_operational_ACT=all(r['operational_ACT']==0 for r in totals),
  untrusted_ancestry_denied=all(z[s,'reference_contract']['unsafe']==0 for s in SC[2:]))
 manifest=dict(bound='AETHER-139',phase='VIII',status='PASS' if all(gates.values()) else 'FAIL',
  seeds=[SEEDS.start,SEEDS.stop-1],scenarios=list(SC),episodes_per_policy=320,
  decisions_per_policy=320*TICKS,checks=len(checks),gates=gates,
  empirical_physical_validation_percent=0,
  assumptions=['Mock HMAC signing keys not hardware roots',
  'Reference value derived from known synthetic ground truth',
  'Source root and national traceability only declared strings',
  'No real instrument connected; all operational actions HOLD'])
 (D/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(manifest=manifest,aggregate=[r for r in totals if r['scenario']=='ALL']),indent=2))
 if manifest['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
