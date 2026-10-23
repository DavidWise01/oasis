"""KET Z1–118 deterministic color, white purity, tempo and resonance cipher.
These are synthetic mappings, NOT measured atomic spectral lines.
"""
import csv
from pathlib import Path
SYMBOLS="H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og".split()
SHELLS=[(1,2),(3,10),(11,18),(19,36),(37,54),(55,86),(87,118)]
PALETTE=[('rd','red',650),('bl','blue',470),('yl','yellow',580),('gr','green',530),('or','orange',610),('pr','purple',410)]
METERS=['3/4','4/4','5/4','6/8','7/8','4/4','9/8']
def generate():
    for z,symbol in enumerate(SYMBOLS,1):
        gen=next(i for i,(a,b) in enumerate(SHELLS) if a<=z<=b)
        first,last=SHELLS[gen];local=z-first+1
        color,name,lambda_nm=PALETTE[(z-1)%6]
        purity=(last-z+1)/(last-first+1)
        optical_hz=299792458/(lambda_nm*1e-9)
        k=1+(local-1)%8
        pattern=''.join('X' if (i+1)*k//8>i*k//8 else '.' for i in range(8))
        yield dict(Z=z,symbol=symbol,generation=gen,closures='>'.join(str(b) for a,b in SHELLS[:gen+1]),
          color=color,white_purity=round(purity,6),wavelength_nm=lambda_nm,
          color_photon_THz=round(optical_hz/1e12,4),color_photon_eV=round(1239.841984/lambda_nm,4),
          resonance_audio_Hz=round(optical_hz/2**40,3),tempo_BPM=round(60*optical_hz/2**48,2),
          meter=METERS[gen],rhythm_pattern=pattern,rhythm_pulses=k)
def main():
    rows=list(generate())
    assert len(rows)==118 and [r['Z'] for r in rows]==list(range(1,119))
    assert all(0<r['white_purity']<=1 for r in rows)
    assert [sum(r['generation']==g for r in rows) for g in range(7)]==[2,8,8,18,18,32,32]
    with open('KET_118_color_tempo_rhythm_resonance.csv','w',newline='') as file:
        writer=csv.DictWriter(file,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    print('PASS: 118 addresses; seven generations; color/purity/pattern/resonance computed')
if __name__=='__main__':main()
