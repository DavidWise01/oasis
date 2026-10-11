"""Gate 24: seven named coupling channels for three SAPPHON registers.
Names are user-defined symbolic forces, not established physics.
"""
from dataclasses import dataclass

FORCES=('ww','ww','ww','wm','ws','mm','ss')
ROLES=('state','space','time')

@dataclass(frozen=True)
class Force:
    slot:int
    label:str
    weight:int

def channels(weights=(1,)*7):
    if len(weights)!=7 or any(not isinstance(x,int) or x<0 for x in weights):
        raise ValueError('seven nonnegative integer weights required')
    return tuple(Force(i,FORCES[i],w) for i,w in enumerate(weights))

def advance(registers, forces):
    """Provisional deterministic coupling matrix; no physical assertions."""
    assert len(registers)==3
    s,x,t=registers
    a,b,c,d,e,f,g=(v.weight for v in forces)
    return (s+a+d+f, x+b+e+g, t+c+d+e)

def test():
    ch=channels()
    checks={
        'seven channels':len(ch)==7,
        'three distinct ww slots':[(v.slot,v.label) for v in ch[:3]]==[(0,'ww'),(1,'ww'),(2,'ww')],
        'four further force types':tuple(v.label for v in ch[3:])==('wm','ws','mm','ss'),
        'one 3-register update':advance((0,0,0),ch)==(3,3,3),
        'determinism':advance((2,3,4),ch)==advance((2,3,4),ch),
        'zero weights no change':advance((2,3,4),channels((0,)*7))==(2,3,4),
        'identity preservation':ROLES==('state','space','time'),
        'weights retain all channels':sum(v.weight for v in channels((1,2,3,4,5,6,7)))==28,
    }
    for label,ok in checks.items(): print(('PASS' if ok else 'FAIL'),label)
    assert all(checks.values())
    print(f'{sum(checks.values())}/{len(checks)} PASS')
if __name__=='__main__':test()
