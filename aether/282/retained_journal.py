#!/usr/bin/env python3
"""AETHER-282-RS — retained original challenges, signed receipt replay, prefix audit.

Single SQLite journal. No external custody, physical ACT, or trusted timestamp.
"""
import argparse,base64,hashlib,json,sqlite3
from pathlib import Path

SCHEMA="AETHER-282/retained-challenge-v1"
ZERO="0"*64
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_qualification_percent":0,"physical_act_allowed":False,
      "external_checkpoint_custody_verified":False}
def canon(x):return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False,ensure_ascii=True).encode()
def sha(x):return hashlib.sha256(canon(x)).hexdigest()
def is_hash(x):return isinstance(x,str) and len(x)==64 and all(c in "0123456789abcdef" for c in x)
def verify(pem,statement,signature):
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key=serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key,Ed25519PublicKey):return False
        raw=base64.b64decode(signature,validate=True)
        if len(raw)!=64:return False
        key.verify(raw,canon(statement));return True
    except (ImportError,InvalidSignature,TypeError,ValueError,UnicodeError):return False
def connect(path):
    db=sqlite3.connect(str(path),timeout=8,isolation_level=None)
    db.execute("PRAGMA busy_timeout=8000")
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")
    return db
def initialize(path):
    db=connect(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS signer(source_id TEXT PRIMARY KEY,controller TEXT NOT NULL UNIQUE,pem TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS metadata(id INTEGER PRIMARY KEY CHECK(id=1),registry_sha TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS challenge(nonce TEXT PRIMARY KEY,original_json TEXT NOT NULL,challenge_sha TEXT NOT NULL UNIQUE)")
        db.execute("CREATE TABLE IF NOT EXISTS receipt(session_nonce TEXT PRIMARY KEY,session_id TEXT NOT NULL UNIQUE,challenge_nonce TEXT NOT NULL REFERENCES challenge(nonce),source_id TEXT NOT NULL REFERENCES signer(source_id),payload_sha TEXT NOT NULL,signature_b64 TEXT NOT NULL,UNIQUE(challenge_nonce,source_id))")
        db.execute("CREATE TABLE IF NOT EXISTS head(seq INTEGER PRIMARY KEY,previous_sha TEXT NOT NULL,head_sha TEXT NOT NULL UNIQUE,registry_sha TEXT NOT NULL,challenge_nonce TEXT NOT NULL UNIQUE REFERENCES challenge(nonce),challenge_count INTEGER NOT NULL,receipt_count INTEGER NOT NULL,run_id INTEGER NOT NULL)")
        db.commit()
    except Exception:db.rollback();raise
    finally:db.close()
def registry(db):
    return [dict(zip(("source_id","controller","pem"),r)) for r in
            db.execute("SELECT source_id,controller,pem FROM signer ORDER BY source_id")]
def bootstrap(path,entries,expected_pin):
    if not isinstance(entries,list) or len(entries)!=3 or not is_hash(expected_pin):
        raise ValueError("BOOTSTRAP_ENTRIES_OR_PIN_INVALID")
    for row in entries:
        if not isinstance(row,dict) or set(row)!={"source_id","controller","pem"} or any(not isinstance(v,str) or not v for v in row.values()):
            raise ValueError("REGISTRY_ROW_INVALID")
    ordered=sorted(entries,key=lambda r:r["source_id"])
    if sha(ordered)!=expected_pin:raise ValueError("REGISTRY_PIN_MISMATCH")
    initialize(path);db=connect(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM metadata WHERE id=1").fetchone():raise ValueError("ALREADY_BOOTSTRAPPED")
        for r in ordered:db.execute("INSERT INTO signer VALUES (?,?,?)",(r["source_id"],r["controller"],r["pem"]))
        if sha(registry(db))!=expected_pin:raise ValueError("REGISTRY_READBACK_CONFLICT")
        db.execute("INSERT INTO metadata VALUES (1,?)",(expected_pin,))
        db.commit()
        return {**HOLD,"registry_sha256":expected_pin}
    except Exception:db.rollback();raise
    finally:db.close()
def head_statement(seq,previous,registry_sha,nonce,nch,nrec,run):
    return {"schema":SCHEMA,"seq":seq,"previous_sha256":previous,
            "registry_sha256":registry_sha,"challenge_nonce":nonce,
            "challenge_count":nch,"receipt_count":nrec,"run_id":run}
def receipt_statement(challenge,registry_sha,source,session,nonce,payload):
    return {"schema":SCHEMA,"operation":"RECEIPT","challenge":challenge,
            "registry_sha256":registry_sha,"source_id":source,
            "session_id":session,"session_nonce":nonce,"payload_sha256":payload}
def append(path,bundle,registry_pin,expected_head):
    if not is_hash(registry_pin) or not is_hash(expected_head):raise ValueError("PIN_REQUIRED")
    if not isinstance(bundle,dict) or set(bundle)!={"challenge","receipts"}:
        raise ValueError("BUNDLE_INVALID")
    challenge=bundle["challenge"];receipts=bundle["receipts"]
    if not isinstance(challenge,dict) or set(challenge)!={"id","nonce","source_commit","run_id"}:
        raise ValueError("CHALLENGE_INVALID")
    if (not isinstance(challenge["id"],str) or not challenge["id"] or
        not isinstance(challenge["nonce"],str) or not challenge["nonce"] or len(challenge["nonce"])>128 or
        not isinstance(challenge["source_commit"],str) or len(challenge["source_commit"])!=40 or
        any(x not in "0123456789abcdef" for x in challenge["source_commit"]) or
        type(challenge["run_id"]) is not int or challenge["run_id"]<1):
        raise ValueError("CHALLENGE_FIELDS_INVALID")
    if not isinstance(receipts,list) or len(receipts)!=3:raise ValueError("THREE_RECEIPTS_REQUIRED")
    initialize(path);db=connect(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        seal=db.execute("SELECT registry_sha FROM metadata WHERE id=1").fetchone()
        keys=registry(db)
        if not seal or seal[0]!=registry_pin or sha(keys)!=registry_pin:
            raise ValueError("REGISTRY_SEAL_INVALID")
        existing=db.execute("SELECT seq,head_sha,run_id FROM head ORDER BY seq DESC LIMIT 1").fetchone()
        previous=existing[1] if existing else ZERO
        if previous!=expected_head:raise ValueError("STALE_HEAD")
        if existing and challenge["run_id"]<existing[2]:raise ValueError("RUN_ROLLBACK")
        key_by_source={r["source_id"]:r["pem"] for r in keys}
        seen=set()
        prepared=[]
        for r in receipts:
            required={"source_id","session_id","session_nonce","payload_sha256","signature_b64"}
            if not isinstance(r,dict) or set(r)!=required:
                raise ValueError("RECEIPT_INVALID")
            s=r["source_id"];sid=r["session_id"];nonce=r["session_nonce"]
            if any(not isinstance(v,str) or not v or len(v)>128 for v in (s,sid,nonce)):
                raise ValueError("RECEIPT_IDENTIFIERS_INVALID")
            if s in seen or s not in key_by_source or nonce==challenge["nonce"] or not is_hash(r["payload_sha256"]):
                raise ValueError("SOURCE_OR_NONCE_INVALID")
            seen.add(s)
            stmt=receipt_statement(challenge,registry_pin,s,sid,nonce,r["payload_sha256"])
            if not verify(key_by_source[s],stmt,r["signature_b64"]):
                raise ValueError("SIGNATURE_INVALID")
            prepared.append((nonce,sid,challenge["nonce"],s,r["payload_sha256"],r["signature_b64"]))
        if seen!=set(key_by_source):raise ValueError("INCOMPLETE_SIGNERS")
        # Signed original challenge bytes are retained with all receipts and head atomically.
        db.execute("INSERT INTO challenge VALUES (?,?,?)",(challenge["nonce"],canon(challenge).decode(),sha(challenge)))
        for row in prepared:db.execute("INSERT INTO receipt VALUES (?,?,?,?,?,?)",row)
        nch=db.execute("SELECT COUNT(*) FROM challenge").fetchone()[0]
        nr=db.execute("SELECT COUNT(*) FROM receipt").fetchone()[0]
        if nr!=3*nch:raise ValueError("CONSERVATION_VIOLATION")
        seq=existing[0]+1 if existing else 1
        stmt=head_statement(seq,previous,registry_pin,challenge["nonce"],nch,nr,challenge["run_id"])
        next_digest=sha(stmt)
        db.execute("INSERT INTO head VALUES (?,?,?,?,?,?,?,?)",
                   (seq,previous,next_digest,registry_pin,challenge["nonce"],nch,nr,challenge["run_id"]))
        db.commit()
        return {**HOLD,"seq":seq,"head_sha256":next_digest}
    except sqlite3.IntegrityError as exc:
        db.rollback();raise ValueError("PERSISTED_REPLAY") from exc
    except Exception:db.rollback();raise
    finally:db.close()
def examine(path,pinned_prefix_seq=None,pinned_prefix_sha=None):
    db=connect(path)
    try:
        db.execute("BEGIN")
        signers=registry(db)
        pinrow=db.execute("SELECT registry_sha FROM metadata WHERE id=1").fetchone()
        challenges=[dict(zip(("nonce","original_json","challenge_sha"),r)) for r in
            db.execute("SELECT nonce,original_json,challenge_sha FROM challenge ORDER BY nonce")]
        receipts=[dict(zip(("session_nonce","session_id","challenge_nonce","source_id","payload_sha","signature_b64"),r)) for r in
            db.execute("SELECT session_nonce,session_id,challenge_nonce,source_id,payload_sha,signature_b64 FROM receipt ORDER BY session_nonce")]
        heads=[dict(zip(("seq","previous_sha","head_sha","registry_sha","challenge_nonce","challenge_count","receipt_count","run_id"),r)) for r in
            db.execute("SELECT seq,previous_sha,head_sha,registry_sha,challenge_nonce,challenge_count,receipt_count,run_id FROM head ORDER BY seq")]
        db.commit()
    finally:db.close()
    problems=[]
    pin=pinrow[0] if pinrow else None
    if sha(signers)!=pin or len(signers)!=3:problems.append("REGISTRY_SEAL_INVALID")
    source_keys={s["source_id"]:s["pem"] for s in signers}
    original={}
    for ch in challenges:
        try:
            parsed=json.loads(ch["original_json"])
            if canon(parsed).decode()!=ch["original_json"] or sha(parsed)!=ch["challenge_sha"] or parsed["nonce"]!=ch["nonce"]:
                problems.append("ORIGINAL_CHALLENGE_TAMPERED")
            original[ch["nonce"]]=parsed
        except (ValueError,TypeError,KeyError):
            problems.append("ORIGINAL_CHALLENGE_UNREADABLE")
    sources={}
    for r in receipts:
        ch=original.get(r["challenge_nonce"])
        key=source_keys.get(r["source_id"])
        if not ch or not key:problems.append("RECEIPT_SOURCE_OR_CHALLENGE_MISSING");continue
        statement=receipt_statement(ch,pin,r["source_id"],r["session_id"],r["session_nonce"],r["payload_sha"])
        if not verify(key,statement,r["signature_b64"]):problems.append("STORED_RECEIPT_SIGNATURE_INVALID")
        sources.setdefault(r["challenge_nonce"],[]).append(r["source_id"])
    if len(receipts)!=3*len(challenges) or len(heads)!=len(challenges):
        problems.append("COUNT_CONSERVATION_INVALID")
    for ch in challenges:
        s=sources.get(ch["nonce"],[])
        if len(s)!=3 or len(set(s))!=3:problems.append("THREE_SOURCE_SET_INVALID")
    prev=ZERO;last_run=0
    for index,h in enumerate(heads):
        stmt=head_statement(h["seq"],h["previous_sha"],h["registry_sha"],
                            h["challenge_nonce"],h["challenge_count"],h["receipt_count"],h["run_id"])
        if (h["seq"]!=index+1 or h["previous_sha"]!=prev or h["head_sha"]!=sha(stmt)
            or h["challenge_count"]!=index+1 or h["receipt_count"]!=3*(index+1)
            or h["run_id"]<last_run or h["registry_sha"]!=pin or
            h["challenge_nonce"] not in original):
            problems.append("HEAD_CHAIN_INVALID")
        prev=h["head_sha"];last_run=h["run_id"]
    if pinned_prefix_seq is not None or pinned_prefix_sha is not None:
        if type(pinned_prefix_seq) is not int or pinned_prefix_seq<1 or not is_hash(pinned_prefix_sha):
            problems.append("PREFIX_PIN_INVALID")
        elif len(heads)<pinned_prefix_seq:problems.append("HISTORICAL_PREFIX_REMOVED")
        elif heads[pinned_prefix_seq-1]["head_sha"]!=pinned_prefix_sha:
            problems.append("HISTORICAL_PREFIX_CHANGED")
    problems.extend(["EXTERNAL_PREFIX_CUSTODY_UNVERIFIED",
                     "CONTROLLER_INDEPENDENCE_UNVERIFIED",
                     "LOCAL_DATABASE_REPLACEMENT_POSSIBLE"])
    return {**HOLD,"reasons":sorted(set(problems)),"observed":{
        "registry_sha256":sha(signers),"challenges":len(challenges),
        "receipts":len(receipts),"heads":len(heads),"last_head_sha256":prev,
        "all_receipt_signatures_rechecked":True}}
def main():
    p=argparse.ArgumentParser();subs=p.add_subparsers(dest="action",required=True)
    for action in ("bootstrap","append","audit"):
        sub=subs.add_parser(action);sub.add_argument("--db",type=Path,required=True)
        if action=="bootstrap":sub.add_argument("--keys",type=Path,required=True);sub.add_argument("--pin",required=True)
        if action=="append":
            sub.add_argument("--bundle",type=Path,required=True)
            sub.add_argument("--pin",required=True);sub.add_argument("--expected-head",required=True)
        if action=="audit":
            sub.add_argument("--prefix-seq",type=int);sub.add_argument("--prefix-sha256")
    a=p.parse_args()
    try:
        if a.action=="bootstrap":out=bootstrap(a.db,json.loads(a.keys.read_text()),a.pin)
        elif a.action=="append":out=append(a.db,json.loads(a.bundle.read_text()),a.pin,a.expected_head)
        else:out=examine(a.db,a.prefix_seq,a.prefix_sha256)
    except (OSError,ValueError,TypeError,KeyError,sqlite3.Error) as e:
        out={**HOLD,"reasons":["REJECTED:"+type(e).__name__+":"+str(e)[:80]]}
    print(json.dumps(out,sort_keys=True,indent=2))
    return 1
if __name__=="__main__":raise SystemExit(main())
