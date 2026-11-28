#!/usr/bin/env python3
"""AETHER-280-RS — one SQLite commit for signed receipts AND high-water.

This establishes single-database commit atomicity, not external custody or ACT.
"""
import argparse
import base64
import hashlib
import json
import sqlite3
from pathlib import Path

SCHEMA="AETHER-280/atomic-journal-v1"
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "single_database_atomic_commit":True,
      "independent_external_custody_verified":False}
ZERO="0"*64

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def sha(x):return hashlib.sha256(canon(x)).hexdigest()
def hex64(x):return isinstance(x,str) and len(x)==64 and all(c in "0123456789abcdef" for c in x)

def verify_key(pem,statement,signature_b64):
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.exceptions import InvalidSignature
        key=serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key,Ed25519PublicKey):return False
        signature=base64.b64decode(signature_b64,validate=True)
        if len(signature)!=64:return False
        key.verify(signature,canon(statement))
        return True
    except (ImportError,InvalidSignature,ValueError,TypeError,UnicodeError):return False

def connect(path):
    db=sqlite3.connect(str(path),timeout=8,isolation_level=None)
    db.execute("PRAGMA busy_timeout=8000")
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")
    db.execute("PRAGMA foreign_keys=ON")
    return db

def init(path):
    db=connect(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS signer(source_id TEXT PRIMARY KEY, controller TEXT NOT NULL UNIQUE, public_key_pem TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS registry_seal(id INTEGER PRIMARY KEY CHECK(id=1), sha256 TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS challenge(nonce TEXT PRIMARY KEY, content_sha256 TEXT NOT NULL UNIQUE, registry_sha256 TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS receipt(session_nonce TEXT PRIMARY KEY, session_id TEXT NOT NULL UNIQUE, challenge_nonce TEXT NOT NULL REFERENCES challenge(nonce), source_id TEXT NOT NULL REFERENCES signer(source_id), payload_sha256 TEXT NOT NULL, signature_b64 TEXT NOT NULL, UNIQUE(challenge_nonce,source_id))")
        db.execute("CREATE TABLE IF NOT EXISTS highwater(seq INTEGER PRIMARY KEY, previous_sha256 TEXT NOT NULL, head_sha256 TEXT NOT NULL UNIQUE, registry_sha256 TEXT NOT NULL, challenge_count INTEGER NOT NULL, receipt_count INTEGER NOT NULL, run_id INTEGER NOT NULL, challenge_nonce TEXT NOT NULL UNIQUE REFERENCES challenge(nonce))")
        db.commit()
    except Exception:db.rollback();raise
    finally:db.close()

def registry(db):
    return [dict(zip(("source_id","controller","public_key_pem"),r)) for r in
            db.execute("SELECT source_id,controller,public_key_pem FROM signer ORDER BY source_id")]

def bootstrap(path,entries,expected_pin):
    if not isinstance(entries,list) or len(entries)!=3:raise ValueError("THREE_SIGNER_ENTRIES_REQUIRED")
    if not hex64(expected_pin):raise ValueError("OUT_OF_BAND_REGISTRY_PIN_REQUIRED")
    for r in entries:
        if not isinstance(r,dict) or set(r)!={"source_id","controller","public_key_pem"}:
            raise ValueError("REGISTRY_ENTRY_INVALID")
        if any(not isinstance(r[k],str) or not r[k] or len(r[k])>4096 for k in r):
            raise ValueError("REGISTRY_FIELD_INVALID")
    ordered=sorted(entries,key=lambda e:e["source_id"])
    if sha(ordered)!=expected_pin:raise ValueError("REGISTRY_PIN_MISMATCH")
    init(path)
    db=connect(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM registry_seal WHERE id=1").fetchone():
            raise ValueError("REGISTRY_ALREADY_BOOTSTRAPPED")
        for r in ordered:
            db.execute("INSERT INTO signer VALUES (?,?,?)",(r["source_id"],r["controller"],r["public_key_pem"]))
        if sha(registry(db))!=expected_pin:raise ValueError("REGISTRY_READBACK_MISMATCH")
        db.execute("INSERT INTO registry_seal VALUES (1,?)",(expected_pin,))
        db.commit()
        return {**HOLD,"registry_sha256":expected_pin}
    except Exception:
        db.rollback();raise
    finally:db.close()

def checkpoint(seq,previous_sha,registry_sha,challenge_count,receipt_count,run_id,nonce):
    return {"schema":SCHEMA,"seq":seq,"previous_sha256":previous_sha,
            "registry_sha256":registry_sha,"challenge_count":challenge_count,
            "receipt_count":receipt_count,"run_id":run_id,"challenge_nonce":nonce}

def get_head(db):
    return db.execute("SELECT seq,head_sha256,challenge_count,receipt_count,run_id FROM highwater ORDER BY seq DESC LIMIT 1").fetchone()

def commit_bundle(path,bundle,expected_registry_pin,expected_head):
    """Both receipt set and highwater are committed by one SQLite transaction."""
    if not hex64(expected_registry_pin) or not hex64(expected_head):
        raise ValueError("PINS_REQUIRED")
    if not isinstance(bundle,dict) or set(bundle)!={"challenge","receipts"}:
        raise ValueError("BUNDLE_INVALID")
    challenge=bundle["challenge"];receipts=bundle["receipts"]
    if not isinstance(challenge,dict) or set(challenge)!={"id","nonce","run_id","source_commit"}:
        raise ValueError("CHALLENGE_INVALID")
    if (not isinstance(challenge["id"],str) or not challenge["id"] or len(challenge["id"])>128 or
        not isinstance(challenge["nonce"],str) or not challenge["nonce"] or len(challenge["nonce"])>128 or
        type(challenge["run_id"]) is not int or challenge["run_id"]<1 or
        not isinstance(challenge["source_commit"],str) or len(challenge["source_commit"])!=40 or
        any(c not in "0123456789abcdef" for c in challenge["source_commit"])):
        raise ValueError("CHALLENGE_FIELDS_INVALID")
    if not isinstance(receipts,list) or len(receipts)!=3:raise ValueError("THREE_RECEIPTS_REQUIRED")
    init(path)
    db=connect(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        current=registry(db)
        sealed=db.execute("SELECT sha256 FROM registry_seal WHERE id=1").fetchone()
        if not sealed or sealed[0]!=expected_registry_pin or sha(current)!=expected_registry_pin:
            raise ValueError("REGISTRY_SEAL_MISMATCH")
        head=get_head(db)
        old_sha=head[1] if head else ZERO
        if old_sha!=expected_head:raise ValueError("STALE_CHECKPOINT_HEAD")
        if head and challenge["run_id"]<head[4]:raise ValueError("RUN_ID_ROLLBACK")
        lookup={r["source_id"]:r for r in current}
        ids=set();nonces=set();sources=set();prepared=[]
        for r in receipts:
            required={"source_id","session_id","session_nonce","payload_sha256","signature_b64"}
            if not isinstance(r,dict) or set(r)!=required:raise ValueError("RECEIPT_SCHEMA_INVALID")
            sid=r["session_id"];nonce=r["session_nonce"];source=r["source_id"]
            if any(not isinstance(x,str) or not x or len(x)>128 for x in (sid,nonce,source)):
                raise ValueError("RECEIPT_FIELDS_INVALID")
            if source in sources or sid in ids or nonce in nonces or nonce==challenge["nonce"]:
                raise ValueError("LOCAL_REPLAY_OR_SOURCE_REUSE")
            ids.add(sid);nonces.add(nonce);sources.add(source)
            if source not in lookup:raise ValueError("SOURCE_UNPINNED")
            if not hex64(r["payload_sha256"]):raise ValueError("PAYLOAD_HASH_INVALID")
            stmt={"schema":SCHEMA,"operation":"SIGNED_RECEIPT","challenge":challenge,
                  "registry_sha256":expected_registry_pin,"source_id":source,
                  "session_id":sid,"session_nonce":nonce,"payload_sha256":r["payload_sha256"]}
            if not verify_key(lookup[source]["public_key_pem"],stmt,r["signature_b64"]):
                raise ValueError("RECEIPT_SIGNATURE_INVALID")
            if db.execute("SELECT 1 FROM receipt WHERE session_nonce=? OR session_id=?",(nonce,sid)).fetchone():
                raise ValueError("PERSISTED_SESSION_REPLAY")
            prepared.append((nonce,sid,challenge["nonce"],source,r["payload_sha256"],r["signature_b64"]))
        if sources!=set(lookup):raise ValueError("INCOMPLETE_SOURCE_SET")
        # Both sets and the highwater transition are in this same transaction.
        db.execute("INSERT INTO challenge VALUES (?,?,?)",(challenge["nonce"],sha(challenge),expected_registry_pin))
        for data in prepared:db.execute("INSERT INTO receipt VALUES (?,?,?,?,?,?)",data)
        nch=db.execute("SELECT COUNT(*) FROM challenge").fetchone()[0]
        nrc=db.execute("SELECT COUNT(*) FROM receipt").fetchone()[0]
        if nrc!=3*nch:raise ValueError("RECEIPT_CONSERVATION_FAILED")
        seq=(head[0]+1) if head else 1
        next_statement=checkpoint(seq,old_sha,expected_registry_pin,nch,nrc,challenge["run_id"],challenge["nonce"])
        next_sha=sha(next_statement)
        db.execute("INSERT INTO highwater VALUES (?,?,?,?,?,?,?,?)",
                   (seq,old_sha,next_sha,expected_registry_pin,nch,nrc,challenge["run_id"],challenge["nonce"]))
        db.commit()
        return {**HOLD,"seq":seq,"highwater_sha256":next_sha,
                "challenge_count":nch,"receipt_count":nrc,
                "reasons":["ATOMIC_LOCAL_COMMIT_NOT_EXTERNAL_CUSTODY"]}
    except sqlite3.IntegrityError as exc:
        db.rollback();raise ValueError("PERSISTED_CHALLENGE_OR_SESSION_REPLAY") from exc
    except Exception:
        db.rollback();raise
    finally:db.close()

def inspect(path):
    init(path);db=connect(path)
    try:
        db.execute("BEGIN")
        current=registry(db);heads=list(db.execute("SELECT seq,previous_sha256,head_sha256,registry_sha256,challenge_count,receipt_count,run_id,challenge_nonce FROM highwater ORDER BY seq"))
        nch=db.execute("SELECT COUNT(*) FROM challenge").fetchone()[0]
        nrc=db.execute("SELECT COUNT(*) FROM receipt").fetchone()[0]
        seal=db.execute("SELECT sha256 FROM registry_seal WHERE id=1").fetchone()
        problems=[]
        if not seal or sha(current)!=seal[0]:problems.append("REGISTRY_SEAL_INVALID")
        previous=ZERO;prior_run=0
        for idx,row in enumerate(heads):
            seq,prev,head_sha,reg,c,r,run,nonce=row
            if seq!=idx+1 or prev!=previous:problems.append("HIGHWATER_LINK_INVALID")
            if sha(checkpoint(seq,prev,reg,c,r,run,nonce))!=head_sha:
                problems.append("HIGHWATER_HASH_INVALID")
            if r!=3*c or c!=idx+1 or r!=3*(idx+1):
                problems.append("HIGHWATER_COUNT_INVALID")
            if run<prior_run:problems.append("HIGHWATER_RUN_ROLLBACK")
            previous=head_sha;prior_run=run
        if len(heads)!=nch or nrc!=3*nch:problems.append("RECEIPT_HIGHWATER_COUNT_DIVERGENCE")
        db.commit()
        return {**HOLD,"registry_sha256":sha(current),"challenges":nch,
                "receipts":nrc,"checkpoints":len(heads),"last_head_sha256":previous,
                "reasons":sorted(set(problems+["LOCAL_SQLITE_ROLLBACK_POSSIBLE"]))}
    finally:db.close()

def main():
    parser=argparse.ArgumentParser()
    subs=parser.add_subparsers(dest="action",required=True)
    for name in ("bootstrap","commit","inspect"):
        p=subs.add_parser(name);p.add_argument("--db",type=Path,required=True)
        if name=="bootstrap":
            p.add_argument("--keys",type=Path,required=True);p.add_argument("--registry-pin",required=True)
        if name=="commit":
            p.add_argument("--bundle",type=Path,required=True)
            p.add_argument("--registry-pin",required=True);p.add_argument("--expected-head",required=True)
    parser.add_argument("--out",type=Path)
    a=parser.parse_args()
    try:
        if a.action=="bootstrap":result=bootstrap(a.db,json.loads(a.keys.read_text()),a.registry_pin)
        elif a.action=="commit":result=commit_bundle(a.db,json.loads(a.bundle.read_text()),a.registry_pin,a.expected_head)
        else:result=inspect(a.db)
    except (OSError,ValueError,TypeError,sqlite3.Error) as e:
        result={**HOLD,"reasons":["REJECTED:"+type(e).__name__+":"+str(e)[:120]]}
    rendered=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(rendered,encoding="utf-8")
    print(rendered,end="")
    return 1
if __name__=="__main__":raise SystemExit(main())
