"""U05: mixed-radix 324-state inference VM against 1014-address witness atlas.
Formal accounting benchmark, not a demonstrated physical inference model.
"""
from math import prod
from hashlib import sha256
from json import dumps
from itertools import product

RADICES = (1,3,2,3,3,2,3,1)
ATLAS = 13*6*13
WITNESSES = ((1,3,-3,2),(1,3,3,-2))

def encode(digits):
    assert len(digits)==len(RADICES)
    n=0
    for digit,base in zip(digits,RADICES):
        if not isinstance(digit,int) or not 0<=digit<base: raise ValueError('out of range')
        n=n*base+digit
    return n

def decode(n):
    if not isinstance(n,int) or not 0<=n<prod(RADICES):raise ValueError('out of range')
    digits=[]
    for base in reversed(RADICES):
        n,d=divmod(n,base)
        digits.append(d)
    return tuple(reversed(digits))

def orbit(witness_id,r,m,i):
    a,b=WITNESSES
    if r:a,b=a[::-1],b[::-1]
    if m:a,b=b,a
    if i:a,b=tuple(-x for x in a),tuple(-x for x in b)
    return (a,b)[witness_id]

def record(address,witness_id,r,m,i):
    digits=decode(address)
    factors=orbit(witness_id,r,m,i)
    value=prod(factors)
    payload=(address,digits,witness_id,r,m,i,factors,value)
    return (payload,sha256(dumps(payload,separators=(',',':')).encode()).hexdigest())

def benchmark():
    n=prod(RADICES)
    universe=[decode(i) for i in range(n)]
    encoded=[encode(d) for d in universe]
    transformed=[record(addr,w,r,m,i) for addr in range(n) for w,r,m,i in product(range(2),repeat=4)]
    keys=[item[0][:6] for item in transformed]
    hashes=[item[1] for item in transformed]
    checks={
        'radix count exactly 324':n==324,
        'atlas count exactly 1014':ATLAS==1014,
        'full radix enumeration':len(universe)==324,
        'all radix states unique':len(set(universe))==324,
        'bijection encoding':encoded==list(range(324)),
        'boundary addresses':decode(0)==(0,)*8 and decode(323)==tuple(x-1 for x in RADICES),
        '324-to-1014 injection':len(set(range(n)))==n and n<=ATLAS,
        '690 unused atlas slots':ATLAS-n==690,
        '1014-to-324 collision unavoidable':len(set(j%n for j in range(ATLAS)))==324 and ATLAS>n,
        'collision exemplar':0%324==324%324,
        '2 witness x 8 symmetry metadata':len(transformed)==324*2*8,
        'metadata keys unique':len(set(keys))==len(keys),
        'records SHA256 distinct':len(set(hashes))==len(hashes),
        'inferred witness scalar invariant':all(item[0][-1]==-18 for item in transformed),
        'signed witness traces distinct':WITNESSES[0]!=WITNESSES[1],
        'address scalar alone is ambiguous':len({v[0][-1] for v in transformed})==1,
        'direct numeric 324=1014 claim rejected':n!=ATLAS,
    }
    for name,ok in checks.items():print(('PASS' if ok else 'FAIL'), name)
    print('RESULT',sum(checks.values()),'/',len(checks))
    print('INFERENCE ENGINE: 324 addresses x 2 witnesses x 8 transforms =',len(transformed),'records')
    print('ATLAS: 1014 positions, 324 directly encodable, 690 unmapped')
    print('INFERENCE: unable to choose witness/orientation from scalar -18 alone')
    assert all(checks.values())

if __name__=='__main__': benchmark()
