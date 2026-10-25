from fractions import Fraction as F
import json
from pathlib import Path
def test(frac):
    E=[F(1,20),F(0),F(0)]; dead=set(); sink=F(0); waves=[]
    for k in range(3):
        hit=[i for i in range(3) if i not in dead and E[i]>=F(1,50)]
        if not hit:break
        amount=sum((E[i] for i in hit),F(0))
        dead.update(hit)
        for i in hit:E[i]=F(0)
        surviving=[i for i in range(3) if i not in dead]
        transfer=amount*frac if surviving else F(0)
        sink+=amount-transfer
        for i in surviving:E[i]+=transfer/len(surviving)
        assert sum(E,F(0))+sink==F(1,20)
        waves.append(hit)
    return dict(transfer=str(frac),failed=sorted(dead),waves=waves,remaining_J=str(sum(E,F(0))),dissipated_J=str(sink))
results=[test(f) for f in (F(0),F(1,4),F(1,2),F(3,4),F(1))]
assert [len(r['failed']) for r in results]==[1,1,1,1,3]
assert all(F(r['remaining_J'])+F(r['dissipated_J'])==F(1,20) for r in results)
Path(__file__).with_name('results.json').write_text(json.dumps(results,indent=2)+'\n')
print('PASS',json.dumps(results))
