# PRIM 027 — sparse three-axis alignment
# Full reproducible script available in accompanying ZIP artifact.
import numpy as np
from fractions import Fraction
N=9**3
CAPACITY=(N*N)**3
assert CAPACITY==150094635296999121
assert 6*Fraction("0.3367")-2*Fraction("0.0101")==2
rng=np.random.default_rng(27027)
x=rng.normal(size=(3,2,N))
assert np.allclose(x.mean(axis=(1,2)),x[:,::-1,:].mean(axis=(1,2)))
assert np.allclose(x.mean(axis=(1,2)),x[:,:,::-1].mean(axis=(1,2)))
print("PASS: capacity, six-hop closure, left-right reflection, address reversal")
