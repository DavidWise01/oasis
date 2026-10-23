"""KET optical generational tuning: 2 grandmothers, 2 mothers, 4 daughters, 8 granddaughters."""
from math import erf,sqrt
import json
STAGES=[('G0','grandmother','orange',600,2,0),('G1','mother','green',530,2,1),('G2','daughter','teal',490,4,2),('G3','granddaughter','teal',490,8,3)]
DARK={300:100.,77:2.}
WIDTHS=[x/10 for x in range(10,1201)]
def metrics(width,gen,temp):
    signal=1000*(.85**gen)*erf((width/2)/(sqrt(2)*4))
    background=8*width
    snr=signal/sqrt(signal+background+DARK[temp]+25)
    return signal,background,snr
def optimize(gen,temp):
    width=max(WIDTHS,key=lambda w:metrics(w,gen,temp)[2])
    signal,bg,snr=metrics(width,gen,temp)
    return dict(width_nm=width,snr=round(snr,4),signal_counts=round(signal,2),background_counts=round(bg,2))
def main():
    results=[]
    for temperature in (300,77):
        for code,role,color,wl,count,gen in STAGES:
            o=optimize(gen,temperature)
            results.append(dict(generation=code,role=role,color=color,wavelength_nm=wl,nodes=count,temperature_K=temperature,**o))
            print(f"{temperature}K {code}: width={o['width_nm']}nm SNR={o['snr']}")
    assert [s[4] for s in STAGES]==[2,2,4,8] and sum(s[4] for s in STAGES)==16
    for g in range(4):
        assert optimize(g,77)['snr']>optimize(g,300)['snr']
        for temp in (300,77):
            best=optimize(g,temp)['snr']
            assert all(best>=round(metrics(w,g,temp)[2],4) for w in WIDTHS)
    print('PASS: 16 nodes, 8 optimized stage-temperature cases')
    print('LIMIT: synthetic photon model; no real cryogenic detector evidence.')
if __name__=='__main__':main()
