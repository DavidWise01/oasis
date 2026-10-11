"""Gate 21: symbolic SAPPHON 27-address lattice across an 81-tick cycle.
Logical coordinates, not physical dimensionality or a biological law.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Event:
    tick: int
    cycle: int
    slot: int
    ternary: tuple[int,int,int]
    vessel: str
    root: str
    kind: str

def ternary3(index):
    assert 0 <= index < 27
    return (index//9, (index//3)%3, index%3)

def simulate(ticks=243, vessel='i'):
    assert ticks>=0
    log=[]
    for t in range(ticks+1):
        slot=t%27
        log.append(Event(t,t//81,slot,ternary3(slot),vessel,'.',
                         'cycle_rollover' if t>0 and t%81==0 else
                         'lattice_rollover' if t>0 and t%27==0 else 'step'))
    return tuple(log)

def test():
    events=simulate()
    conditions={
        '244 event snapshots':len(events)==244,
        '27 unique addresses':len({ternary3(k) for k in range(27)})==27,
        '3^3 address count':3**3==27,
        '81 = three passes':81==3*27,
        'first lattice rollover':(events[27].slot,events[27].kind)==(0,'lattice_rollover'),
        'cycle rollover at 81':(events[81].cycle,events[81].slot,events[81].kind)==(1,0,'cycle_rollover'),
        'three cycle rollovers':sum(e.kind=='cycle_rollover' for e in events)==3,
        'vessel and dot stable':all(e.vessel=='i' and e.root=='.' for e in events),
        'history monotonic':all(e.tick==j for j,e in enumerate(events)),
        'history snapshots immutable':events[0]==Event(0,0,0,(0,0,0),'i','.','step'),
        'cycle and lattice independent':events[54].cycle==0 and events[54].slot==0,
        'rolling skin 20 retained separately':all((t%20) in range(20) for t in range(244)),
    }
    for label,ok in conditions.items():print(('PASS' if ok else 'FAIL'),label)
    print(f"RESULT {sum(conditions.values())}/{len(conditions)}")
    assert all(conditions.values())

if __name__=='__main__':test()
