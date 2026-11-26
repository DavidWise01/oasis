#!/usr/bin/env python3
"""AETHER-230 — documentary out-of-band challenge/replay evidence gate.

All bytes are read-only. This module validates exact receipt/ledger SHA-256,
challenge bindings and a hash-chained consumption history; it neither fetches
external evidence nor cryptographically authenticates controllers or devices.
Caller-provided pins and ledgers are NOT independent external witnesses.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

SCHEMA="AETHER-230/external-challenge-v1"
HEX64=re.compile(r"^[a-f0-9]{64}$")
HOLD={"independent_nonce_consumption_authenticated":False,
      "remote_signature_cryptographically_verified":False,
      "external_controller_authenticated":False,
      "independently_authenticated_witness_roots":0,
      "original_physical_captures_authenticated":0,
      "physical_qualification_percent":0,"operational_authority":"HOLD",
      "physical_act_allowed":False,"may_recover":False,"may_repair":False,
      "may_reclaim_lock":False,"may_choose_history":False}

def sha(raw:bytes)->str:
    return hashlib.sha256(raw).hexdigest()

def stable(v:object)->bytes:
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")

def valid_sha(v:object)->bool:
    return isinstance(v,str) and bool(HEX64.fullmatch(v))

def assess(record:dict,receipt_bytes:bytes|None,ledger_bytes:bytes|None)->dict:
    issues:set[str]=set()
    if not isinstance(record,dict):
        record={}
    if record.get("schema")!=SCHEMA:issues.add("CHALLENGE_SCHEMA_INVALID")
    nonce=record.get("nonce")
    if not isinstance(nonce,str) or len(nonce)<24 or len(set(nonce))<8:
        issues.add("NONCE_INVALID_OR_WEAK")
    for field in ("enrollment_id","challenge_id","custodian_id","source_root",
                  "holder_root","issuer_root","holder_key_sha256"):
        if not isinstance(record.get(field),str) or not record[field].strip():
            issues.add("REQUIRED_BINDING_MISSING:"+field)
    for name in ("source_root","holder_root","issuer_root"):
        for other in ("source_root","holder_root","issuer_root"):
            if name<other and record.get(name) and record.get(name)==record.get(other):
                issues.add("SHARED_SOURCE_CUSTODIAN_ISSUER_CONTROL")
    if not valid_sha(record.get("holder_key_sha256")):
        issues.add("HOLDER_KEY_FINGERPRINT_INVALID")
    for name in ("receipt_sha256","ledger_sha256","capture_sha256"):
        if not valid_sha(record.get(name)):
            issues.add("SHA256_PIN_MISSING:"+name)
    if receipt_bytes is None:issues.add("EXTERNAL_RECEIPT_NOT_OBSERVED")
    elif sha(receipt_bytes)!=record.get("receipt_sha256"):
        issues.add("RECEIPT_BYTE_DIGEST_MISMATCH")
    if ledger_bytes is None:issues.add("CONSUMPTION_LEDGER_NOT_OBSERVED")
    elif sha(ledger_bytes)!=record.get("ledger_sha256"):
        issues.add("LEDGER_BYTE_DIGEST_MISMATCH")
    receipt={}
    if receipt_bytes is not None:
        try:
            receipt=json.loads(receipt_bytes)
            if not isinstance(receipt,dict):raise ValueError("not object")
            for field in ("nonce","enrollment_id","challenge_id","custodian_id",
                          "holder_key_sha256","capture_sha256"):
                if receipt.get(field)!=record.get(field):
                    issues.add("RECEIPT_CHALLENGE_BINDING_MISMATCH:"+field)
            if receipt.get("signature_verification")!="NOT_PERFORMED":
                issues.add("RECEIPT_SIGNATURE_AUTHENTICATION_MISREPRESENTED")
            if receipt.get("operational_authority")!="HOLD" or receipt.get("physical_act_allowed") is not False:
                issues.add("RECEIPT_AUTHORITY_PROMOTION")
        except (UnicodeError,ValueError):
            issues.add("RECEIPT_JSON_INVALID")
    ledger={}
    if ledger_bytes is not None:
        try:
            ledger=json.loads(ledger_bytes)
            if not isinstance(ledger,dict):raise ValueError("not object")
            rows=ledger.get("entries")
            if not isinstance(rows,list) or not rows:raise ValueError("entries missing")
            previous="0"*64
            observed=set()
            matched=0
            for i,entry in enumerate(rows):
                if not isinstance(entry,dict):
                    issues.add("LEDGER_ENTRY_INVALID")
                    continue
                current=entry.get("nonce")
                if not isinstance(current,str) or not current:
                    issues.add("LEDGER_NONCE_INVALID")
                if current in observed:
                    issues.add("LEDGER_NONCE_REPLAY")
                observed.add(current)
                if entry.get("previous_sha256")!=previous:
                    issues.add("LEDGER_CHAIN_BROKEN")
                body={key:entry.get(key) for key in
                      ("nonce","enrollment_id","challenge_id","custodian_id","previous_sha256")}
                expected=sha(stable(body))
                if entry.get("entry_sha256")!=expected:
                    issues.add("LEDGER_ENTRY_DIGEST_INVALID")
                previous=expected
                if current==nonce:
                    matched+=1
                    if any(entry.get(key)!=record.get(key) for key in
                           ("enrollment_id","challenge_id","custodian_id")):
                        issues.add("LEDGER_CHALLENGE_BINDING_MISMATCH")
            if matched!=1:issues.add("CHALLENGE_NONCE_NOT_UNIQUELY_CONSUMED")
            if ledger.get("head_sha256")!=previous:
                issues.add("LEDGER_HEAD_MISMATCH")
            if ledger.get("controller_authentication")!="NOT_PERFORMED":
                issues.add("LEDGER_INDEPENDENCE_MISREPRESENTED")
        except (UnicodeError,ValueError):
            issues.add("LEDGER_JSON_INVALID")
    if record.get("external_controller_authentication")!="NOT_PERFORMED" or record.get("signature_verification")!="NOT_PERFORMED":
        issues.add("EXTERNAL_AUTHENTICATION_MISREPRESENTED")
    if record.get("operational_authority")!="HOLD" or record.get("physical_act_allowed") is not False or record.get("may_recover") is not False:
        issues.add("OPERATIONAL_AUTHORITY_PROMOTION")
    if record.get("previous_phase_freeze")!="../224/decision.json":
        issues.add("PREVIOUS_FREEZE_BINDING_INVALID")
    return {"schema":"AETHER-230/challenge-assessment-v1",
        "verdict":"REJECT" if issues else "DOCUMENTARY_CHALLENGE_LEDGER_CONSISTENT_ONLY",
        "reasons":sorted(issues) if issues else
          ["CONSUMPTION_LEDGER_AND_SIGNING_KEYS_NOT_AUTHENTICATED_OUT_OF_BAND"],
        "receipt_observed_sha256":sha(receipt_bytes) if receipt_bytes is not None else None,
        "ledger_observed_sha256":sha(ledger_bytes) if ledger_bytes is not None else None,
        **HOLD}

def read(path:Path|None)->bytes|None:
    try:
        if path is None or not path.is_file() or path.stat().st_size>4*1024*1024:return None
        return path.read_bytes()
    except OSError:return None

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--challenge",type=Path,required=True)
    ap.add_argument("--receipt",type=Path)
    ap.add_argument("--ledger",type=Path)
    ap.add_argument("--out",type=Path)
    a=ap.parse_args()
    try:
        challenge=json.loads(a.challenge.read_text(encoding="utf-8"))
    except (OSError,UnicodeError,ValueError):
        challenge={}
    result=assess(challenge,read(a.receipt),read(a.ledger))
    payload=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(payload,encoding="utf-8")
    print(payload,end="")
    return 0 if result["verdict"]=="DOCUMENTARY_CHALLENGE_LEDGER_CONSISTENT_ONLY" else 1

if __name__=="__main__":
    sys.exit(main())
