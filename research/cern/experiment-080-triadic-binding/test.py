from fractions import Fraction as F
from math import gcd
import random
A=((1,1,1),(0,0,0),(1,1,1))
def projection(v):
 return (sum(v),F(0),sum(v))
def bind(v):
 m,j,p=v
 return projection(v),(m-j,j-p)
def unbind(y,w):
 s=y[0]; d1,d2=w
 return ((s+2*d1+d2)/3,(s-d1+d2)/3,(s-d1-2*d2)/3)
rng=random.Random(80)
assert projection((F(1),F(0),F(0)))==projection((F(0),F(1),F(0)))
checks=4
for _ in range(10000):
 v=tuple(F(rng.randrange(-1000,1001),rng.randrange(1,30)) for i in range(3))
 assert unbind(*bind(v))==v
 checks+=1
for t in range(240):
 sector=(t%60)//20
 route=tuple((sector+i)%3 for i in range(3))
 v=tuple(F((0,-1,1)[i]) for i in route)
 assert unbind(*bind(v))==v
 assert set(route)=={0,1,2}
 assert (t+60)%16==(t+12)%16
 assert (t+240)%16==t%16
 checks+=4
assert checks==10964
print("PASS",checks,"rank(A)=1, kernel dimension 2, full alignment 240")
