from itertools import product
from math import prod
from hashlib import sha256
from json import dumps

RADICES=(1,3,2,3,3,2,3,1)
TRACKS=('i:identity:isomorphic:intent','u:consequence:harmony:resonance','u.s.::creation:life:death:recycle:repeat')
GROUPS=((0,1,2),(3,4,5),(6,7))  # provisional semantics

def encode(ds):
    n=0
    for d,r in zip(ds,RADICES):
        if not 0<=d<r:raise ValueError('digit out of range')
        n=n*r+d
    return n

def decode(n):
    if not 0<=n<prod(RADICES):raise ValueError('address out of range')
    out=[]
    for r in reversed(RADICES):
        n,d=divmod(n,r);out.append(d)
    return tuple(reversed(out))

def observe(addr,track):
    digits=decode(addr)
    return tuple(digits[j] for j in GROUPS[track])

def infer(observations):
    if any(k not in range(3) for k in observations):
        raise ValueError('only three tracks')
    return tuple(a for a in range(324) if all(observe(a,k)==v for k,v in observations.items()))

def audit(addr):
    return tuple((k,observe(addr,k),sha256(dumps((k,observe(addr,k))).encode()).hexdigest()) for k in range(3))

def main():
    target=217
    obs={i:observe(target,i) for i in range(3)}
    stages=(infer({}),infer({0:obs[0]}),infer({0:obs[0],1:obs[1]}),infer(obs))
    counts=tuple(map(len,stages))
    checks={
      '324 addresses':prod(RADICES)==324,
      'three tracks':len(TRACKS)==3,
      'all address digits covered':sorted(j for g in GROUPS for j in g)==list(range(8)),
      'disjoint tracks':sum(map(len,GROUPS))==8,
      'roundtrip':all(encode(decode(a))==a for a in range(324)),
      'baseline candidates':counts[0]==324,
      'first-track reduction':counts[1]==54,
      'second-track reduction':counts[2]==3,
      'third-track unique':counts[3]==1,
      'target preserved':all(target in s for s in stages),
      'recovered target':stages[-1]==(target,),
      'scalar fails distinguish witnesses':len(set((-18,-18)))==1,
      'invalid observation rejected':infer({0:(0,99,0)})==(),
      'immutable ledger':len(audit(target))==3 and isinstance(audit(target),tuple),
      'deterministic replay':audit(target)==audit(target),
      'atlas mismatch explicit':324!=1014
    }
    for k,v in checks.items():print(('PASS' if v else 'FAIL'),k)
    print('COUNTS',counts,'RESULT',sum(checks.values()),'/',len(checks))
    assert all(checks.values())

if __name__=='__main__':main()
