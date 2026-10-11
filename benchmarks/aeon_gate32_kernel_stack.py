"""Gate32: symbolic nested K crosspipe reversible stack.
Crossovers are explicitly defined swaps of two payload lanes; no physical claim.
"""
from dataclasses import dataclass

PAIRS=(('u24u','u42u'),('d24','d42'),('l24','l42'),('r24','r42'),('b24','b42'),('a24','a42'),('sel24','sel42'),('star24','star42'))
ROOT='/0\\'
@dataclass(frozen=True)
class Frame:
    stage: str
    channel: str
    payload: tuple
    root: str

def run(initial=('alpha','omega')):
    stack=[]
    log=[Frame('seed','.',initial,ROOT)]
    payload=initial
    for left,right in PAIRS:
        stack.append((left,right))
        payload=(payload[1],payload[0])
        log.append(Frame('enter',left+'|'+right,payload,ROOT))
    while stack:
        left,right=stack.pop()
        payload=(payload[1],payload[0])
        log.append(Frame('return',right+'|'+left,payload,ROOT))
    return payload,tuple(log),stack

def test():
    end,log,stack=run()
    enters=[x for x in log if x.stage=='enter']
    returns=[x for x in log if x.stage=='return']
    checks={
       'eight pairs':len(PAIRS)==8,
       '16 unique address tokens':len({x for p in PAIRS for x in p})==16,
       '17 append-only events':len(log)==17,
       'eight entered eight returned':len(enters)==len(returns)==8,
       'LIFO order': [x.channel for x in returns]==[b+'|'+a for a,b in reversed(PAIRS)],
       'original payload restored':end==('alpha','omega'),
       'root always pinned':all(x.root==ROOT for x in log),
       'stack empty after return':not stack,
       'intermediate pair swap':enters[0].payload==('omega','alpha'),
       'double application reversible':run(end)[0]==end,
       'history not erased':log[0].stage=='seed' and log[-1].stage=='return',
       'failure detection by missing return':log[-2].payload!=('alpha','omega'),
    }
    for name,ok in checks.items():print(('PASS' if ok else 'FAIL'),name)
    print(f"{sum(checks.values())}/{len(checks)} PASS")
    assert all(checks.values())
if __name__=='__main__':test()
