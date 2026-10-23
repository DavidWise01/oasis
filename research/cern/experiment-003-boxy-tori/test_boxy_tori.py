import numpy as np
from itertools import product

j=1j
lambdas=[
[[0,1,0],[1,0,0],[0,0,0]],
[[0,-j,0],[j,0,0],[0,0,0]],
[[1,0,0],[0,-1,0],[0,0,0]],
[[0,0,1],[0,0,0],[1,0,0]],
[[0,0,-j],[0,0,0],[j,0,0]],
[[0,0,0],[0,0,1],[0,1,0]],
[[0,0,0],[0,0,-j],[0,j,0]],
np.diag([1,1,-2])/np.sqrt(3)
]
T=[np.asarray(x,dtype=complex)/2 for x in lambdas]
c=lambda A: np.array([2*np.trace(A@t) for t in T])
tests={}
tests["Hermiticity"]=max(np.linalg.norm(t-t.conj().T) for t in T)
tests["Tracelessness"]=max(abs(np.trace(t)) for t in T)
tests["Normalization"]=max(abs(np.trace(T[a]@T[b])-(.5 if a==b else 0)) for a,b in product(range(8),repeat=2))
tests["Commutator closure"]=max(np.linalg.norm((A:=T[a]@T[b]-T[b]@T[a])-sum((1j*c(A/1j)[k]*T[k] for k in range(8)))) for a,b in product(range(8),repeat=2))
V=np.eye(8,dtype=complex)[:,:3]
rng=np.random.default_rng(371)
errors=np.zeros(3)
for _ in range(128):
    weights=rng.normal(size=8); weights/=np.linalg.norm(weights)
    H=sum(weights[k]*T[k] for k in range(8))
    d,W=np.linalg.eigh(H)
    U=(W*np.exp(-1j*d*1.137))@W.conj().T
    U8=np.eye(8)+V@(U-np.eye(3))@V.conj().T
    psi=rng.normal(size=3)+1j*rng.normal(size=3)
    psi/=np.linalg.norm(psi)
    phi=U8@(V@psi)
    errors=np.maximum(errors,[np.linalg.norm(U8.conj().T@U8-np.eye(8)),abs(np.linalg.norm(phi)-1),np.linalg.norm((np.eye(8)-V@V.conj().T)@phi)])
tests.update(zip(["8-state unitarity","State norm","Auxiliary leakage"],errors))
for name,err in tests.items():
    print(f"{name}: {err:.3e} "+("PASS" if err<1e-10 else "FAIL"))
assert len(tests)==7 and all(v<1e-10 for v in tests.values())
print("7/7 PASS: encoding only; no experimental proof of quark substructure")
