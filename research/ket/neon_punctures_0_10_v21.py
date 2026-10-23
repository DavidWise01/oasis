"""KET Neon test: 0..10 successive ionization punctures.
Data: NIST ASD Ne I .. Ne X sequential ionization energies (eV).
The derived lambda=hc/E values are thresholds, NOT emitted spectral lines.
"""
import csv
from pathlib import Path
IONIZATION_EV=(21.564541,40.96297,63.4233,97.1900,126.247,157.934,207.271,239.0970,1195.8082,1362.199256)
ANALOGUES=('Ne','F','O','N','C','B','Be','Li','He','H','bare Ne nucleus')
CONFIGS=('1s2 2s2 2p6','1s2 2s2 2p5','1s2 2s2 2p4','1s2 2s2 2p3','1s2 2s2 2p2','1s2 2s2 2p1','1s2 2s2','1s2 2s1','1s2','1s1','empty')
def run(out='neon_punctures_0_10.csv'):
    total=0.;rows=[]
    for n in range(11):
        if n:total+=IONIZATION_EV[n-1]
        energy=IONIZATION_EV[n] if n<10 else None
        wl=1239.841984/energy if energy else None
        rows.append(dict(puncture=n,electrons_remaining=10-n,charge=n,isoelectronic_analogue=ANALOGUES[n],configuration=CONFIGS[n],next_ionization_eV=energy if energy else '',threshold_nm=round(wl,5) if wl else '',cumulative_eV=round(total,6),subshell_next=('2p' if n<6 else '2s' if n<8 else '1s' if n<10 else 'none')))
    assert len(rows)==11 and rows[8]['configuration']=='1s2' and rows[-1]['electrons_remaining']==0
    assert round(total,6)==3511.697267
    with open(out,'w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    print('PASS: 11 states, 10 removals, 2p^6 -> 2s^2 -> 1s^2 -> zero, energy sum',round(total,6),'eV')
if __name__=='__main__':run()
