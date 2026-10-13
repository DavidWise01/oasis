#!/usr/bin/env python3
"""Earth@0 counterfactual gas / Sgr A* physical scaling + mnemonic rotation.
Compact runnable repo audit; the companion ZIP has all 35 checks and the SVG.
"""
import math, json
from decimal import Decimal, localcontext
G=6.67430e-11
C=299792458.0
EARTH=5.9722e24
EARTH_RADIUS=6371000.0
SUN=1.98847e30
SGR=4.0e6*SUN
RGAS=8.314462618
ROTATIONS=['SAGA'[i:]+'SAGA'[:i] for i in range(4)]
GLYPH=r'123 {{45/|\54}} 678'
AMPLITUDES=['red','green','blue','orange','purple','green','yellow']
CARRIERS=['white','black','gray']

def gas_radius(molar_mass,T=300.0,P=101325.0):
    """Ideal gas in a hypothetical external container, NOT hydrostatic equilibrium."""
    volume=EARTH/molar_mass*RGAS*T/P
    return (3*volume/(4*math.pi))**(1/3)

def main():
    with localcontext() as ctx:
        ctx.prec=450
        elapsed=Decimal('4.3')*Decimal(10)**9*Decimal(31557600)
        ticks=int(elapsed/Decimal('1.6161e-360'))
    re=2*G*EARTH/C**2
    rs=2*G*SGR/C**2
    result={
        'clock':'earth@0, -4.3 Ga to now, symbolic snapshot jumps',
        'earth_mass_kg':EARTH,
        'earth_lb_mass':EARTH*2.2046226218487757,
        'hydrogen_300K_1atm_equivalent_radius_m':gas_radius(.00201588),
        'nitrogen_300K_1atm_equivalent_radius_m':gas_radius(.0280134),
        'earth_Schwarzschild_radius_m':re,
        'Sgr_A_mass_kg':SGR,'Sgr_A_mass_in_Earths':SGR/EARTH,
        'Sgr_A_Schwarzschild_radius_m':rs,
        'mnemonic_orbit':ROTATIONS,'chariot':GLYPH,
        'amplitudes':AMPLITUDES,'carriers':CARRIERS,
        'bubble_tick_count':str(ticks),'cipher_physically_predictive':False,
        'status':'all-gas Earth is counterfactual; ideal-gas radius is not free cloud equilibrium'
    }
    assert ROTATIONS==['SAGA','AGAS','GASA','ASAG']
    assert GLYPH==r'123 {{45/|\54}} 678'
    assert len(AMPLITUDES)==7 and AMPLITUDES.count('green')==2 and len(CARRIERS)==3
    assert len(str(ticks))==377
    assert 0.0088<re<0.009
    assert 1.3e12<SGR/EARTH<1.4e12
    assert 40<result['hydrogen_300K_1atm_equivalent_radius_m']/EARTH_RADIUS<42
    assert 16<result['nitrogen_300K_1atm_equivalent_radius_m']/EARTH_RADIUS<18
    print(json.dumps(result,sort_keys=True,indent=2))

if __name__=='__main__':main()
