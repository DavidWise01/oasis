#!/usr/bin/env python3
"""AETHER-286-RS: atomic complete acquisition preimages and nonce ledger.

Acquisition records are preserved as supplied by AETHER-264. TLS claims and
pinned signer keys do not establish independently controlled external custody.
"""
import argparse,base64,hashlib,json,sqlite3,sys
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"264"))
sys.path.insert(0,str(ROOT/"283"))
from acquisition import acquire,validate_url
from prefix_witness import assess as assess_prefix
SCHEMA="AETHER-286/atomic-manifest-v1"
ZERO="0"*64
MAX_RAW=65536
OBS_FIELDS={"schema","requested_url","host","pinned_ip","dns_address_count",
            "tls_hostname_validation","status","elapsed_ms","raw_length",
            "raw_sha256","raw_b64"}
CUSTODY_LIMITS={"WITNESS_PUBLIC_KEY_CUSTODY_UNVERIFIED",
                "CLAIMED_CONTROLLER_GRAPH_NOT_INDEPENDENTLY_ATTESTED",
                "WITNESS_HISTORY_NOT_EXTERNALLY_PERSISTED",
                "LOCAL_JOURNAL_CAN_BE_REPLACED"}
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "independent_custody_verified":False,"external_antirollback_verified":False}

def canonical(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def sha(v):return sha_bytes(canonical(v))
def valid_hash(v):return isinstance(v,str) and len(v)==64 and all(c in "0123456789abcdef" for c in v)

def extract(observation,url):
    """Verify actual 264 observation preimage; exclude its post-hash HOLD fields."""
    if not isinstance(observation,dict) or not OBS_FIELDS.issubset(observation):
        raise ValueError("OBSERVATION_FIELDS_INVALID")
    host,_=validate_url(url,[urlsplit(url).hostname])
    fields={k:observation[k] for k in OBS_FIELDS}
    if (fields["schema"]!="AETHER-264/https-acquisition-v1" or
        fields["requested_url"]!=url or fields["host"]!=host or
        fields["tls_hostname_validation"] is not True or
        type(fields["status"]) is not int or fields["status"] not in (200,206)):
        raise ValueError("OBSERVATION_TRANSPORT_MISMATCH")
    raw_b64=fields["raw_b64"]
    if not isinstance(raw_b64,str) or len(raw_b64)>90000:
        raise ValueError("ENCODED_BODY_TOO_LARGE")
    try: raw=base64.b64decode(raw_b64,validate=True)
    except (TypeError,ValueError) as e:raise ValueError("RAW_BASE64_INVALID") from e
    if (len(raw)>MAX_RAW or type(fields["raw_length"]) is not int or
        fields["raw_length"]!=len(raw) or fields["raw_sha256"]!=sha_bytes(raw)):
        raise ValueError("RAW_BODY_TAMPER")
    if observation.get("observation_sha256")!=sha(fields):
        raise ValueError("OBSERVATION_PREIMAGE_TAMPER")
    return raw,fields

def connection(path):
    db=sqlite3.connect(str(path),timeout=10,isolation_level=None)
    db.execute("PRAGMA busy_timeout=10000")
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")
    db.execute("PRAGMA foreign_keys=ON")
    return db

def init(path):
    db=connection(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS batch(id INTEGER PRIMARY KEY AUTOINCREMENT,challenge_nonce TEXT NOT NULL UNIQUE,previous_sha TEXT NOT NULL,head_sha TEXT NOT NULL UNIQUE,trust_sha TEXT NOT NULL,manifest_json TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS witness_nonce(nonce TEXT PRIMARY KEY,batch_id INTEGER NOT NULL REFERENCES batch(id),key_id TEXT NOT NULL,UNIQUE(batch_id,key_id))")
        db.commit()
    except Exception:db.rollback();raise
    finally:db.close()

def audit_rows(rows,nonces,prefix_seq=None,prefix_sha=None):
    errors=[];previous=ZERO;used_challenges=set();used_nonces=set()
    grouped={}
    for n in nonces:
        if not isinstance(n,dict) or set(n)!={"nonce","batch_id","key_id"}:
            errors.append("NONCE_SCHEMA_INVALID");continue
        if n["nonce"] in used_nonces:errors.append("NONCE_REPLAY")
        used_nonces.add(n["nonce"])
        grouped.setdefault(n["batch_id"],[]).append(n)
    for ix,row in enumerate(rows,1):
        if row["id"]!=ix:errors.append("BATCH_SEQUENCE_GAP")
        if row["previous_sha"]!=previous:errors.append("BATCH_PARENT_MISMATCH")
        if row["challenge_nonce"] in used_challenges:errors.append("CHALLENGE_REPLAY")
        used_challenges.add(row["challenge_nonce"])
        try: m=json.loads(row["manifest_json"])
        except (ValueError,TypeError):
            errors.append("MANIFEST_JSON_INVALID");previous=row["head_sha"];continue
        if (canonical(m).decode()!=row["manifest_json"] or
            not isinstance(m,dict) or set(m)!={"schema","trust_sha256","challenge_nonce","previous_head_sha256","witnesses"}):
            errors.append("MANIFEST_CANONICAL_SCHEMA_INVALID")
            previous=row["head_sha"];continue
        if (m["schema"]!=SCHEMA or m["trust_sha256"]!=row["trust_sha"] or
            m["challenge_nonce"]!=row["challenge_nonce"] or
            m["previous_head_sha256"]!=row["previous_sha"]):
            errors.append("MANIFEST_HEADER_CONFLICT")
        if sha(m)!=row["head_sha"]:errors.append("BATCH_HEAD_TAMPER")
        witnesses=m["witnesses"]
        local=grouped.get(row["id"],[])
        if not isinstance(witnesses,list) or len(witnesses)!=3 or len(local)!=3:
            errors.append("THREE_WITNESS_CONSERVATION_INVALID")
        else:
            key_ids=set();manifest_nonces=set()
            for w in witnesses:
                needed={"key_id","url","observation","claim_json"}
                if not isinstance(w,dict) or set(w)!=needed:
                    errors.append("WITNESS_MANIFEST_INVALID");continue
                if w["key_id"] in key_ids:errors.append("DUPLICATE_MANIFEST_KEY")
                key_ids.add(w["key_id"])
                try:
                    claim=json.loads(w["claim_json"])
                    if canonical(claim).decode()!=w["claim_json"] or claim["key_id"]!=w["key_id"]:
                        errors.append("CLAIM_CANONICAL_MISMATCH")
                    raw,obs=extract(w["observation"],w["url"])
                    if raw!=w["claim_json"].encode():
                        errors.append("RAW_CLAIM_MISMATCH")
                    manifest_nonces.add((claim["witness_nonce"],w["key_id"]))
                except (KeyError,ValueError,TypeError,UnicodeError):
                    errors.append("RETAINED_PREIMAGE_INVALID")
            if manifest_nonces!={(n["nonce"],n["key_id"]) for n in local}:
                errors.append("NONCE_MANIFEST_MISMATCH")
        previous=row["head_sha"]
    if len(nonces)!=3*len(rows) or len(grouped)!=len(rows):
        errors.append("GLOBAL_NONCE_CONSERVATION_INVALID")
    if prefix_seq is not None or prefix_sha is not None:
        if type(prefix_seq) is not int or prefix_seq<1 or not valid_hash(prefix_sha):
            errors.append("EXTERNAL_PREFIX_FORMAT_INVALID")
        elif len(rows)<prefix_seq:errors.append("EXTERNAL_PREFIX_MISSING")
        elif rows[prefix_seq-1]["head_sha"]!=prefix_sha:
            errors.append("EXTERNAL_PREFIX_CONFLICT")
    return sorted(set(errors))

def readback(path):
    db=sqlite3.connect(Path(path).resolve().as_uri()+"?mode=ro",uri=True,timeout=5,isolation_level=None)
    try:
        db.execute("PRAGMA query_only=ON")
        db.execute("BEGIN")
        rows=[dict(zip(("id","challenge_nonce","previous_sha","head_sha","trust_sha","manifest_json"),r)) for r in
              db.execute("SELECT id,challenge_nonce,previous_sha,head_sha,trust_sha,manifest_json FROM batch ORDER BY id")]
        nonces=[dict(zip(("nonce","batch_id","key_id"),r)) for r in
                db.execute("SELECT nonce,batch_id,key_id FROM witness_nonce ORDER BY batch_id,key_id")]
        db.commit()
    finally:db.close()
    return rows,nonces

def inspect(path,prefix_seq=None,prefix_sha=None):
    rows,nonces=readback(path)
    return {**HOLD,"batches":len(rows),"witness_nonces":len(nonces),
            "latest_head_sha256":rows[-1]["head_sha"] if rows else ZERO,
            "reasons":sorted(set(audit_rows(rows,nonces,prefix_seq,prefix_sha)+
                ["EXTERNAL_CUSTODY_UNVERIFIED","SQLITE_ROLLBACK_POSSIBLE"]))}

def capture(path,journal,trust,pin,urls,challenge,collector=acquire):
    if not valid_hash(pin) or sha(trust)!=pin:raise ValueError("TRUST_PIN_INVALID")
    if not isinstance(challenge,str) or len(challenge)<16 or len(challenge)>128:
        raise ValueError("CHALLENGE_NONCE_INVALID")
    if (not isinstance(trust,dict) or set(trust)!={"witness_keys","controller_ancestry","journal_controller"} or
        not isinstance(trust["witness_keys"],dict) or len(trust["witness_keys"])!=3 or
        not isinstance(urls,dict) or set(urls)!=set(trust["witness_keys"])):
        raise ValueError("TRUST_AND_ENDPOINTS_INVALID")
    hosts=set()
    for url in urls.values():
        host,_=validate_url(url,[urlsplit(url).hostname])
        if host in hosts:raise ValueError("DUPLICATE_ENDPOINT_HOST")
        hosts.add(host)
    init(path);db=connection(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM batch WHERE challenge_nonce=?",(challenge,)).fetchone():
            raise ValueError("PERSISTED_CHALLENGE_REPLAY")
        existing=db.execute("SELECT head_sha FROM batch ORDER BY id DESC LIMIT 1").fetchone()
        previous=existing[0] if existing else ZERO
        witnesses=[];claims=[];nonce_set=set()
        for kid in sorted(urls):
            url=urls[kid]
            host,_=validate_url(url,[urlsplit(url).hostname])
            observation=collector(url,[host])
            raw,obs=extract(observation,url)
            try: claim=json.loads(raw)
            except (ValueError,UnicodeError) as e:raise ValueError("CLAIM_JSON_INVALID") from e
            if canonical(claim)!=raw:raise ValueError("NONCANONICAL_ORIGINAL_CLAIM")
            if not isinstance(claim,dict) or claim.get("key_id")!=kid:
                raise ValueError("CLAIM_SOURCE_MISMATCH")
            nonce=claim.get("witness_nonce")
            if not isinstance(nonce,str) or not nonce or len(nonce)>128 or nonce in nonce_set or nonce==challenge:
                raise ValueError("DUPLICATED_WITNESS_NONCE")
            if db.execute("SELECT 1 FROM witness_nonce WHERE nonce=?",(nonce,)).fetchone():
                raise ValueError("PERSISTED_WITNESS_REPLAY")
            nonce_set.add(nonce);claims.append(claim)
            witnesses.append({"key_id":kid,"url":url,
                              "observation":{**obs,"observation_sha256":observation["observation_sha256"]},
                              "claim_json":raw.decode("utf-8")})
        prior=[r[0] for r in db.execute("SELECT nonce FROM witness_nonce ORDER BY nonce")]
        review=assess_prefix(journal,{"trust_record":trust,"witnesses":claims,
                           "previous_witness_nonces":prior},pin)
        errors=set(review.get("reasons",[]))-CUSTODY_LIMITS
        if errors:raise ValueError("SIGNED_PREFIX_REJECTED:"+",".join(sorted(errors))[:160])
        manifest={"schema":SCHEMA,"trust_sha256":pin,"challenge_nonce":challenge,
                  "previous_head_sha256":previous,"witnesses":witnesses}
        head=sha(manifest)
        db.execute("INSERT INTO batch(challenge_nonce,previous_sha,head_sha,trust_sha,manifest_json) VALUES (?,?,?,?,?)",
                   (challenge,previous,head,pin,canonical(manifest).decode()))
        bid=db.execute("SELECT last_insert_rowid()").fetchone()[0]
        for claim in claims:
            db.execute("INSERT INTO witness_nonce VALUES (?,?,?)",
                       (claim["witness_nonce"],bid,claim["key_id"]))
        db.commit()
        return {**HOLD,"batch_id":bid,"head_sha256":head,
                "manifest_sha256":head,"manifest_preimages_retained":3,
                "reasons":["EXTERNAL_CUSTODY_UNVERIFIED","LOCAL_SQLITE_ROLLBACK_POSSIBLE"]}
    except Exception:
        db.rollback();raise
    finally:db.close()

def main():
    p=argparse.ArgumentParser()
    s=p.add_subparsers(dest="action",required=True)
    a=s.add_parser("capture")
    a.add_argument("--db",type=Path,required=True);a.add_argument("--journal",type=Path,required=True)
    a.add_argument("--trust",type=Path,required=True);a.add_argument("--pin",required=True)
    a.add_argument("--endpoints",type=Path,required=True);a.add_argument("--challenge",required=True)
    b=s.add_parser("audit")
    b.add_argument("--db",type=Path,required=True);b.add_argument("--prefix-seq",type=int)
    b.add_argument("--prefix-sha")
    x=p.parse_args()
    try:
        if x.action=="capture":result=capture(x.db,x.journal,json.loads(x.trust.read_bytes()),
                                              x.pin,json.loads(x.endpoints.read_bytes()),x.challenge)
        else:result=inspect(x.db,x.prefix_seq,x.prefix_sha)
    except (ValueError,TypeError,KeyError,OSError,sqlite3.Error) as error:
        result={**HOLD,"reasons":["REJECTED:"+type(error).__name__+":"+str(error)[:100]]}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 1
if __name__=="__main__":raise SystemExit(main())
