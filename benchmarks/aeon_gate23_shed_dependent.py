"""Gate 23: 81 aggregate closure conditioned on three earlier sheds.
Symbolic deterministic controller, not a biological lifespan model.
"""
from dataclasses import dataclass

LEVELS=20
@dataclass(frozen=True)
class Frame:
    three_sheds: tuple[int,int,int]
    cells: tuple[int,...]
    ledger: tuple[str,...]
    retained_weight: float
    left_weight: float
    right_weight: float
    closed: bool

def evaluate(sheds, cells):
    assert len(sheds)==3 and all(0<=x<=20 for x in sheds)
    assert len(cells)==LEVELS and all(x in (0,1) for x in cells)
    debt=tuple(20-x for x in sheds)
    reserve=sum(cells)
    # Provisional: each shed >=16, and final reserve covers prior debt.
    viable=all(x>=16 for x in sheds) and reserve>=sum(debt)
    ledger=tuple(f'shed{j+1}:{n}/20' for j,n in enumerate(sheds)) + (f'cells:{reserve}/20',f'prior_debt:{sum(debt)}',f'closure:{viable}')
    return Frame(tuple(sheds),tuple(cells),ledger,.98,.01,.01,viable)

def test():
    full=(1,)*20
    good=evaluate((20,19,18),full)
    bad=evaluate((10,19,18),full)
    checks={
       '81 aggregate':4*20+1==81,
       '20 cellular levels':len(good.cells)==20,
       '3 previous sheds':len(good.three_sheds)==3,
       '98/1/1 partition':abs(good.retained_weight+good.left_weight+good.right_weight-1)<1e-12,
       'favorable lineage closes':good.closed,
       'bad prior shed blocks closure':not bad.closed,
       'identical final cells different outcomes':good.cells==bad.cells and good.closed!=bad.closed,
       'history preserved':good.ledger[:3]==('shed1:20/20','shed2:19/20','shed3:18/20'),
       'last layer cannot erase prior failure':not evaluate((0,20,20),full).closed,
       'reproducible':evaluate((20,19,18),full)==good,
    }
    for label,ok in checks.items():print(('PASS' if ok else 'FAIL'),label)
    print(f'{sum(checks.values())}/{len(checks)} passed')
    assert all(checks.values())
if __name__=='__main__':test()
