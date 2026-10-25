from fractions import Fraction as F
import json
from pathlib import Path
E0=F(1,20);TH=F(1,50)
rows=[]
for trapped in (F(0),F(1,5),F(1,2),F(3,5),F(4,5),F(1)):
 held=E0*trapped;neighbor=(E0-held)/2
 failed=neighbor>=TH
 dissipated=neighbor*2 if failed else F(0)
 active=F(0) if failed else neighbor*2
 assert held+dissipated+active==E0
 rows.append({'trapped':str(trapped),'per_neighbor_J':str(neighbor),'secondary_failed':failed})
assert [x['secondary_failed'] for x in rows]==[True,True,False,False,False,False]
assert E0*(1-F(1,5))/2==TH
assert E0*(1-F(201,1000))/2<TH
print(json.dumps({'status':'PASS','rows':rows},indent=2))
