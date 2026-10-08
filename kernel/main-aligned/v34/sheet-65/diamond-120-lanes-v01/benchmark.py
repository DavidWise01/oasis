#!/usr/bin/env python3
"""SHEET65: transport lanes, NOT neural attention heads."""
import json, hashlib
from collections import deque, Counter
from itertools import combinations
N=9; PAIRS=list(combinations(range(N),2)); PORTAL_CAP=16
MSGS=[(r,s,a,d) for r in range(12) for s in range(9) for a in range(4) for d in range(9) if d!=s]
def route_slots(lanes):
    base=lanes//36;rem=lanes%36
    return {pair:base+(i<rem) for i,pair in enumerate(PAIRS)}
def simulate(lanes, per_lane=1, portal_cap=PORTAL_CAP):
    allocation=route_slots(lanes)
    queues={p:deque() for p in PAIRS}; delivered=set(); source=Counter(); finish=-1
    accepted=0;peak=0;max_wait=0; waits=0; hops=0; eventhash=hashlib.sha256()
    for tick in range(3000):
        if tick<108:
            for r,s,a,d in MSGS[32*tick:32*(tick+1)]:
                uid=f'{r}:C{s+1}-A{a+1}:C{d+1}'
                p=tuple(sorted((s,d)))
                queues[p].append((uid,tick,s,d));accepted+=1
        sender_cap=[portal_cap]*9;receive_cap=[portal_cap]*9
        for p in PAIRS:
            k=min(len(queues[p]),allocation[p]*per_lane)
            for _ in range(k):
                uid,born,s,d=queues[p][0]
                if sender_cap[s]==0 or receive_cap[d]==0:break
                queues[p].popleft();sender_cap[s]-=1;receive_cap[d]-=1
                assert uid not in delivered
                delivered.add(uid);hops+=1;max_wait=max(max_wait,tick-born);waits+=tick-born
                eventhash.update((uid+'\n').encode());source[s]+=1
        peak=max(peak,sum(len(q) for q in queues.values()))
        if tick>=107 and all(not q for q in queues.values()): finish=tick;break
    ids=hashlib.sha256(json.dumps(sorted(delivered)).encode()).hexdigest()
    return dict(lanes=lanes,lane_capacity=per_lane,portal_capacity=portal_cap,
        pair_lane_min=min(allocation.values()),pair_lane_max=max(allocation.values()),
        arrived=accepted,delivered=len(delivered),loss=accepted-len(delivered),
        unique=len(delivered),hops=hops,peak_queue=peak,finish_tick=finish,
        max_wait=max_wait,mean_wait=waits/len(delivered),identity_digest=ids,
        event_digest=eventhash.hexdigest(),by_sender=dict(source))
def main():
    runs={str(l):simulate(l) for l in (36,72,120,144)}
    bottleneck={str(l):simulate(l,portal_cap=2) for l in (36,120)}
    checks={
        'same_workload':all(r['arrived']==3456 for r in runs.values()),
        'no_loss':all(r['loss']==0 for r in runs.values()),
        'unique_id':all(r['unique']==3456 for r in runs.values()),
        'same_identity_set':len({r['identity_digest'] for r in runs.values()})==1,
        'one_hop_all':all(r['hops']==3456 for r in runs.values()),
        '36_pairs':len(PAIRS)==36,
        '120_distribution':sorted(Counter(route_slots(120).values()).items())==[(3,24),(4,12)],
        'all_ambassadors_sourced':all(len(r['by_sender'])==9 for r in runs.values()),
        '120_not_slower_than_36':runs['120']['finish_tick']<=runs['36']['finish_tick'],
        '120_not_more_backlog_than_36':runs['120']['peak_queue']<=runs['36']['peak_queue'],
        'bottleneck_delivers':all(r['delivered']==3456 for r in bottleneck.values()),
        'portal_bottleneck_nonregression':bottleneck['120']['finish_tick']<=bottleneck['36']['finish_tick']}
    return dict(schema='oasis/sheet65/diamond-120-lanes-v01',
        model='transport lanes, NOT transformer attention heads',
        base_portal_cap=PORTAL_CAP,runs=runs,portal_bottleneck=bottleneck,
        checks=checks,passed=sum(checks.values()),total=len(checks),
        limitations=['Per-pair physical lane capacity modeled as one delivery/tick per lane',
         'Shared per-portal ingress and egress caps; no real GPU or neural attention benchmark',
         'Hash commits to delivered IDs; corruption injection and durable restart not tested here'])
if __name__=='__main__':
 r=main();print(json.dumps(r,indent=2));assert r['passed']==r['total']
