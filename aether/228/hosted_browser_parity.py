#!/usr/bin/env python3
"""AETHER-228 — read-only hosted-artifact ↔ browser evidence parity.

The caller supplies an actual downloaded hosted archive, the bytes delivered
to the browser, an out-of-band pinned digest, and a claimed Actions run record.
Equality demonstrates bytes, NOT independent provenance. No network, recovery
or physical actions are performed here.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

SCHEMA="AETHER-228/hosted-browser-parity-v1"
HEX40=re.compile(r"^[a-f0-9]{40}$")
HEX64=re.compile(r"^[a-f0-9]{64}$")
HOLD={"independently_authenticated_hosted_artifact":False,
      "original_hardware_captures_authenticated":0,
      "independent_external_custodians":0,
      "physical_qualification_percent":0,"operational_authority":"HOLD",
      "physical_act_allowed":False,"may_repair":False,"may_recover":False,
      "may_reclaim_lock":False,"may_choose_history":False}

def digest(raw:bytes)->str:
    return hashlib.sha256(raw).hexdigest()

def decision(reasons:set[str],hosted:bytes|None,browser:bytes|None,
             claimed_run:int|None)->dict:
    return {"schema":SCHEMA,
            "verdict":"DOCUMENTARY_HOSTED_BROWSER_BYTES_MATCH_ONLY" if not reasons else "REJECT_OR_UNVERIFIED",
            "reasons":sorted(reasons) or ["PIN_AUTHORITY_AND_REMOTE_ARTIFACT_ORIGIN_NOT_INDEPENDENTLY_AUTHENTICATED"],
            "run_id":claimed_run,
            "hosted_sha256":digest(hosted) if hosted is not None else None,
            "browser_sha256":digest(browser) if browser is not None else None,
            "hosted_length":len(hosted) if hosted is not None else None,
            "browser_length":len(browser) if browser is not None else None,
            **HOLD}

def evaluate(reference:dict,hosted:bytes|None,browser:bytes|None,
             inventory:dict|None,run:dict|None)->dict:
    errors=set()
    if not isinstance(reference,dict):
        reference={}
    if reference.get("schema")!="AETHER-228/expected-hosted-archive-v1":
        errors.add("REFERENCE_SCHEMA_INVALID")
    pin=reference.get("sha256")
    expected_commit=reference.get("source_commit")
    run_id=reference.get("run_id")
    if not isinstance(pin,str) or HEX64.fullmatch(pin) is None:
        errors.add("EXTERNAL_DIGEST_PIN_MISSING")
    if not isinstance(expected_commit,str) or HEX40.fullmatch(expected_commit) is None:
        errors.add("SOURCE_REVISION_PIN_MISSING")
    if not isinstance(run_id,int) or isinstance(run_id,bool) or run_id<1:
        errors.add("RUN_ID_PIN_MISSING")
    if reference.get("origin_type")!="GITHUB_HOSTED_ARTIFACT_DOWNLOADED":
        errors.add("HOSTED_ORIGIN_NOT_DECLARED")
    if not isinstance(hosted,bytes):
        errors.add("HOSTED_BYTES_NOT_OBSERVED")
    if not isinstance(browser,bytes):
        errors.add("BROWSER_BYTES_NOT_OBSERVED")
    if isinstance(hosted,bytes) and isinstance(browser,bytes):
        if hosted!=browser:errors.add("HOSTED_BROWSER_BYTES_DIVERGE")
    if isinstance(hosted,bytes) and isinstance(pin,str) and digest(hosted)!=pin:
        errors.add("HOSTED_DIGEST_PIN_MISMATCH")
    if isinstance(browser,bytes) and isinstance(pin,str) and digest(browser)!=pin:
        errors.add("BROWSER_DIGEST_PIN_MISMATCH")
    if not isinstance(run,dict):
        errors.add("RUN_RECORD_NOT_OBSERVED")
    else:
        if run.get("id")!=run_id:errors.add("RUN_ID_MISMATCH")
        if run.get("head_sha")!=expected_commit:errors.add("RUN_SOURCE_COMMIT_MISMATCH")
        if run.get("repository")!="DavidWise01/oasis":errors.add("RUN_REPOSITORY_MISMATCH")
        if run.get("status")!="completed" or run.get("conclusion")!="success":
            errors.add("RUN_NOT_SUCCESSFULLY_COMPLETED")
        if run.get("artifact_name")!="aether218-rust-qualification":
            errors.add("RUN_ARTIFACT_NAME_MISMATCH")
        if run.get("artifact_expired") is not False:
            errors.add("RUN_ARTIFACT_EXPIRED")
    if not isinstance(inventory,dict):
        errors.add("ARTIFACT_INVENTORY_NOT_OBSERVED")
    else:
        if inventory.get("schema")!="AETHER-227/archive-inventory-v1":
            errors.add("INVENTORY_SCHEMA_INVALID")
        if inventory.get("source_commit")!=expected_commit:
            errors.add("INVENTORY_SOURCE_REVISION_MISMATCH")
        if inventory.get("verdict")!="DOCUMENTARY_ARCHIVE_BYTES_CONSISTENT_ONLY":
            errors.add("INVENTORY_QUALIFICATION_NOT_CONSISTENT")
        # Inventory covers the LOCAL archive inside uploaded evidence,
        # NOT the outer GitHub-hosted upload-artifact ZIP. Never conflate.
        if inventory.get("operational_authority")!="HOLD" or inventory.get("physical_qualification_percent")!=0:
            errors.add("INVENTORY_AUTHORITY_PROMOTION")
    return decision(errors,hosted,browser,run_id if isinstance(run_id,int) else None)

def read(path:Path|None,limit:int=32*1024*1024)->bytes|None:
    try:
        if path is None or not path.is_file() or path.stat().st_size>limit:return None
        return path.read_bytes()
    except OSError:return None

def json_read(path:Path|None)->dict|None:
    raw=read(path,2*1024*1024)
    if raw is None:return None
    try:
        value=json.loads(raw)
        return value if isinstance(value,dict) else None
    except (UnicodeError,ValueError):return None

def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--reference",type=Path,required=True)
    parser.add_argument("--hosted",type=Path)
    parser.add_argument("--browser",type=Path)
    parser.add_argument("--inventory",type=Path)
    parser.add_argument("--run",type=Path)
    parser.add_argument("--out",type=Path)
    a=parser.parse_args()
    result=evaluate(json_read(a.reference) or {},read(a.hosted),read(a.browser),
                    json_read(a.inventory),json_read(a.run))
    content=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(content,encoding="utf-8")
    print(content,end="")
    return 0 if result["verdict"]=="DOCUMENTARY_HOSTED_BROWSER_BYTES_MATCH_ONLY" else 1

if __name__=="__main__":
    sys.exit(main())
