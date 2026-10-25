import math,json
from pathlib import Path
p=Path(__file__).parent
m,k,b=1.,1.,.12
F0=.02;xmax=.3
rows=[]
for w in (.2,.5,.8,.95,1.,1.05,1.2,1.5,2.):
 A=F0/math.hypot(k-m*w*w,b*w)
 phi=math.atan2(b*w,k-m*w*w)
 Pin=.5*F0*A*w*math.sin(phi)
 Ploss=.5*b*w*w*A*A
 assert math.isclose(Pin,Ploss,rel_tol=1e-12,abs_tol=1e-15)
 assert A<xmax
 rows.append((w,A,Pin,Ploss))
wpeak=math.sqrt(k/m-b*b/(2*m*m))
peak=F0/math.hypot(k-m*wpeak*wpeak,b*wpeak)
assert .99<wpeak<1 and peak>rows[4][1]
stress=.1/math.hypot(k-m*wpeak*wpeak,b*wpeak)
assert stress>xmax
print(json.dumps({'status':'PASS','frequency_cases':len(rows),'peak_omega_rad_s':wpeak,'peak_displacement_m':peak,'stress_unconstrained_displacement_m':stress,'cap_m':xmax},indent=2))
