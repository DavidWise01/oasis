#!/usr/bin/env python3
"""AETHER-117B: separate signed time and fresh risk authority.
Assumes trusted HMAC root and tamper-resistant local counter/epoch state.
"""
import csv,hashlib,hmac,json
from pathlib import Path
import numpy as np
from scipy.stats import beta
D=Path(__file__).resolve().parent
SCENARIOS=('clean','stale_anchor','counter_rollback','verified_restart','unverified_restart','anchor_replay','delayed_anchor')
SEEDS=range(117001,117041);T=36;N=560;LEASE=5;MAX_AGE=4;LIMIT=.025
ROOT=b'aether117-synthetic-only-root';PK=b'aether117-synthetic-only-packet';RISK_KEY=b'aether117b-risk-audit-synthetic'
def sig(o,k):return hmac.new(k,json.dumps(o,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest()
def sign(o,k):return dict(o,tag=sig(o,k))
def auth(o,k):return hmac.compare_digest(o.get('tag',''),sig({a:b for a,b in o.items() if a!='tag'},k))
def cp_upper(e):return 1. if e>=N else float(beta.ppf(.95,e+1,N-e))
def episode(seed,scenario):
 rng=np.random.default_rng(seed+SCENARIOS.index(scenario)*10000)
 packets=[];anchors=[];ticks=[];risk_audits=[]
 for t in range(T):
  risk=.003 if scenario=='clean' or t<15 or t>=26 else .085
  hw=t-14 if scenario in ('counter_rollback','verified_restart','unverified_restart') and t>=14 else t
  epoch=1 if scenario in ('verified_restart','unverified_restart') and t>=14 else 0
  errors=0 if 15<=t<26 else int(rng.binomial(N,risk))
  packets.append(sign(dict(counter=hw,epoch=epoch,n=N,errors=errors,independent=True),PK))
  ticks.append(dict(t=t,risk=risk,counter=hw,epoch=epoch))
  # Independently acquired, authenticated current risk evidence. The controller
  # receives errors and metadata only; the simulator's true risk is evaluation-only.
  audit_errors=int(rng.binomial(N,risk))
  risk_audits.append(sign(dict(counter=hw,epoch=epoch,n=N,errors=audit_errors,independent=True,observed_t=t),RISK_KEY))
  if t%LEASE==0:
   if scenario=='stale_anchor' and 15<=t<30:continue
   arrival=t+11 if scenario=='delayed_anchor' and 15<=t<25 else t
   if scenario=='anchor_replay' and 15<=t<30:continue
   if scenario=='unverified_restart' and 15<=t<30:continue
   bridge=scenario=='verified_restart' and t==30
   a=sign(dict(seq=t//LEASE,issued=t,epoch=epoch,counter=hw,expiry=t+LEASE,
    bridge=bridge,previous_epoch=0 if bridge else -1,previous_final_counter=13 if bridge else -1),ROOT)
   anchors.append(dict(arrival=arrival,data=a))
  if scenario=='anchor_replay' and t==17:
   anchors.append(dict(arrival=17,data=anchors[0]['data']))
 return ticks,packets,anchors,risk_audits
def trial(seed,scenario,policy):
 ticks,packets,anchors,risk_audits=episode(seed,scenario)
 current=None;last_seq=-1;last_counter=-1;epoch=0;closed=False
 previous='0'*64;rows=[];recovered=False
 for t,(info,p) in enumerate(zip(ticks,packets)):
  for obj in sorted((x['data'] for x in anchors if x['arrival']==t),key=lambda z:z['seq']):
   if not auth(obj,ROOT):continue
   if policy=='weak':current=obj;last_seq=obj['seq']
   else:
    if obj['seq']<=last_seq or obj['issued']>t or obj['expiry']>obj['issued']+LEASE:continue
    if obj['epoch']!=epoch:
     if not(obj['bridge'] and closed and obj['previous_epoch']==epoch and
      obj['previous_final_counter']==13 and obj['epoch']==epoch+1 and obj['issued']>=26):continue
     epoch=obj['epoch'];last_counter=-1;closed=False
    if obj['counter']!=info['counter'] or obj['issued']!=t:continue
    current=obj;last_seq=obj['seq']
  packet_ok=bool(auth(p,PK) and p['n']==N and p['independent'] and p['counter']==info['counter'])
  if policy in ('strong','fresh'):
   if last_counter>=0 and (p['epoch']!=epoch or p['counter']<=last_counter or p['counter']!=last_counter+1):closed=True
   if p['epoch']!=epoch:closed=True
   lease_ok=bool(current and current['epoch']==epoch and current['issued']<=t and
    t-current['issued']<=MAX_AGE and t<current['expiry'] and not closed)
  else:lease_ok=bool(current and t<current['expiry']+20 and packet_ok)
  accepted=bool(packet_ok and lease_ok)
  # Clock recovery is not action recovery. Require a current separately signed
  # audit obtained after the valid anchor, with the matching epoch/counter.
  fresh=risk_audits[t]
  audit_ok=bool(auth(fresh,RISK_KEY) and fresh['independent'] and fresh['n']==N and
    fresh['counter']==p['counter'] and fresh['epoch']==p['epoch'] and
    fresh['observed_t']==t and current and fresh['observed_t']>=current['issued'])
  if policy=='fresh':
   action='ACT' if accepted and audit_ok and cp_upper(fresh['errors'])<=LIMIT else 'HOLD'
  else:
   action='ACT' if accepted and cp_upper(p['errors'])<=LIMIT else 'HOLD'
  if policy in ('strong','fresh') and p['epoch']==epoch and not closed:last_counter=p['counter']
  unsafe=int(action=='ACT' and info['risk']>LIMIT)
  safe_act=int(action=='ACT' and info['risk']<=LIMIT)
  safe_hold=int(action=='HOLD' and info['risk']<=LIMIT)
  cost=(10*N*info['risk'] if action=='ACT' else .05*N)+.01*N+(.01*N if policy=='fresh' and accepted else 0)
  row=dict(scenario=scenario,seed=seed,tick=t,policy=policy,counter=p['counter'],packet_epoch=p['epoch'],
   anchor_seq=-1 if current is None else current['seq'],anchor_age=-1 if current is None else t-current['issued'],
   closed=int(closed),accepted=int(accepted),risk_audit_ok=int(audit_ok),risk_audit_errors=fresh['errors'] if policy=='fresh' else -1,action=action,unsafe=unsafe,safe_act=safe_act,safe_hold=safe_hold,
   recovery=int(policy in ('strong','fresh') and action=='ACT' and t>=26 and not recovered),cost=round(cost,3))
  if row['recovery']:recovered=True
  canonical=json.dumps(row,sort_keys=True,separators=(',',':'))
  row['prev_hash']=previous;previous=hashlib.sha256((previous+canonical).encode()).hexdigest();row['hash']=previous
  rows.append(row)
 return rows
def save(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def chain_ok(rows):
 p='0'*64
 for x in rows:
  body={k:v for k,v in x.items() if k not in ('hash','prev_hash')}
  if x['prev_hash']!=p or x['hash']!=hashlib.sha256((p+json.dumps(body,sort_keys=True,separators=(',',':'))).encode()).hexdigest():return False
  p=x['hash']
 return True
def main():
 seedrows=[];checks=[];samples=[];recoveries=[]
 for scenario in SCENARIOS:
  for seed in SEEDS:
   for policy in ('weak','strong','fresh'):
    z=trial(seed,scenario,policy)
    seedrows.append(dict(scenario=scenario,seed=seed,policy=policy,unsafe=sum(x['unsafe'] for x in z),
     safe_act=sum(x['safe_act'] for x in z),safe_hold=sum(x['safe_hold'] for x in z),
     recovered=sum(x['recovery'] for x in z),cost=round(sum(x['cost'] for x in z),2)))
    checks.append(dict(scenario=scenario,seed=seed,policy=policy,replay=int(z==trial(seed,scenario,policy)),
     hash=int(chain_ok(z)),one_action=int(all(x['action'] in ('ACT','HOLD') for x in z)),
     fail_closed=int(all(x['action']=='HOLD' for x in z if not x['accepted']))))
    if seed==min(SEEDS):samples.extend(z)
    if policy=='fresh' and scenario=='verified_restart':
     recoveries.append(next((x['tick'] for x in z if x['recovery']),-1))
 save('seed_results.csv',seedrows);save('checks.csv',checks);save('trace_samples.csv',samples)
 summary=[]
 for scenario in (*SCENARIOS,'ALL'):
  for policy in ('weak','strong','fresh'):
   z=[r for r in seedrows if r['policy']==policy and (scenario=='ALL' or r['scenario']==scenario)]
   summary.append(dict(scenario=scenario,policy=policy,episodes=len(z),unsafe=sum(x['unsafe'] for x in z),
    safe_act=sum(x['safe_act'] for x in z),safe_hold=sum(x['safe_hold'] for x in z),
    recovered=sum(x['recovered'] for x in z),cost=round(sum(x['cost'] for x in z),2)))
 save('results.csv',summary)
 ix={(x['scenario'],x['policy']):x for x in summary}
 gates=dict(replay_and_record=all(all(v[k] for k in ('replay','hash','one_action','fail_closed')) for v in checks),
  no_unsafe=ix['ALL','fresh']['unsafe']==0,
  improves_over_weak=ix['ALL','fresh']['unsafe']<ix['ALL','strong']['unsafe'],
  clean_availability=ix['clean','fresh']['safe_act']==ix['clean','strong']['safe_act'],
  verified_recovery=ix['verified_restart','fresh']['recovered']==len(SEEDS),
  unauthorized_restart_closed=ix['unverified_restart','fresh']['unsafe']==0)
 manifest=dict(bound='AETHER-117B',phase='V',status='PASS' if all(gates.values()) else 'FAIL',
  seeds=[min(SEEDS),max(SEEDS)],cases=len(SCENARIOS)*len(SEEDS),checks=len(checks)*4,gates=gates,
  recovery_ticks=sorted(set(recoveries)),limitations=['Synthetic trusted root and bridge','Integrity-protected local epoch/counter assumed','Risk permission requires separately signed current audit; signer independence is assumed, not proven'])
 (D/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(manifest=manifest,results=summary),indent=2))
if __name__=='__main__':main()
