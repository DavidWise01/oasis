# Experiment 006: SU(3) invariant 3 + 5 singlets
import numpy as np
from scipy.linalg import block_diag
rng=np.random.default_rng(6006)
L=[[[0,1,0],[1,0,0],[0,0,0]],[[0,-1j,0],[1j,0,0],[0,0,0]],[[1,0,0],[0,-1,0],[0,0,0]],[[0,0,1],[0,0,0],[1,0,0]],[[0,0,-1j],[0,0,0],[1j,0,0]],[[0,0,0],[0,0,1],[0,1,0]],[[0,0,0],[0,0,-1j],[0,1j,0]],np.diag([1,1,-2])/np.sqrt(3)]
T=np.array(L,dtype=complex)/2
G=[block_diag(t,np.zeros((5,5))) for t in T]
K=rng.normal(size=(3,5))+1j*rng.normal(size=(3,5));K/=np.linalg.norm(K)
Hmix=np.block([[np.zeros((3,3)),K],[K.conj().T,np.zeros((5,5))]])
def residual(H):return max(np.linalg.norm(H@g-g@H) for g in G)
A=rng.normal(size=(5,5))+1j*rng.normal(size=(5,5));A=(A+A.conj().T)/2
Hinv=block_diag(0.7*np.eye(3),A)
R=rng.normal(size=(8,8))+1j*rng.normal(size=(8,8));R=(R+R.conj().T)/2
Hproj=block_diag(np.trace(R[:3,:3])/3*np.eye(3),R[3:,3:])
M=np.concatenate([np.kron(np.eye(5),t) for t in T],axis=0)
s=np.linalg.svd(M,compute_uv=False)
assert residual(Hmix)>1e-6 and residual(Hinv)<1e-12 and residual(Hproj)<1e-12 and min(s)>1e-8
print('coupled:',residual(Hmix),'invariant:',residual(Hinv),'projected:',residual(Hproj),'intertwiner nullity:',sum(s<1e-10))
