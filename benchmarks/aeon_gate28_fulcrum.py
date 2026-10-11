"""Gate 28: fixed lower fulcrum, four 15-degree phases and inverse closure."""
from math import cos, sin, radians, isclose
FULCRUM=(0.0,0.0)
RADIUS=1.0

def moving_dot(deg):
    # 0 degrees is vertically up from the bottom pivot.
    a=radians(deg)
    return (RADIUS*sin(a), RADIUS*cos(a))

def test():
    forward=[0,15,30,45,60]
    backwards=[45,30,15,0]
    trace=forward+backwards
    coords=[moving_dot(d) for d in trace]
    checks={
      'four 15 degree increments': all(forward[i+1]-forward[i]==15 for i in range(4)),
      'forward sweep 60 degrees':forward[-1]==60,
      'inverse sweep restores angle':trace[-1]==0,
      'fixed bottom fulcrum':FULCRUM==(0.,0.),
      'initial movable dot over fulcrum':moving_dot(0)==(0.,1.),
      'distance invariant':all(isclose(x*x+y*y,1,abs_tol=1e-12) for x,y in coords),
      'return coordinate matches':all(isclose(a,b,abs_tol=1e-12) for a,b in zip(coords[0],coords[-1])),
      'five distinct positions':len(set(forward))==5,
      'dot not confused with pinned pivot':all(c != FULCRUM for c in coords),
    }
    for name,ok in checks.items():print(('PASS' if ok else 'FAIL'),name)
    print(f'{sum(checks.values())}/{len(checks)} PASS')
    assert all(checks.values())
if __name__=='__main__':test()
