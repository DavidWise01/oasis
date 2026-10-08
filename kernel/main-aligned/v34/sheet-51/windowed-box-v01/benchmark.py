#!/usr/bin/env python3
"""SHEET 51 ⊞ append-only successor to SHEET 50 #. Deterministic toy benchmark."""
from collections import deque,Counter
import hashlib,json
DIR=('W','N','E','S');RATES=(4,2,1,3);TICKS=720;MOD=2**32
PANE_TO_JUNCTION=(0,0,1,0,0,1,2,2,3)
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def transform(s,seq,lane,node,undo=False):
 a=list(s);i=lane%8;j=(lane+3+node)%8
 if j==i:j=(j+1)%8
 v=1+(seq*7+lane*13+node*17)%65521
 def f(sign):a[8]=(a[8]+sign*(a[i]+v))%MOD
 def g(sign):a[9]=(a[9]+sign*(a[8]+a[j]+node))%MOD
 def h(sign):a[i]=(a[i]+sign*(a[9]+v+node))%MOD
 if undo:h(-1);g(-1);f(-1)
 else:f(1);g(1);h(1)
 return tuple(a)
def case(window,budget,center_limit=None):
 panes=[deque() for _ in range(9)];junctions=[deque() for _ in range(4)]
 center=deque();state=(0,)*10;hist=[];ledger=[];tip='0'*64
 arrived=departed=peak=0;waits=[];pane_use=Counter();junction_use=Counter()
 for tick in range(TICKS+2000):
  if tick<TICKS:
   for d,rate in enumerate(RATES):
    for k in range(rate):
     uid=f'{tick}:{DIR[d]}:{k}';p=(d*2+k+tick)%9
     panes[p].append((tick,uid,d,k,p,sha([uid,'EXITRON'])));arrived+=1
  for p in range(9):
   while panes[p]:
    tok=panes[p].popleft()
    if window:pane_use[p]+=1;n=PANE_TO_JUNCTION[p]
    else:n=(tok[2]+tok[3]+tick)%4
    junctions[n].append(tok)
  limits=[0]*4
  def deliver(tok,n):
   nonlocal state,departed,tip
   born,uid,d,k,p,watermark=tok
   lane=(d*2+k%2)%8;seq=len(hist)
   state=transform(state,seq,lane,n)
   hist.append((seq,lane,n));departed+=1;waits.append(tick-born)
   event=(uid,p,n,lane,watermark,seq)
   h=sha([tip,event]);ledger.append((tip,event,h));tip=h
  for _ in range(budget):
   eligible=[n for n in range(4) if junctions[n] and limits[n]<8]
   if not eligible:break
   n=min(eligible,key=lambda z:(junctions[z][0][0],z))
   limits[n]+=1;junction_use[n]+=1;tok=junctions[n].popleft()
   if window and center_limit is not None and tok[4]==4:center.append((tok,n))
   else:deliver(tok,n)
  if center_limit is not None:
   for _ in range(min(center_limit,len(center))):
    tok,n=center.popleft();deliver(tok,n)
  peak=max(peak,sum(map(len,panes))+sum(map(len,junctions))+len(center))
  if tick>=TICKS-1 and not any(panes) and not any(junctions) and not center:break
 final=sha(state)
 for seq,lane,n in reversed(hist):state=transform(state,seq,lane,n,True)
 valid=all(rec[0]==(ledger[i-1][2] if i else '0'*64) and
   sha([rec[0],rec[1]])==rec[2] and
   rec[1][4]==sha([rec[1][0],'EXITRON']) for i,rec in enumerate(ledger))
 return dict(window=window,capacity=budget,center_limit=center_limit,
  arrivals=arrived,departures=departed,loss=arrived-departed,
  peak_backlog=peak,max_wait=max(waits),mean_wait=sum(waits)/len(waits),
  finish_tick=tick,panes_used=len(pane_use),junctions_used=len(junction_use),
  inverse_exact=state==(0,)*10,provenance_valid=valid,
  unique_tokens=len({r[1][0] for r in ledger})==len(ledger),
  end_hash=final)
def main():
 prior=case(False,8);equal=case(True,8);expanded=case(True,32);center=case(True,32,2)
 all_cases=(prior,equal,expanded,center)
 checks={
  'all_7200':all(c['arrivals']==7200 for c in all_cases),
  'all_delivered':all(c['departures']==7200 for c in all_cases),
  'no_loss':all(c['loss']==0 for c in all_cases),
  'reversible':all(c['inverse_exact'] for c in all_cases),
  'hash_ledger_valid':all(c['provenance_valid'] for c in all_cases),
  'unique_ids':all(c['unique_tokens'] for c in all_cases),
  'nine_panes':equal['panes_used']==9,
  'four_junctions':equal['junctions_used']==4,
  'same_budget':prior['capacity']==equal['capacity']==8,
  'parallel_budget':expanded['capacity']==32,
  'equal_budget_same_finish':equal['finish_tick']==prior['finish_tick'],
  'expanded_faster':expanded['finish_tick']<prior['finish_tick'],
  'center_stage_checked':center['center_limit']==2,
  'center_not_overloaded':center['finish_tick']==expanded['finish_tick']}
 return dict(schema='oasis/sheet51/windowed-box-v01',lineage='SHEET 48 + -> SHEET 50 # -> SHEET 51 ⊞',
  previous=prior,window_equal_budget=equal,window_expanded=expanded,window_center_limited=center,
  checks=checks,passed=sum(checks.values()),total=len(checks),
  limits=['Routing adds 9 panes without increasing service rate','Center-only bottleneck not saturated by this workload','Simulation, not physical Cooper-pair evidence'])
if __name__=='__main__':
 result=main();print(json.dumps(result,indent=2));assert result['passed']==result['total']
