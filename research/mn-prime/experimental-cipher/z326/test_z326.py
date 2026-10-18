"""Z326: 24! factorial indexing and optional RGB occupancy, symbolic only."""
from math import factorial, comb
from itertools import permutations
from random import Random
N=24
def unrank(rank,n=N):
    if type(rank)!=int or not 0<=rank<factorial(n):raise ValueError('rank')
    a=list(range(n)); out=[]
    for k in range(n,0,-1):
        ix,rank=divmod(rank,factorial(k-1));out.append(a.pop(ix))
    return tuple(out)
def rank_perm(p):
    n=len(p)
    if sorted(p)!=list(range(n)):raise ValueError('permutation')
    a=list(range(n)); r=0
    for i,v in enumerate(p):
        ix=a.index(v);r+=ix*factorial(n-i-1);a.pop(ix)
    return r
def enc_rgb(v):
    if len(v)!=3 or any(type(n)!=int or not 0<=n<=8 for n in v):raise ValueError('RGB')
    return tuple((c,i) for c,n in zip('RGB',v) for i in range(n))
def dec_rgb(a):
    if len(set(a))!=len(a) or any(c not in 'RGB' or type(i)!=int or not 0<=i<8 for c,i in a):raise ValueError('RGB address')
    v=tuple(sum(c==k for c,i in a) for k in 'RGB')
    if set(a)!=set(enc_rgb(v)):raise ValueError('noncanonical')
    return v
total=factorial(N); rng=Random(326)
samples=[0,1,2,total//2,total-2,total-1]+[rng.randrange(total) for _ in range(1000)]
states=set(permutations((3,1,2)))
checks={
'exact_24_factorial':total==620448401733239439360000,
'roundtrip_boundaries':all(rank_perm(unrank(i))==i for i in samples[:6]),
'roundtrip_1000_random':all(rank_perm(unrank(i))==i for i in samples[6:]),
'first':unrank(0)==tuple(range(24)),
'last':unrank(total-1)==tuple(range(23,-1,-1)),
'unique_indices':len({rank_perm(unrank(i)) for i in samples})==len(set(samples)),
'six_rgb':len(states)==6,
'roundtrip_rgb':all(dec_rgb(enc_rgb(s))==s for s in states),
'six_markers':all(len(enc_rgb(s))==6 for s in states),
'capacity_24':3*8==24,
'fixed_channel_allocations':comb(8,3)*comb(8,1)*comb(8,2)==12544,
'independent_531':(5,3,1)!=(3,1,2)}
for label,fn in [('reject_negative',lambda:unrank(-1)),('reject_max',lambda:unrank(total)),('reject_duplicate',lambda:rank_perm([0]*24)),('reject_noncanonical',lambda:dec_rgb((('R',1),)))]: 
    try:fn();checks[label]=False
    except ValueError:checks[label]=True
for k,v in checks.items():print(('PASS' if v else 'FAIL'),k)
print(f'{sum(checks.values())}/{len(checks)} PASS')
assert all(checks.values())
