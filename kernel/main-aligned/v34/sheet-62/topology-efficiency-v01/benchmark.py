#!/usr/bin/env python3
"""SHEET62 deterministic portal topology cost test, append-only."""
from collections import deque,Counter
import hashlib,json
N=9
MESSAGES=[(r,s,a,d) for r in range(12) for s in range(N) for a in range(4) for d in range(N) if d!=s]
def sha(o):return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def edges(name):
 if name=="full":return {(i,j) for i in range(N) for j in range(i+1,N)}
 if name=="grid":return {(i,i+1) for i in range(N) if i%3<2}|{(i,i+3) for i in range(6)}
 if name=="ring":return {tuple(sorted((i,(i+1)%N))) for i in range(N)}
 if name=="hub":return {tuple(sorted((i,4))) for i in range(N) if i!=4}
 raise ValueError(name)
def path(es,s,d):
 adj={i:[] for i in range(N)}
 for i,j in es:adj[i].append(j);adj[j].append(i)
 q=deque([(s,(s,))]);visited={s}
 while q:
  i,p=q.popleft()
  if i==d:return p
  for j in sorted(adj[i]):
   if j not in visited:visited.add(j);q.append((j,p+(j,)))
 raise AssertionError("disconnected")
def bench(name):
 es=edges(name);loads=Counter();tip="0"*64;uids=set()
 for r,s,a,d in MESSAGES:
  uid=f"{r}:C{s+1}-A{a+1}:C{d+1}";payload=sha([uid,"EXITRON"])
  for i,j in zip(path(es,s,d),path(es,s,d)[1:]):
   loads[tuple(sorted((i,j)))]+=1;tip=sha([tip,uid,i,j,payload])
  assert uid not in uids;uids.add(uid)
 return dict(links=len(es),directed_links=2*len(es),delivered=len(uids),
  hops=sum(loads.values()),mean_hops=sum(loads.values())/len(uids),
  max_edge_load=max(loads.values()),min_edge_load=min(loads.values()),
  ledger_tip=tip,delivery_digest=sha(sorted(uids)))
def run():
 d={x:bench(x) for x in ("full","grid","ring","hub")}
 checks=dict(all_delivered=all(x["delivered"]==3456 for x in d.values()),
  identical_delivery_set=len({x["delivery_digest"] for x in d.values()})==1,
  full_direct=d["full"]["hops"]==3456,grid_links=d["grid"]["links"]==12,
  ring_links=d["ring"]["links"]==9,hub_links=d["hub"]["links"]==8,
  sparse_extra_hops=all(d[k]["hops"]>3456 for k in ("grid","ring","hub")))
 return dict(schema="oasis/sheet62/topology-efficiency-v01",results=d,
  checks=checks,passed=sum(checks.values()),total=len(checks),
  caveat="Edge load is total across rounds; no finite-capacity queues or link-delay simulation.")
if __name__=="__main__":
 result=run();print(json.dumps(result,indent=2));assert result["passed"]==result["total"]
