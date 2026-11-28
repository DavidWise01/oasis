#!/usr/bin/env python3
"""AETHER-276-RS: persistent signed receipts and two-key rotation fencing.

Local SQLite replay protection is not externally anchored anti-rollback.
"""
import argparse, base64, hashlib, json, sqlite3
from pathlib import Path

SCHEMA="AETHER-276/durable-receipts-v1"
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "external_custody_verified":False,"external_antirollback_verified":False}

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def digest(x):return hashlib.sha256(canon(x)).hexdigest()
def hex64(x):return isinstance(x,str) and len(x)==64 and all(c in "0123456789abcdef" for c in x)

def valid_signature(pem,statement,signature_b64):
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.exceptions import InvalidSignature
        public=serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(public,Ed25519PublicKey):return False
        signature=base64.b64decode(signature_b64,validate=True)
        if len(signature)!=64:return False
        public.verify(signature,canon(statement));return True
    except (ImportError,InvalidSignature,TypeError,ValueError,UnicodeError):return False

def dbopen(path):
    db=sqlite3.connect(str(path),timeout=10,isolation_level=None)
    db.execute("PRAGMA busy_timeout=10000")
    db.execute("PRAGMA synchronous=FULL")
    db.execute("PRAGMA journal_mode=WAL")
    return db

def initialize(path):
    db=dbopen(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS signer (source_id TEXT PRIMARY KEY, controller TEXT NOT NULL UNIQUE, key_pem TEXT NOT NULL, version INTEGER NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS rotation (id INTEGER PRIMARY KEY AUTOINCREMENT, source_id TEXT NOT NULL, old_key_sha TEXT NOT NULL, new_key_sha TEXT NOT NULL, old_sig_b64 TEXT NOT NULL, new_sig_b64 TEXT NOT NULL, previous_registry_sha TEXT NOT NULL, next_registry_sha TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS challenge (challenge_nonce TEXT PRIMARY KEY, challenge_sha TEXT NOT NULL UNIQUE, registry_sha TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS receipt (session_nonce TEXT PRIMARY KEY, session_id TEXT NOT NULL UNIQUE, challenge_nonce TEXT NOT NULL, source_id TEXT NOT NULL, payload_sha TEXT NOT NULL, signature_b64 TEXT NOT NULL)")
        db.commit()
    except Exception:
        db.rollback();raise
    finally:db.close()

def rows(db):
    return [dict(zip(("source_id","controller","key_pem","version"),entry)) for entry in
            db.execute("SELECT source_id,controller,key_pem,version FROM signer ORDER BY source_id")]

def registry_hash(db):
    return digest(rows(db))

def bootstrap(path,entries,expected_digest):
    if not isinstance(entries,list) or len(entries)!=3:
        raise ValueError("THREE_KEYS_REQUIRED")
    if not hex64(expected_digest) or digest(sorted(entries,key=lambda e:e["source_id"]))!=expected_digest:
        raise ValueError("BOOTSTRAP_PIN_MISMATCH")
    initialize(path);db=dbopen(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT COUNT(*) FROM signer").fetchone()[0]:
            raise ValueError("BOOTSTRAP_ALREADY_PERFORMED")
        for entry in entries:
            if not isinstance(entry,dict) or set(entry)!={"source_id","controller","key_pem","version"} or entry["version"]!=1:
                raise ValueError("KEY_ENTRY_INVALID")
            if any(not isinstance(entry[x],str) or not entry[x] for x in ("source_id","controller","key_pem")):
                raise ValueError("KEY_FIELD_INVALID")
            # The PEM must be an actual supported Ed25519 public key.
            if not isinstance(entry["key_pem"],str) or not len(entry["key_pem"])<4096:
                raise ValueError("KEY_PEM_INVALID")
            db.execute("INSERT INTO signer VALUES (?,?,?,?)",
                       (entry["source_id"],entry["controller"],entry["key_pem"],1))
        if registry_hash(db)!=expected_digest:raise ValueError("BOOTSTRAP_DIGEST_MISMATCH")
        db.commit()
    except Exception:
        db.rollback();raise
    finally:db.close()
    return {"registry_sha256":expected_digest,**HOLD}

def rotate(path,source_id,new_pem,old_signature,new_signature,expected_registry_sha):
    """Require both incumbent and successor key signatures over exact rotation."""
    if not hex64(expected_registry_sha):raise ValueError("REGISTRY_PIN_REQUIRED")
    initialize(path);db=dbopen(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        if registry_hash(db)!=expected_registry_sha:raise ValueError("REGISTRY_PIN_STALE")
        existing=db.execute("SELECT controller,key_pem,version FROM signer WHERE source_id=?",(source_id,)).fetchone()
        if not existing:raise ValueError("UNKNOWN_SOURCE")
        controller,old_pem,version=existing
        if not isinstance(new_pem,str) or len(new_pem)>4096 or new_pem==old_pem:
            raise ValueError("NEW_KEY_INVALID")
        statement={"schema":SCHEMA,"operation":"ROTATE","source_id":source_id,
                   "controller":controller,"previous_registry_sha256":expected_registry_sha,
                   "old_key_sha256":hashlib.sha256(old_pem.encode()).hexdigest(),
                   "new_key_sha256":hashlib.sha256(new_pem.encode()).hexdigest(),
                   "next_version":version+1}
        if not valid_signature(old_pem,statement,old_signature):
            raise ValueError("OLD_KEY_AUTHORIZATION_INVALID")
        if not valid_signature(new_pem,statement,new_signature):
            raise ValueError("NEW_KEY_POSSESSION_INVALID")
        db.execute("UPDATE signer SET key_pem=?,version=? WHERE source_id=?",(new_pem,version+1,source_id))
        next_hash=registry_hash(db)
        db.execute("INSERT INTO rotation (source_id,old_key_sha,new_key_sha,old_sig_b64,new_sig_b64,previous_registry_sha,next_registry_sha) VALUES (?,?,?,?,?,?,?)",
                   (source_id,statement["old_key_sha256"],statement["new_key_sha256"],
                    old_signature,new_signature,expected_registry_sha,next_hash))
        db.commit()
        return {"registry_sha256":next_hash,"rotation_statement_sha256":digest(statement),**HOLD}
    except Exception:
        db.rollback();raise
    finally:db.close()

def consume(path,bundle,expected_registry_sha):
    if not hex64(expected_registry_sha):raise ValueError("REGISTRY_PIN_REQUIRED")
    if not isinstance(bundle,dict) or set(bundle)!={"challenge","receipts"}:
        raise ValueError("BUNDLE_INVALID")
    challenge=bundle["challenge"];receipts=bundle["receipts"]
    if not isinstance(challenge,dict) or set(challenge)!={"nonce","id","run_id","source_commit"}:
        raise ValueError("CHALLENGE_INVALID")
    if not isinstance(challenge["nonce"],str) or not challenge["nonce"] or len(challenge["nonce"])>128:
        raise ValueError("CHALLENGE_NONCE_INVALID")
    if not isinstance(challenge["id"],str) or not challenge["id"]:raise ValueError("CHALLENGE_ID_INVALID")
    if type(challenge["run_id"]) is not int or challenge["run_id"]<1:raise ValueError("RUN_INVALID")
    if not isinstance(challenge["source_commit"],str) or len(challenge["source_commit"])!=40:
        raise ValueError("SOURCE_COMMIT_INVALID")
    if not isinstance(receipts,list) or len(receipts)!=3:raise ValueError("THREE_RECEIPTS_REQUIRED")
    initialize(path);db=dbopen(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        if registry_hash(db)!=expected_registry_sha:raise ValueError("REGISTRY_PIN_STALE")
        owners={r["source_id"]:r for r in rows(db)}
        seen_sources=set();seen_nonces=set();seen_sessions=set();prepared=[]
        for receipt in receipts:
            fields={"source_id","session_id","session_nonce","payload_sha256","signature_b64"}
            if not isinstance(receipt,dict) or set(receipt)!=fields:
                raise ValueError("RECEIPT_SCHEMA_INVALID")
            source=receipt["source_id"];sid=receipt["session_id"];nonce=receipt["session_nonce"]
            if not all(isinstance(x,str) and x and len(x)<=128 for x in (source,sid,nonce)):
                raise ValueError("RECEIPT_FIELD_INVALID")
            if source in seen_sources or sid in seen_sessions or nonce in seen_nonces or nonce==challenge["nonce"]:
                raise ValueError("DUPLICATE_OR_REPLAYED_LOCAL_RECEIPT")
            seen_sources.add(source);seen_sessions.add(sid);seen_nonces.add(nonce)
            if not hex64(receipt["payload_sha256"]):raise ValueError("PAYLOAD_DIGEST_INVALID")
            owner=owners.get(source)
            if not owner:raise ValueError("UNPINNED_SOURCE")
            stmt={"schema":SCHEMA,"operation":"RECEIPT","challenge":challenge,
                  "registry_sha256":expected_registry_sha,"source_id":source,
                  "session_id":sid,"session_nonce":nonce,
                  "payload_sha256":receipt["payload_sha256"]}
            if not valid_signature(owner["key_pem"],stmt,receipt["signature_b64"]):
                raise ValueError("RECEIPT_SIGNATURE_INVALID")
            if db.execute("SELECT 1 FROM receipt WHERE session_nonce=? OR session_id=?",
                          (nonce,sid)).fetchone():raise ValueError("PERSISTED_RECEIPT_REPLAY")
            prepared.append((nonce,sid,challenge["nonce"],source,receipt["payload_sha256"],
                             receipt["signature_b64"]))
        if set(owners)!=seen_sources:raise ValueError("SOURCE_SET_INCOMPLETE")
        db.execute("INSERT INTO challenge VALUES (?,?,?)",
                   (challenge["nonce"],digest(challenge),expected_registry_sha))
        for entry in prepared:db.execute("INSERT INTO receipt VALUES (?,?,?,?,?,?)",entry)
        db.commit()
        return {"challenge_sha256":digest(challenge),"receipts_committed":3,**HOLD}
    except sqlite3.IntegrityError as exc:
        db.rollback();raise ValueError("PERSISTED_CHALLENGE_OR_RECEIPT_REPLAY") from exc
    except Exception:
        db.rollback();raise
    finally:db.close()

def inspect(path):
    initialize(path);db=dbopen(path)
    try:
        db.execute("BEGIN")
        result={"registry_sha256":registry_hash(db),
                "registered_sources":len(rows(db)),
                "rotations":db.execute("SELECT COUNT(*) FROM rotation").fetchone()[0],
                "challenges":db.execute("SELECT COUNT(*) FROM challenge").fetchone()[0],
                "receipts":db.execute("SELECT COUNT(*) FROM receipt").fetchone()[0],**HOLD}
        db.commit();return result
    finally:db.close()

def main():
    p=argparse.ArgumentParser()
    subs=p.add_subparsers(dest="command",required=True)
    for name in ("bootstrap","rotate","consume","inspect"):
        sub=subs.add_parser(name);sub.add_argument("--db",type=Path,required=True)
        if name=="bootstrap":
            sub.add_argument("--keys",type=Path,required=True);sub.add_argument("--pin",required=True)
        if name=="rotate":
            sub.add_argument("--source-id",required=True);sub.add_argument("--new-key",type=Path,required=True)
            sub.add_argument("--old-signature-b64",required=True);sub.add_argument("--new-signature-b64",required=True)
            sub.add_argument("--pin",required=True)
        if name=="consume":
            sub.add_argument("--bundle",type=Path,required=True);sub.add_argument("--pin",required=True)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    try:
        if a.command=="bootstrap":
            result=bootstrap(a.db,json.loads(a.keys.read_text()),a.pin)
        elif a.command=="rotate":
            result=rotate(a.db,a.source_id,a.new_key.read_text(),
                          a.old_signature_b64,a.new_signature_b64,a.pin)
        elif a.command=="consume":
            result=consume(a.db,json.loads(a.bundle.read_text()),a.pin)
        else:result=inspect(a.db)
    except (OSError,ValueError,TypeError,sqlite3.Error) as exc:
        result={**HOLD,"reasons":["REJECTED:"+type(exc).__name__+":"+str(exc)[:96]]}
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(text,encoding="utf-8")
    print(text,end="")
    return 1
if __name__=="__main__":raise SystemExit(main())
