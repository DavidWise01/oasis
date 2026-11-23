#!/usr/bin/env python3
"""AETHER-125: independent synthetic replacement recovery verifier.

A signed OLD calibration cannot authorize a NEW instrument. Assumes trusted
instrument identity, signing, monotonic acquisition epochs and probe truth.
"""
import csv,hashlib,hmac,json
from pathlib import Path
import numpy as np
from scipy.stats import beta
D=Path(__file__).resolve().parent
T=32;SWAP=12;N=560;LIM=.025;KEY=b'aether-125-synthetic-signer'
PILOTS=(32.,96.,160.,224.)
CASES=('clean_replacement','stale_certificate','device_id_reuse','counter_reset',
       'uncalibrated_new','noisy_replacement','delayed_attestation','mixed_faults')
SEEDS=range(125001,125041)
def mac(b):return hmac.new(KEY,json.dumps(b,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest()
def sign(b):return dict(b,mac=mac(b))
def auth(p):return hmac.compare_digest(p.get('mac',''),mac({k:v for k,v in p.items() if k!='mac'}))
def bound(e):return 1. if e>=N else float(beta.ppf(.95,e+1,N-e))
def risk(s,t):return .08 if SWAP<=t<19 and s!='clean_replacement' else .003
def evidence(seed,s):
 rng=np.random.default_rng(seed+100003*CASES.index(s))
 old=sign(dict(kind='calibration',device='A',generation=1,epoch=1,created=0,valid_from=0,
  valid_until=SWAP,noise_bound=0.,probes=list(PILOTS),cal_nonce='A:1:0',acquisition_epoch=1))
 new=sign(dict(kind='calibration',device='B',generation=2,epoch=1,created=SWAP,valid_from=SWAP+2,
  valid_until=T,noise_bound=4. if s=='noisy_replacement' else 0.,probes=list(PILOTS),
  cal_nonce='B:2:12',acquisition_epoch=2))
 packets=[]
 for t in range(T):
  q=risk(s,t);k=int(rng.binomial(N,q));after=t>=SWAP
  eps=4. if after and s=='noisy_replacement' else 0.
  fake=after and t<19 and s in ('stale_certificate','uncalibrated_new','mixed_faults','device_id_reuse')
  measured=0 if fake else k+(float(rng.uniform(-eps,eps)) if eps else 0.)
  probes=[p+float(rng.uniform(-eps,eps)) if eps else p for p in PILOTS]
  p=dict(kind='risk',device='B' if after else 'A',generation=2 if after else 1,
   epoch=1,acquisition_epoch=2 if after else 1,seq=t,observed_t=t,
   counter=t-SWAP if after else t,measured=round(measured,8),n=N,independent=True,
   probes=[round(float(x),8) for x in probes],
   cal_nonce='B:2:12' if after else 'A:1:0',noise_bound=eps,noise_certified=True)
  if after and t<19 and s in ('stale_certificate','mixed_faults'):p['cal_nonce']='A:1:0'
  if after and t<19 and s=='device_id_reuse':
   p.update(device='A',generation=1,acquisition_epoch=1,cal_nonce='A:1:0',counter=t)
  if after and t<19 and s=='counter_reset':p['counter']=t
  if after and t<19 and s in ('uncalibrated_new','mixed_faults'):p['noise_certified']=False
  packets.append(sign(p))
 return packets,(old,new)
def authority(s,t):
 if t<SWAP:return 0
 if t<19 and s in ('stale_certificate','device_id_reuse','counter_reset','uncalibrated_new','mixed_faults'):return None
 if t<18 and s=='delayed_attestation':return None
 return 1
def packet_ok(p,c,t):
 return bool(c and auth(p) and auth(c) and p.get('kind')=='risk' and c['kind']=='calibration'
  and p.get('device')==c['device'] and p.get('generation')==c['generation']
  and p.get('acquisition_epoch')==c['acquisition_epoch']
  and p.get('cal_nonce')==c['cal_nonce'] and p.get('seq')==t and p.get('observed_t')==t
  and p.get('independent') is True and p.get('n')==N
  and p.get('counter')==(t-SWAP if t>=SWAP else t)
  and c['valid_from']<=t<c['valid_until']
  and p['noise_certified'] is True and p['noise_bound']==c['noise_bound']
  and len(p['probes'])==4
  and all(abs(y-x)<=c['noise_bound']+1e-6 for x,y in zip(PILOTS,p['probes'])))
def iterate(seed,s,policy):
 packets,certs=evidence(seed,s);rows=[];last_ok=False;h='0'*64
 for t,p in enumerate(packets):
  cid=authority(s,t);c=certs[cid] if cid is not None else None
  current=packet_ok(p,c,t)
  if policy=='guarded':
   permitted=current and (t<SWAP or (t>SWAP and last_ok))
   e=max(0,min(N,p['measured']+p['noise_bound']))
  else:
   permitted=auth(p) and p['kind']=='risk';e=max(0,min(N,p['measured']))
  action='ACT' if permitted and bound(int(np.ceil(e)))<=LIM else 'HOLD'
  last_ok=current
  q=risk(s,t)
  row=dict(scenario=s,seed=seed,policy=policy,tick=t,device=p['device'],
    generation=p['generation'],authority=cid,packet_quality=int(current),
    permitted=int(permitted),action=action,ground_risk=q,
    unsafe=int(action=='ACT' and q>LIM),safe_act=int(action=='ACT' and q<=LIM),
    safe_hold=int(action=='HOLD' and q<=LIM),
    cost=round((10*N*q if action=='ACT' else .05*N)+
      (.01*4*224 if policy=='guarded' else 0),3))
  raw=json.dumps(row,sort_keys=True,separators=(',',':'))
  row['prev_hash']=h;h=hashlib.sha256((h+raw).encode()).hexdigest();row['hash']=h;rows.append(row)
 return rows
def chain(a):
 h='0'*64
 for r in a:
  data={k:v for k,v in r.items() if k not in ('prev_hash','hash')}
  hh=hashlib.sha256((h+json.dumps(data,sort_keys=True,separators=(',',':'))).encode()).hexdigest()
  if r['prev_hash']!=h or r['hash']!=hh:return False
  h=hh
 return True
def calibration_only_recovery(seed,s):
 # Separate oracle recomputes authorized quality + risk bound from original packets.
 packets,certs=evidence(seed,s);prev=False
 for t,p in enumerate(packets):
  cid=authority(s,t);current=packet_ok(p,certs[cid] if cid is not None else None,t)
  good=current and (t<SWAP or (t>SWAP and prev))
  if t>=SWAP and risk(s,t)<=LIM and good:
   e=max(0,min(N,p['measured']+p['noise_bound']))
   return t
  prev=current
 return -1
def write(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 per=[];checks=[];sample=[]
 for s in CASES:
  for seed in SEEDS:
   for policy in ('inherited','guarded'):
    a=iterate(seed,s,policy);b=iterate(seed,s,policy)
    ref=calibration_only_recovery(seed,s) if policy=='guarded' else -1
    first_act=min((r['tick'] for r in a if r['tick']>=SWAP and
      r['ground_risk']<=LIM and r['action']=='ACT'),default=-1)
    check=dict(replay=a==b,chain=chain(a),unique=len(a)==T and all(r['action'] in ('ACT','HOLD') for r in a),
      no_unsafe=policy!='guarded' or all(r['unsafe']==0 for r in a),
      reject_unqualified=policy!='guarded' or all(r['action']=='HOLD' for r in a if not r['permitted']),
      no_old_authority=policy!='guarded' or all(r['action']=='HOLD' for r in a if r['tick']>=SWAP and r['authority'] is None),
      first_risk_admissible=policy!='guarded' or first_act==ref)
    checks.append(dict(scenario=s,seed=seed,policy=policy,**{k:int(v) for k,v in check.items()}))
    per.append(dict(scenario=s,seed=seed,policy=policy,unsafe=sum(r['unsafe'] for r in a),
      safe_act=sum(r['safe_act'] for r in a),safe_hold=sum(r['safe_hold'] for r in a),
      cost=round(sum(r['cost'] for r in a),2),
      recovered=int(ref>=0 and first_act==ref) if policy=='guarded' else -1))
    if seed==SEEDS.start:sample.extend(a)
 write('checks.csv',checks);write('seed_results.csv',per);write('trace_samples.csv',sample)
 totals=[]
 for s in (*CASES,'ALL'):
  for pol in ('inherited','guarded'):
   z=[r for r in per if r['policy']==pol and (s=='ALL' or r['scenario']==s)]
   totals.append(dict(scenario=s,policy=pol,cases=len(z),unsafe=sum(r['unsafe'] for r in z),
    safe_act=sum(r['safe_act'] for r in z),safe_hold=sum(r['safe_hold'] for r in z),
    cost=round(sum(r['cost'] for r in z),2),
    recovered=sum(r['recovered']==1 for r in z)))
 write('results.csv',totals)
 at={(r['scenario'],r['policy']):r for r in totals}
 gates=dict(no_unsafe=at['ALL','guarded']['unsafe']==0,
  strict_improvement=at['ALL','inherited']['unsafe']>0,
  clean_recovery=at['clean_replacement','guarded']['recovered']==len(SEEDS),
  all_recovery=all(at[s,'guarded']['recovered']==len(SEEDS) for s in CASES),
  checks=all(all(v==1 for k,v in c.items() if k not in ('scenario','seed','policy')) for c in checks))
 manifest=dict(bound='AETHER-125',phase='VI',status='PASS' if all(gates.values()) else 'FAIL',
  paired_episodes=len(SEEDS)*len(CASES),decisions_per_policy=len(SEEDS)*len(CASES)*T,
  deterministic_checks=len(checks)*7,gates=gates,assumptions=[
  'Trusted signer and device identities; protected epoch and acquisition counter',
  'Synthetic truthful calibration probes and noise bound; no live security proof',
  'Risk admissibility is separate from instrument calibration validity',
  'Per-tick Clopper-Pearson bound does not control familywise false authorization'])
 (D/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(manifest=manifest,results=totals),indent=2))
 if manifest['status']!='PASS':raise SystemExit(2)
if __name__=='__main__':main()
