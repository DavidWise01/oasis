#!/usr/bin/env python3
"""AETHER-284-RS — bounded HTTPS witness acquisition + local nonce sealing.

Observed TLS and pinned signatures do NOT establish external witness ownership.
"""
import argparse,base64,hashlib,json,sqlite3,sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"264"))
sys.path.insert(0,str(ROOT/"283"))
from acquisition import acquire,validate_url
from prefix_witness import assess as assess_prefix

SCHEMA="AETHER-284/acquired-prefix-v1"
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "independent_external_custody_verified":False,
      "externally_sealed_nonce_history_verified":False}
MAX_RESPONSE=65536
BLOCKING_EXCEPTIONS={"WITNESS_PUBLIC_KEY_CUSTODY_UNVERIFIED",
                     "CLAIMED_CONTROLLER_GRAPH_NOT_INDEPENDENTLY_ATTESTED",
                     "WITNESS_HISTORY_NOT_EXTERNALLY_PERSISTED",
                     "LOCAL_JOURNAL_CAN_BE_REPLACED"}

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def objhash(x):return digest(canon(x))
def hex64(x):return isinstance(x,str) and len(x)==64 and all(c in "0123456789abcdef" for c in x)

def raw_body(observation,url):
    if not isinstance(observation,dict) or observation.get("schema")!="AETHER-264/https-acquisition-v1":
        raise ValueError("OBSERVATION_SCHEMA_INVALID")
    if observation.get("requested_url")!=url:
        raise ValueError("OBSERVATION_URL_SUBSTITUTION")
    host,_=validate_url(url,[urlsplit(url).hostname])
    if observation.get("host")!=host or observation.get("tls_hostname_validation") is not True:
        raise ValueError("TLS_HOST_OBSERVATION_INVALID")
    if type(observation.get("status")) is not int or observation["status"] not in (200,206):
        raise ValueError("HTTP_STATUS_INVALID")
    encoded=observation.get("raw_b64")
    if not isinstance(encoded,str) or len(encoded)>90000:raise ValueError("RAW_LIMIT")
    try:raw=base64.b64decode(encoded,validate=True)
    except (ValueError,TypeError) as e:raise ValueError("RAW_ENCODING_INVALID") from e
    if len(raw)>MAX_RESPONSE or type(observation.get("raw_length")) is not int or len(raw)!=observation["raw_length"]:
        raise ValueError("RAW_SIZE_INVALID")
    if observation.get("raw_sha256")!=digest(raw):raise ValueError("RAW_DIGEST_INVALID")
    if observation.get("observation_sha256")!=objhash({k:v for k,v in observation.items() if k in {"schema","requested_url","host","pinned_ip","dns_address_count","tls_hostname_validation","status","elapsed_ms","raw_length","raw_sha256","raw_b64"}}):
        raise ValueError("OBSERVATION_HASH_INVALID")
    return raw

def connect(path):
    db=sqlite3.connect(str(path),timeout=10,isolation_level=None)
    db.execute("PRAGMA busy_timeout=10000")
    db.execute("PRAGMA synchronous=FULL")
    db.execute("PRAGMA journal_mode=WAL")
    return db

def initialize(path):
    db=connect(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS batch(id INTEGER PRIMARY KEY AUTOINCREMENT,trust_sha TEXT NOT NULL,challenge_nonce TEXT NOT NULL UNIQUE,previous_head TEXT NOT NULL,head_sha TEXT NOT NULL UNIQUE)")
        db.execute("CREATE TABLE IF NOT EXISTS witness_nonce(nonce TEXT PRIMARY KEY,batch_id INTEGER NOT NULL, key_id TEXT NOT NULL, raw_sha TEXT NOT NULL, observation_sha TEXT NOT NULL,FOREIGN KEY(batch_id) REFERENCES batch(id))")
        db.commit()
    except Exception:db.rollback();raise
    finally:db.close()

def acquire_and_seal(path,journal_path,trust_record,trust_pin,endpoints,challenge_nonce,collector=acquire):
    """Explicit opt-in to live HTTPS; no network is used by mock tests."""
    if not hex64(trust_pin) or objhash(trust_record)!=trust_pin:
        raise ValueError("TRUST_ROOT_PIN_MISMATCH")
    if (not isinstance(challenge_nonce,str) or len(challenge_nonce)<16 or len(challenge_nonce)>128):
        raise ValueError("FRESH_CHALLENGE_NONCE_REQUIRED")
    if not isinstance(trust_record,dict) or set(trust_record)!={"witness_keys","controller_ancestry","journal_controller"}:
        raise ValueError("TRUST_SCHEMA_INVALID")
    keys=trust_record["witness_keys"]
    if not isinstance(keys,dict) or len(keys)!=3 or not isinstance(endpoints,dict) or set(endpoints)!=set(keys):
        raise ValueError("THREE_PINNED_ENDPOINTS_REQUIRED")
    hosts=set()
    for url in endpoints.values():
        if not isinstance(url,str):raise ValueError("URL_INVALID")
        host,_=validate_url(url,[urlsplit(url).hostname])
        if host in hosts:raise ValueError("SHARED_ENDPOINT_HOST")
        hosts.add(host)
    initialize(path)
    db=connect(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM batch WHERE challenge_nonce=?",(challenge_nonce,)).fetchone():
            raise ValueError("PERSISTED_CHALLENGE_REPLAY")
        previous=db.execute("SELECT head_sha FROM batch ORDER BY id DESC LIMIT 1").fetchone()
        previous_head=previous[0] if previous else "0"*64
        claims=[];observations=[]
        seen_nonce=set()
        for key_id in sorted(keys):
            url=endpoints[key_id]
            host,_=validate_url(url,[urlsplit(url).hostname])
            observation=collector(url,[host])
            raw=raw_body(observation,url)
            if len(raw)>MAX_RESPONSE:raise ValueError("RAW_TOO_LARGE")
            try:claim=json.loads(raw)
            except (ValueError,UnicodeError) as e:raise ValueError("RAW_WITNESS_JSON_INVALID") from e
            expected={"key_id","controller_id","witness_nonce","prefix_seq",
                      "prefix_sha256","run_id","signature_b64"}
            if not isinstance(claim,dict) or set(claim)!=expected or claim["key_id"]!=key_id:
                raise ValueError("WITNESS_KEY_OR_SCHEMA_MISMATCH")
            nonce=claim["witness_nonce"]
            if not isinstance(nonce,str) or not nonce or len(nonce)>128 or nonce in seen_nonce or nonce==challenge_nonce:
                raise ValueError("WITNESS_NONCE_DUPLICATE")
            if db.execute("SELECT 1 FROM witness_nonce WHERE nonce=?",(nonce,)).fetchone():
                raise ValueError("PERSISTED_WITNESS_REPLAY")
            seen_nonce.add(nonce)
            claims.append(claim)
            observations.append({"key_id":key_id,"raw_sha256":digest(raw),
                                 "observation_sha256":observation["observation_sha256"],
                                 "requested_url":url})
        prior_nonces=[r[0] for r in db.execute("SELECT nonce FROM witness_nonce ORDER BY nonce")]
        review=assess_prefix(journal_path,{"trust_record":trust_record,
             "witnesses":claims,"previous_witness_nonces":prior_nonces},trust_pin)
        disallowed=set(review.get("reasons",[]))-BLOCKING_EXCEPTIONS
        if disallowed:raise ValueError("PREFIX_REVIEW_REJECTED:"+",".join(sorted(disallowed))[:160])
        receipt={"schema":SCHEMA,"trust_sha256":trust_pin,
                 "challenge_nonce":challenge_nonce,"previous_head_sha256":previous_head,
                 "witnesses":observations}
        head=objhash(receipt)
        db.execute("INSERT INTO batch(trust_sha,challenge_nonce,previous_head,head_sha) VALUES (?,?,?,?)",
                   (trust_pin,challenge_nonce,previous_head,head))
        batch_id=db.execute("SELECT last_insert_rowid()").fetchone()[0]
        for claim,observation in zip(claims,observations):
            db.execute("INSERT INTO witness_nonce VALUES (?,?,?,?,?)",
                       (claim["witness_nonce"],batch_id,claim["key_id"],
                        observation["raw_sha256"],observation["observation_sha256"]))
        db.commit()
        return {**HOLD,"batch_id":batch_id,"head_sha256":head,
                "witness_records":observations,
                "reasons":sorted(BLOCKING_EXCEPTIONS)}
    except Exception:
        db.rollback();raise
    finally:db.close()

def inspect(path):
    initialize(path);db=connect(path)
    try:
        db.execute("BEGIN")
        batches=db.execute("SELECT COUNT(*),MAX(id) FROM batch").fetchone()
        nonces=db.execute("SELECT COUNT(*) FROM witness_nonce").fetchone()[0]
        latest=db.execute("SELECT head_sha FROM batch ORDER BY id DESC LIMIT 1").fetchone()
        db.commit()
        return {**HOLD,"batches":batches[0],"witness_nonces":nonces,
                "last_head_sha256":latest[0] if latest else "0"*64,
                "reasons":["SQLITE_NONCE_HISTORY_NOT_EXTERNALLY_SEALED"]}
    finally:db.close()

def main():
    p=argparse.ArgumentParser()
    s=p.add_subparsers(dest="action",required=True)
    a=s.add_parser("capture")
    a.add_argument("--db",type=Path,required=True)
    a.add_argument("--journal",type=Path,required=True)
    a.add_argument("--trust-record",type=Path,required=True)
    a.add_argument("--trust-sha256",required=True)
    a.add_argument("--endpoints",type=Path,required=True)
    a.add_argument("--challenge-nonce",required=True)
    b=s.add_parser("inspect");b.add_argument("--db",type=Path,required=True)
    args=p.parse_args()
    try:
        if args.action=="capture":
            report=acquire_and_seal(args.db,args.journal,
                json.loads(args.trust_record.read_bytes()),args.trust_sha256,
                json.loads(args.endpoints.read_bytes()),args.challenge_nonce)
        else:report=inspect(args.db)
    except (OSError,ValueError,TypeError,KeyError,sqlite3.Error) as e:
        report={**HOLD,"reasons":["ACQUISITION_REJECTED:"+type(e).__name__+":"+str(e)[:100]]}
    print(json.dumps(report,sort_keys=True,indent=2))
    return 1
if __name__=="__main__":raise SystemExit(main())