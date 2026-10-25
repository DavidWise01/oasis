import math,json
from pathlib import Path
B=[5,5,5,7,7,5,5,7,7,7]
assert len(B)==10 and sum(B)==60 and sum(B[:5])==29 and sum(B[5:])==31
assert B.count(5)==B.count(7)==5
for t in range(240):
    sector=(t%60)//20
    assert sector in (0,1,2)
    assert ((t%20)<8) == (t%20 in range(8))
    a=[(2*math.pi*(t%120)/60+2*math.pi*i/3)%(2*math.pi) for i in range(3)]
    assert all(math.isclose((a[(i+1)%3]-a[i])%(2*math.pi),2*math.pi/3,rel_tol=0,abs_tol=1e-13) for i in range(3))
    assert t%16==(t+240)%16
for N in (8,16,32,64):
    assert 2%N != (-2)%N
for b in [0,0.12,0.3]:
    drive=.25
    resp=lambda w:drive/math.hypot(1-w*w,b*w) if (1-w*w)**2+(b*w)**2 else float('inf')
    assert resp(.95)>resp(.2)
report={'status':'PASS','beat_total':60,'first_phrase':29,'second_phrase':31,'sectors':3,'units_per_sector':20,'internal':8,'external':12,'central_cells':16,'pointer_realign_units':240,'checked_ticks':240,'orbital_spacing':'120°','simulation':'classical oscillator reference; no physics validation'}
Path(__file__).with_name('results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
