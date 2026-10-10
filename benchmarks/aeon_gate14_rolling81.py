"""Gate 14: symbolic rolling vessel and four 20-tick generations."""
from dataclasses import dataclass

LAYERS=('quanta','nuclear','atomic','cellular')

@dataclass(frozen=True)
class Event:
    tick: int
    generation: int
    skin: int
    kind: str


def run(vessel='i', ticks=80):
    assert ticks >= 0
    log=[Event(0,0,0,'seed')]
    for tick in range(1,ticks+1):
        gen=(tick-1)//20+1
        skin=(tick-1)%20+1
        log.append(Event(tick,gen,skin,'shed' if skin==20 else 'step'))
    return {'vessel':vessel,'events':tuple(log),'controller':1}


def test():
    r=run()
    e=r['events']
    checks={
        '81 retained records':len(e)==81,
        'one preserved vessel':r['vessel']=='i',
        'four generations':set(x.generation for x in e)==set(range(5)),
        '20 ticks per generation':all(sum(x.generation==g for x in e)==20 for g in range(1,5)),
        'generation boundaries':[(x.tick,x.generation) for x in e if x.kind=='shed']==[(20,1),(40,2),(60,3),(80,4)],
        '80 skin plus 1 controller':80+r['controller']==81,
        'append-only chronology':all(x.tick==j for j,x in enumerate(e)),
        'seed untouched':e[0]==Event(0,0,0,'seed'),
        'next cycle independent':run(ticks=100)['events'][-1]==Event(100,5,20,'shed'),
    }
    for k,v in checks.items():print(('PASS' if v else 'FAIL'), k)
    assert all(checks.values())
    print(f'{len(checks)}/{len(checks)} PASS')
if __name__=='__main__':test()
