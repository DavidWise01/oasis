from fractions import Fraction as F
from itertools import product
K=(F(1),F(4),F(16))
LIMITS=(F(1,10),F(1,2),F(1))
PULSES=(F(0),F(1,100),F(1,10),F(1),F(10))
AREAS=(F(1,10),F(1),F(10))
checks=0;stopped=0
for k,limit,pulse,area in product(K,LIMITS,PULSES,AREAS):
 capacity=k*limit*limit/2
 stored=min(pulse,capacity)
 reflected=pulse-stored
 x2=2*stored/k
 pmax=k*limit/area
 assert pulse==stored+reflected;checks+=1
 assert x2<=limit*limit;checks+=1
 assert stored>=0 and reflected>=0;checks+=1
 assert stored==k*x2/2;checks+=1
 assert pmax*area==k*limit;checks+=1
 stopped+=pulse>capacity
assert checks==675 and stopped==57
print(f'PASS {checks} assertions across 135 cases, {stopped} deformation-cap crossings')
