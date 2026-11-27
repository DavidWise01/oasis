#!/usr/bin/env python3
"""AETHER-268-RS: byte-exact issuance pin check and durable local nonce fence.

An observed HTTPS body and locally committed nonce do not establish external custody.
"""
import argparse
import base64
import hashlib
import json
import sqlite3
from pathlib import Path
from urllib.parse import urlsplit

SCHEMA="AETHER-268/pinned-issuance-nonce-v1"
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_qualification_percent":0,"physical_act_allowed":False,
      "independent_issuer_custody_verified":False,"external_rollback_resistance_verified":False}
LIMIT=65536

def canon(data):
    return json.dumps(data,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def digest(data):
    return hashlib.sha256(data).hexdigest()
def sha(data):
    return digest(canon(data))

def check_pin(bundle):
    """Compare captured bytes to a prior expected digest and signed claim."""
    problems=[]
    if not isinstance(bundle,dict):
        return ["BUNDLE_INVALID"]
    expected={"issuance_url","challenge_sha256","expected_raw_sha256","retrieval","pin"}
    if set(bundle)!=expected:return ["BUNDLE_SCHEMA_INVALID"]
    url=bundle["issuance_url"]
    try:
        parsed=urlsplit(url)
        if parsed.scheme!="https" or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
            problems.append("ISSUANCE_URL_INVALID")
    except (TypeError,ValueError):
        problems.append("ISSUANCE_URL_INVALID")
    retrieval=bundle["retrieval"]
    pin=bundle["pin"]
    if not isinstance(retrieval,dict) or not isinstance(pin,dict):
        return problems+["RETRIEVAL_OR_PIN_INVALID"]
    wanted={"requested_url","raw_b64","raw_sha256","raw_length","observation_sha256"}
    if set(retrieval)!=wanted:return problems+["RETRIEVAL_SCHEMA_INVALID"]
    try:
        if not isinstance(retrieval["raw_b64"],str) or len(retrieval["raw_b64"])>90000:
            raise ValueError("ENCODING_LIMIT")
        raw=base64.b64decode(retrieval["raw_b64"],validate=True)
        if len(raw)>LIMIT or type(retrieval["raw_length"]) is not int or len(raw)!=retrieval["raw_length"]:
            problems.append("RAW_LENGTH_MISMATCH")
        if digest(raw)!=retrieval["raw_sha256"]:problems.append("RAW_DIGEST_MISMATCH")
        if digest(raw)!=bundle["expected_raw_sha256"]:problems.append("EXPECTED_ISSUANCE_PIN_MISMATCH")
    except (ValueError,TypeError):
        problems.append("RAW_BYTES_INVALID")
    if retrieval["requested_url"]!=url:problems.append("ISSUANCE_URL_SUBSTITUTED")
    if retrieval["observation_sha256"]!=sha({k:v for k,v in retrieval.items() if k!="observation_sha256"}):
        problems.append("RETRIEVAL_OBSERVATION_TAMPER")
    if set(pin)!={"challenge_sha256","raw_sha256","issuer_controller_claim","pin_sha256"}:
        problems.append("PIN_SCHEMA_INVALID")
    else:
        if pin["challenge_sha256"]!=bundle["challenge_sha256"]:
            problems.append("PIN_CHALLENGE_MISMATCH")
        if pin["raw_sha256"]!=bundle["expected_raw_sha256"]:
            problems.append("PIN_RAW_HASH_MISMATCH")
        if pin["pin_sha256"]!=sha({k:v for k,v in pin.items() if k!="pin_sha256"}):
            problems.append("PIN_SELF_HASH_MISMATCH")
    problems.extend(["RETRIEVAL_TRANSPORT_NOT_INDEPENDENTLY_ATTESTED",
                     "PIN_CUSTODIAN_NOT_INDEPENDENTLY_AUTHENTICATED"])
    return sorted(set(problems))

def connection(path):
    db=sqlite3.connect(str(path),timeout=8,isolation_level=None)
    db.execute("PRAGMA busy_timeout=8000")
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")
    return db

def initialize(path):
    db=connection(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS nonce_receipts (nonce TEXT PRIMARY KEY, challenge_sha256 TEXT NOT NULL, issuance_sha256 TEXT NOT NULL, receipt_sha256 TEXT NOT NULL UNIQUE)")
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:db.close()

def consume(path,nonce,challenge_sha256,issuance_sha256):
    if not isinstance(nonce,str) or not nonce or len(nonce)>128:
        raise ValueError("NONCE_INVALID")
    for field in (challenge_sha256,issuance_sha256):
        if not isinstance(field,str) or len(field)!=64 or any(c not in "0123456789abcdef" for c in field):
            raise ValueError("SHA256_INVALID")
    initialize(path)
    claim={"schema":SCHEMA,"nonce":nonce,"challenge_sha256":challenge_sha256,
           "issuance_sha256":issuance_sha256}
    receipt=sha(claim)
    db=connection(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        try:
            db.execute("INSERT INTO nonce_receipts VALUES (?,?,?,?)",
                       (nonce,challenge_sha256,issuance_sha256,receipt))
        except sqlite3.IntegrityError as e:
            db.rollback()
            raise ValueError("NONCE_REPLAY_OR_RECEIPT_COLLISION") from e
        db.commit()
        return {**claim,"receipt_sha256":receipt,**HOLD}
    except Exception:
        if db.in_transaction:db.rollback()
        raise
    finally:db.close()

def inspect(path):
    db=connection(path)
    try:
        db.execute("BEGIN")
        rows=db.execute("SELECT nonce,challenge_sha256,issuance_sha256,receipt_sha256 FROM nonce_receipts ORDER BY nonce").fetchall()
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:db.close()
    faults=[]
    for nonce,challenge,issuance,receipt in rows:
        if sha({"schema":SCHEMA,"nonce":nonce,"challenge_sha256":challenge,
                "issuance_sha256":issuance})!=receipt:
            faults.append("RECEIPT_TAMPER")
    return {"schema":SCHEMA,"consumed":len(rows),"reasons":sorted(set(faults+
            ["LOCAL_NONCE_HISTORY_NOT_EXTERNALLY_SEALED"])),**HOLD}

def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="operation",required=True)
    p=sub.add_parser("check-pin");p.add_argument("--input",type=Path,required=True)
    c=sub.add_parser("consume");c.add_argument("--db",type=Path,required=True)
    c.add_argument("--nonce",required=True);c.add_argument("--challenge-sha256",required=True)
    c.add_argument("--issuance-sha256",required=True)
    i=sub.add_parser("inspect");i.add_argument("--db",type=Path,required=True)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    try:
        if args.operation=="check-pin":
            raw=args.input.read_bytes()
            if len(raw)>200000:raise ValueError("BUNDLE_OVERSIZE")
            result={"schema":SCHEMA,"reasons":check_pin(json.loads(raw)),**HOLD}
        elif args.operation=="consume":
            result=consume(args.db,args.nonce,args.challenge_sha256,args.issuance_sha256)
        else:result=inspect(args.db)
    except (OSError,ValueError,TypeError,sqlite3.Error) as e:
        result={"schema":SCHEMA,"reasons":["INPUT_REJECTED:"+str(e)],**HOLD}
    rendered=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(rendered,encoding="utf-8")
    print(rendered,end="")
    return 1
if __name__=="__main__":raise SystemExit(main())
