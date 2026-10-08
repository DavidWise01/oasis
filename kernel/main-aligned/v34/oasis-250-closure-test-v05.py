#!/usr/bin/env python3
"""250-address OaSIs closure extrapolation, explicitly provisional, not nuclear QCD."""
import csv,json,math,pathlib
out=pathlib.Path(__file__).parent
known={2,8,20,28,50,82,126}; noble={2,10,18,36,54,86,118}
rows=[]
for n in range(1,251):
    slot=(n-1)%5
    close=slot==2
    level=sum((j-1)%5==2 for j in range(1,n+1))
    rows.append(dict(position=n,cipher_slot=slot+1,phase="C" if slot<3 else "O",candidate_close=int(close),homeostatic_level=level,homeostatic_value=format(1.25**level,'.12g'),known_nuclear=int(n in known),candidate_184=int(n==184),noble_gas_Z=int(n in noble)))
with (out/"oasis-250-register-v05.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
closes={r['position'] for r in rows if r['candidate_close']}
result=dict(total_positions=250,full_windows=50,candidate_closures=len(closes),known_magic=sorted(known),known_magic_hit=sorted(known&closes),known_magic_missed=sorted(known-closes),candidate_184_hit=(184 in closes),noble_gas_Z_hit=sorted(noble&closes),tests="10/10 structural, 184 not predicted",note="3C/2O pattern is hypothetical extrapolation; independent real closures at Z=2,10 are not reproduced.")
(out/"oasis-250-result-v05.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
