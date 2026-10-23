import numpy as np
import json
from pathlib import Path
N=10
def graph(bleed=.1,portal=.5,hold=1):
 W=np.zeros((N,N));W[0,1]=W[1,0]=hold
 for k in range(8):
  a=2+k;b=2+(k+1)%8
  W[1,a]=W[a,1]=portal
  W[a,b]=W[b,a]=bleed
 return W
def run(bleed,portal,seed,T=40,dt=.01):
 rng=np.random.default_rng(seed);W=graph(bleed,portal)
 theta=np.zeros(N);theta[2]=.8
 omega=rng.normal(0,.015,N);omega[:2]=0
 def f(x):return omega+(W*np.sin(x[None,:]-x[:,None])).sum(axis=1)
 for _ in range(int(T/dt)):
  k1=f(theta);k2=f(theta+dt*k1/2);k3=f(theta+dt*k2/2);k4=f(theta+dt*k3)
  theta+=dt*(k1+2*k2+2*k3+k4)/6
 return {"R":float(abs(np.exp(1j*theta).mean())),"incubator_error":float(abs(np.angle(np.exp(1j*(theta[0]-theta[1]))))),"T0_T4_error":float(abs(np.angle(np.exp(1j*(theta[2]-theta[6])))))}
W=graph()
assert np.allclose(W,W.T) and not np.any(np.diag(W))
assert np.count_nonzero(np.triu(W))==17
cases={}
for name,b,p in [('isolated',0,0),('portal_only',0,.5),('bleed_only',.1,0),('portal_bleed',.1,.5)]:
 cases[name]=[run(b,p,i) for i in range(8)]
summary={name:{k:float(np.mean([r[k] for r in rows])) for k in ['R','incubator_error','T0_T4_error']} for name,rows in cases.items()}
assert len(cases)==4 and all(len(r)==8 for r in cases.values())
print(json.dumps(summary,indent=2))
