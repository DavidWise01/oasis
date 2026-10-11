"""Gate 8: Nuclear bookkeeping with exact integer mass and atomic numbers.
This validates reaction accounting, not nuclear reaction dynamics or energy.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Nuclide:
    name: str
    A: int
    Z: int
    def __post_init__(self):
        if not (0 <= self.Z <= self.A):
            raise ValueError('invalid isotope')

def totals(items):
    return tuple(sum(getattr(x, key) for x in items) for key in ('A','Z'))

def conserved(inputs, outputs):
    return totals(inputs) == totals(outputs)

d=Nuclide('2H',2,1)
t=Nuclide('3H',3,1)
he4=Nuclide('4He',4,2)
n=Nuclide('neutron',1,0)
he3=Nuclide('3He',3,2)
h=Nuclide('1H',1,1)

def test():
    checks={
      'D + T inputs A=5 Z=2':totals((d,t))==(5,2),
      'He4 + n outputs A=5 Z=2':totals((he4,n))==(5,2),
      'fusion conserves both':conserved((d,t),(he4,n)),
      'charge-only deceptive failure':sum(x.Z for x in (d,t))==he4.Z,
      'missing neutron detected':not conserved((d,t),(he4,)),
      'nucleon deficit exactly one':totals((d,t))[0]-totals((he4,))[0]==1,
      'reverse bookkeeping':conserved((he4,n),(d,t)),
      'individual neutron neutral':n.Z==0 and n.A==1,
      'invalid isotope rejected':False,
      'second balanced example':conserved((d,h),(he3,)),
    }
    try:Nuclide('bad',2,3)
    except ValueError:checks['invalid isotope rejected']=True
    for label,ok in checks.items():print(('PASS' if ok else 'FAIL'),label)
    print(f'RESULT {sum(checks.values())}/{len(checks)}')
    assert all(checks.values())
if __name__=='__main__':test()
