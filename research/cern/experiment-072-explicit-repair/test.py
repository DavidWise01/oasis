from fractions import Fraction as F
HELD,VENT,HEAL,SAFE,COST=F('.10'),F('.02'),F('.005'),F('.02'),F('.03')
def simulate(resource,repair_at=None):
 state=-1;held=HELD;vented=damage=F(0);damage=F('.06');spent=F(0);success=None
 for tick in range(1,21):
  vent=min(held,VENT);held-=vent;vented+=vent
  damage=max(F(0),damage-HEAL)
  assert held+vented==HELD
  assert resource+spent==(F('.02') if repair_at==12 and resource==F('.02') else F('.03') if repair_at in (None,4,12) else F('.05'))
  if tick==repair_at and state==-1 and held==0 and damage<SAFE and resource>=COST:
   resource-=COST;spent+=COST;state=0;success=tick
 return state,success
assert simulate(F('.03'))==(-1,None)
assert simulate(F('.03'),4)==(-1,None)
assert simulate(F('.02'),12)==(-1,None)
assert simulate(F('.03'),12)==(0,12)
assert simulate(F('.05'),20)==(0,20)
print('PASS 5 scenarios; explicit repair only')
