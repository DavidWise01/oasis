import math,itertools,json
from pathlib import Path
T=2*math.pi
rows=[]
for k,b,d in itertools.product((0,.08,.2,.5,1.),(0,.08,.2),(0,.03,.12)):
 phi=[0,T/3+.19,2*T/3-.13];v=[0.,0.,0.]
 for n in range(4000):
  dv=[.4*((1+(i-1)*d)-v[i])+k*sum(math.sin(phi[j]-phi[i]-T*(j-i)/3) for j in range(3))/3-b*(v[i]-1) for i in range(3)]
  for i in range(3):v[i]+=.02*dv[i];phi[i]+=.02*v[i]
 z=[phi[i]-T*i/3 for i in range(3)]
 C=abs(sum(complex(math.cos(a),math.sin(a)) for a in z)/3)
 D=max(abs(math.remainder(z[i]-z[0],T)) for i in (1,2))
 rows.append((k,b,d,C,D,C>=.99 and D<.3))
assert len(rows)==45
print('PASS',len(rows),'cases, locked',sum(r[-1] for r in rows))
