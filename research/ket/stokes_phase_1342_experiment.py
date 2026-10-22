"""Reduced-order 24-sector breathing pump toy experiment. Not Navier-Stokes."""
import math
N=24
FORWARD=(1,3,4,2)
REVERSE=tuple(reversed(FORWARD))
def simulate(order,offset=.15,cycles=100,steps=240):
    sign=1 if order==FORWARD else (-1 if order==REVERSE else 0)
    if not sign:raise ValueError("unknown phase order")
    dt=2*math.pi/steps
    total=0.
    for _ in range(cycles):
        for j in range(steps):
            t=j*dt
            q1=math.cos(t)
            q2=math.cos(t-sign*2*math.pi*offset)
            d1=-math.sin(t)
            d2=-math.sin(t-sign*2*math.pi*offset)
            total+=(q1*d2-q2*d1)*dt
    return total/cycles
def test():
    f=simulate(FORWARD);r=simulate(REVERSE);z=simulate(FORWARD,0)
    assert f>0 and r<0 and math.isclose(f,-r,rel_tol=1e-10)
    assert abs(z)<1e-10
    assert all(math.isclose(simulate(FORWARD,cycles=c),f,rel_tol=1e-10) for c in (1,10,100))
    print("PASS", f,r,z)
    print("LIMITATION: imposed phase direction determines transport sign; not validated fluid dynamics.")
if __name__=="__main__":test()
