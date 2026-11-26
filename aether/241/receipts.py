#!/usr/bin/env python3
"""AETHER-241-RS: fail-closed signed cross-controller checkpoint receipts.

Cryptographic signatures validate statements only. Keys, clocks, controller
independence and externally held evidence must be authenticated separately.
"""
import argparse
import base64
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime, timezone

HOLD={"operational_authority":"HOLD","physical_qualification_percent":0,
      "physical_act_allowed":False,"independent_custody_authenticated":False}
SCHEMA="AETHER-241/cross-controller-checkpoint-v1"
HEX64=re.compile(r"^[0-9a-f]{64}$")
HEX40=re.compile(r"^[0-9a-f]{40}$")

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode("utf-8")

def utc(value):
    if not isinstance(value,str) or not value.endswith("Z"):
        raise ValueError("UTC_TIME_INVALID")
    t=datetime.fromisoformat(value.replace("Z","+00:00"))
    if t.utcoffset().total_seconds()!=0:
        raise ValueError("UTC_OFFSET_INVALID")
    return t

def openssl_ed25519(pem,message,signature):
    try:
        with tempfile.TemporaryDirectory() as root:
            root=Path(root)
            (root/"key.pem").write_text(pem,encoding="utf-8")
            (root/"msg").write_bytes(message)
            (root/"sig").write_bytes(signature)
            return subprocess.run(["openssl","pkeyutl","-verify","-pubin",
                "-inkey",str(root/"key.pem"),"-rawin","-in",str(root/"msg"),
                "-sigfile",str(root/"sig")],timeout=5,check=False,
                stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
    except (OSError,ValueError,subprocess.TimeoutExpired):
        return False

def evaluate(bundle,verify=openssl_ed25519):
    reasons=[]
    observed=[]
    if not isinstance(bundle,dict):
        return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
                "reasons":["BUNDLE_INVALID"],"observed":observed,**HOLD}
    receipts=bundle.get("receipts")
    trust=bundle.get("externally_pinned_keys")
    consumed=bundle.get("prior_consumed_nonces")
    run=bundle.get("run")
    if not isinstance(receipts,list) or len(receipts)!=3:
        reasons.append("EXACT_THREE_RECEIPTS_REQUIRED");receipts=[]
    if not isinstance(trust,dict):reasons.append("TRUST_ROOTS_MISSING");trust={}
    if not isinstance(consumed,list) or any(not isinstance(n,str) for n in consumed):
        reasons.append("NONCE_LEDGER_INVALID");consumed=[]
    if len(consumed)!=len(set(consumed)):reasons.append("NONCE_LEDGER_DUPLICATES")
    if not isinstance(run,dict):reasons.append("RUN_METADATA_MISSING");run={}
    ids=set();controllers=set();nonces=set();bindings=set()
    for envelope in receipts:
        if not isinstance(envelope,dict) or set(envelope)!={"key_id","signature_b64","statement"}:
            reasons.append("ENVELOPE_INVALID");continue
        kid=envelope["key_id"];statement=envelope["statement"]
        if not isinstance(kid,str) or not isinstance(statement,dict):
            reasons.append("STATEMENT_INVALID");continue
        required={"schema","repository","pin_commit","manifest_sha256","run_id",
                  "run_head","checkpoint_sha256","challenge_id","nonce",
                  "issued_at","checkpoint_at","controller_id"}
        if set(statement)!=required or statement.get("schema")!="AETHER-241/checkpoint-receipt-v1":
            reasons.append("STATEMENT_SCHEMA_INVALID");continue
        if kid in ids:reasons.append("DUPLICATE_KEY")
        ids.add(kid)
        controller=statement["controller_id"]
        if not isinstance(controller,str) or not controller:reasons.append("CONTROLLER_INVALID")
        elif controller in controllers:reasons.append("CONTROLLER_LABEL_DUPLICATE")
        controllers.add(controller)
        nonce=statement["nonce"]
        if not isinstance(nonce,str) or not nonce or len(nonce)>128:
            reasons.append("NONCE_INVALID")
        elif nonce in nonces or nonce in consumed:
            reasons.append("NONCE_REPLAY")
        nonces.add(nonce)
        if not all(isinstance(statement[k],str) and HEX40.fullmatch(statement[k])
                   for k in ("pin_commit","run_head")):
            reasons.append("COMMIT_INVALID")
        if not all(isinstance(statement[k],str) and HEX64.fullmatch(statement[k])
                   for k in ("manifest_sha256","checkpoint_sha256")):
            reasons.append("DIGEST_INVALID")
        if statement["repository"]!="DavidWise01/oasis" or type(statement["run_id"]) is not int or statement["run_id"]<=0:
            reasons.append("RUN_BINDING_INVALID")
        bind=tuple(statement.get(k) for k in
                   ("repository","pin_commit","manifest_sha256","run_id","run_head",
                    "checkpoint_sha256","challenge_id"))
        bindings.add(bind)
        if any(statement.get(k)!=run.get(k) for k in
               ("repository","pin_commit","manifest_sha256","run_id","run_head","checkpoint_sha256","challenge_id")):
            reasons.append("RECEIPT_RUN_MISMATCH")
        try:
            issued=utc(statement["issued_at"]);checkpoint=utc(statement["checkpoint_at"])
            started=utc(run["started_at"]);completed=utc(run["completed_at"])
            if issued>started:reasons.append("RECEIPT_ISSUED_AFTER_RUN_START")
            if checkpoint>issued:reasons.append("CHECKPOINT_TIMESTAMP_AFTER_RECEIPT")
            if completed<started:reasons.append("RUN_TIME_INVERTED")
        except (ValueError,KeyError,TypeError,OverflowError):
            reasons.append("TIMESTAMP_INVALID")
        root=trust.get(kid)
        if not isinstance(root,dict) or root.get("controller_id")!=controller or not isinstance(root.get("pem"),str):
            reasons.append("KEY_NOT_EXTERNALLY_PINNED");continue
        try:
            signature=base64.b64decode(envelope["signature_b64"],validate=True)
            if len(signature)!=64:raise ValueError("SIGNATURE_SIZE")
            valid=bool(verify(root["pem"],canonical(statement),signature))
        except (TypeError,ValueError):
            valid=False
        if not valid:reasons.append("SIGNATURE_INVALID")
        observed.append({"key_id":kid,"controller_label":controller,
                         "statement_sha256":hashlib.sha256(canonical(statement)).hexdigest(),
                         "signature_valid":valid})
    if len(bindings)!=1:reasons.append("CROSS_RECEIPT_BINDING_MISMATCH")
    if len(controllers)<3:reasons.append("THREE_CONTROLLER_LABELS_ABSENT")
    # This boundary deliberately cannot infer independence or trusted time from labels.
    reasons.append("EXTERNAL_CUSTODY_CONTROLLER_ANCESTRY_AND_CLOCK_UNAUTHENTICATED")
    return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
            "reasons":sorted(set(reasons)),"observed":observed,**HOLD}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--bundle",type=Path,required=True)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    try:
        raw=a.bundle.read_bytes()
        if len(raw)>256*1024:raise ValueError("INPUT_TOO_LARGE")
        result=evaluate(json.loads(raw))
    except (OSError,ValueError,TypeError) as error:
        result={"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
                "reasons":["INPUT_INVALID:"+type(error).__name__],"observed":[],**HOLD}
    s=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(s,encoding="utf-8")
    print(s,end="")
    return 1

if __name__=="__main__":
    raise SystemExit(main())
