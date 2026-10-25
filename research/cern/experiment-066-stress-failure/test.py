import math,json
from pathlib import Path
p=Path(__file__).parent
m,k,b,wall,e=1.,1.,.12,.30,.6
limit=.02;dt=.001;omega=math.sqrt(1-b*b/2)
def simulate(force):
 x=v=work=heat=impact=0.;events=0;peak=0.;residual=0.
 for j in range(40000):
  t=j*dt;f=force*math.sin(omega*t)
  v2=v+(f-b*v-k*x)*dt
  x2=x+v2*dt
  work+=f*(x2-x);heat+=b*v2*v2*dt
  if x2>wall:
   impact+=.5*k*(x2*x2-wall*wall)+.5*m*(1-e*e)*v2*v2
   x2=wall;v2=-e*v2;events+=1
  x,v=x2,v2;peak=max(peak,x)
  stored=.5*m*v*v+.5*k*x*x
  residual=max(residual,abs(work-stored-heat-impact))
  if impact>=limit:
   return {'force_N':force,'failed':True,'state':-1,'time_s':(j+1)*dt,'impacts':events,'max_error_J':residual}
 return {'force_N':force,'failed':False,'state':0,'time_s':None,'impacts':events,'max_error_J':residual}
result=[simulate(f) for f in (.01,.02,.03,.05,.10,.15,.20)]
assert [r['failed'] for r in result]==[False]*4+[True]*3
assert [r['impacts'] for r in result]==[0,0,0,3,2,1,1]
print(json.dumps(result,indent=2))
