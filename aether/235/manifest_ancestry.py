#!/usr/bin/env python3
"""AETHER-235: fail-closed manifest ancestry and run linkage review.

All input snapshots are untrusted until independently authenticated.
This checks internal consistency, not GitHub signature/custody provenance.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

SHA40=re.compile(r"^[0-9a-f]{40}$")
SHA256=re.compile(r"^[0-9a-f]{64}$")
SCHEMA="AETHER-235/manifest-ancestry-v1"
HOLD={"physical_qualification_percent":0,"operational_authority":"HOLD",
      "physical_act_allowed":False,"independent_custody_authenticated":False}

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()

def review(e):
    reasons=[]
    observations={}
    if not isinstance(e,dict):
        return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
                "reasons":["EVIDENCE_OBJECT_INVALID"],"observed":observations,**HOLD}
    manifest=e.get("manifest")
    pin=e.get("pin")
    run=e.get("run")
    ancestry=e.get("ancestry")
    for label,value in [("manifest",manifest),("pin",pin),("run",run),("ancestry",ancestry)]:
        if not isinstance(value,dict):
            reasons.append(label.upper()+"_MISSING")
        else:
            observations[label+"_sha256"]=hashlib.sha256(canonical(value)).hexdigest()
    if not all(isinstance(x,dict) for x in (manifest,pin,run,ancestry)):
        return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
                "reasons":sorted(reasons),"observed":observations,**HOLD}
    manifest_commit=manifest.get("source_commit")
    manifest_hash=hashlib.sha256(canonical(manifest)).hexdigest()
    if not isinstance(manifest_commit,str) or not SHA40.fullmatch(manifest_commit):
        reasons.append("MANIFEST_SOURCE_INVALID")
    pin_commit=pin.get("commit_sha")
    if not isinstance(pin_commit,str) or not SHA40.fullmatch(pin_commit):
        reasons.append("PIN_COMMIT_INVALID")
    if pin.get("manifest_sha256")!=manifest_hash:
        reasons.append("PINNED_MANIFEST_DIGEST_MISMATCH")
    if pin.get("repository")!="DavidWise01/oasis" or run.get("repository")!="DavidWise01/oasis":
        reasons.append("REPOSITORY_MISMATCH")
    if pin.get("path")!="aether/evidence/pinned-members.json":
        reasons.append("PIN_PATH_UNTRUSTED")
    source_sha=run.get("head_sha")
    if not isinstance(source_sha,str) or not SHA40.fullmatch(source_sha):
        reasons.append("RUN_SOURCE_INVALID")
    if source_sha!=manifest_commit:
        reasons.append("RUN_MANIFEST_SOURCE_MISMATCH")
    if pin.get("source_commit")!=source_sha:
        reasons.append("PIN_SOURCE_MISMATCH")
    if type(run.get("id")) is not int or run["id"]<=0:
        reasons.append("RUN_ID_INVALID")
    if run.get("status")!="completed" or run.get("conclusion")!="success":
        reasons.append("RUN_NOT_SUCCESSFUL_COMPLETED")
    if pin.get("run_id")!=run.get("id"):
        reasons.append("PIN_RUN_ID_MISMATCH")
    if ancestry.get("source_sha")!=source_sha or ancestry.get("pin_commit_sha")!=pin_commit:
        reasons.append("ANCESTRY_BINDING_MISMATCH")
    if ancestry.get("api_confirmed") is not True:
        reasons.append("ANCESTRY_NOT_CONFIRMED")
    if ancestry.get("pin_is_ancestor") is not True:
        reasons.append("PIN_NOT_PROVEN_ANCESTOR")
    if pin_commit==source_sha:
        reasons.append("PIN_COMMIT_EQUALS_RUN_HEAD")
    if not isinstance(pin.get("manifest_sha256"),str) or not SHA256.fullmatch(pin["manifest_sha256"]):
        reasons.append("PIN_DIGEST_INVALID")
    if not e.get("independent_pre_run_custody_receipt"):
        reasons.append("INDEPENDENT_PRE_RUN_CUSTODY_UNOBSERVED")
    else:
        # A supplied receipt is not authenticated merely because it is present.
        reasons.append("CUSTODY_RECEIPT_NOT_CRYPTOGRAPHICALLY_AUTHENTICATED")
    if not reasons:
        reasons.append("SELF_REPORTED_ANCESTRY_NOT_INDEPENDENTLY_ATTESTED")
    return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
            "reasons":sorted(set(reasons)),"observed":observations,**HOLD}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--evidence",type=Path,required=True)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    try:
        raw=a.evidence.read_bytes()
        if len(raw)>256*1024:raise ValueError("INPUT_TOO_LARGE")
        result=review(json.loads(raw))
    except (OSError,ValueError,UnicodeError) as error:
        result={"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
                "reasons":["INPUT_UNAVAILABLE_OR_INVALID:"+type(error).__name__],
                "observed":{},**HOLD}
    value=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(value,encoding="utf-8")
    print(value,end="")
    return 1

if __name__=="__main__":
    raise SystemExit(main())
