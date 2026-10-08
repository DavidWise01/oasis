#!/usr/bin/env python3
"""SHEET 66 adaptive versus fixed 120 virtual transport lanes; not attention heads."""
import hashlib,json
from collections import deque,Counter
from itertools import combinations
PAIRS=list(combinations(range(9),2));LANES=120;BASE={p:3+(i<12) for i,p in enumerate(PAIRS)}
def traffic(kind):
 if kind=="balanced":
  return [(r,s,a,d) for r in range(12) for s in range(9) for a in range(4) for d in range(9) if s!=d]
 return [(r,s,a,(4 if s!=4 else (r+a)%8+((r+a)%8>=4))) for r in range(96) for s in range(9) for a in range(4)]
def run(kind,adaptive):
 offers=traffic(kind);qs={p:deque() for p in PAIRS};done=set();waits=[];peak=0;tip="0"*64;sources=set()
 for tick in range(2000):
  if tick<108:
   for r,s,a,d in offers[tick*32:(tick+1)*32]:
    uid=f"{r}:C{s+1}-A{a+1}:C{d+1}"
    qs[tuple(sorted((s,d)))].append((uid,tick,s,d))
  send=[16]*9;receive=[16]*9;used={p:0 for p in PAIRS}
  if adaptive:
   alloc={p:0 for p in PAIRS};active=[p for p in PAIRS if qs[p]]
   for p in active:alloc[p]=1
   spare=LANES-len(active)
   for p in sorted(active,key=lambda p:(-len(qs[p]),p)):
    take=min(spare,max(0,len(qs[p])-alloc[p]));alloc[p]+=take;spare-=take
  else:alloc=BASE
  order=sorted(PAIRS,key=lambda p:(qs[p][0][1] if qs[p] else 10**8,p))
  progress=True
  while progress:
   progress=False
   for p in order:
    if not qs[p] or used[p]>=alloc[p]:continue
    uid,born,s,d=qs[p][0]
    if send[s]<=0 or receive[d]<=0:continue
    qs[p].popleft();send[s]-=1;receive[d]-=1;used[p]+=1;progress=True
    assert uid not in done
    done.add(uid);sources.add((s,int(uid.split("-A")[1].split(":")[0])));waits.append(tick-born)
    tip=hashlib.sha256((tip+uid).encode()).hexdigest()
  peak=max(peak,sum(map(len,qs.values())))
  if tick>=107 and not any(qs.values()):break
 return dict(offered=len(offers),delivered=len(done),lost=len(offers)-len(done),
   peak_backlog=peak,finish_tick=tick,mean_wait=sum(waits)/len(waits),max_wait=max(waits),
   ambassadors=len(sources),identity_digest=hashlib.sha256(json.dumps(sorted(done)).encode()).hexdigest(),
   ledger_tip=tip)
def main():
 data={name:{m:run(name,m=="adaptive") for m in ("fixed","adaptive")} for name in ("balanced","hotspot")}
 checks={
  "all_36_ambassadors":all(v["ambassadors"]==36 for group in data.values() for v in group.values()),
  "3456_deliveries":all(v["delivered"]==3456 for group in data.values() for v in group.values()),
  "zero_loss":all(v["lost"]==0 for group in data.values() for v in group.values()),
  "same_identity_set":all(group["fixed"]["identity_digest"]==group["adaptive"]["identity_digest"] for group in data.values()),
  "fixed_120":sum(BASE.values())==120,
  "hotspot_finish_nonregression":data["hotspot"]["adaptive"]["finish_tick"]<=data["hotspot"]["fixed"]["finish_tick"],
  "deterministic":data["hotspot"]["adaptive"]==run("hotspot",True),
  "same_balanced_finish":data["balanced"]["fixed"]["finish_tick"]==data["balanced"]["adaptive"]["finish_tick"]}
 return dict(schema="oasis/sheet66/adaptive-lanes-v01",data=data,checks=checks,passed=sum(checks.values()),total=len(checks),
  limits=["Lane reassignment has zero cost in this model","Per-portal capacity is 16 transfers/tick","No real neural attention computation"])
if __name__=="__main__":
 result=main();print(json.dumps(result,indent=2));assert result["passed"]==result["total"]
