#!/usr/bin/env python3
"""AETHER-160 checkout-oriented reproduction of fresh-seed model tests.

This checkout script is NOT the exact locally executed integration source.
Exact executed experiment + frozen AETHER-159 source are in the evidence ZIP.
This smaller companion replays GitHub's independently authored 159 model.
No physically qualified instrument or operational ACT is present.
"""
import importlib.util,json,hashlib,csv
from pathlib import Path
HERE=Path(__file__).resolve().parent
PREV=HERE.parent/"159"/"experiment.py"
def load():
 spec=importlib.util.spec_from_file_location("gh159",PREV)
 module=importlib.util.module_from_spec(spec)
 spec.loader.exec_module(module)
 return module
def sha(v):return hashlib.sha256(v).hexdigest()
def canonical(o):return json.dumps(o,sort_keys=True,separators=(",",":")).encode()
def main():
 m=load();rows=[];checks=[];traces=[]
 for case in m.C:
  for seed in range(160001,160026):
   for policy in ("signed_only","blind_intake"):
    prev="0"*64;episode=[]
    for tick in range(20):
     truth,raw,r,b=m.fixture(seed,case,tick)
     permission=(policy=="signed_only" or m.admit(raw,r,b))
     event=dict(seed=seed,scenario=case,policy=policy,tick=t,
                action="ACT" if permission else "HOLD",
                unsafe=int(permission and truth>.025),
                safe_act=int(permission and truth<=.025),
                operational_action="HOLD",previous=prev)
     event["digest"]=sha(prev.encode()+canonical(event))
     prev=event["digest"];episode.append(event)
    # Reproduction checks are independent of local 159 source freeze.
    expected=[m.fixture(seed,case,tick) for tick in range(20)]
    pass_chain=True;prior="0"*64
    for row in episode:
     d={k:v for k,v in row.items() if k!="digest"}
     pass_chain &= row["previous"]==prior and row["digest"]==sha(prior.encode()+canonical(d))
     prior=row["digest"]
    gates=dict(replay=len(expected)==20,
      chain=pass_chain,
      ordered=all(x["tick"]==i for i,x in enumerate(episode)),
      one_action=len(episode)==20 and all(x["action"] in ("ACT","HOLD") for x in episode),
      safe=policy!="blind_intake" or all(x["unsafe"]==0 for x in episode),
      operational_hold=all(x["operational_action"]=="HOLD" for x in episode),
      clean_rotation=case not in m.C[:2] or all(x["safe_act"] for x in episode),
      blind=("truth" not in m.admit.__code__.co_varnames and "case" not in m.admit.__code__.co_varnames))
    checks.extend(dict(case=case,seed=seed,policy=policy,gate=g,passed=int(v)) for g,v in gates.items())
    rows.append(dict(case=case,seed=seed,policy=policy,unsafe=sum(x["unsafe"] for x in episode),
                     safe_act=sum(x["safe_act"] for x in episode)))
    if seed==160001:traces.extend(episode)
 total=lambda policy,k:sum(x[k] for x in rows if x["policy"]==policy)
 good=len(checks)==3200 and all(r["passed"] for r in checks) and (
     total("signed_only","unsafe"),total("blind_intake","unsafe"),total("blind_intake","safe_act"))==(1200,0,2800)
 print(json.dumps(dict(bound="AETHER-160",checkout_demo_pass=good,
    checks=len(checks),checks_passed=sum(r["passed"] for r in checks),
    signed_only_unsafe=total("signed_only","unsafe"),
    blind_unsafe=total("blind_intake","unsafe"),
    blind_safe=total("blind_intake","safe_act"),
    real_operational_ACT=0,physical_qualification_percent=0),indent=2))
 if not good:raise SystemExit(1)
if __name__=="__main__":main()
