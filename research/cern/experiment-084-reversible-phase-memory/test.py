from fractions import Fraction as F
from math import sin,cos,pi,floor
import random
BEATS=(5,5,5,7,7,5,5,7,7,7)
def bind(m,j,p):return (m+j+p,m-j,j-p)
def unbind(s,d1,d2):return ((s+2*d1+d2)/3,(s-d1+d2)/3,(s-d1-2*d2)/3)
def phase_pack(phi):
 n=floor(phi/(2*pi));return n,phi-2*pi*n
def beat(t):
 x=t%60
 for b in BEATS:
  if x<b:return b
  x-=b
 raise ValueError
checks=0;end=[]
for address in range(24):
 v=(F(address-12,7),F(address+3,11),F(2*address-5,13))
 register=bind(*v)
 assert unbind(*register)==v;checks+=1
 phi0=2*pi*address/24;phi=phi0;work=diss=0.
 for t in range(60):
  current=1.18*beat(t)/6
  for _ in range(100):
   nxt=phi+.01*(current-sin(phi))
   dw=current*(nxt-phi);du=cos(phi)-cos(nxt)
   work+=dw;diss+=dw-du;phi=nxt
   n,theta=phase_pack(phi)
   assert 0<=theta<2*pi;checks+=1
   assert abs(2*pi*n+theta-phi)<2e-14;checks+=1
   assert unbind(*register)==v;checks+=1
   assert abs(work-diss-(cos(phi0)-cos(phi)))<1e-9;checks+=1
 end.append(phase_pack(phi)[0])
assert abs(sin(.4)-sin(.4+2*pi))<1e-14;checks+=1
assert bind(F(1),F(0),F(0))[0]==bind(F(0),F(1),F(0))[0];checks+=1
for t in range(240):
 assert (t+240)%60==t%60 and (t+240)%16==t%16;checks+=1
 assert 0<=t%16<16 and (t%60)//20 in (0,1,2);checks+=1
assert checks==576506
print('PASS',checks,'winding values',sorted(set(end)))
