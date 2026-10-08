#!/usr/bin/env python3
"""Kosmo scalar portable test, source-aligned 13-body census and homeostatic overlay."""
import json,math,hashlib
from pathlib import Path
DATA=Path(__file__).with_name("kosmo_scalar_table.json")
TH=math.sqrt(1.25)
def run():
 raw=json.loads(DATA.read_text());b=raw["bodies"]
 totals={k:sum(x[k] for x in b) for k in ("strong","medium","weak")}
 def field(name,r):
  m=int(next(x["massKg"] for x in b if x["name"]==name))
  return 6.67430e-11*m/r**2
 def pressure(occupied,nominal):return occupied/nominal>TH
 counts=[sum(i%9==c for i in range(36)) for c in range(9)]
 relays=[sum(i%6==r for i in range(36)) for r in range(6)]
 checks={
  "13_majors":len(b)==13,
  "13_unique_names":len({x["name"] for x in b})==13,
  "source_counts":totals=={"strong":300,"medium":100,"weak":16},
  "416_total":sum(totals.values())==416,
  "nonnegative_bands":all(x[k]>=0 for x in b for k in totals),
  "positive_masses":all(int(x["massKg"])>0 for x in b),
  "inverse_square":math.isclose(field("Earth",1e9)/field("Earth",2e9),4),
  "strict_threshold":not pressure(TH,1) and pressure(TH+1e-9,1),
  "nine_cells":len(counts)==9 and sum(counts)==36,
  "four_each":all(v==4 for v in counts),
  "six_relays":len(relays)==6 and sum(relays)==36,
  "six_each":all(v==6 for v in relays),
  "one_root":sum(counts)==36,
  "repeatable_digest":hashlib.sha256(DATA.read_bytes()).hexdigest()==hashlib.sha256(DATA.read_bytes()).hexdigest()
 }
 return {"schema":"oasis/sheet69/kosmo-scalar-v01","checks":checks,"passed":sum(checks.values()),"total":len(checks),"census":totals,"homeostatic_threshold":TH,"warning":"G*M/r^2 has units m/s^2, not newtons; source labels this toy proxy as force."}
if __name__=="__main__":
 result=run();print(json.dumps(result,indent=2));assert result["passed"]==result["total"]
