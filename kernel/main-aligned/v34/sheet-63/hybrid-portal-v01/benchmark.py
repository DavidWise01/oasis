#!/usr/bin/env python3
"""SHEET 63: deterministic nine-portal hybrid versus full/grid/ring/hub."""
from collections import deque, Counter
from itertools import combinations
import hashlib,json
N=9
MESSAGES=[(r,s,a,d) for r in range(12) for s in range(9) for a in range(4) for d in range(9) if d!=s]
def edges(name):
 if name=="mesh":return set(combinations(range(N),2))
 if name=="grid":return {(i,i+1) for i in range(N) if i%3<2}|{(i,i+3) for i in range(6)}
 if name=="ring":return {tuple(sorted((i,(i+1)%N))) for i in range(N)}
 if name=="hub":return {tuple(sorted((i,4))) for i in range(N) if i!=4}
 if name=="hybrid":return edges("grid")|edges("hub")
 raise ValueError(name)
def route(es,s,d):
 adj=[[] for _ in range(N)]
 for i,j in es:adj[i].append(j);adj[j].append(i)
 q=deque([(s,(s,))]);seen={s}
 while q:
  i,p=q.popleft()
  if i==d:return p
  for j in sorted(adj[i]):
   if j not in seen:seen.add(j);q.append((j,p+(j,)))
 raise ValueError("disconnected")
def run(name,cap=16):
 es=edges(name);loads=Counter();hops=0;digest=hashlib.sha256()
 waiting=deque();arrived=done=0;peak=0;last=-1;waits=[]
 for tick in range(3000):
  if tick<108:
   for r,s,a,d in MESSAGES[tick*32:(tick+1)*32]:
    uid=f"{r}:C{s+1}-A{a+1}:C{d+1}"
    p=route(es,s,d);waiting.append((uid,p,0,tick));arrived+=1
  service=min(cap,len(waiting))
  for _ in range(service):
   uid,p,k,born=waiting.popleft()
   loads[tuple(sorted((p[k],p[k+1])))]+=1;hops+=1
   if k+1==len(p)-1:done+=1;waits.append(tick-born);digest.update(uid.encode()+b"\n")
   else:waiting.append((uid,p,k+1,born))
  peak=max(peak,len(waiting))
  if tick>=107 and not waiting:last=tick;break
 return dict(links=len(es),directed=2*len(es),hops=hops,mean_hops=hops/len(MESSAGES),
  peak_queue=peak,finish_tick=last,mean_end_to_end_ticks=sum(waits)/len(waits),
  max_edge_load=max(loads.values()),delivered=done,arrived=arrived,delivery_digest=digest.hexdigest())
def main():
 data={k:run(k) for k in ("mesh","grid","ring","hub","hybrid")}
 checks=dict(all_delivered=all(v["delivered"]==3456 for v in data.values()),
  link_savings=data["hybrid"]["links"]<data["mesh"]["links"],
  hybrid_fewer_hops_grid=data["hybrid"]["hops"]<data["grid"]["hops"],
  hybrid_fewer_hops_ring=data["hybrid"]["hops"]<data["ring"]["hops"],
  mesh_min_hops=data["mesh"]["hops"]==3456,
  all_accounted=all(v["arrived"]==v["delivered"] for v in data.values()),
  all_links_connected=all(v["finish_tick"]>=107 for v in data.values()))
 return dict(schema="oasis/sheet63/hybrid-portal-v01",capacity_shared_hops_per_tick=16,
  workload=3456,results=data,checks=checks,passed=sum(checks.values()),total=len(checks),
  limitations=["Single global hop server, not separate edge capacities",
   "FIFO shared hop queue, synthetic traffic; no physical latency or measured energy",
   "Delivery hashes depend on completion order; identity set is the same in all models"])
if __name__=="__main__":
 x=main();print(json.dumps(x,indent=2));assert x["passed"]==x["total"]
