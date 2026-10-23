"""KET Experiment 10: 2:2:4:8 phase-sensitive receiver, dark-reference and GLS comparison.
Requires numpy. Synthetic sensor data; not a hardware RF/optical measurement.
"""
import numpy as np
FS,N,F=1000,2000,73
G=np.array([0]*2+[1]*2+[2]*4+[3]*8)
B=np.flatnonzero((np.fft.rfftfreq(N,1/FS)>=15)&(np.fft.rfftfreq(N,1/FS)<=250))
HZ=np.fft.rfftfreq(N,1/FS)[B]
def gain(gap):
    cb=2e-12/gap; co=20e-12
    fc=1/(2*np.pi*2e6*(cb+co))
    return cb/(cb+co)/np.hypot(1,F/fc)
def setup(gap,common,ind=.4,reference=.3):
    signal=np.r_[.85**G*gain(gap)/gain(1),0.]
    cov=np.diag([ind**2]*16+[reference**2])+common**2*np.ones((17,17))
    mean=np.r_[[1/16]*16,0.]
    subtract=np.r_[[1/16]*16,-1.]
    optimal=np.linalg.solve(cov,signal)
    optimal=optimal/(signal@optimal)
    return signal,np.array([mean,subtract,optimal])
def generate(rng,k,signal,common,present):
    t=np.arange(N)/FS
    phases=rng.uniform(0,2*np.pi,k)
    wave=np.sin(2*np.pi*F*t[None,:]+phases[:,None])
    x=np.concatenate([rng.normal(0,.4,(k,N,16)),rng.normal(0,.3,(k,N,1))],axis=2)
    x+=rng.normal(0,common,(k,N,1))
    if present:x+=.055*wave[:,:,None]*signal
    return x
def spectral(x,weights):
    combined=np.einsum('tnc,mc->tmn',x,weights)
    powers=np.abs(np.fft.rfft(combined,axis=2))[:,:,B]
    idx=np.argmax(powers,axis=2)
    return powers.max(axis=2),HZ[idx]
def case(gap,common,seed):
    rng=np.random.default_rng(seed)
    s,w=setup(gap,common)
    train,_=spectral(generate(rng,220,s,common,False),w)
    threshold=np.quantile(train,.99,axis=0)
    null,_=spectral(generate(rng,120,s,common,False),w)
    signal,peaks=spectral(generate(rng,120,s,common,True),w)
    correct=((signal>threshold)&(np.abs(peaks-F)<=.5)).mean(axis=0)
    false=(null>threshold).mean(axis=0)
    return [list(np.round(correct*100,1)),list(np.round(false*100,1))]
def main():
    assert len(G)==16 and gain(.85)>gain(1)>gain(1.15)
    for gi,g in enumerate((.85,1,1.15)):
        for ci,c in enumerate((0,.45,1.8)):
            hits,false=case(g,c,184257+100*gi+ci)
            print('gap',g,'common',c,'correct % [avg, reference, GLS]',hits,'false %',false)
    print('PASS: null-calibrated thresholds, independent test samples, 16 optical+1 reference')
    print('LIMIT: GLS uses exact modeled covariance, giving an optimistic upper bound.')
if __name__=='__main__':main()
