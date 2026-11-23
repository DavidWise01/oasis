#!/usr/bin/env python3
"""AETHER-116: authenticated short leases under faulty local wall time.
Synthetic trust-anchor and monotonic-counter assumptions are explicitly tested.
No true risk or true time enters runtime policy; true time is evaluation-only.
"""
import csv,hashlib,hmac,json
from pathlib import Path
import numpy as np
from scipy.stats import beta
D=Path(__file__).resolve().parent
SCENARIOS=('clean_rotation','backward_jump','forward_jump','slow_drift','expiry_boundary','anchor_outage')
SEEDS=range(116001,116061);T=32;N=560;LEASE=4;ROTATE=12;LIMIT=.025
ROOT=b'aether116-testing-only-root';KEYS={'K0':b'testing-only-k0','K1':b'testing-only-k1'}
def digest(obj,key):return hmac.new(key,json.dumps(obj,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest()
def signed(obj,key):return dict(obj,tag=digest(obj,key))
def authentic(obj,key):
 body={k:v for k,v in obj.items() if k!='tag'}
 return hmac.compare_digest(obj.get('tag',''),digest(body,key))
def make(seed,scenario):
 rng=np.random.default_rng(seed+SCENARIOS.index(scenario)*100000)
 # K0 is retired at true tick 12; K1 is valid thereafter. This truth is never given to the controller.
 risk=np.array([.003 if t<12 or t>=19 else .075 for t in range(T)])
 packets=[];notices=[];anchors=[];clock=[]
 for t in range(T):
  wall=float(t)
  if scenario=='backward_jump' and t>=12:wall=t-7.
  if scenario=='forward_jump' and t>=11:wall=t+8.
  if scenario=='slow_drift':wall=float(t)*.75
  if scenario=='expiry_boundary' and 10<=t<20:wall=float(t-3)
  if scenario=='anchor_outage' and t>=10:wall=t-6.
  clock.append(wall)
  key='K0' if t<12 else 'K1'
  # Adversarial stale key after retirement: correct signature but no valid authority.
  if scenario in ('backward_jump','slow_drift','expiry_boundary','anchor_outage') and 12<=t<19:key='K0'
  err=0 if key=='K0' and t>=12 else int(rng.binomial(N,risk[t]))
  packets.append(signed({'seq':t,'key_id':key,'n':N,'errors':err,'independent':True},KEYS[key]))
  if t%LEASE==0:
   active='K0' if t<ROTATE else 'K1'
   arrival=t
   if scenario in ('backward_jump','expiry_boundary','anchor_outage') and 12<=t<20:arrival=t+7
   if scenario=='slow_drift' and t==12:arrival=t+5
   if scenario=='forward_jump' and t==12:arrival=t+2
   notices.append(dict(signed=signed({'seq':t//LEASE,'issued':t,'expires':t+LEASE,'active':active},ROOT),arrival=arrival))
   if scenario!='anchor_outage' or t<8 or t>=24:
    anchors.append(dict(signed=signed({'counter':t,'authorized_time':t,'max_drift_per_tick':.1},ROOT),arrival=t))
 return risk,packets,notices,anchors,clock

def bound(err):return float(beta.ppf(.95,int(err)+1,N-int(err))) if err<N else 1.
def trial(seed,scenario,policy):
 risk,packets,notices,anchors,wall=make(seed,scenario)
 active=None;expiry=-1;seq=-1;anchor=None;last_counter=-1;seen=set();previous='0'*64;rows=[]
 for counter,p in enumerate(packets):
  for item in sorted((x for x in notices if x['arrival']==counter),key=lambda a:a['signed']['seq']):
   n=item['signed']
   if authentic(n,ROOT) and n['seq']>seq and n['issued']==n['seq']*LEASE and n['expires']==n['issued']+LEASE and n['issued']<=counter:
    seq=n['seq'];active=n['active'];expiry=n['expires']
  for item in (x for x in anchors if x['arrival']==counter):
   a=item['signed']
   if authentic(a,ROOT) and a['counter']==counter and a['counter']>last_counter and a['authorized_time']==counter:
    anchor=a;last_counter=a['counter']
  packet_valid=bool(p['key_id'] in KEYS and authentic(p,KEYS[p['key_id']]) and p['seq']==counter and p['seq'] not in seen and p['independent'] and p['n']==N)
  if packet_valid:seen.add(p['seq'])
  wall_now=wall[counter]
  if policy=='wall':
   # Weak policy trusts wall time for lease and does not require fresh time anchor.
   accepted=bool(packet_valid and p['key_id']==active and wall_now<expiry)
  else:
   # Bound time from last authenticated anchor using a strictly monotonic inspection counter.
   # Any inconsistent wall reading is reported, but does not extend expiry.
   upper=(anchor['authorized_time']+1.1*(counter-anchor['counter'])) if anchor is not None else float('inf')
   # A stale time anchor has no authority if its uncertainty reaches lease expiry.
   accepted=bool(packet_valid and p['key_id']==active and counter>=0 and upper<expiry)
  act=bool(accepted and bound(p['errors'])<=LIMIT)
  # loss assumes N independent outcomes if ACT; evaluator only uses hidden risk here.
  loss=10*N*risk[counter] if act else .05*N
  loss+=.01*N
  row=dict(scenario=scenario,seed=seed,tick=counter,policy=policy,wall_time=round(wall_now,3),active=active or '',schedule_seq=seq,expiry=expiry,
       latest_anchor='' if anchor is None else anchor['counter'],packet_key=p['key_id'],packet_valid=int(packet_valid),accepted=int(accepted),
       act=int(act),unsafe=int(act and risk[counter]>LIMIT),safe_act=int(act and risk[counter]<=LIMIT),safe_hold=int(not act and risk[counter]<=LIMIT),cost=round(loss,3))
  canonical=json.dumps(row,sort_keys=True,separators=(',',':'))
  row['hashprev']=previous;previous=hashlib.sha256((previous+canonical).encode()).hexdigest();row['hash']=previous
  rows.append(row)
 return rows

def save(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def chainok(rows):
 prev='0'*64
 for row in rows:
  r={k:v for k,v in row.items() if k not in ('hash','hashprev')}
  if row['hashprev']!=prev or row['hash']!=hashlib.sha256((prev+json.dumps(r,sort_keys=True,separators=(',',':'))).encode()).hexdigest():return False
  prev=row['hash']
 return True

def main():
 seedrows=[];checks=[];samples=[]
 for sc in SCENARIOS:
  for seed in SEEDS:
   for policy in ('wall','monotonic'):
    rows=trial(seed,sc,policy);copy=trial(seed,sc,policy)
    seedrows.append(dict(scenario=sc,seed=seed,policy=policy,acts=sum(x['act'] for x in rows),unsafe=sum(x['unsafe'] for x in rows),safe_act=sum(x['safe_act'] for x in rows),safe_hold=sum(x['safe_hold'] for x in rows),cost=round(sum(x['cost'] for x in rows),2)))
    checks.append(dict(scenario=sc,seed=seed,policy=policy,replay=int(rows==copy),chain=int(chainok(rows)),one_action=int(all(x['act'] in (0,1) for x in rows)),fail_closed=int(all(not x['act'] for x in rows if not x['accepted']))))
    if seed==min(SEEDS):samples.extend(rows)
 save('seed_results.csv',seedrows);save('checks.csv',checks);save('trace_samples.csv',samples)
 summary=[]
 for sc in (*SCENARIOS,'ALL'):
  for policy in ('wall','monotonic'):
   z=[x for x in seedrows if x['policy']==policy and (sc=='ALL' or x['scenario']==sc)]
   summary.append(dict(scenario=sc,policy=policy,episodes=len(z),unsafe=sum(x['unsafe'] for x in z),safe_act=sum(x['safe_act'] for x in z),safe_hold=sum(x['safe_hold'] for x in z),cost=round(sum(x['cost'] for x in z),2)))
 save('results.csv',summary)
 lookup={(r['scenario'],r['policy']):r for r in summary}
 gates={'deterministic':all(all(c[x] for x in ('replay','chain','one_action','fail_closed')) for c in checks),
        'zero_unsafe':lookup['ALL','monotonic']['unsafe']==0,
        'improves_unsafe':lookup['ALL','monotonic']['unsafe']<lookup['ALL','wall']['unsafe'],
        'clean_rotation_preserved':lookup['clean_rotation','monotonic']['safe_act']==lookup['clean_rotation','wall']['safe_act'],
        'total_cost_nonincreasing':lookup['ALL','monotonic']['cost']<=lookup['ALL','wall']['cost']}
 manifest={'bound':'AETHER-116','phase':'V','status':'PASS' if all(gates.values()) else 'FAIL','seeds':[min(SEEDS),max(SEEDS)],'cases':len(SEEDS)*len(SCENARIOS),'checks':len(checks)*4,'gates':gates,
  'assumptions':['signed time anchor authentic','local monotonic inspection counter cannot roll back','clock drift bounded by 0.1 per tick','HMAC testing keys are uncompromised'],
  'warning':'The verifier cannot detect a malicious or compromised trusted clock anchor. No field guarantee.'}
 (D/'manifest.json').write_text(json.dumps(manifest,indent=2,default=lambda x:x.item())+'\n')
 print(json.dumps({'manifest':manifest,'results':summary},indent=2,default=lambda x:x.item()))
if __name__=='__main__':main()
