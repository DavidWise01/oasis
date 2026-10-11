"""U04: 8-fold witness orbit under explicit reversible transforms.
R reverses factor order, M swaps lanes, I negates every factor.
These meanings are provisional; not canonical physics operators.
"""
from itertools import product
from math import prod
from hashlib import sha256
from json import dumps
BASE=((1,3,-3,2),(1,3,3,-2))
def apply(state, r=0,m=0,i=0):
    a,b=state
    if r:a,b=a[::-1],b[::-1]
    if m:a,b=b,a
    if i:a,b=tuple(-x for x in a),tuple(-x for x in b)
    return a,b
def h(v):return sha256(dumps(v,separators=(',',':')).encode()).hexdigest()
def main():
    orbit={(r,m,i):apply(BASE,r,m,i) for r,m,i in product((0,1),repeat=3)}
    checks={
      '8 distinct transformations':len(orbit)==8,
      '8 unique ordered states':len({str(x) for x in orbit.values()})==8,
      'base both equal -18':tuple(map(prod,BASE))==(-18,-18),
      'every output product invariant':all(tuple(map(prod,s))==(-18,-18) for s in orbit.values()),
      'each witness factors distinct':all(a!=b for a,b in orbit.values()),
      'every transform has inverse itself':all(apply(apply(BASE,*key),*key)==BASE for key in orbit),
      'hash retains transformed history':len({h(state) for state in orbit.values()})==8,
      'one-factor sign flip breaks conserved product':prod((-1,3,-3,2))!=prod(BASE[0]),
      'componentwise reciprocal does not conserve product':prod([1/x for x in BASE[0]])!=prod(BASE[0]),
      'product alone cannot recover 8 histories':len({tuple(map(prod,s)) for s in orbit.values()})==1,
      'operator address 13x6x13':13*6*13==1014,
      'original paired witness product':prod(BASE[0])*prod(BASE[1])==324,
    }
    for key,state in orbit.items():print('orbit',key,'=>',state,'products',tuple(map(prod,state)))
    for k,v in checks.items():print('PASS' if v else 'FAIL',k)
    print('RESULT',sum(checks.values()),'/',len(checks))
    assert all(checks.values())
if __name__=='__main__':main()
