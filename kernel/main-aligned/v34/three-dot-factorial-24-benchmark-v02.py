#!/usr/bin/env python3
"""OaSIs three-dot factorial address space test: 24 distinct labels, not physical atoms."""
import math,random,time,json
N=24; TRIALS=100000; rng=random.Random(340424)
facts=[math.factorial(i) for i in range(N+1)]
def unrank(rank):
    pool=list(range(N)); out=[]
    for remaining in range(N,0,-1):
        q,rank=divmod(rank,facts[remaining-1]); out.append(pool.pop(q))
    return out
def rank_perm(p):
    pool=list(range(N)); out=0
    for i,x in enumerate(p):
        q=pool.index(x); out+=q*facts[N-1-i]; pool.pop(q)
    return out
start=time.perf_counter(); seen=set(); failures=0
for _ in range(TRIALS):
    r=rng.randrange(facts[N]); p=unrank(r)
    if rank_perm(p)!=r or sorted(p)!=list(range(N)):failures+=1
    seen.add(r)
elapsed=time.perf_counter()-start
report={'scope':'Permutation indexing only; no particle dynamics','factorial_24':str(facts[N]),'untagged_duplicate_pair_arrangements':str(facts[N]//(2**12)),'trials':TRIALS,'unique_samples':len(seen),'failures':failures,'elapsed_seconds':elapsed,'samples_per_second':TRIALS/elapsed}
print(json.dumps(report,indent=2))
if failures:raise SystemExit(1)
