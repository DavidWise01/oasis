#!/usr/bin/env python3
"""SHEET 50 Double Cross #, append-only linear successor to SHEET 48 Cross v03."""
import json,hashlib
from collections import Counter,deque
DIR=('W','N','E','S');RATES={'W':4,'N':2,'E':1,'S':3}
MOD=2**32;START=(0,)*10;TICKS=720
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def op(state,seq,lane,node,undo=False):
 x=list(state);i=lane%8;j=(lane+3+node)%8
 if i==j:j=(j+1)%8
 a=1+(seq*7+lane*13+node*17)%65521
 def f(z):x[8]=(x[8]+z*(x[i]+a))%MOD
 def g(z):x[9]=(x[9]+z*(x[8]+x[j]+node))%MOD
 def h(z):x[i]=(x[i]+z*(x[9]+a+node))%MOD
 if undo:h(-1);g(-1);f(-1)
 else:f(1);g(1);h(1)
 return tuple(x)
def benchmark(nodes,per_node):
 queues=[deque() for _ in range(nodes)];arr=Counter();dep=Counter()
 used=Counter();history=[];ledger=[];tip='0'*64;s=START;peak=0;waits=[]
 for tick in range(TICKS+2000):
  if tick<TICKS:
   for origin in DIR:
    for k in range(RATES[origin]):
     uid=f'{tick}:{origin}:{k}';node=(DIR.index(origin)+k+tick)%nodes
     queues[node].append((tick,uid,origin,k,node,sha({'uid':uid,'word':'EXITRON'})));arr[origin]+=1
  for node in range(nodes):
   for _ in range(per_node):
    if not queues[node]:break
    born,uid,origin,k,n,mark=queues[node].popleft()
    lane=(DIR.index(origin)*2+k%2)%8;seq=len(history)
    s=op(s,seq,lane,node);history.append((seq,lane,node))
    row=(tip,uid,node,lane,mark)
    h=sha({'prev':tip,'uid':uid,'node':node,'lane':lane,'mark':mark})
    ledger.append((row,h));tip=h
    dep[origin]+=1;used[node]+=1;waits.append(tick-born)
  peak=max(peak,sum(map(len,queues.values())))
  if tick>=TICKS-1 and all(not q for q in queues):break
 final=sha(s)
 for seq,lane,node in reversed(history):s=op(s,seq,lane,node,True)
 valid=all(r[0][0]==(ledger[i-1][1] if i else '0'*64) and
  r[1]==sha({'prev':r[0][0],'uid':r[0][1],'node':r[0][2],'lane':r[0][3],'mark':r[0][4]})
  for i,r in enumerate(ledger))
 return dict(intersections=nodes,total_capacity=nodes*per_node,arrivals=sum(arr.values()),
  departures=sum(dep.values()),by_direction=dict(dep),by_intersection=dict(used),
  peak_backlog=peak,max_wait=max(waits),mean_wait=sum(waits)/len(waits),
  finish_tick=tick,loss=sum(arr.values())-sum(dep.values()),reverse_exact=s==START,
  hash_chain_valid=valid,unique_ids=len({r[0][1] for r in ledger})==len(ledger),
  state_sha256=final,ledger_tip=tip)
def run():
 old=benchmark(1,8);equal=benchmark(4,2);wide=benchmark(4,8);rs=[old,equal,wide]
 checks={
 'arrivals_7200':all(x['arrivals']==7200 for x in rs),
 'departures_7200':all(x['departures']==7200 for x in rs),
 'zero_loss':all(x['loss']==0 for x in rs),
 'exact_reverse':all(x['reverse_exact'] for x in rs),
 'ledger_valid':all(x['hash_chain_valid'] for x in rs),
 'unique_watermark_ids':all(x['unique_ids'] for x in rs),
 'equal_budget':old['total_capacity']==equal['total_capacity']==8,
 'fourfold_capacity':wide['total_capacity']==32,
 'four_intersections_active':len(wide['by_intersection'])==4,
 'backlog_improves_only_with_capacity':wide['peak_backlog']<old['peak_backlog']==equal['peak_backlog'],
 'finish_improves_only_with_capacity':wide['finish_tick']<old['finish_tick']==equal['finish_tick'],
 'same_arrival_vector':all(x['by_direction']=={'W':2880,'N':1440,'E':720,'S':2160} for x in rs)}
 return dict(schema='oasis/sheet50/double-cross-v01',lineage='sheet48-cross-v03 -> sheet50-double-cross-v01',
  prior_plus=old,grid_same_capacity=equal,grid_fourfold_capacity=wide,
  checks=checks,passed=sum(checks.values()),total=len(checks),
  caveats=['Shared center cell not yet a modeled contention stage',
    'Extra capacity, not grid shape alone, explains congestion gains',
    'Symbolic reversible routing, not physical quantum transport'])
if __name__=='__main__':
 r=run();print(json.dumps(r,indent=2));assert r['passed']==r['total']
