#!/usr/bin/env python3
"""SHEET67: 9 ingress cells / 6 relays / 1 root; sqrt(1.25) homeostasis."""
import json,math,hashlib
from collections import deque,Counter
N=9; REGIONS=6; ROOT=1; BUDGET=36; TICKS=108; TH=math.sqrt(1.25)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def offers(mode):
 out=[]
 for tick in range(TICKS):
  for k in range(32):
   cell=k%9 if mode=='balanced' else (4 if k<24 else (tick*8+k-24)%9)
   amb=k%4
   out.append((tick,f'{tick}:C{cell+1}-A{amb+1}:{k}',cell,amb,digest([tick,cell,amb,k,'EXITRON'])))
 return out
def run(mode,adaptive):
 all_offers=offers(mode);cell=[deque() for _ in range(N)];relay=[deque() for _ in range(REGIONS)];root=deque()
 original={x[1]:x[4] for x in all_offers};delivered=set();tip='0'*64;events=0
 peak=0;wait=[];overloads=0;alloc_history=[];regional_util=Counter();cell_util=Counter()
 for tick in range(4000):
  if tick<TICKS:
   for x in all_offers[tick*32:(tick+1)*32]:cell[x[2]].append(x)
  queues=cell+relay+[root];pending=[len(q) for q in queues]
  target=BUDGET/len(queues)
  weights=[(max(1,len(q)) if len(q)>TH*target else 1) for q in queues] if adaptive else [1]*len(queues)
  raw=[BUDGET*w/sum(weights) for w in weights]
  alloc=[int(x) for x in raw];remaining=BUDGET-sum(alloc)
  for i in sorted(range(len(raw)),key=lambda i:(-(raw[i]-alloc[i]),i))[:remaining]:alloc[i]+=1
  assert sum(alloc)==BUDGET
  alloc_history.append(alloc)
  if any(p>TH*target for p in pending):overloads+=1
  for _ in range(min(alloc[-1],len(root))):
   born,uid,c,a,mark=root.popleft();assert uid not in delivered and mark==original[uid]
   delivered.add(uid);wait.append(tick-born)
   tip=digest([tip,uid,mark,'EARTH','HELL','HEAVEN','EARTH']);events+=1
  for r in range(REGIONS):
   for _ in range(min(alloc[N+r],len(relay[r]))):root.append(relay[r].popleft());regional_util[r]+=1
  for c in range(N):
   for _ in range(min(alloc[c],len(cell[c]))):relay[c%REGIONS].append(cell[c].popleft());cell_util[c]+=1
  peak=max(peak,sum(map(len,queues)))
  if tick>=TICKS-1 and not any(queues):break
 return dict(mode=mode,adaptive=adaptive,offered=len(all_offers),delivered=len(delivered),lost=len(all_offers)-len(delivered),
  peak_backlog=peak,finish_tick=tick,mean_wait=sum(wait)/len(wait),max_wait=max(wait),overload_ticks=overloads,
  budget=BUDGET,homeostasis_sqrt_1_25=TH,ledger_tip=tip,ledger_events=events,
  identity_digest=digest(sorted(delivered)),all_cells_used=len(cell_util)==N,all_regions_used=len(regional_util)==REGIONS,
  allocations_sum_correct=all(sum(x)==BUDGET for x in alloc_history))
def main():
 data={kind:{label:run(kind,label=='adaptive') for label in ('fixed','adaptive')} for kind in ('balanced','hotspot')}
 checks={
 'same_offered':all(v['offered']==3456 for x in data.values() for v in x.values()),
 'all_delivered':all(v['delivered']==3456 for x in data.values() for v in x.values()),
 'no_loss':all(v['lost']==0 for x in data.values() for v in x.values()),
 'identity_preservation':all(x['fixed']['identity_digest']==x['adaptive']['identity_digest'] for x in data.values()),
 'budget_fixed':all(v['allocations_sum_correct'] for x in data.values() for v in x.values()),
 'six_regions_reached':all(v['all_regions_used'] for x in data.values() for v in x.values()),
 'nine_cells_reached':all(v['all_cells_used'] for x in data.values() for v in x.values()),
 'homeostasis_exact':TH==math.sqrt(1.25),
 'adaptive_hotspot_gain':data['hotspot']['adaptive']['finish_tick']<data['hotspot']['fixed']['finish_tick']}
 return dict(schema='oasis/sheet67/adaptive-9-6-1-v01',architecture={'cell':9,'regional':6,'root':1},
  homeostasis={'threshold':'sqrt(1.25)','numeric':TH,'trigger':'queue_depth > threshold * (budget/16)'},
  data=data,checks=checks,passed=sum(checks.values()),total=len(checks),
  limitations=['9/6/1 interpreted as cells/relays/root; user notation may intend another structure.',
  'Homeostatic overload threshold switches the affected node to backlog-weighted allocation.',
  'Budget counts per-hop service operations; not real model attention heads.','SHA-256 ledger is integrity-only and in memory.'])
if __name__=='__main__':
 r=main();print(json.dumps(r,indent=2));assert r['passed']==r['total']
