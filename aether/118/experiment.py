#!/usr/bin/env python3
"""AETHER-118: risk packet delivery freshness, single deterministic verifier.
Synthetic HMAC signer, trustworthy protected counter, independent Bernoulli audit.
No witness/quorum/Byzantine agreement. Uses only current received evidence.
"""
import csv,hashlib,hmac,json
from pathlib import Path
import numpy as np
from scipy.stats import beta
ROOT=Path(__file__).resolve().parent
SCENARIOS=('clean','delayed','missing','replayed','counter_mismatch','stale_signed','duplicate_id','outage_recovery')
SEEDS=range(118001,118051)
T=36;N=560;LIMIT=.025;KEY=b'aether118-synthetic-risk-key';MAX_CACHE_AGE=8
def sign(d):
 s=json.dumps(d,sort_keys=True,separators=(',',':')).encode()
 return dict(d,mac=hmac.new(KEY,s,hashlib.sha256).hexdigest())
def verify(d):
 tag=d.get('mac','');b={k:v for k,v in d.items() if k!='mac'}
 return hmac.compare_digest(tag,sign(b)['mac'])
def bound(errors):
 return 1. if errors>=N else float(beta.ppf(.95,errors+1,N-errors))
def episode(seed,scenario):
 rng=np.random.default_rng(seed+SCENARIOS.index(scenario)*100000)
 risk=np.array([.075 if 12<=t<=20 else .003 for t in range(T)])
 original=[]
 for t in range(T):
  original.append(sign(dict(source='risk-audit',seq=t,observed_t=t,counter=t,
   epoch=1,valid_until=t+1,independent=True,n=N,errors=int(rng.binomial(N,risk[t])))))
 deliveries=[]
 for t in range(T):
  p=dict(original[t]);arrival=t
  if scenario=='delayed' and 12<=t<=20:arrival=t+3
  if scenario=='missing' and 12<=t<=20:continue
  if scenario=='replayed' and 12<=t<=20:p=dict(original[11])
  if scenario=='counter_mismatch' and 12<=t<=20:
   p=sign(dict(original[t],counter=t-2,mac=''))
   p=sign({k:v for k,v in p.items() if k!='mac'})
  if scenario=='stale_signed' and 12<=t<=20:p=dict(original[11])
  if scenario=='duplicate_id' and 12<=t<=20:
   b={k:v for k,v in original[t].items() if k!='mac'};b['seq']=11;p=sign(b)
  if scenario=='outage_recovery' and 12<=t<=16:continue
  deliveries.append((arrival,p))
 return risk,deliveries
def evaluate(seed,scenario,policy):
 risk,delivery=episode(seed,scenario)
 latest=None;last_seq=-1;prev='0'*64;rows=[]
 for t in range(T):
  received=[p for arrival,p in delivery if arrival==t]
  received.sort(key=lambda p:p['seq'])
  fresh_ok=False
  for p in received:
   if policy=='cached':
    if verify(p):latest=p
   else:
    if (verify(p) and p['independent'] is True and p['n']==N and p['source']=='risk-audit'
      and p['epoch']==1 and p['seq']==t and p['seq']>last_seq
      and p['observed_t']==t and p['counter']==t and t<p['valid_until']
      and p['valid_until']<=p['observed_t']+1):
      latest=p;last_seq=p['seq'];fresh_ok=True
  if policy=='cached':
   eligible=bool(latest is not None and 0<=t-latest['observed_t']<=MAX_CACHE_AGE and verify(latest))
  else:eligible=fresh_ok
  action='ACT' if eligible and bound(latest['errors'])<=LIMIT else 'HOLD'
  wrong=int(action=='ACT' and risk[t]>.025)
  safeact=int(action=='ACT' and risk[t]<=.025)
  safehold=int(action=='HOLD' and risk[t]<=.025)
  cost=round((10*N*risk[t] if action=='ACT' else .05*N)+(.01*N if received else 0),2)
  record=dict(seed=seed,scenario=scenario,tick=t,policy=policy,receipts=len(received),
   accepted=int(eligible),packet_seq=latest['seq'] if eligible else -1,
   action=action,unsafe=wrong,safe_act=safeact,safe_hold=safehold,cost=cost)
  base=json.dumps(record,sort_keys=True,separators=(',',':'))
  record['previous_hash']=prev
  prev=hashlib.sha256((prev+base).encode()).hexdigest()
  record['hash']=prev;rows.append(record)
 return rows
def verify_chain(rows):
 prev='0'*64
 for row in rows:
  b={k:v for k,v in row.items() if k not in ('previous_hash','hash')}
  if row['previous_hash']!=prev or row['hash']!=hashlib.sha256((prev+json.dumps(b,sort_keys=True,separators=(',',':'))).encode()).hexdigest():return False
  prev=row['hash']
 return True
def save(name,records):
 with (ROOT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
def main():
 seeds=[];checks=[];samples=[]
 for scenario in SCENARIOS:
  for seed in SEEDS:
   for policy in ('cached','strict'):
    rows=evaluate(seed,scenario,policy)
    seeds.append(dict(scenario=scenario,seed=seed,policy=policy,unsafe=sum(x['unsafe'] for x in rows),
     safe_act=sum(x['safe_act'] for x in rows),safe_hold=sum(x['safe_hold'] for x in rows),
     received=sum(x['receipts'] for x in rows),cost=round(sum(x['cost'] for x in rows),2)))
    checks.append(dict(scenario=scenario,seed=seed,policy=policy,
     replay=int(rows==evaluate(seed,scenario,policy)),
     hash_chain=int(verify_chain(rows)),
     one_action=int(all(x['action'] in ('ACT','HOLD') for x in rows)),
     fail_closed=int(all(x['action']=='HOLD' for x in rows if policy=='strict' and not x['accepted'])),
     no_stale_packet=int(all(x['packet_seq']==x['tick'] for x in rows if policy=='strict' and x['accepted']))))
    if seed==min(SEEDS):samples.extend(rows)
 save('seed_results.csv',seeds);save('checks.csv',checks);save('trace_samples.csv',samples)
 summary=[]
 for sc in (*SCENARIOS,'ALL'):
  for policy in ('cached','strict'):
   q=[x for x in seeds if x['policy']==policy and (sc=='ALL' or x['scenario']==sc)]
   summary.append(dict(scenario=sc,policy=policy,cases=len(q),unsafe=sum(x['unsafe'] for x in q),
    safe_act=sum(x['safe_act'] for x in q),safe_hold=sum(x['safe_hold'] for x in q),
    cost=round(sum(x['cost'] for x in q),2)))
 save('results.csv',summary)
 lookup={(x['scenario'],x['policy']):x for x in summary}
 gates=dict(no_unsafe=lookup['ALL','strict']['unsafe']==0,
  fewer_unsafe=lookup['ALL','strict']['unsafe']<lookup['ALL','cached']['unsafe'],
  clean_availability=lookup['clean','strict']['safe_act']==lookup['clean','cached']['safe_act'],
  outage_recovery=lookup['outage_recovery','strict']['safe_act']>=lookup['outage_recovery','cached']['safe_act']-250,
  deterministic=all(all(x[k] for k in ('replay','hash_chain','one_action','fail_closed','no_stale_packet')) for x in checks))
 manifest=dict(bound='AETHER-118',phase='V',status='PASS' if all(gates.values()) else 'FAIL',
  cases=len(SCENARIOS)*len(SEEDS),ticks_per_policy=len(SCENARIOS)*len(SEEDS)*T,
  checks=len(checks)*5,gates=gates,seed_start=min(SEEDS),seed_end=max(SEEDS),
  limitations=['Synthetic pretrusted HMAC signer; signed wrong measurements not detected',
   'Sensor independence and local counter integrity assumed',
   'Risk truth is evaluation-only; fixed-time confidence bound not guaranteed under drift'])
 (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(manifest=manifest,results=summary),indent=2))
if __name__=='__main__':main()
