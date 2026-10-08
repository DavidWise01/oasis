#!/usr/bin/env python3
"""SHEET 64: 16-edge optimized portal topology; deterministic preservation benchmark."""
from collections import deque,Counter
from itertools import combinations
import hashlib,json
N=9;CAP=16;ALL=set(combinations(range(N),2))
MSGS=[(r,s,a,d) for r in range(12) for s in range(N) for a in range(4) for d in range(N) if d!=s]
def routes(edges):
 adj=[[] for _ in range(N)]
 for i,j in sorted(edges):adj[i].append(j);adj[j].append(i)
 out={}
 for s in range(N):
  q=deque([(s,(s,))]);seen={s}
  while q:
   u,path=q.popleft();out[s,u]=path
   for v in adj[u]:
    if v not in seen:seen.add(v);q.append((v,path+(v,)))
 if len(out)!=81:raise ValueError('Disconnected')
 return out
def metric(es):
 p=routes(es)
 return sum(len(p[s,d])-1 for s in range(N) for d in range(N) if s!=d)
def hybrid():
 grid={(i,i+1) for i in range(N) if i%3<2}|{(i,i+3) for i in range(6)}
 return grid|{tuple(sorted((i,4))) for i in range(N) if i!=4}
def optimize(base):
 def descend(e):
  e=set(e)
  while True:
   best=None;v=metric(e)
   for old in sorted(e):
    for new in sorted(ALL-e):
     trial=e-{old}|{new}
     try:m=metric(trial)
     except ValueError:continue
     if m<v and (best is None or (m,old,new)<best[:3]):best=(m,old,new,trial)
   if best is None:return e
   e=best[3]
 seeds=[descend(base)]
 for hub in range(N):
  e={tuple(sorted((i,hub))) for i in range(N) if i!=hub}
  while len(e)<16:e=min((e|{x} for x in ALL-e),key=lambda t:(metric(t),sorted(t)))
  seeds.append(descend(e))
 return min(seeds,key=lambda e:(metric(e),sorted(e)))
def simulate(es):
 p=routes(es);waiting=deque();offered=0;delivered=set();hops=peak=0;last=-1;tip='0'*64
 for tick in range(2500):
  if tick<108:
   for r,s,a,d in MSGS[tick*32:(tick+1)*32]:
    waiting.append((f'{r}:C{s+1}-A{a+1}:C{d+1}',p[s,d],0));offered+=1
  for _ in range(min(CAP,len(waiting))):
   uid,route,k=waiting.popleft();hops+=1
   tip=hashlib.sha256((tip+json.dumps([uid,route[k],route[k+1],k],separators=(',',':'))).encode()).hexdigest()
   if k+1==len(route)-1:
    assert uid not in delivered;delivered.add(uid)
   else:waiting.append((uid,route,k+1))
  peak=max(peak,len(waiting))
  if tick>=107 and not waiting:last=tick;break
 return dict(links=len(es),hops=hops,peak_queue=peak,finish_tick=last,offered=offered,delivered=len(delivered),
  identities_sha256=hashlib.sha256(json.dumps(sorted(delivered)).encode()).hexdigest(),ledger_tip=tip)
def main():
 old=hybrid();new=optimize(old)
 results={'sheet63_hybrid':simulate(old),'sheet64_optimized':simulate(new),'full_mesh':simulate(ALL)}
 ck={
 'equal_links':len(old)==len(new)==16,
 'connected':len(routes(new))==81,
 'all_offered':all(v['offered']==3456 for v in results.values()),
 'all_delivered':all(v['delivered']==3456 for v in results.values()),
 'all_identities_preserved':len({v['identities_sha256'] for v in results.values()})==1,
 'optimal_hop_bound':results['sheet64_optimized']['hops']==results['sheet63_hybrid']['hops']==5376,
 'queue_no_worse':results['sheet64_optimized']['peak_queue']<=results['sheet63_hybrid']['peak_queue'],
 'same_finish':results['sheet64_optimized']['finish_tick']==results['sheet63_hybrid']['finish_tick'],
 'mesh_floor':results['full_mesh']['hops']==3456,
 'uniform_pairwise_demand':len({Counter((s,d) for r,s,a,d in MSGS)[s,d] for s in range(N) for d in range(N) if s!=d})==1}
 return dict(schema='oasis/sheet64/demand-aware-topology-v01',results=results,
  optimized_edges=sorted(map(list,new)),checks=ck,passed=sum(ck.values()),total=len(ck),
  theoretical_hop_floor=5376,notes='No hop improvement: uniform demand gives no traffic hotspots; no node failure or per-link contention simulated.')
if __name__=='__main__':
 r=main();print(json.dumps(r,indent=2));assert r['passed']==r['total']
