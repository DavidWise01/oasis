#!/usr/bin/env python3
"""AETHER-155 GitHub standalone raw-capture and timing gate example.

This independently authored condensed implementation is NOT the exact locally
executed 3200-check experiment included in the downloadable evidence ZIP.
All observations, credentials, clock anchors and raw bytes are simulated.
"""
import hashlib,hmac,json
SC=('clean_capture','valid_clock_rotation','missing_raw_file','modified_raw_bytes',
    'counter_gap','clock_rollback','timestamp_forgery','capture_identity_swap')
KEY=b'AETHER155-SIMULATED-REFERENCE'
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sha(x):return hashlib.sha256(x).hexdigest()
def seal(x):return dict(x,mac=hmac.new(KEY,enc(x),hashlib.sha256).hexdigest())
def valid(x):return hmac.compare_digest(x.get('mac',''),hmac.new(KEY,enc({k:v for k,v in x.items() if k!='mac'}),hashlib.sha256).hexdigest())
def generate(seed,scenario,t):
 adverse=scenario not in SC[:2] and 6<=t<14
 truth=.045 if adverse else .005
 generation=2 if scenario=='valid_clock_rotation' and t>=10 else 1
 nonce=sha(enc([seed,scenario,t]))[:24]
 base=1700000000000+t*1000
 samples=[dict(counter=t*3+i,timestamp_ms=base+10*i,reading=truth) for i in range(3)]
 x=dict(device='REF-155',generation=generation,nonce=nonce,samples=samples)
 original=enc(x)
 certificate=dict(device='REF-155',generation=generation,nonce=nonce,tick=t,counter=t*3,
    first_ms=base,sample_interval_ms=10,sample_count=3,raw_sha=sha(original),
    risk=truth,uncertainty=.0005,valid_until=t+1,issuer='MOCK-REFERENCE-ROOT')
 if adverse:
  if scenario=='missing_raw_file':original=b''
  elif scenario=='modified_raw_bytes':original+=b'\n'
  elif scenario=='counter_gap':
   samples[1]['counter']+=2;original=enc(x);certificate['raw_sha']=sha(original)
  elif scenario=='clock_rollback':
   samples[2]['timestamp_ms']=base-20;original=enc(x);certificate['raw_sha']=sha(original)
  elif scenario=='timestamp_forgery':certificate['first_ms']+=10
  elif scenario=='capture_identity_swap':certificate['device']='OTHER'
 return truth,original,seal(certificate)
def accept(original,receipt):
 if not valid(receipt) or not original or sha(original)!=receipt['raw_sha']:return False
 if receipt['device']!='REF-155' or receipt['issuer']!='MOCK-REFERENCE-ROOT':return False
 if receipt['first_ms']!=1700000000000+receipt['tick']*1000:return False
 if receipt['valid_until']!=receipt['tick']+1 or receipt['sample_interval_ms']!=10:return False
 try:
  obj=json.loads(original);s=obj['samples']
  if enc(obj)!=original:return False
  if obj['device']!=receipt['device'] or obj['generation']!=receipt['generation'] or obj['nonce']!=receipt['nonce']:return False
  if len(s)!=3 or receipt['sample_count']!=3:return False
  if [v['counter'] for v in s]!=[receipt['counter']+i for i in range(3)]:return False
  if [v['timestamp_ms'] for v in s]!=[receipt['first_ms']+i*10 for i in range(3)]:return False
  mean=sum(v['reading'] for v in s)/3
  return abs(mean-receipt['risk'])<=1e-10 and mean+receipt['uncertainty']<=.025
 except (ValueError,KeyError,TypeError):return False
def main():
 baseline=unsafe=safe=0
 for case in SC:
  for seed in range(155001,155026):
   for t in range(20):
    truth,original,receipt=generate(seed,case,t)
    approved=accept(original,receipt)
    baseline+=int(truth>.025);unsafe+=int(approved and truth>.025);safe+=int(approved and truth<=.025)
 assert (baseline,unsafe,safe)==(1200,0,2800),(baseline,unsafe,safe)
 print(json.dumps(dict(bound='AETHER-155',mode='SYNTHETIC',signed_only_unsafe=baseline,
    guarded_unsafe=unsafe,guarded_safe=safe,operational_act=0,physical_samples=0),indent=2))
if __name__=='__main__':main()
