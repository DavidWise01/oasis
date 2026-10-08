#!/usr/bin/env python3
"""SHEET 52: center-pane saturation, linear append-only successor to SHEET51."""
import json,hashlib
from collections import deque
MOD=2**32
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def step(state,seq,lane,node,undo=False):
 x=list(state);i=lane%8;j=(lane+3+node)%8
 if j==i:j=(j+1)%8
 a=1+(seq*7+lane*13+node*17)%65521
 def f(z):x[8]=(x[8]+z*(x[i]+a))%MOD
 def g(z):x[9]=(x[9]+z*(x[8]+x[j]+node))%MOD
 def h(z):x[i]=(x[i]+z*(x[9]+a+node))%MOD
 if undo:h(-1);g(-1);f(-1)
 else:f(1);g(1);h(1)
 return tuple(x)
def run(capacity):
 state=(0,)*10;queues=[deque() for _ in range(4)];center=deque()
 history=[];ledger=[];tip='0'*64;arrived=set();served=set();waits=[];peak=0
 for t in range(720+7000):
  if t<720:
   for k in range(12):
    uid=f'{t}:C:{k}';n=k%4;queues[n].append((t,uid,k,n,sha({'uid':uid,'word':'EXITRON'})));arrived.add(uid)
  for n in range(4):
   for _ in range(min(8,len(queues[n]))):center.append(queues[n].popleft())
  for _ in range(min(capacity,len(center))):
   born,uid,k,n,mark=center.popleft();lane=(k+n)%8;seq=len(history)
   state=step(state,seq,lane,n);history.append((seq,lane,n));served.add(uid);waits.append(t-born)
   ev={'uid':uid,'lane':lane,'node':n,'mark':mark,'seq':seq,'pane':4}
   h=sha({'previous':tip,'event':ev});ledger.append((tip,ev,h));tip=h
  backlog=sum(map(len,queues))+len(center);peak=max(peak,backlog)
  if t>=719 and backlog==0:break
 final=sha(state)
 for seq,lane,n in reversed(history):state=step(state,seq,lane,n,True)
 valid=all(r[0]==(ledger[i-1][2] if i else '0'*64) and
  r[2]==sha({'previous':r[0],'event':r[1]}) and
  r[1]['mark']==sha({'uid':r[1]['uid'],'word':'EXITRON'}) for i,r in enumerate(ledger))
 changed=dict(ledger[0][1]);changed['mark']='FORGED'
 return {'capacity':capacity,'arrivals':len(arrived),'departures':len(served),
  'lost':len(arrived-served),'duplicates':len(ledger)-len(served),
  'peak_backlog':peak,'max_wait':max(waits),'mean_wait':sum(waits)/len(waits),
  'finish_tick':t,'inverse_exact':state==(0,)*10,'ledger_valid':valid,
  'tamper_rejected':sha({'previous':ledger[0][0],'event':changed})!=ledger[0][2],
  'final_hash':final,'ledger_tip':tip}
def benchmark():
 old=run(32);new=run(2)
 checks={'same_arrivals':old['arrivals']==new['arrivals']==8640,
 'all_depart':old['departures']==new['departures']==8640,
 'no_loss':old['lost']==new['lost']==0,
 'no_duplicates':old['duplicates']==new['duplicates']==0,
 'reverse':old['inverse_exact'] and new['inverse_exact'],
 'hash_provenance':old['ledger_valid'] and new['ledger_valid'],
 'tamper_detected':old['tamper_rejected'] and new['tamper_rejected'],
 'center_capacity_two':new['capacity']==2,
 'baseline_capacity_32':old['capacity']==32,
 'bottleneck':new['peak_backlog']>old['peak_backlog'],
 'longer_completion':new['finish_tick']>old['finish_tick'],
 'waiting':new['mean_wait']>old['mean_wait'],
 'identical_end_register':new['final_hash']==old['final_hash'],
 'identical_ledger_tip':new['ledger_tip']==old['ledger_tip']}
 return {'schema':'oasis/sheet52/window-saturation-v01',
 'lineage':'SHEET48 + -> SHEET50 # -> SHEET51 ⊞ -> SHEET52 center saturation',
 'previous':old,'upgrade':new,'checks':checks,'passed':sum(checks.values()),'total':len(checks),
 'caveat':'Unbounded queues guarantee no overflow here. The lower service rate is deliberately imposed.'}
if __name__=='__main__':
 r=benchmark();print(json.dumps(r,indent=2));assert r['passed']==r['total']
