"""Numerical photon-to-charge capacitive readout test; illustrative parameters only."""
import math
H=6.62607015e-34; C0=299792458.; Q=1.602176634e-19
STAGES=[('GM','orange',600,2,0),('MA','green',530,2,1),('DA','teal',490,4,2),('GDA','teal',490,8,3)]
QE=.65; PHOTONS=1e6; DT=.01; C_DET=10e-12; C_BRIDGE=2e-12; C_OUT=20e-12
TRANSFER=C_BRIDGE/(C_BRIDGE+C_OUT)
DARK={300:1e-12,77:1e-15}; READ={300:1000.,77:500.}
def sample(g,temp):
    signal=PHOTONS*.85**g*QE
    dark=DARK[temp]*DT/Q
    voltage=(signal*Q/C_DET)*TRANSFER
    snr=signal/math.sqrt(signal+dark+READ[temp]**2)
    return voltage,snr
if __name__=='__main__':
    assert sum(row[3] for row in STAGES)==16
    for temp in (300,77):
        for name,color,nm,nodes,g in STAGES:
            voltage,snr=sample(g,temp)
            assert voltage>0 and snr>0
            assert sample(g,77)[1]>sample(g,300)[1]
            energy=(H*C0/(nm*1e-9))/Q
            print(f'{temp} K {name} {color} {nm}nm {energy:.4f}eV bridge={voltage*1000:.4f}mV SNR={snr:.2f}')
    assert (0*Q/C_DET)*TRANSFER==0
    assert C_BRIDGE*0==0
    print('PASS: 16 nodes, 300/77K comparisons, no-photon control')
    print('LIMITATION: illustrative semiconductor parameters; not measured cryogenic response or RF reception.')
