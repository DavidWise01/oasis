#!/usr/bin/env python3
"""AETHER-272-RS: persistent local trust registry and atomic challenge receipt fence.

Local signed observation != independently acquired transport transcript or ACT.
"""
import argparse
import base64
import hashlib
import json
import sqlite3
from pathlib import Path

SCHEMA="AETHER-272/transcript-registry-v1"
MAX_BODY=65536
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_qualification_percent":0,"physical_act_allowed":False,
      "external_registry_custody_verified":False,"independent_transport_verified":False}

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),
                      ensure_ascii=True,allow_nan=False).encode("ascii")
def sha(value):return hashlib.sha256(canonical(value)).hexdigest()
def sha_bytes(raw):return hashlib.sha256(raw).hexdigest()
def hex64(x):return isinstance(x,str) and len(x)==64 and all(c in "0123456789abcdef" for c in x)

def signature_valid(pem,message,sig):
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key=serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key,Ed25519PublicKey) or len(sig)!=64:return False
        key.verify(sig,message);return True
    except (ImportError,InvalidSignature,ValueError,UnicodeError,TypeError):return False

def dbopen(path):
    db=sqlite3.connect(str(path),timeout=10,isolation_level=None)
    db.execute("PRAGMA busy_timeout=10000")
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")
    db.execute("PRAGMA foreign_keys=ON")
    return db

def init(path):
    db=dbopen(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS signer (key_id TEXT PRIMARY KEY, source_id TEXT NOT NULL UNIQUE, controller_id TEXT NOT NULL, public_key_pem TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS metadata (id INTEGER PRIMARY KEY CHECK(id=1), sealed_digest TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS receipt (session_nonce TEXT PRIMARY KEY, challenge_nonce TEXT NOT NULL, session_id TEXT NOT NULL UNIQUE, key_id TEXT NOT NULL, evidence_sha256 TEXT NOT NULL, signed_statement_sha256 TEXT NOT NULL, FOREIGN KEY(key_id) REFERENCES signer(key_id))")
        db.execute("CREATE TABLE IF NOT EXISTS challenge (challenge_nonce TEXT PRIMARY KEY, challenge_sha256 TEXT NOT NULL UNIQUE, registry_sha256 TEXT NOT NULL)")
        db.commit()
    except Exception:
        db.rollback();raise
    finally:db.close()

def registry_rows(db):
    return [dict(zip(("key_id","source_id","controller_id","public_key_pem"),row))
            for row in db.execute("SELECT key_id,source_id,controller_id,public_key_pem FROM signer ORDER BY key_id")]

def register(path,key_id,source_id,controller_id,pem):
    for name,value in (("key_id",key_id),("source_id",source_id),("controller_id",controller_id)):
        if not isinstance(value,str) or not value or len(value)>128:raise ValueError(name+"_INVALID")
    if not isinstance(pem,str) or len(pem)>4096 or not pem:raise ValueError("KEY_INVALID")
    init(path);db=dbopen(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM metadata WHERE id=1").fetchone():
            raise ValueError("REGISTRY_ALREADY_SEALED")
        db.execute("INSERT INTO signer VALUES (?,?,?,?)",(key_id,source_id,controller_id,pem))
        db.commit()
    except Exception:
        db.rollback();raise
    finally:db.close()

def seal(path):
    init(path);db=dbopen(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        registered=registry_rows(db)
        if len(registered)!=3 or len({r["controller_id"] for r in registered})!=3:
            raise ValueError("THREE_DISTINCT_LOCAL_CONTROLLER_CLAIMS_REQUIRED")
        digest=sha(registered)
        existing=db.execute("SELECT sealed_digest FROM metadata WHERE id=1").fetchone()
        if existing and existing[0]!=digest:raise ValueError("REGISTRY_SEAL_MISMATCH")
        db.execute("INSERT OR IGNORE INTO metadata VALUES (1,?)",(digest,))
        db.commit()
        return digest
    except Exception:
        db.rollback();raise
    finally:db.close()

def inspect(path):
    db=dbopen(path)
    try:
        db.execute("BEGIN")
        records=registry_rows(db)
        sealrow=db.execute("SELECT sealed_digest FROM metadata WHERE id=1").fetchone()
        challenges=db.execute("SELECT COUNT(*) FROM challenge").fetchone()[0]
        receipts=db.execute("SELECT COUNT(*) FROM receipt").fetchone()[0]
        db.commit()
        actual=sha(records)
        issues=[]
        if not sealrow:issues.append("REGISTRY_NOT_SEALED")
        elif actual!=sealrow[0]:issues.append("REGISTRY_SEAL_TAMPER")
        return {**HOLD,"schema":SCHEMA,"registry_digest":actual,
                "registered_keys":len(records),"used_challenges":challenges,
                "used_receipts":receipts,"reasons":issues+["LOCAL_REGISTRY_CUSTODY_ONLY"]}
    finally:db.close()

def consume_bundle(path,bundle,pin_sha256):
    """All-or-nothing signed receipt insertion, one SQLite writer transaction."""
    if not hex64(pin_sha256):raise ValueError("OUT_OF_BAND_PIN_REQUIRED")
    if not isinstance(bundle,dict) or set(bundle)!={"challenge","transcripts"}:
        raise ValueError("BUNDLE_SCHEMA_INVALID")
    challenge=bundle["challenge"];transcripts=bundle["transcripts"]
    if not isinstance(challenge,dict) or set(challenge)!={"challenge_id","nonce","source_commit","run_id"}:
        raise ValueError("CHALLENGE_SCHEMA_INVALID")
    for key in ("challenge_id","nonce"):
        if not isinstance(challenge[key],str) or not challenge[key] or len(challenge[key])>128:
            raise ValueError("CHALLENGE_FIELD_INVALID")
    if not isinstance(challenge["source_commit"],str) or len(challenge["source_commit"])!=40 or any(x not in "0123456789abcdef" for x in challenge["source_commit"]):
        raise ValueError("COMMIT_INVALID")
    if type(challenge["run_id"]) is not int or challenge["run_id"]<=0:raise ValueError("RUN_INVALID")
    if not isinstance(transcripts,list) or len(transcripts)!=3:
        raise ValueError("THREE_TRANSCRIPTS_REQUIRED")
    init(path);db=dbopen(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        registry=registry_rows(db)
        sealed=db.execute("SELECT sealed_digest FROM metadata WHERE id=1").fetchone()
        if not sealed or sealed[0]!=pin_sha256 or sha(registry)!=sealed[0]:
            raise ValueError("SEALED_REGISTRY_PIN_MISMATCH")
        lookup={x["key_id"]:x for x in registry}
        previous=db.execute("SELECT 1 FROM challenge WHERE challenge_nonce=?",(challenge["nonce"],)).fetchone()
        if previous:raise ValueError("CHALLENGE_REPLAY")
        nonces=set();sessions=set();keys=set();sources=set();controllers=set()
        prepared=[]
        for t in transcripts:
            required={"key_id","source_id","controller_id","session_id","session_nonce",
                      "requested_url","raw_b64","raw_sha256","signature_b64"}
            if not isinstance(t,dict) or set(t)!=required:
                raise ValueError("TRANSCRIPT_SCHEMA_INVALID")
            for k in ("key_id","source_id","controller_id","session_id","session_nonce"):
                if not isinstance(t[k],str) or not t[k] or len(t[k])>128:raise ValueError("TRANSCRIPT_FIELD_INVALID")
            if t["session_nonce"] in nonces or t["session_nonce"]==challenge["nonce"]:
                raise ValueError("SESSION_NONCE_REPLAY")
            if t["session_id"] in sessions:raise ValueError("SESSION_ID_REPLAY")
            if t["key_id"] in keys or t["source_id"] in sources or t["controller_id"] in controllers:
                raise ValueError("DUPLICATE_SIGNER_SOURCE_OR_CONTROLLER")
            nonces.add(t["session_nonce"]);sessions.add(t["session_id"])
            keys.add(t["key_id"]);sources.add(t["source_id"]);controllers.add(t["controller_id"])
            signer=lookup.get(t["key_id"])
            if not signer or signer["source_id"]!=t["source_id"] or signer["controller_id"]!=t["controller_id"]:
                raise ValueError("PINNED_SIGNER_MISMATCH")
            if not isinstance(t["requested_url"],str) or not t["requested_url"].startswith("https://") or len(t["requested_url"])>2048:
                raise ValueError("URL_INVALID")
            try:
                encoded=t["raw_b64"]
                if not isinstance(encoded,str) or len(encoded)>90000:raise ValueError("BODY_OVERSIZE")
                raw=base64.b64decode(encoded,validate=True)
                if len(raw)>MAX_BODY:raise ValueError("BODY_OVERSIZE")
                signature=base64.b64decode(t["signature_b64"],validate=True)
            except (ValueError,TypeError) as exc:raise ValueError("BAD_BASE64_OR_BODY") from exc
            if sha_bytes(raw)!=t["raw_sha256"]:raise ValueError("RAW_BODY_HASH_INVALID")
            statement={"schema":SCHEMA,"challenge":challenge,
                       "key_id":t["key_id"],"source_id":t["source_id"],"controller_id":t["controller_id"],
                       "session_id":t["session_id"],"session_nonce":t["session_nonce"],
                       "requested_url":t["requested_url"],"raw_sha256":t["raw_sha256"]}
            if not signature_valid(signer["public_key_pem"],canonical(statement),signature):
                raise ValueError("SIGNATURE_INVALID")
            if db.execute("SELECT 1 FROM receipt WHERE session_nonce=? OR session_id=?",(t["session_nonce"],t["session_id"])).fetchone():
                raise ValueError("PERSISTED_SESSION_REPLAY")
            prepared.append((t["session_nonce"],challenge["nonce"],t["session_id"],t["key_id"],
                             t["raw_sha256"],sha(statement)))
        db.execute("INSERT INTO challenge VALUES (?,?,?)",(challenge["nonce"],sha(challenge),pin_sha256))
        for entry in prepared:db.execute("INSERT INTO receipt VALUES (?,?,?,?,?,?)",entry)
        db.commit()
        return {**HOLD,"schema":SCHEMA,"locally_accepted_signed_transcripts":3,
                "challenge_sha256":sha(challenge),"registry_sha256":pin_sha256,
                "reasons":["LOCAL_SIGNATURE_VALIDITY_NOT_EXTERNAL_CUSTODY",
                           "TRANSPORT_ORIGIN_NOT_INDEPENDENTLY_OBSERVED"]}
    except Exception:
        db.rollback();raise
    finally:db.close()

def main():
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="operation",required=True)
    register_cmd=sub.add_parser("register")
    for name in ("key-id","source-id","controller-id"):
        register_cmd.add_argument("--"+name,required=True)
    register_cmd.add_argument("--public-key-file",type=Path,required=True)
    seal_cmd=sub.add_parser("seal");seal_cmd.add_argument("--db",type=Path,required=True)
    consume_cmd=sub.add_parser("consume")
    consume_cmd.add_argument("--db",type=Path,required=True)
    consume_cmd.add_argument("--bundle",type=Path,required=True)
    consume_cmd.add_argument("--trusted-registry-sha256",required=True)
    inspect_cmd=sub.add_parser("inspect");inspect_cmd.add_argument("--db",type=Path,required=True)
    register_cmd.add_argument("--db",type=Path,required=True)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    try:
        if a.operation=="register":
            register(a.db,a.key_id,a.source_id,a.controller_id,a.public_key_file.read_text(encoding="ascii"))
            result={**HOLD,"reasons":["REGISTRY_ENTRY_RECORDED_LOCALLY"]}
        elif a.operation=="seal":
            result={**HOLD,"registry_sha256":seal(a.db),"reasons":["LOCAL_REGISTRY_SEALED"]}
        elif a.operation=="inspect":result=inspect(a.db)
        else:
            raw=a.bundle.read_bytes()
            if len(raw)>512*1024:raise ValueError("BUNDLE_OVERSIZE")
            result=consume_bundle(a.db,json.loads(raw),a.trusted_registry_sha256)
    except (OSError,ValueError,TypeError,sqlite3.Error) as e:
        result={**HOLD,"reasons":["REJECTED:"+type(e).__name__+":"+str(e)[:128]]}
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(text,encoding="utf-8")
    print(text,end="")
    return 1
if __name__=="__main__":raise SystemExit(main())
