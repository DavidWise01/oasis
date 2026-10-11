"""Gate 22: four symbolic clocks and append-only cumulative history."""
from dataclasses import dataclass
from math import lcm
SKIN=20
LATTICE=27
VESSEL=81
ALIGN=lcm(SKIN,LATTICE,VESSEL)
@dataclass(frozen=True)
class Frame:
    tick:int
    skin:int
    lattice:int
    vessel:int
    completed_vessels:int
    entropy_ledger:int
    identity:str='i'
    root:str='.'
def step(t:int)->Frame:
    return Frame(t,t%SKIN,t%LATTICE,t%VESSEL,t//VESSEL,t)
def run():
    history=tuple(step(t) for t in range(ALIGN+1))
    tests={
        'lcm 1620':ALIGN==1620,
        '20 skin resets':sum(t.skin==0 for t in history[1:])==81,
        '27 lattice resets':sum(t.lattice==0 for t in history[1:])==60,
        '81 vessel resets':sum(t.vessel==0 for t in history[1:])==20,
        'first simultaneous positive reset':next(t.tick for t in history[1:] if (t.skin,t.lattice,t.vessel)==(0,0,0))==ALIGN,
        'all phase counters reset':history[-1].skin==history[-1].lattice==history[-1].vessel==0,
        'father time does not reset':history[-1].entropy_ledger==1620,
        '20 complete vessel cycles':history[-1].completed_vessels==20,
        'identity remains stable':all(x.identity=='i' and x.root=='.' for x in history),
        'append-only chronological snapshots':all(x.tick==i for i,x in enumerate(history)),
        'frozen dataclass snapshot':history[0]==step(0),
        '81 year reset not skin reset':(step(81).skin,step(81).lattice,step(81).vessel)==(1,0,0),
    }
    for name,result in tests.items():print(('PASS' if result else 'FAIL'),name)
    print(f'RESULT {sum(tests.values())}/{len(tests)}; ALIGN={ALIGN}')
    assert all(tests.values())
if __name__=='__main__':run()
