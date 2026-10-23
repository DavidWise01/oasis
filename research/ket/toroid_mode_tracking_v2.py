"""Track peaks of the 24-section toroidal circuit across bridge gap changes.
Requires numpy, scipy, and distributed_toroid.py (same directory or PYTHONPATH).
This is a circuit approximation, not an electromagnetic field measurement.
"""
import json
import numpy as np
from scipy.signal import find_peaks
from scipy.optimize import minimize_scalar
from distributed_toroid import response
GAPS=(0.85,1.0,1.15)
def spectrum(gap,count):
    freqs=np.linspace(10e6,800e6,count)
    signal=np.array([response(f,gap)[0] for f in freqs])
    indices,_=find_peaks(signal,prominence=max(signal)*.008,distance=max(3,count//150))
    peaks=[]
    for idx in indices:
        fit=minimize_scalar(lambda hz:-response(hz,gap)[0],bounds=(freqs[idx-1],freqs[idx+1]),method='bounded',options={'xatol':10})
        peaks.append({'mhz':round(float(fit.x)/1e6,5),'mv':round(float(-fit.fun)*1e3,5)})
    return sorted(peaks,key=lambda p:p['mhz'])
def match(previous,current,tolerance=30):
    free=set(range(len(current)));out=[]
    for old in previous:
        if not free:break
        idx=min(free,key=lambda i:abs(current[i]['mhz']-old['mhz']))
        step=current[idx]['mhz']-old['mhz']
        if abs(step)<=tolerance:
            out.append({'from_mhz':old['mhz'],'to_mhz':current[idx]['mhz'],'shift_mhz':round(step,5)})
            free.remove(idx)
    return out
def main():
    coarse={g:spectrum(g,500) for g in GAPS}
    fine={g:spectrum(g,1000) for g in GAPS}
    for g in GAPS:
        same_grid=match(coarse[g],fine[g],4)
        assert len(same_grid)>=2
        print('gap',g,'refined modes',fine[g])
    assert match(fine[.85],fine[1.0]) and match(fine[1.0],fine[1.15])
    assert response(130e6,1.0,coupling=0)[0]==0
    print('PASS 3 branches, resolution consistency, continuous nearby-gap matching, null-coupling control')
    print('LIMITATION nearest-peak matching may fail near crossings; not Maxwell/FDTD.')
if __name__=='__main__':main()
