#!/usr/bin/env python3
"""AETHER-289-RS — exact remote export readback and ACK high-water anchoring.

This module records observation, not independent custody or operational authority.
"""
import argparse,base64,hashlib,json,sqlite3,sys
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"264"),str(ROOT/"286"),str(ROOT/"287"),str(ROOT/"288")]
from acquisition import acquire,validate_url
from atomic_manifest import readback as source_readback
from export_audit import verify_export
from ack_acquisition import audit as ack_audit
SCHEMA="AETHER-289/remote-export-readback-v1"
ANCHOR_SCHEMA="AETHER-289/highwater-anchor-v1"
ZERO="0"*64
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "independent_external_custody_verified":False,
      "external_antirollback_verified":False}
FIELDS=("schema","requested_url","host","pinned_ip","dns_address_count",
        "tls_hostname_validation","status","elapsed_ms","raw_length",
        "raw_sha256","raw_b64")
MAX_BYTES=65536
def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def digest(raw):return hashlib.sha256(raw).hexdigest()
def sha(x):return digest(canon(x))
def hash64(x):return isinstance(x,str) and len(x)==64 and all(c in "0123456789abcdef" for c in x)
def observation(raw_obs,url):
    """Hash only AETHER-264 acquisition-preimage fields, not appended HOLD values."""
    if not isinstance(raw_obs,dict) or any(field not in raw_obs for field in FIELDS):
        raise ValueError("ACQUISITION_OBSERVATION_INCOMPLETE")
    host,_=validate_url(url,[urlsplit(url).hostname])
    fields={k:raw_obs[k] for k in FIELDS}
    if (fields["schema"]!="AETHER-264/https-acquisition-v1"
        or fields["requested_url"]!=url or fields["host"]!=host
        or fields["tls_hostname_validation"] is not True
        or type(fields["status"]) is not int or fields["status"]!=200):
        raise ValueError("ACQUISITION_TRANSPORT_MISMATCH")
    if not isinstance(fields["raw_b64"],str) or len(fields["raw_b64"])>90000:
        raise ValueError("RAW_BODY_LIMIT")
    try:raw=base64.b64decode(fields["raw_b64"],validate=True)
    except (ValueError,TypeError) as e:raise ValueError("RAW_BASE64_INVALID") from e
    if (len(raw)>MAX_BYTES or type(fields["raw_length"]) is not int
        or len(raw)!=fields["raw_length"] or fields["raw_sha256"]!=digest(raw)):
        raise ValueError("REMOTE_BODY_DIGEST_OR_LENGTH_INVALID")
    if raw_obs.get("observation_sha256")!=sha(fields):
        raise ValueError("OBSERVATION_PREIMAGE_CHANGED")
    return raw,{**fields,"observation_sha256":raw_obs["observation_sha256"]}
def connect(path):
    db=sqlite3.connect(str(path),timeout=10,isolation_level=None)
    db.execute("PRAGMA busy_timeout=10000")
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")
    db.execute("PRAGMA foreign_keys=ON")
    return db
def init(path):
    db=connect(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS readback(id INTEGER PRIMARY KEY AUTOINCREMENT,request_nonce TEXT NOT NULL UNIQUE,previous_sha TEXT NOT NULL,head_sha TEXT NOT NULL UNIQUE,remote_url TEXT NOT NULL,artifact_sha TEXT NOT NULL,ack_seq INTEGER NOT NULL,ack_head TEXT NOT NULL,ack_nonces INTEGER NOT NULL,observation_json TEXT NOT NULL)")
        db.commit()
    except Exception:db.rollback();raise
    finally:db.close()
def ack_state(path):
    """A read-only snapshot of a prior AETHER-288 journal."""
    db=sqlite3.connect(Path(path).resolve().as_uri()+"?mode=ro",uri=True,isolation_level=None,timeout=5)
    try:
        db.execute("PRAGMA query_only=ON");db.execute("BEGIN")
        entries=[dict(zip(("id","nonce","previous","head","manifest"),r)) for r in
                 db.execute("SELECT id,nonce,previous,head,manifest FROM batch ORDER BY id")]
        nonces=[dict(zip(("nonce","batch","custodian"),r)) for r in
                db.execute("SELECT nonce,batch,custodian FROM receipt ORDER BY batch,custodian")]
        db.commit()
        return entries,nonces
    finally:db.close()
def anchor_statement(artifact_sha,ack_seq,ack_head,nonce_count,source_url,observation_sha):
    return {"schema":ANCHOR_SCHEMA,"artifact_sha256":artifact_sha,
            "ack_batch_id":ack_seq,"ack_head_sha256":ack_head,
            "ack_nonce_count":nonce_count,"source_url":source_url,
            "source_observation_sha256":observation_sha}
def replay_anchor(state,anchor,anchor_pin):
    errors=[]
    if not hash64(anchor_pin):
        errors.append("OUT_OF_BAND_ANCHOR_DIGEST_REQUIRED")
    if not isinstance(anchor,dict) or set(anchor)!={"schema","artifact_sha256","ack_batch_id",
                         "ack_head_sha256","ack_nonce_count","source_url","source_observation_sha256"}:
        return ["ANCHOR_SCHEMA_INVALID"]+errors
    if hash64(anchor_pin) and sha(anchor)!=anchor_pin:errors.append("ANCHOR_DIGEST_CONFLICT")
    if anchor["schema"]!=ANCHOR_SCHEMA:errors.append("ANCHOR_VERSION_INVALID")
    seq=anchor["ack_batch_id"];head=anchor["ack_head_sha256"]
    entries,nonces=state
    if type(seq) is not int or seq<1 or not hash64(head):
        errors.append("ANCHOR_PREFIX_FORMAT_INVALID")
    elif len(entries)<seq:errors.append("ACK_PREFIX_ROLLBACK")
    elif entries[seq-1]["head"]!=head:errors.append("ACK_PREFIX_REPLACED")
    count=anchor["ack_nonce_count"]
    if type(count) is not int or count<0:errors.append("ANCHOR_NONCE_FORMAT_INVALID")
    elif len(nonces)<count:errors.append("ACK_NONCE_HIGHWATER_ROLLBACK")
    if not hash64(anchor["artifact_sha256"]) or not hash64(anchor["source_observation_sha256"]):
        errors.append("ANCHOR_DIGEST_FIELD_INVALID")
    return errors
def row_statement(row):
    return {"schema":SCHEMA,"request_nonce":row["request_nonce"],
            "previous_sha256":row["previous_sha"],"remote_url":row["remote_url"],
            "artifact_sha256":row["artifact_sha"],"ack_batch_id":row["ack_seq"],
            "ack_head_sha256":row["ack_head"],"ack_nonce_count":row["ack_nonces"],
            "observation_sha256":json.loads(row["observation_json"])["observation_sha256"]}
def capture(path,source_journal,ack_db,artifact_bytes,url,request_nonce,collector=acquire):
    """Opt-in GET. Commit the unchanged AETHER-264 observation in a new local journal."""
    host,_=validate_url(url,[urlsplit(url).hostname])
    if not isinstance(request_nonce,str) or not 16<=len(request_nonce)<=128:
        raise ValueError("FRESH_READBACK_NONCE_REQUIRED")
    if not isinstance(artifact_bytes,bytes) or not artifact_bytes or len(artifact_bytes)>MAX_BYTES:
        raise ValueError("EXPORT_BYTES_INVALID")
    try:artifact=json.loads(artifact_bytes)
    except (UnicodeError,ValueError) as e:raise ValueError("EXPORT_JSON_INVALID") from e
    if canon(artifact)!=artifact_bytes:raise ValueError("EXPORT_NOT_CANONICAL")
    if verify_export(artifact,*source_readback(source_journal)):
        raise ValueError("SOURCE_EXPORT_VERIFICATION_FAILED")
    local_ack=ack_audit(ack_db)
    blocking=set(local_ack["reasons"])-{"EXTERNAL_CUSTODY_NOT_AUTHENTICATED","LOCAL_DATABASE_ROLLBACK_POSSIBLE"}
    if blocking:raise ValueError("ACKNOWLEDGMENT_LEDGER_INVALID")
    entries,nonces=ack_state(ack_db)
    if not entries or len(nonces)!=3*len(entries):
        raise ValueError("ACKNOWLEDGMENT_HIGHWATER_MISSING")
    init(path)
    db=connect(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM readback WHERE request_nonce=?",(request_nonce,)).fetchone():
            raise ValueError("READBACK_NONCE_REPLAY")
        last=db.execute("SELECT head_sha FROM readback ORDER BY id DESC LIMIT 1").fetchone()
        previous=last[0] if last else ZERO
        raw_obs=collector(url,[host]);remote,obs=observation(raw_obs,url)
        if remote!=artifact_bytes:
            raise ValueError("REMOTE_EXPORTED_BYTES_DIVERGE")
        statement={"schema":SCHEMA,"request_nonce":request_nonce,
                   "previous_sha256":previous,"remote_url":url,
                   "artifact_sha256":digest(artifact_bytes),
                   "ack_batch_id":entries[-1]["id"],"ack_head_sha256":entries[-1]["head"],
                   "ack_nonce_count":len(nonces),"observation_sha256":obs["observation_sha256"]}
        head=sha(statement)
        db.execute("INSERT INTO readback(request_nonce,previous_sha,head_sha,remote_url,artifact_sha,ack_seq,ack_head,ack_nonces,observation_json) VALUES (?,?,?,?,?,?,?,?,?)",
                   (request_nonce,previous,head,url,digest(artifact_bytes),
                    entries[-1]["id"],entries[-1]["head"],len(nonces),canon(obs).decode()))
        db.commit()
        return {**HOLD,"readback_head_sha256":head,"remote_bytes_equal":True,
                "ack_highwater":anchor_statement(digest(artifact_bytes),entries[-1]["id"],
                         entries[-1]["head"],len(nonces),url,obs["observation_sha256"]),
                "reasons":["HTTPS_ENDPOINT_NOT_INDEPENDENT_CUSTODY_PROOF",
                           "EXTERNAL_ANCHOR_NOT_YET_PRESERVED"]}
    except Exception:db.rollback();raise
    finally:db.close()
def audit(path,ack_db,anchor=None,anchor_pin=None):
    entries,nonces=ack_state(ack_db)
    rows_db=sqlite3.connect(Path(path).resolve().as_uri()+"?mode=ro",uri=True,isolation_level=None)
    try:
        rows_db.execute("PRAGMA query_only=ON");rows_db.execute("BEGIN")
        rows=[dict(zip(("id","request_nonce","previous_sha","head_sha","remote_url","artifact_sha",
                        "ack_seq","ack_head","ack_nonces","observation_json"),r))
              for r in rows_db.execute("SELECT id,request_nonce,previous_sha,head_sha,remote_url,artifact_sha,ack_seq,ack_head,ack_nonces,observation_json FROM readback ORDER BY id")]
        rows_db.commit()
    finally:rows_db.close()
    errors=[];previous=ZERO;request_nonces=set()
    for index,row in enumerate(rows,1):
        if row["id"]!=index or row["previous_sha"]!=previous:
            errors.append("READBACK_CHAIN_BROKEN")
        if row["request_nonce"] in request_nonces:errors.append("READBACK_NONCE_DUPLICATE")
        request_nonces.add(row["request_nonce"])
        try:
            obs=json.loads(row["observation_json"])
            body,_=observation(obs,row["remote_url"])
            if row["artifact_sha"]!=digest(body):
                errors.append("RETAINED_REMOTE_BODY_CHANGED")
            if sha(row_statement(row))!=row["head_sha"]:
                errors.append("READBACK_HASH_CHANGED")
        except (ValueError,KeyError,TypeError,UnicodeError):
            errors.append("RETAINED_OBSERVATION_INVALID")
        seq=row["ack_seq"]
        if type(seq) is not int or not 1<=seq<=len(entries):
            errors.append("ACK_HISTORY_REMOVED")
        elif entries[seq-1]["head"]!=row["ack_head"]:
            errors.append("ACK_HISTORY_REWRITTEN")
        if type(row["ack_nonces"]) is not int or len(nonces)<row["ack_nonces"]:
            errors.append("ACK_NONCE_ROLLBACK")
        previous=row["head_sha"]
    if anchor is not None or anchor_pin is not None:
        errors+=replay_anchor((entries,nonces),anchor,anchor_pin)
        if isinstance(anchor,dict) and rows:
            if not any(row["artifact_sha"]==anchor.get("artifact_sha256") and
                       row["remote_url"]==anchor.get("source_url") and
                       json.loads(row["observation_json"]).get("observation_sha256")==anchor.get("source_observation_sha256")
                       for row in rows):
                errors.append("ANCHOR_READBACK_OBSERVATION_NOT_FOUND")
    errors+=["ANCHOR_EXTERNAL_CUSTODY_UNVERIFIED","HTTP_SOURCE_INDEPENDENCE_UNVERIFIED",
             "LOCAL_NONCE_AND_READBACK_ROLLBACK_POSSIBLE"]
    return {**HOLD,"readbacks":len(rows),"ack_batches":len(entries),
            "ack_nonces":len(nonces),"latest_head_sha256":previous,
            "reasons":sorted(set(errors))}
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="action",required=True)
    c=sub.add_parser("capture")
    c.add_argument("--db",type=Path,required=True)
    c.add_argument("--source-journal",type=Path,required=True)
    c.add_argument("--ack-db",type=Path,required=True)
    c.add_argument("--export",type=Path,required=True)
    c.add_argument("--url",required=True);c.add_argument("--nonce",required=True)
    a=sub.add_parser("audit")
    a.add_argument("--db",type=Path,required=True);a.add_argument("--ack-db",type=Path,required=True)
    a.add_argument("--anchor",type=Path);a.add_argument("--anchor-pin")
    args=p.parse_args()
    try:
        if args.action=="capture":
            raw=args.export.read_bytes()
            result=capture(args.db,args.source_journal,args.ack_db,raw,args.url,args.nonce)
        else:
            anchor=json.loads(args.anchor.read_bytes()) if args.anchor else None
            result=audit(args.db,args.ack_db,anchor,args.anchor_pin)
    except (OSError,ValueError,TypeError,KeyError,sqlite3.Error) as e:
        result={**HOLD,"reasons":["REJECTED:"+type(e).__name__+":"+str(e)[:100]]}
    print(json.dumps(result,indent=2,sort_keys=True))
    return 1
if __name__=="__main__":raise SystemExit(main())
