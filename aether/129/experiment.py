#!/usr/bin/env python3
"""AETHER-129 GitHub-checkout reproducer (synthetic evidence, no real hardware).
The exact locally tested variant and logs are in the local downloadable bundle.
Requires numpy and scipy. This GitHub-compatible version is independently authored.
"""
import csv,hashlib,hmac,json
from pathlib import Path
import numpy as np
from scipy.stats import beta
OUT=Path(__file__).resolve().parent
N,T,LIMIT=560,32,.025
SEEDS=range(129001,129061)
SC=('clean','risk_underreport','reference_missing','reference_stale','reference_wrong_device',
    'reference_expired','reference_bad_signature','reference_uncertainty_unknown','reference_recovery')
RISK_KEY=b'AETHER129-DEMO-risk-signer'
REF_KEY=b'AETHER129-DEMO-reference-signer'
def raw(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def signed(b,key):return dict(b,mac=hmac.new(key,raw(b),hashlib.sha256).hexdigest())
def authentic(p,key):
 if p is None:return False
 b={k:v for k,v in p.items() if k!='mac'}
 return hmac.compare_digest(str(p.get('mac','')),hmac.new(key,raw(b),hashlib.sha256).hexdigest())
def bound(k):return float(beta.ppf(.95,k+1,N-k)) if k<N else 1.
def actual(sc,t):return .085 if sc!='clean' and 10<=t<20 else .003
def packets(seed,sc):
 rng=np.random.default_rng(seed+SC.index(sc)*11939)
 rows=[]
 for t in range(T):
  p=actual(sc,t);k=int(rng.binomial(N,p))
  risk=signed(dict(kind='risk',source='sensor-1',device='S1',generation=1,seq=t,
    observed_tick=t,counter=t,epoch=1,independent=True,n=N,
    errors=0 if sc=='risk_underreport' and 10<=t<20 else k),RISK_KEY)
  ref=signed(dict(kind='physical_reference',device='S1',generation=1,epoch=1,
    seq=t,observed_tick=t,certified_upper_risk=min(1,p+.002),
    uncertainty_bound=.002,standard='SIMULATED_REFERENCE_V1',valid_from=t,
    valid_until=t+1,calibration_serial='synthetic-129',source='reference-1'),REF_KEY)
  if sc=='reference_missing' and 8<=t<24:ref=None
  if sc=='reference_recovery' and 10<=t<17:ref=None
  if ref is not None:
   if sc=='reference_stale' and 10<=t<20:ref=signed(dict({k:v for k,v in ref.items() if k!='mac'},observed_tick=t-3),REF_KEY)
   if sc=='reference_wrong_device' and 10<=t<20:ref=signed(dict({k:v for k,v in ref.items() if k!='mac'},device='OTHER'),REF_KEY)
   if sc=='reference_expired' and 10<=t<20:ref=signed(dict({k:v for k,v in ref.items() if k!='mac'},valid_until=t),REF_KEY)
   if sc=='reference_bad_signature' and 10<=t<20:ref['certified_upper_risk']=0
   if sc=='reference_uncertainty_unknown' and 10<=t<20:ref=signed(dict({k:v for k,v in ref.items() if k!='mac'},uncertainty_bound=None),REF_KEY)
  rows.append((p,risk,ref))
 return rows
def gate(t,r,ref):
 if not authentic(r,RISK_KEY):return False
 if not (r['kind']=='risk' and r['device']=='S1' and r['seq']==t and r['counter']==t
    and r['epoch']==1 and r['observed_tick']==t and r['independent'] is True and r['n']==N):return False
 if not authentic(ref,REF_KEY):return False
 if not(ref['kind']=='physical_reference' and ref['device']==r['device'] and
   ref['generation']==r['generation'] and ref['epoch']==r['epoch'] and
   ref['seq']==t and ref['observed_tick']==t and ref['valid_from']<=t<ref['valid_until'] and
   ref['standard']=='SIMULATED_REFERENCE_V1' and ref['calibration_serial']=='synthetic-129'):return False
 eps=ref['uncertainty_bound']
 if eps is None or not 0<=eps<=.01:return False
 return max(bound(r['errors']),ref['certified_upper_risk'])<=LIMIT
def run(seed,sc,policy):
 out=[];prev='0'*64
 for t,(p,r,ref) in enumerate(packets(seed,sc)):
  yes=gate(t,r,ref) if policy=='reference_bound' else authentic(r,RISK_KEY) and r['seq']==t and bound(r['errors'])<=LIMIT
  action='ACT' if yes else 'HOLD'
  row=dict(seed=seed,scenario=sc,policy=policy,tick=t,actual_risk=p,action=action,
    unsafe=int(yes and p>LIMIT),safe_act=int(yes and p<=LIMIT),
    safe_hold=int(not yes and p<=LIMIT),reference_valid=int(authentic(ref,REF_KEY)))
  h=hashlib.sha256(prev.encode()+raw(row)).hexdigest()
  row['previous_hash']=prev;row['hash']=h;prev=h;out.append(row)
 return out
def save(name,rows):
 with (OUT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 seeds=[];checks=[];traces=[]
 for sc in SC:
  for seed in SEEDS:
   for pol in ('signed_only','reference_bound'):
    a=run(seed,sc,pol);b=run(seed,sc,pol)
    no_unsafe=pol!='reference_bound' or all(not x['unsafe'] for x in a)
    contract=pol!='reference_bound' or all((r['action']=='ACT')==gate(i,packets(seed,sc)[i][1],packets(seed,sc)[i][2]) for i,r in enumerate(a))
    checks.append(dict(scenario=sc,seed=seed,policy=pol,replay=int(a==b),
      unsafe_gate=int(no_unsafe),contract=int(contract)))
    seeds.append(dict(scenario=sc,seed=seed,policy=pol,unsafe=sum(x['unsafe'] for x in a),
      safe_act=sum(x['safe_act'] for x in a),safe_hold=sum(x['safe_hold'] for x in a)))
    if seed==SEEDS.start:traces.extend(a)
 save('github_checks.csv',checks);save('github_seed_results.csv',seeds);save('github_trace_samples.csv',traces)
 totals=[]
 for sc in (*SC,'ALL'):
  for pol in ('signed_only','reference_bound'):
   z=[x for x in seeds if x['policy']==pol and (sc=='ALL' or x['scenario']==sc)]
   totals.append(dict(scenario=sc,policy=pol,cases=len(z),
     unsafe=sum(x['unsafe'] for x in z),safe_act=sum(x['safe_act'] for x in z),
     safe_hold=sum(x['safe_hold'] for x in z)))
 save('github_results.csv',totals)
 print(json.dumps(dict(github_checkout_reproduction=True,summary=totals[-2:]),indent=2))
if __name__=='__main__':main()
