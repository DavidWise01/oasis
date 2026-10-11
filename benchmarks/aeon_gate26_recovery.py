"""Gate26: append-only lineage repair and bounded left-first audit.
Seven-force weights and closure thresholds remain symbolic assumptions.
"""
from dataclasses import dataclass
from aeon_gate25_force_closure import evaluate

@dataclass(frozen=True)
class Snapshot:
    tick:int
    origin:tuple[int,int,int]
    credits:tuple[int,int,int]
    effective:tuple[int,int,int]
    closure:bool
    event:str

def simulate(origin=(10,19,19),cells=(1,)*20,weights=(1,)*7,max_ticks=16):
    if len(origin)!=3 or any(not isinstance(x,int) or not 0<=x<=20 for x in origin):
        raise ValueError('invalid shed history')
    if max_ticks<0: raise ValueError('negative ticks')
    credits=[0,0,0]; snapshots=[]
    for tick in range(max_ticks+1):
        effective=tuple(min(20,origin[i]+credits[i]) for i in range(3))
        result=evaluate(effective,cells,weights)
        if result.closed:
            event='closure'
        else:
            eligible=next((i for i in range(3) if effective[i]<16),None)
            event='repair_shed_'+str(eligible+1) if eligible is not None else 'hold_unresolved'
        snapshots.append(Snapshot(tick,tuple(origin),tuple(credits),effective,result.closed,event))
        if result.closed or event=='hold_unresolved' or tick==max_ticks:break
        credits[eligible]+=1
    return tuple(snapshots)

def test():
    trail=simulate();held=simulate(max_ticks=5);zero=simulate(max_ticks=0)
    healthy=simulate((19,19,19))
    checks={
     'initially held':not trail[0].closure,
     'six bounded repairs before closure':len(trail)==7 and trail[-1].credits==(6,0,0),
     'recovery closes':trail[-1].closure and trail[-1].effective==(16,19,19),
     'left-first always':all(x.event=='repair_shed_1' for x in trail[:-1]),
     'origin immutable in every snapshot':all(s.origin==(10,19,19) for s in trail),
     'snapshots append chronologically':all(s.tick==i for i,s in enumerate(trail)),
     'no instantaneous rescue':len(zero)==1 and not zero[0].closure,
     'insufficient time remains held':not held[-1].closure,
     'healthy lineage closes without repair':len(healthy)==1 and healthy[0].closure,
     'reproducible deterministic trajectory':trail==simulate(),
     'zero occupancy cannot be fixed by shed repair':not simulate(cells=(0,)*20)[-1].closure,
     'repair bounded per step':all(sum(trail[i+1].credits)-sum(trail[i].credits)==1 for i in range(len(trail)-1)),
    }
    for label,ok in checks.items():print(('PASS' if ok else 'FAIL'),label)
    print(f'{sum(checks.values())}/{len(checks)} PASS; ticks={trail[-1].tick}; closure={trail[-1].closure}')
    assert all(checks.values())
if __name__=='__main__':test()
