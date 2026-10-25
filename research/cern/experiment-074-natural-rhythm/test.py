from fractions import Fraction as F
from math import gcd,lcm
from collections import Counter
import csv,json
from pathlib import Path
P=Path(__file__).parent
beats=list(map(int,"5557755777"))
assert len(beats)==10 and sum(beats)==60
assert beats.count(5)==beats.count(7)==5
assert sum(beats[:5])==29 and sum(beats[5:])==31
expanded=[i for i,b in enumerate(beats) for _ in range(b)]
assert len(expanded)==60
rows=[]
for tick in range(60):
 sector=tick//20
 local=tick%20
 rows.append(dict(unit=tick+1,beat=expanded[tick]+1,spinor=sector,domain="internal" if local<8 else "external",center_cell=tick%16))
assert Counter(r["spinor"] for r in rows)=={0:20,1:20,2:20}
assert all(sum(r["domain"]=="internal" for r in rows if r["spinor"]==i)==8 for i in range(3))
assert all(sum(r["domain"]=="external" for r in rows if r["spinor"]==i)==12 for i in range(3))
mean=F(sum(beats),len(beats));var=sum((F(b)-mean)**2 for b in beats)/10
assert mean==6 and var==1
assert 60//3==20 and 20*F(2,5)==8 and 20*F(3,5)==12
reset=16//gcd(60,16)
assert reset==4 and 60*reset==240
with (P/"timeline.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
result=dict(status="PASS",beat="5557755777",beat_units=60,beat_phrase_sums=[29,31],mean_beat=6,beat_variance=1,spinor_units=20,internal_units_per_spinor=8,external_units_per_spinor=12,internal_total=24,external_total=36,degrees_per_unit=6,cell_loop_reset=4,complete_alignment_units=240,note="16-cell scanning is an explicit model assumption; no physical frequency given")
(P/"results.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
