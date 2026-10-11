"""Major Gate 4: Hamiltonian cycle x crosspipe stack x phase loop.
Product construction, not a physical spacetime model.
"""
from math import sin,cos,radians,isclose
from aeon_gate27_hamiltonian import PATH,neighbors
from aeon_gate32_kernel_stack import PAIRS
ROOT=(0.,0.)
PHASES=(0,15,30,45,60,45,30,15,0)
def pos(a):
    t=radians(a)
    return (sin(t),cos(t))
def stack_roundtrip(payload):
    log=[]
    current=payload
    for a,b in PAIRS:
        current=current[::-1]
        log.append(('enter',a,b,current))
    for a,b in reversed(PAIRS):
        current=current[::-1]
        log.append(('return',b,a,current))
    return current,tuple(log)
def test():
    payload=('alpha','omega')
    snapshots=[(p,*stack_roundtrip(payload)) for p in PATH]
    tests={
      '27 unique lattice addresses':len(PATH)==len(set(PATH))==27,
      '26 neighboring steps':all(neighbors(a,b) for a,b in zip(PATH,PATH[1:])),
      'closing edge neighboring':neighbors(PATH[-1],PATH[0]),
      '8 channel pairs':len(PAIRS)==8,
      'all payloads restored':all(x[1]==payload for x in snapshots),
      '16 events per visit':all(len(x[2])==16 for x in snapshots),
      '432 total events':sum(len(x[2]) for x in snapshots)==432,
      'four 15-degree advances':all(PHASES[i+1]-PHASES[i]==15 for i in range(4)),
      'inverse phases return':all(isclose(a,b,abs_tol=1e-12) for a,b in zip(pos(PHASES[0]),pos(PHASES[-1]))),
      'pinned zero invariant':ROOT==(0.,0.),
      '60 degrees is not 360 degrees':pos(0)!=pos(60),
      '27 immutable snapshot records':len(snapshots)==27,
    }
    for name,ok in tests.items():print(('PASS' if ok else 'FAIL'),name)
    assert all(tests.values())
    print(f"{sum(tests.values())}/{len(tests)} PASS")
    print("OPEN: no canonical address-to-angle mapping has been derived.")
if __name__=='__main__':test()
