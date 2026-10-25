from fractions import Fraction as F
from itertools import product
PULSE,CAP,VENT,TH=F(1,20),F(1,10),F(1,50),F(1,20)
SCHEDULES=[(20,0),(4,1),(4,2),(4,4),(2,2),(1,3)]
RECOVERY=[F(0),F(1,200),F(1,100)]
checks=0
for on,off in SCHEDULES:
 for recovery in RECOVERY:
  held=vented=overflow=damage=total=F(0);failed=None
  for tick in range(1,121):
   active=(tick-1)%(on+off)<on
   v=min(held,VENT);held-=v;vented+=v
   leaked=F(0)
   if active:
    total+=PULSE;take=min(PULSE,CAP-held);held+=take
    leaked=PULSE-take;overflow+=leaked;damage+=leaked/2
   else:damage=max(F(0),damage-recovery)
   if failed is None and damage>=TH:failed=tick
   assert held+vented+overflow==total;checks+=1
   assert 0<=held<=CAP;checks+=1
   assert damage>=0;checks+=1
   assert leaked>=0;checks+=1
  print(on,off,str(recovery),failed)
assert checks==8640
print('PASS 8640/8640')
