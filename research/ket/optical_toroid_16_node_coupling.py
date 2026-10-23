"""16-node optical readout with simplified toroidal coupling and correlated noise. Requires numpy."""
import numpy as np
from math import erf,sqrt
rng=np.random.default_rng(184257)
GEN=[("GM",2,600,0),("MA",2,530,1),("DA",4,490,2),("GDA",8,490,3)]
nodes=[(name,nm,1000*.85**g*erf((18/2)/(sqrt(2)*4))) for name,count,nm,g in GEN for _ in range(count)]
s=np.array([node[2] for node in nodes]);n=len(s)
def ring_coupler(k=.08):
    eye=np.eye(n)
    return (1-2*k)*eye+k*np.roll(eye,1,axis=1)+k*np.roll(eye,-1,axis=1)
C=ring_coupler()
assert n==16 and np.allclose(C.sum(axis=1),1)
def experiment(rho,trials=5000):
    V=np.diag(s+8*18+2+25)+200*rho*np.ones((n,n))
    response=C@s;cov=C@V@C.T
    inv=np.linalg.solve(cov,response);fisher=response@inv;weights=inv/fisher
    noise=rng.multivariate_normal(np.zeros(n),cov,trials)
    measured=(noise+response)@weights
    null=noise@weights
    result=(response[0]/np.sqrt(cov[0,0]),np.sqrt(fisher),measured.mean(),null.mean())
    assert abs(result[2]-1)<.04 and abs(result[3])<.04
    return result
if __name__=="__main__":
    for rho in (0,.1,1,10):
        single,combined,estimate,null=experiment(rho)
        assert combined>single
        print(f"shared_noise={rho}: single={single:.3f}, combined={combined:.3f}, gain={combined/single:.3f}x, reconstructed={estimate:.4f}, null={null:.4f}")
    print("PASS synthetic model; no hardware or electromagnetic reception claim")
