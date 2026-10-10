"""Symbolic 81-year renewal cycle with non-resetting entropy ledger.
Not a physical law or a prediction of human lifespan.
"""
from dataclasses import dataclass

CYCLE = 81
@dataclass(frozen=True)
class State:
    age: int
    cycle: int
    phase: int
    entropy: int
    maintenance: int

def simulate(years, choices=None):
    choices = choices or {}
    states = [State(0, 0, 0, 0, 0)]
    for year in range(1, years+1):
        prior = states[-1]
        repair = int(bool(choices.get(year, False)))
        # Entropy ledger records gross stress, regardless of repairs.
        states.append(State(year, year//CYCLE, year%CYCLE,
                            prior.entropy+1, prior.maintenance+repair))
    return tuple(states)

def test():
    s = simulate(243, {20:True, 81:True, 100:True})
    checks = {
        '244 immutable snapshots': len(s)==244,
        'mother cycle at age 80': (s[80].cycle,s[80].phase)==(0,80),
        'mother reset at 81': (s[81].cycle,s[81].phase)==(1,0),
        'father ledger not reset at 81': s[81].entropy==81,
        'three full rolls': (s[243].cycle,s[243].phase)==(3,0),
        'ledger monotonic':all(s[i].entropy<=s[i+1].entropy for i in range(243)),
        'maintenance independent':s[243].maintenance==3,
        'retained origin':s[0]==State(0,0,0,0,0),
    }
    for k,v in checks.items():print(('PASS' if v else 'FAIL'),k)
    assert all(checks.values())
    print(f'{sum(checks.values())}/{len(checks)} PASS')
if __name__=='__main__':test()
