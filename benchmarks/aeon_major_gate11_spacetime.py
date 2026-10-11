"""Gate 11: Lorentz invariance checks in 1+1-dimensional spacetime.
Demonstrates special relativity, not derivation of curved spacetime gravity.
"""
import math
from fractions import Fraction as F
def boost(ct,x,beta):
    assert abs(beta)<1
    b=float(beta);gamma=1/math.sqrt(1-b*b)
    return gamma*(float(ct)-b*float(x)),gamma*(float(x)-b*float(ct))
def interval(ct,x):return ct*ct-x*x
def close(a,b):return math.isclose(float(a),float(b),rel_tol=1e-12,abs_tol=1e-12)
def run():
    samples=[(F(0),F(0)),(F(5),F(3)),(F(3),F(5)),(F(1),F(1)),(F(-7),F(2))]
    betas=[F(0),F(3,5),F(-5,13)]
    cases=[(ct,x,b) for ct,x in samples for b in betas]
    checks={
       '15 boost cases':len(cases)==15,
       'interval invariant':all(close(interval(*boost(ct,x,b)),interval(ct,x)) for ct,x,b in cases),
       'pinned origin':all(boost(0,0,b)==(0,0) for b in betas),
       'inverse boost':all(all(close(a,z) for a,z in zip(boost(*boost(ct,x,b),-b),(ct,x))) for ct,x,b in cases),
       'timelike':interval(F(5),F(3))==16,
       'spacelike':interval(F(3),F(5))==-16,
       'null':interval(F(1),F(1))==0,
       'invalid scaling detected':interval(F(5),F(6))!=interval(F(5),F(3)),
       'subluminal relative speeds':all(abs(b)<1 for b in betas),
       'space-time mixed by boost':boost(5,3,F(3,5))!=(5.,3.),
    }
    for name,ok in checks.items():print(('PASS' if ok else 'FAIL'),name)
    print(f'{sum(checks.values())}/{len(checks)} PASS')
    assert all(checks.values())
if __name__=='__main__':run()
