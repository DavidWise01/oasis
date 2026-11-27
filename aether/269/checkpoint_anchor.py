#!/usr/bin/env python3
"""AETHER-269-RS — locally anchored nonce snapshot rollback detection.

Signed snapshots establish consistency against a claimed public key, not external
custody, independent timestamps, or hardware-backed anti-rollback.
"""
import argparse
import base64
import hashlib
import json
import sqlite3
from pathlib import Path

SCHEMA="AETHER-269/nonce-anchor-v1"
RECEIPT_SCHEMA="AETHER-268/pinned-issuance-nonce-v1"
MAX_ROWS=4096
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_qualification_percent":0,"physical_act_allowed":False,
      "external_anchor_authenticated":False,
      "rollback_resistant_custody_verified":False}

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),
                      ensure_ascii=True,allow_nan=False).encode()

def sha(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()

def is_hex64(value):
    return (isinstance(value,str) and len(value)==64
            and all(c in "0123456789abcdef" for c in value))

def snapshot(path):
    """Read a consistent bounded AETHER-268 nonce set from local SQLite."""
    db=sqlite3.connect(str(path),timeout=5,isolation_level=None)
    try:
        db.execute("BEGIN")
        rows=db.execute("SELECT nonce,challenge_sha256,issuance_sha256,receipt_sha256 "
                        "FROM nonce_receipts ORDER BY nonce").fetchmany(MAX_ROWS+1)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    if len(rows)>MAX_ROWS:
        raise ValueError("NONCE_SET_TOO_LARGE")
    receipts=[dict(zip(("nonce","challenge_sha256","issuance_sha256","receipt_sha256"),r)) for r in rows]
    data={"schema":SCHEMA,"count":len(receipts),"receipts":receipts}
    return {**data,"snapshot_sha256":sha(data)}

def signed_anchor(snapshot_digest,count,run_id,controller_id,nonce):
    return {"schema":SCHEMA,"snapshot_sha256":snapshot_digest,"count":count,
            "run_id":run_id,"controller_id":controller_id,"anchor_nonce":nonce}

def verify_ed25519(public_pem,message,signature):
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key=serialization.load_pem_public_key(public_pem.encode("ascii"))
        if not isinstance(key,Ed25519PublicKey) or len(signature)!=64:return False
        key.verify(signature,message)
        return True
    except (ImportError,InvalidSignature,TypeError,ValueError,UnicodeError):
        return False

def verify_snapshot(data):
    failures=[]
    if not isinstance(data,dict) or set(data)!={"schema","count","receipts","snapshot_sha256"}:
        return ["SNAPSHOT_SCHEMA_INVALID"]
    if data["schema"]!=SCHEMA:failures.append("SNAPSHOT_VERSION_INVALID")
    receipts=data["receipts"]
    if not isinstance(receipts,list) or len(receipts)>MAX_ROWS:
        return failures+["SNAPSHOT_ROWS_INVALID"]
    if type(data["count"]) is not int or data["count"]!=len(receipts):
        failures.append("SNAPSHOT_COUNT_INVALID")
    if not is_hex64(data["snapshot_sha256"]) or data["snapshot_sha256"]!=sha({k:v for k,v in data.items() if k!="snapshot_sha256"}):
        failures.append("SNAPSHOT_DIGEST_INVALID")
    seen=set();previous=None
    for receipt in receipts:
        if not isinstance(receipt,dict) or set(receipt)!={"nonce","challenge_sha256","issuance_sha256","receipt_sha256"}:
            failures.append("RECEIPT_SCHEMA_INVALID")
            continue
        nonce=receipt["nonce"]
        if not isinstance(nonce,str) or not nonce or len(nonce)>128 or nonce in seen:
            failures.append("NONCE_DUPLICATE_OR_INVALID")
        if isinstance(nonce,str):
            if previous is not None and nonce<=previous:failures.append("NONCE_SORT_ORDER_INVALID")
            previous=nonce
            seen.add(nonce)
        if not all(is_hex64(receipt[k]) for k in ("challenge_sha256","issuance_sha256","receipt_sha256")):
            failures.append("RECEIPT_HASH_FORMAT_INVALID")
            continue
        statement={"schema":RECEIPT_SCHEMA,"nonce":nonce,
                   "challenge_sha256":receipt["challenge_sha256"],
                   "issuance_sha256":receipt["issuance_sha256"]}
        if receipt["receipt_sha256"]!=sha(statement):
            failures.append("NONCE_RECEIPT_HASH_INVALID")
    return sorted(set(failures))

def assess(bundle,signature_verify=verify_ed25519):
    problems=[];observed={"signature_valid":False}
    if not isinstance(bundle,dict):
        return {**HOLD,"reasons":["BUNDLE_INVALID"],"observed":observed}
    before=bundle.get("anchored_snapshot")
    after=bundle.get("recovered_snapshot")
    anchor=bundle.get("signed_anchor")
    pin=bundle.get("public_key_pin")
    problems.extend("BEFORE_"+issue for issue in verify_snapshot(before))
    problems.extend("AFTER_"+issue for issue in verify_snapshot(after))
    if not isinstance(anchor,dict) or set(anchor)!={"statement","signature_b64"}:
        problems.append("ANCHOR_ENVELOPE_INVALID")
        anchor={}
    statement=anchor.get("statement")
    expected={"schema","snapshot_sha256","count","run_id","controller_id","anchor_nonce"}
    if not isinstance(statement,dict) or set(statement)!=expected:
        problems.append("ANCHOR_STATEMENT_INVALID")
        statement={}
    else:
        if statement["schema"]!=SCHEMA or not is_hex64(statement["snapshot_sha256"]):
            problems.append("ANCHOR_STATEMENT_HASH_INVALID")
        if type(statement["run_id"]) is not int or statement["run_id"]<=0:
            problems.append("ANCHOR_RUN_INVALID")
        if not isinstance(statement["controller_id"],str) or not statement["controller_id"]:
            problems.append("ANCHOR_CONTROLLER_INVALID")
        if not isinstance(statement["anchor_nonce"],str) or not statement["anchor_nonce"]:
            problems.append("ANCHOR_NONCE_INVALID")
        if not isinstance(before,dict) or statement["snapshot_sha256"]!=before.get("snapshot_sha256") or statement["count"]!=before.get("count"):
            problems.append("SIGNED_ANCHOR_NOT_MATCHING_BEFORE")
    if not isinstance(pin,dict) or set(pin)!={"controller_id","public_key_pem"} or pin["controller_id"]!=statement.get("controller_id") or not isinstance(pin["public_key_pem"],str):
        problems.append("PUBLIC_KEY_PIN_UNAVAILABLE")
    else:
        try:
            signature=base64.b64decode(anchor["signature_b64"],validate=True)
            observed["signature_valid"]=bool(signature_verify(pin["public_key_pem"],canonical(statement),signature))
        except (ValueError,TypeError,UnicodeError):
            pass
        if not observed["signature_valid"]:
            problems.append("ANCHOR_SIGNATURE_INVALID")
    if isinstance(before,dict) and isinstance(after,dict) and isinstance(before.get("receipts"),list) and isinstance(after.get("receipts"),list):
        if len(after["receipts"])<len(before["receipts"]):
            problems.append("ROLLBACK_COUNT_DECREASED")
        prev={}
        for item in before["receipts"]:
            if isinstance(item,dict) and isinstance(item.get("nonce"),str):
                prev[item["nonce"]]=item
        present={}
        for item in after["receipts"]:
            if isinstance(item,dict) and isinstance(item.get("nonce"),str):
                present[item["nonce"]]=item
        for nonce,item in prev.items():
            if nonce not in present:problems.append("ANCHORED_NONCE_REMOVED")
            elif present[nonce]!=item:problems.append("ANCHORED_NONCE_REWRITTEN")
        observed["previous_nonces"]=len(prev)
        observed["recovered_nonces"]=len(present)
    problems.extend(["PIN_CUSTODY_NOT_EXTERNALLY_AUTHENTICATED",
                     "SIGNED_SNAPSHOT_NOT_EXTERNALLY_RETAINED",
                     "LOCAL_SQLITE_NOT_ROLLBACK_RESISTANT"])
    return {**HOLD,"reasons":sorted(set(problems)),"observed":observed}

def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="command",required=True)
    collect=sub.add_parser("snapshot")
    collect.add_argument("--db",type=Path,required=True)
    compare=sub.add_parser("review")
    compare.add_argument("--bundle",type=Path,required=True)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    try:
        if args.command=="snapshot":
            result=snapshot(args.db)
        else:
            raw=args.bundle.read_bytes()
            if len(raw)>2*1024*1024:raise ValueError("BUNDLE_SIZE_LIMIT")
            result=assess(json.loads(raw))
    except (OSError,ValueError,TypeError,sqlite3.Error) as exc:
        result={**HOLD,"reasons":["INPUT_REJECTED:"+type(exc).__name__]}
    value=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(value,encoding="utf-8")
    print(value,end="")
    return 1

if __name__=="__main__":
    raise SystemExit(main())
