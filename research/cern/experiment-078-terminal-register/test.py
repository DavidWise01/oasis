import random
from math import gcd
B={8:8**8,9:9**9,10:10**10}
def encode(x,radix,width):
    assert 0<=x<radix**width
    d=[]
    for _ in range(width):x,r=divmod(x,radix);d.append(r)
    return tuple(reversed(d))
def decode(ds,radix):
    x=0
    for d in ds:
        assert 0<=d<radix
        x=x*radix+d
    return x
rng=random.Random(78); checks=0
for src,dst in ((8,9),(9,10),(8,10)):
    xs=[0,1,src,B[src]//2,B[src]-2,B[src]-1]
    xs += [rng.randrange(B[src]) for _ in range(20000)]
    for x in xs:
        assert decode(encode(x,src,src),src)==decode(encode(x,dst,dst),dst)
        checks+=1
assert B[8]<B[9]<B[10]
assert 16//gcd(16,60)==4
for t in range(240):
    assert 0<=(t%60)//20<3;checks+=1
    assert ((t%20)<8)!=((t%20)>=8);checks+=1
    assert t%16==(t+240)%16;checks+=1
assert checks==60738
print('PASS',checks,'bounds',B,'max index',B[10]-1)
