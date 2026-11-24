#!/usr/bin/env python3
"""AETHER-161 — physical evidence acquisition intake (SYNTHETIC DRY-RUN).
No real physical reference is supplied. Neither passing tests nor mock
certificates grant real instrument qualification or operational ACT.
"""
import csv,hashlib,hmac,json
from pathlib import Path

OUT=Path(__file__).resolve().parent
CASES=("clean_mock","legitimate_mock_rotation","missing_instrument_serial",
       "self_issued_certificate","modified_raw_capture","missing_clock_record",
       "shared_reference_ancestry","forged_physical_qualification")
SEEDS=range(161001,161026)
DUT=b"AETHER161_SIM_DUT";REF=b"AETHER161_SIM_REFERENCE"
LIMIT=.025
def canonical(x):return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def sha(x):return hashlib.sha256(x).hexdigest()
def sign(x,k):return dict(x,mac=hmac.new(k,canonical(x),hashlib.sha256).hexdigest())
def authentic(x,k):
 if not isinstance(x,dict):return False
 return hmac.compare_digest(str(x.get("mac","")),
   hmac.new(k,canonical({a:b for a,b in x.items() if a!="mac"}),hashlib.sha256).hexdigest())

def fixture(seed,case,t):
 # Ground truth is ONLY for post-decision synthetic scoring.
 fault=case not in CASES[:2] and 6<=t<14
 truth=.045 if fault else .005
 gen=2 if case=="legitimate_mock_rotation" and t>=10 else 1
 nonce=sha(canonical([seed,case,t]))[:24]
 capture=canonical(dict(serial="DUT-161",tick=t,nonce=nonce,reading=truth))
 device=dict(serial="DUT-161",generation=gen,tick=t,nonce=nonce,
   path="INPUT-A",reading=.005,source="MOCK-DUT")
 reference=dict(serial="REF-161",dut_serial="DUT-161",generation=gen,
   tick=t,nonce=nonce,path="INPUT-A",source="SIM-REF",
   lab="MOCK-THIRD-PARTY",calibration_ancestry="MOCK-EXTERNAL",
   expires=t+1,measured=truth,uncertainty=.0005,
   original_capture_sha256=sha(capture),clock_record="MOCK-CLOCK-161",
   physical_evidence_status="UNVERIFIED")
 if fault:
  if case=="missing_instrument_serial":device["serial"]=""
  elif case=="self_issued_certificate":reference["lab"]="DUT-SELF"
  elif case=="modified_raw_capture":capture+=b"\n"
  elif case=="missing_clock_record":reference["clock_record"]=""
  elif case=="shared_reference_ancestry":reference["calibration_ancestry"]="DUT-SHARED"
  elif case=="forged_physical_qualification":reference["physical_evidence_status"]="QUALIFIED"
 return truth,capture,sign(device,DUT),sign(reference,REF)

def dry_run_gate(capture,device,reference):
 """No fault labels, synthetic truth, seed or scenario input."""
 if not(authentic(device,DUT) and authentic(reference,REF)):return "HOLD","signature"
 if not capture or sha(capture)!=reference["original_capture_sha256"]:
  return "HOLD","original_capture"
 if device["serial"]!="DUT-161" or reference["dut_serial"]!=device["serial"]:
  return "HOLD","device_identity"
 if reference["serial"]!="REF-161" or reference["source"]!="SIM-REF":
  return "HOLD","reference_identity"
 if reference["lab"]!="MOCK-THIRD-PARTY" or reference["calibration_ancestry"]!="MOCK-EXTERNAL":
  return "HOLD","ancestry"
 if reference["physical_evidence_status"]!="UNVERIFIED":
  return "HOLD","physical_status_claim"
 for k in ("generation","tick","nonce","path"):
  if device[k]!=reference[k]:return "HOLD","acquisition_binding"
 if reference["path"]!="INPUT-A" or reference["clock_record"]!="MOCK-CLOCK-161":
  return "HOLD","clock_or_path"
 if reference["expires"]!=reference["tick"]+1:return "HOLD","expired"
 try:
  original=json.loads(capture)
  if canonical(original)!=capture or original["serial"]!=device["serial"]:
   return "HOLD","raw_identity"
  if original["nonce"]!=reference["nonce"] or original["tick"]!=reference["tick"]:
   return "HOLD","raw_challenge"
  mean=original["reading"]
  if abs(mean-reference["measured"])>reference["uncertainty"]:
   return "HOLD","measurement_conflict"
  if mean+reference["uncertainty"]>LIMIT:return "HOLD","upper_bound"
 except (KeyError,ValueError,TypeError):
  return "HOLD","raw_parse"
 return "ACT","SYNTHETIC_DRY_RUN_ONLY"

def hash_chain_ok(rows):
 prev="0"*64
 for row in rows:
  if row["previous"]!=prev:return False
  body={k:v for k,v in row.items() if k!="digest"}
  if sha(prev.encode()+canonical(body))!=row["digest"]:return False
  prev=row["digest"]
 return True

def episode(seed,case,policy):
 rows=[];previous="0"*64
 for t in range(20):
  truth,raw,device,reference=fixture(seed,case,t)
  if policy=="signed_only":
   act="ACT" if authentic(device,DUT) else "HOLD";reason="signed_only"
  else: act,reason=dry_run_gate(raw,device,reference)
  rec=dict(seed=seed,scenario=case,policy=policy,tick=t,action=act,reason=reason,
   unsafe=int(act=="ACT" and truth>LIMIT),
   safe_act=int(act=="ACT" and truth<=LIMIT),
   operational_action="HOLD",physical_qualified=False,previous=previous)
  rec["digest"]=sha(previous.encode()+canonical(rec))
  previous=rec["digest"]
  rows.append(rec)
 return rows

def write_csv(name,rows):
 with (OUT/name).open("w",newline="",encoding="utf8") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]))
  w.writeheader();w.writerows(rows)

def main():
 checks=[];episodes=[];samples=[]
 for case in CASES:
  for seed in SEEDS:
   for policy in ("signed_only","physical_intake_gated"):
    rows=episode(seed,case,policy)
    gates=dict(replay=rows==episode(seed,case,policy),chain=hash_chain_ok(rows),
      ordered=all(r["tick"]==i for i,r in enumerate(rows)),
      one_action=len(rows)==20 and all(r["action"] in ("ACT","HOLD") for r in rows),
      guarded_safe=policy!="physical_intake_gated" or all(not r["unsafe"] for r in rows),
      operational_hold=all(r["operational_action"]=="HOLD" and not r["physical_qualified"] for r in rows),
      clean_preserved=case not in CASES[:2] or all(r["safe_act"] for r in rows),
      blind_gate="truth" not in dry_run_gate.__code__.co_varnames and
          "case" not in dry_run_gate.__code__.co_varnames)
    checks.extend(dict(case=case,seed=seed,policy=policy,check=k,passed=int(v))
      for k,v in gates.items())
    episodes.append(dict(case=case,seed=seed,policy=policy,
      unsafe=sum(r["unsafe"] for r in rows),safe_act=sum(r["safe_act"] for r in rows)))
    if seed==SEEDS.start:samples.extend(rows)
 summary=[]
 for case in (*CASES,"ALL"):
  for policy in ("signed_only","physical_intake_gated"):
   x=[r for r in episodes if r["policy"]==policy and (case=="ALL" or r["case"]==case)]
   summary.append(dict(case=case,policy=policy,episodes=len(x),
     unsafe=sum(r["unsafe"] for r in x),safe_act=sum(r["safe_act"] for r in x),
     operational_act=0))
 ix={(r["case"],r["policy"]):r for r in summary}
 success=(len(checks)==3200 and all(r["passed"] for r in checks)
   and ix["ALL","signed_only"]["unsafe"]==1200
   and ix["ALL","physical_intake_gated"]["unsafe"]==0
   and ix["ALL","physical_intake_gated"]["safe_act"]==2800
   and ix["clean_mock","physical_intake_gated"]["safe_act"]==500
   and ix["legitimate_mock_rotation","physical_intake_gated"]["safe_act"]==500)
 write_csv("checks.csv",checks);write_csv("seed_results.csv",episodes)
 write_csv("trace_samples.csv",samples);write_csv("results.csv",summary)
 m=dict(bound="AETHER-161",phase="XI",status="PASS" if success else "FAIL",
    checks=len(checks),checks_passed=sum(r["passed"] for r in checks),
    episodes_per_policy=200,decisions_per_policy=4000,
    signed_only_unsafe=ix["ALL","signed_only"]["unsafe"],
    guarded_unsafe=ix["ALL","physical_intake_gated"]["unsafe"],
    guarded_safe_dry_run=ix["ALL","physical_intake_gated"]["safe_act"],
    synthetic_setup_readiness_percent=12.5 if success else 0,
    physical_qualification_percent=0,actual_physical_samples=0,
    operational_act=0,physical_evidence_status="OPEN_UNVERIFIED",
    limits=["Mock references do not constitute physical acquisition",
     "Lab identity and sample clocks are synthetic string assertions",
     "No physical ACT possible without authenticated instrument data"])
 (OUT/"manifest.json").write_text(json.dumps(m,indent=2)+"\n")
 print(json.dumps(m,indent=2))
 if not success:raise SystemExit(1)
if __name__=="__main__":main()
