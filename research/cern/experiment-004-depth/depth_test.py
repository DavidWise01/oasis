# Experiment 004: recursively embedded SU(3) depth stress test
# Three active color states in each 8-slot box; five inert auxiliaries.
# Factorized sequential propagation, NOT the full 8**depth tensor Hilbert space.
import numpy as np
import json

L=[[[0,1,0],[1,0,0],[0,0,0]],[[0,-1j,0],[1j,0,0],[0,0,0]],[[1,0,0],[0,-1,0],[0,0,0]],[[0,0,1],[0,0,0],[1,0,0]],[[0,0,-1j],[0,0,0],[1j,0,0]],[[0,0,0],[0,0,1],[0,1,0]],[[0,0,0],[0,0,-1j],[0,1j,0]],np.diag([1,1,-2])/np.sqrt(3)]
T=np.array(L,dtype=complex)/2
rng=np.random.default_rng(4004)
def unitary():
 a=rng.normal(size=8);H=np.einsum('i,ijk->jk',a,T);w,v=np.linalg.eigh(H);return (v*np.exp(1j*w))@v.conj().T
def test(depth):
 max_u=max_norm=max_leak=0.;psi=rng.normal(size=3)+1j*rng.normal(size=3);psi/=np.linalg.norm(psi)
 for i in range(depth):
  U=unitary();full=np.eye(8,dtype=complex);full[:3,:3]=U
  max_u=max(max_u,np.linalg.norm(full.conj().T@full-np.eye(8)))
  embedded=full@np.r_[psi,np.zeros(5,dtype=complex)];max_leak=max(max_leak,np.linalg.norm(embedded[3:]));psi=embedded[:3];max_norm=max(max_norm,abs(np.linalg.norm(psi)-1))
 U=unitary();closure=max(np.linalg.norm((B:=U@A@U.conj().T)-sum((2*np.trace(B@G))*G for G in T)) for A in T)
 return dict(depth=depth,unitarity=float(max_u),norm_drift=float(max_norm),leakage=float(max_leak),closure=float(closure),pass_all=max(max_u,max_norm,max_leak,closure)<1e-9)
if __name__=='__main__':
 for d in [1,2,3,5,10,25,50,100,250,500,1000,2500,5000,10000]: print(json.dumps(test(d)))
