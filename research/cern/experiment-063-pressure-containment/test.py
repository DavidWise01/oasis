from fractions import Fraction as F
import json
from pathlib import Path
C=299792458
SETTINGS=[('transparent',F(0),F(1)),('mirror',F(1),F(0)),('absorber',F(0),F(0)),('balanced',F(1,4),F(1,2)),('reflective',F(3,5),F(1,5)),('partial',F(1,8),F(3,8))]
ENERGIES=[F(1),F(7,3),F(23,11),F(1000)]
checks=0;rows=[]
for name,R,T in SETTINGS:
 A=1-R-T
 for E in ENERGIES:
  Er,Et,Es=E*R,E*T,E*A
  assert Er+Et+Es==E;checks+=1
  assert min(Er,Et,Es)>=0;checks+=1
  J=(E+Er-Et)/C
  assert J==(2*Er+Es)/C;checks+=1
  state={'stored':Es,'released':False}
  def release():
   if state['released']:return F(0)
   state['released']=True;return state['stored']
  first,second=release(),release()
  assert first==Es and second==0;checks+=1
  assert Er+Et+first==E;checks+=1
  rows.append({'setting':name,'incident_J':str(E),'reflected_J':str(Er),'transmitted_J':str(Et),'stored_J':str(Es),'impulse_N_s':str(J)})
assert checks==120
result={'experiment':'PRIM-063','status':'PASS','cases':24,'assertions':checks,'rows':rows,'scope':'idealized 1D radiation scattering; not quantum-gravity containment'}
Path(__file__).with_name('results.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS 24 cases; 120 assertions')
