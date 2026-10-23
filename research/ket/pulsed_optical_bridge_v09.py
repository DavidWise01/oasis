"""KET Exp 09: synthetic 73-Hz optical modulation through capacitive bridge."""
import numpy as np
FS=2000.;N=4000;T=np.arange(N)/FS;F=73.
GENERATIONS=[0]*2+[1]*2+[2]*4+[3]*8
def gain(gap):
    cb=2e-12/gap;cout=20e-12;r=2e6
    fc=1/(2*np.pi*r*(cout+cb))
    return cb/(cb+cout)/np.sqrt(1+(F/fc)**2)
def sample(gap,shared,seed,present):
    rng=np.random.default_rng(seed)
    a=np.array([.85**g for g in GENERATIONS])*gain(gap)/gain(1)
    pulse=(np.sin(2*np.pi*F*T)>0).astype(float)
    pulse-=pulse.mean()
    signal=(.25*pulse[:,None]*a[None,:]) if present else 0.
    return signal+rng.normal(0,.40,(N,16))+rng.normal(0,.40*shared,(N,1))
def recover(values):
    magnitude=np.abs(np.fft.rfft(values.mean(axis=1)))
    freq=np.fft.rfftfreq(N,1/FS)
    band=(freq>=15)&(freq<=250)
    candidate=np.where(band)[0];index=candidate[np.argmax(magnitude[candidate])]
    floor=np.median(magnitude[band & (np.abs(freq-freq[index])>3)])
    ratio=magnitude[index]/floor
    return freq[index],ratio,ratio>=6
if __name__=='__main__':
    assert len(GENERATIONS)==16
    assert gain(.85)>gain(1)>gain(1.15)
    for gap in (.85,1.,1.15):
        for shared in (0.,.5,2.):
            good=bad=0
            for i in range(20):
                f,r,lock=recover(sample(gap,shared,184257+i,True))
                good+=int(lock and abs(f-F)<=.5)
                bad+=int(recover(sample(gap,shared,994184+i,False))[2])
            print(f'gap={gap:.2f}, common_noise={shared:.1f}, correct={good}/20, false={bad}/20')
            assert bad==0
    print('LIMIT: phenomenological optical-electrical model, not RF or hardware verification.')
