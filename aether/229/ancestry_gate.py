#!/usr/bin/env python3
"""AETHER-229: fail-closed documentary ancestry-screening for three witnesses.

Different URLs, signatures or labels are NOT independent control. This module
does not contact external operators or validate signatures; all control data
is self-declared and therefore cannot prove real-world independence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

SCHEMA="AETHER-229/three-root-ancestry-v1"
SHA64=re.compile(r"^[0-9a-f]{64}$")
OWNED_CORPUS="DavidWise01-GitHub-0root-one-ancestry"
FIELDS=("root_id","ultimate_controller","operator","administrator","custody_host","signing_key_sha256","artifact_sha256","source_url")
HOLD={"independent_witness_roots_authenticated":0,"external_control_authenticated":False,
      "physical_qualification_percent":0,"operational_authority":"HOLD",
      "physical_act_allowed":False,"may_recover":False,"may_repair":False,
      "may_reclaim_lock":False,"may_choose_history":False}

def digest(record:object)->str:
    return hashlib.sha256(json.dumps(record,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def owned_url(url:str)->bool:
    try:
        parsed=urlsplit(url)
        host=(parsed.hostname or "").lower().rstrip(".")
        path=parsed.path.lower()
        if host in ("0root.ai","www.0root.ai","davidwise01.github.io"):
            return True
        if host in ("github.com","www.github.com","raw.githubusercontent.com") and (
            path.startswith("/davidwise01/") or path=="/davidwise01"):
            return True
        return False
    except ValueError:
        return False

def assess(record:dict)->dict:
    errors=set()
    if not isinstance(record,dict) or record.get("schema")!=SCHEMA:
        errors.add("ANCESTRY_SCHEMA_INVALID")
        record=record if isinstance(record,dict) else {}
    rows=record.get("witnesses")
    if not isinstance(rows,list) or len(rows)!=3:
        errors.add("EXACTLY_THREE_WITNESS_RECORDS_REQUIRED")
        rows=[]
    actual=[w if isinstance(w,dict) else {} for w in rows]
    for i,w in enumerate(actual):
        if any(not isinstance(w.get(field),str) or not w[field].strip() for field in FIELDS):
            errors.add("WITNESS_REQUIRED_FIELD_MISSING:"+str(i))
        if not SHA64.fullmatch(str(w.get("signing_key_sha256",""))):
            errors.add("WITNESS_KEY_FINGERPRINT_INVALID:"+str(i))
        if not SHA64.fullmatch(str(w.get("artifact_sha256",""))):
            errors.add("WITNESS_ARTIFACT_DIGEST_INVALID:"+str(i))
        url=w.get("source_url","")
        try:
            parsed=urlsplit(url)
            if parsed.scheme!="https" or not parsed.hostname or parsed.username or parsed.password:
                errors.add("WITNESS_SOURCE_URL_INVALID:"+str(i))
        except ValueError:
            errors.add("WITNESS_SOURCE_URL_INVALID:"+str(i))
        if owned_url(url) and w.get("corpus_id")!=OWNED_CORPUS:
            errors.add("OWNED_MIRROR_ANCESTRY_MISDECLARED:"+str(i))
        if owned_url(url) and w.get("claimed_independent_external") is True:
            errors.add("OWNED_MIRROR_MISCLASSIFIED_EXTERNAL:"+str(i))
        if w.get("signature_verified_out_of_band") is True or w.get("controller_authenticated_out_of_band") is True:
            errors.add("UNSUPPORTED_EXTERNAL_AUTHENTICATION_CLAIM:"+str(i))
        if w.get("operational_authority")!="HOLD" or w.get("physical_act_allowed") is not False:
            errors.add("WITNESS_AUTHORITY_PROMOTION:"+str(i))
    for i in range(len(actual)):
        for j in range(i+1,len(actual)):
            a,b=actual[i],actual[j]
            if a.get("corpus_id") and a.get("corpus_id")==b.get("corpus_id"):
                errors.add("SHARED_SOURCE_CORPUS:"+str(i)+":"+str(j))
            for k in ("root_id","ultimate_controller","operator","administrator","custody_host","signing_key_sha256"):
                if a.get(k) and a.get(k)==b.get(k):
                    errors.add("SHARED_CONTROL_OR_KEY:"+k+":"+str(i)+":"+str(j))
            if owned_url(a.get("source_url","")) and owned_url(b.get("source_url","")):
                errors.add("SAME_OWNED_MIRROR_ANCESTRY:"+str(i)+":"+str(j))
    if record.get("operational_authority")!="HOLD" or record.get("physical_act_allowed") is not False:
        errors.add("ROOT_AUTHORITY_PROMOTION")
    if record.get("previous_phase_freeze")!="../224/decision.json":
        errors.add("PREVIOUS_FREEZE_BINDING_MISSING")
    return {"schema":"AETHER-229/ancestry-assessment-v1",
        "verdict":"REJECT" if errors else "DOCUMENTARY_DISTINCT_CONTROL_CLAIMS_ONLY",
        "reasons":sorted(errors) if errors else ["EXTERNAL_CONTROLLER_ORIGIN_NOT_INDEPENDENTLY_AUTHENTICATED"],
        "witness_records_received":len(actual),"declared_witness_roots":len({x.get("root_id") for x in actual if x.get("root_id")}),
        "record_sha256":digest(record),**HOLD}

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--evidence",type=Path,required=True)
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    try:
        doc=json.loads(args.evidence.read_text(encoding="utf-8"))
    except (OSError,UnicodeError,ValueError):
        doc={}
    result=assess(doc)
    output=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(output,encoding="utf-8")
    print(output,end="")
    return 0 if result["verdict"]=="DOCUMENTARY_DISTINCT_CONTROL_CLAIMS_ONLY" else 1
if __name__=="__main__":
    sys.exit(main())
