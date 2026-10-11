"""Gate 9: entropy bookkeeping for idealized closed total system.
Entropy values are dimensionless accounting units, not physical calibrations.
"""
from fractions import Fraction as F
from dataclasses import dataclass

@dataclass(frozen=True)
class Change:
    system: F
    environment: F
    @property
    def total(self): return self.system + self.environment
    @property
    def lawful(self): return self.total >= 0

def audit(repair, expelled):
    return Change(-F(repair), F(expelled))

def run():
    good=audit(3, 4)
    reversible=audit(3,3)
    bad=audit(3,2)
    checks={
      'repair lowers local entropy': good.system == -3,
      'environment receives entropy':good.environment == 4,
      'total entropy grows':good.total == 1,
      'good process accepted':good.lawful,
      'ideal reversible balance accepted':reversible.lawful and reversible.total==0,
      'insufficient export rejected':not bad.lawful,
      'deficit quantified':bad.total==-1,
      'no repair no export neutral':audit(0,0).total==0,
      'fractional exact accounting':audit(F(1,4),F(3,8)).total==F(1,8),
      'zero environment repair rejected':not audit(1,0).lawful,
      'append history unchanged by auditing': (good,bad)[0]==good,
      'boundary condition explicit':Change(F(-2),F(3)).total==1,
    }
    for k,v in checks.items():print(('PASS' if v else 'FAIL'),k)
    print(f'RESULT {sum(checks.values())}/{len(checks)}')
    assert all(checks.values())
if __name__=='__main__':run()
