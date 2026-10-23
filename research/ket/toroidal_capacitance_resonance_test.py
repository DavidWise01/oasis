"""Parameterized toroidal LC sensor: simplified series RLC demonstration."""
import math
EPS0=8.8541878128e-12; MU0=4*math.pi*1e-7
turns=12; major_radius=.03; core_radius=.006; area=.0001
L=MU0*turns**2*math.pi*core_radius**2/(2*math.pi*major_radius)
R=2.0; V=.01; stray=10e-12
rows=[]
for strain in (-.15,0,.15):
    d=.0005*(1+strain)
    C=EPS0*area/d+stray
    resonance=1/(2*math.pi*math.sqrt(L*C))
    bandwidth=R/(2*math.pi*L)
    def amplitude(freq,coupling=1):
        omega=2*math.pi*freq
        return (V*coupling)/math.hypot(R,omega*L-1/(omega*C))
    sweep=[resonance*(.7+i*.6/4000) for i in range(4001)]
    peak=max(sweep,key=amplitude)
    assert abs(peak/resonance-1)<.0002
    assert abs(amplitude(peak)-V/R)<1e-5
    assert amplitude(resonance,0)==0
    rows.append((strain,resonance,bandwidth))
assert rows[0][1]<rows[1][1]<rows[2][1]
for strain,f,bw in rows:print(f'{strain:+.0%}: {f/1e6:.3f} MHz; bandwidth {bw/1e6:.3f} MHz')
print('PASS: resonance frequency shift, numerical frequency sweep, uncoupled control')
print('LIMIT: lumped approximation only. Coil size/lead geometry and distributed RF effects make these values NOT validated hardware predictions.')
