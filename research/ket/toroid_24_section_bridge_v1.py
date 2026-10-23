"""24-section toroidal transmission-line circuit approximation. NOT a Maxwell/FDTD solver."""
import numpy as np
N=24
L_TOTAL=180e-9
C_GROUND_TOTAL=12e-12
R_TOTAL=1.2
C_BRIDGE=3e-12
SOURCE_AMPLITUDE=.01
R_SOURCE=50.
def response(frequency_hz,gap_scale=1.,coupling=1.,bridge=True):
    if frequency_hz<=0 or gap_scale<=0:raise ValueError('positive frequency and gap required')
    w=2*np.pi*frequency_hz;L=L_TOTAL/N;R=R_TOTAL/N;Cg=C_GROUND_TOTAL/N
    Y=np.zeros((N,N),dtype=complex)
    for i in range(N):
        j=(i+1)%N;z=R+1j*w*L
        if bridge and i==N-1:z+=1/(1j*w*(C_BRIDGE/gap_scale))
        y=1/z;Y[i,i]+=y;Y[j,j]+=y;Y[i,j]-=y;Y[j,i]-=y
    Y[np.diag_indices(N)]+=1j*w*Cg
    Y[0,0]+=1/R_SOURCE
    b=np.zeros(N,dtype=complex);b[0]=SOURCE_AMPLITUDE*coupling/R_SOURCE
    return abs(np.linalg.solve(Y,b)[12])
def sweep(gap):
    freqs=np.linspace(10e6,800e6,500)
    amps=np.array([response(f,gap) for f in freqs])
    idx=int(np.argmax(amps))
    return float(freqs[idx]),float(amps[idx])
def test():
    assert response(120e6,coupling=0)==0
    results=[sweep(g) for g in (.85,1.,1.15)]
    for gap,(f,a) in zip((.85,1.,1.15),results):
        assert np.isfinite(a) and a>0
        print(f'gap {gap}: peak {f/1e6:.2f} MHz, transfer {a*1e3:.4f} mV')
    assert len(set(f for f,a in results))>1
    print('PASS: zero-coupling and gap-dependent sampled peaks')
    print('CAUTION: strongest-peak switching is not continuous mode tracking.')
    print('LIMIT: 24-section lumped network; no radiation physics or real antenna.')
if __name__=='__main__':test()
