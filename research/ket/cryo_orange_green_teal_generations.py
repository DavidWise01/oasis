"""Illustrative photon-counting optical tuner: three generations, two temperatures."""
from math import erf,sqrt
STAGES=(('Grandmother','orange',600.,60.,0),('Mother','green',530.,25.,1),('Daughter','teal',490.,10.,2))
DARK={300:100.,77:2.}
def measure(generation,width_nm,temp):
    signal=1000.*(.85**generation)*erf((width_nm/2)/(sqrt(2)*4.))
    background=8.*width_nm
    snr=signal/sqrt(signal+background+DARK[temp]+25.)
    return signal,snr
def test():
    for name,color,wavelength,width,g in STAGES:
        room=measure(g,width,300);cryo=measure(g,width,77)
        assert cryo[1]>room[1]>0
        print(f'{name:12s} {color:6s} {wavelength:.0f} nm | {room[1]:.2f} room SNR | {cryo[1]:.2f} cryo SNR')
    assert measure(2,10,77)[1]>measure(2,60,77)[1]
    assert measure(2,10,77)[1]<measure(0,60,77)[1]
    print('PASS: cryo lowers modeled noise; daughter fine tuning improves its own SNR without fully recovering ancestor SNR')
    print('ASSUMPTIONS: fixed 1000 input photons/window, 15% attenuation/generation, 4 nm Gaussian line sigma, background 8 counts/nm, 25 read variance, 100 vs 2 dark counts.')
    print('LIMITATION: no actual detector/optical filter measurement or cryogenic test')
if __name__=='__main__':test()
