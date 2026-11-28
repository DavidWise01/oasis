#!/usr/bin/env python3
"""AETHER-291-RS: two-window exact remote object readback and claimed ancestry.

Window ordinals are local ordering, NOT authenticated elapsed time.
Distinct hosts and signed retention claims are NOT independent custody.
"""
import argparse,base64,hashlib,json,sqlite3,sys
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"264"),str(ROOT/"289"),str(ROOT/"290")]
from acquisition import acquire,validate_url
from remote_readback import observation,canon,sha,digest
from external_highwater import family,verify,RECORD_SCHEMA
SCHEMA="AETHER-291/paired-observation-v1"
ZERO="0"*64
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "independent_external_custody_verified":False,
      "independent_elapsed_time_verified":False,
      "remote_immutable_storage_verified":False}
def ishash(v):return isinstance(v,str) and len(v)==64 and all(c in "0123456789abcdef" for c in v)
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
        db.execute("CREATE TABLE IF NOT EXISTS observation_window(seq INTEGER PRIMARY KEY,window_nonce TEXT NOT NULL UNIQUE,previous_sha TEXT NOT NULL,head_sha TEXT NOT NULL UNIQUE,artifact_sha TEXT NOT NULL,trust_sha TEXT NOT NULL,manifest_json TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS used_observation_nonce(value TEXT PRIMARY KEY,window_seq INTEGER NOT NULL REFERENCES observation_window(seq),endpoint_id TEXT NOT NULL,UNIQUE(window_seq,endpoint_id))")
        db.commit()
    except Exception:db.rollback();raise
    finally:db.close()
def read(path):
    uri=Path(path).resolve().as_uri()+"?mode=ro"
    db=sqlite3.connect(uri,uri=True,isolation_level=None,timeout=5)
    try:
        db.execute("PRAGMA query_only=ON");db.execute("BEGIN")
        windows=[dict(zip(("seq","window_nonce","previous_sha","head_sha","artifact_sha","trust_sha","manifest_json"),r))
                 for r in db.execute("SELECT seq,window_nonce,previous_sha,head_sha,artifact_sha,trust_sha,manifest_json FROM observation_window ORDER BY seq")]
        used=[dict(zip(("value","window_seq","endpoint_id"),r)) for r in db.execute("SELECT value,window_seq,endpoint_id FROM used_observation_nonce ORDER BY window_seq,endpoint_id")]
        db.commit()
        return windows,used
    finally:db.close()
def validate_trust(trust,pin,urls):
    if (not ishash(pin) or sha(trust)!=pin or not isinstance(trust,dict)
        or set(trust)!={"journal_controller","controllers","endpoints"}
        or not isinstance(trust["endpoints"],dict) or len(trust["endpoints"])!=3
        or not isinstance(urls,dict) or set(urls)!=set(trust["endpoints"])):
        raise ValueError("PINNED_TRUST_OR_ENDPOINTS_INVALID")
    hosts=set()
    graph=trust["controllers"]
    if not isinstance(graph,dict):raise ValueError("ANCESTRY_GRAPH_INVALID")
    journal=family(trust["journal_controller"],graph)
    families=[]
    for kid in sorted(urls):
        host,_=validate_url(urls[kid],[urlsplit(urls[kid]).hostname])
        if host in hosts:raise ValueError("ENDPOINT_HOST_REUSED")
        hosts.add(host)
        info=trust["endpoints"][kid]
        if not isinstance(info,dict) or set(info)!={"controller_id","public_key_pem"}:
            raise ValueError("TRUST_KEY_INVALID")
        f=family(info["controller_id"],graph)
        if f & journal:raise ValueError("SHARED_JOURNAL_ANCESTRY")
        if any(f & prev for prev in families):raise ValueError("SHARED_ENDPOINT_ANCESTRY")
        families.append(f)
def check_retention_record(record,kid,trust,artifact_sha):
    required={"schema","endpoint_id","controller_id","challenge_nonce","ack_batch_id",
              "ack_head_sha256","ack_nonce_count","source_artifact_sha256",
              "retained_until_claim","signature_b64"}
    if not isinstance(record,dict) or set(record)!=required:
        raise ValueError("RETENTION_RECORD_SCHEMA_INVALID")
    info=trust["endpoints"][kid]
    if (record["schema"]!=RECORD_SCHEMA or record["endpoint_id"]!=kid
        or record["controller_id"]!=info["controller_id"]
        or record["source_artifact_sha256"]!=artifact_sha):
        raise ValueError("RETENTION_RECORD_BINDING_INVALID")
    signed={k:v for k,v in record.items() if k!="signature_b64"}
    if not verify(info["public_key_pem"],signed,record["signature_b64"]):
        raise ValueError("RETENTION_SIGNATURE_INVALID")
    return record["retained_until_claim"]
def capture(path,artifact_bytes,trust,pin,urls,retention_records,window_nonce,collector=acquire):
    """One explicit capture invocation per locally ordered window; no timers."""
    if not isinstance(artifact_bytes,bytes) or not artifact_bytes or len(artifact_bytes)>65536:
        raise ValueError("ARTIFACT_BYTES_INVALID")
    if not isinstance(window_nonce,str) or not 16<=len(window_nonce)<=128:
        raise ValueError("WINDOW_NONCE_INVALID")
    validate_trust(trust,pin,urls)
    if not isinstance(retention_records,dict) or set(retention_records)!=set(urls):
        raise ValueError("RETENTION_RECORD_SET_INVALID")
    target=digest(artifact_bytes)
    for kid in sorted(urls):check_retention_record(retention_records[kid],kid,trust,target)
    init(path);db=dbopen(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        previous=db.execute("SELECT seq,head_sha,manifest_json,artifact_sha,trust_sha FROM observation_window ORDER BY seq DESC LIMIT 1").fetchone()
        seq=previous[0]+1 if previous else 1
        if seq>2:raise ValueError("TWO_WINDOWS_ALREADY_RECORDED")
        if db.execute("SELECT 1 FROM observation_window WHERE window_nonce=?",(window_nonce,)).fetchone():
            raise ValueError("WINDOW_NONCE_REPLAY")
        if previous:
            old=json.loads(previous[2])
            if previous[3]!=target or previous[4]!=pin or old["urls"]!=urls:
                raise ValueError("WINDOW_ANCESTRY_OR_ARTIFACT_DIVERGENCE")
        parent=previous[1] if previous else ZERO
        readings=[]
        for kid in sorted(urls):
            url=urls[kid];host,_=validate_url(url,[urlsplit(url).hostname])
            obs=collector(url,[host])
            body,normalized=observation(obs,url)
            if body!=artifact_bytes:raise ValueError("REMOTE_OBJECT_BYTES_CHANGED")
            local_nonce=window_nonce+":"+kid
            if db.execute("SELECT 1 FROM used_observation_nonce WHERE value=?",(local_nonce,)).fetchone():
                raise ValueError("OBSERVATION_NONCE_REPLAY")
            readings.append({"endpoint_id":kid,"url":url,"observation":normalized,
                             "retention_record":retention_records[kid],
                             "observation_nonce":local_nonce})
        manifest={"schema":SCHEMA,"seq":seq,"window_nonce":window_nonce,
                  "previous_head_sha256":parent,"artifact_sha256":target,
                  "trust_sha256":pin,"urls":urls,"readings":readings}
        head=sha(manifest)
        db.execute("INSERT INTO observation_window VALUES (?,?,?,?,?,?,?)",
                   (seq,window_nonce,parent,head,target,pin,canon(manifest).decode()))
        for reading in readings:
            db.execute("INSERT INTO used_observation_nonce VALUES (?,?,?)",
                       (reading["observation_nonce"],seq,reading["endpoint_id"]))
        db.commit()
        return {**HOLD,"window":seq,"head_sha256":head,"matched_remote_objects":3,
                "reasons":["NO_INDEPENDENT_ELAPSED_TIME_EVIDENCE",
                           "RETENTION_METADATA_IS_SIGNED_CLAIM",
                           "SOURCE_OPERATOR_ANCESTRY_SELF_DECLARED"]}
    except Exception:db.rollback();raise
    finally:db.close()
def audit(path,prefix_seq=None,prefix_sha=None):
    windows,used=read(path)
    errors=[];parent=ZERO;seen=set()
    for i,row in enumerate(windows,1):
        if row["seq"]!=i or row["previous_sha"]!=parent:errors.append("WINDOW_CHAIN_BROKEN")
        try:
            manifest=json.loads(row["manifest_json"])
            if canon(manifest).decode()!=row["manifest_json"] or sha(manifest)!=row["head_sha"]:
                errors.append("WINDOW_MANIFEST_HEAD_INVALID")
            if (manifest["seq"]!=i or manifest["window_nonce"]!=row["window_nonce"]
                or manifest["previous_head_sha256"]!=row["previous_sha"]
                or manifest["artifact_sha256"]!=row["artifact_sha"]
                or manifest["trust_sha256"]!=row["trust_sha"]):
                errors.append("WINDOW_MANIFEST_HEADER_INVALID")
            match=set()
            for entry in manifest["readings"]:
                body,_=observation(entry["observation"],entry["url"])
                if digest(body)!=row["artifact_sha"]:errors.append("RETAINED_REMOTE_BYTES_INVALID")
                pair=(entry["observation_nonce"],entry["endpoint_id"])
                if pair in seen:errors.append("OBSERVATION_NONCE_REUSED")
                seen.add(pair);match.add(pair)
            actual={(r["value"],r["endpoint_id"]) for r in used if r["window_seq"]==i}
            if len(match)!=3 or actual!=match:errors.append("NONCE_OR_WITNESS_TRIPLE_DIVERGENCE")
            if i==2:
                previous=json.loads(windows[0]["manifest_json"])
                if (manifest["urls"]!=previous["urls"] or
                    manifest["artifact_sha256"]!=previous["artifact_sha256"] or
                    manifest["trust_sha256"]!=previous["trust_sha256"]):
                    errors.append("SECOND_WINDOW_SOURCE_OR_OBJECT_CHANGED")
        except (ValueError,TypeError,KeyError,UnicodeError):
            errors.append("RETAINED_WINDOW_PREIMAGE_INVALID")
        parent=row["head_sha"]
    if len(windows)>2:errors.append("EXCESS_WINDOW_COUNT")
    if len(used)!=3*len(windows):errors.append("NONCE_CONSERVATION_FAILED")
    if prefix_seq is not None or prefix_sha is not None:
        if type(prefix_seq) is not int or prefix_seq<1 or not ishash(prefix_sha):
            errors.append("PREFIX_PIN_INVALID")
        elif len(windows)<prefix_seq:errors.append("HISTORICAL_WINDOW_REMOVED")
        elif windows[prefix_seq-1]["head_sha"]!=prefix_sha:
            errors.append("HISTORICAL_WINDOW_REWRITTEN")
    errors+=["WINDOW_ORDINAL_NOT_AUTHENTICATED_TIME",
             "REMOTE_IMMUTABILITY_NOT_ESTABLISHED",
             "INDEPENDENT_OPERATOR_CUSTODY_UNVERIFIED",
             "LOCAL_HISTORY_AND_PIN_CAN_ROLL_BACK"]
    return {**HOLD,"windows":len(windows),"readbacks":len(used),
            "latest_head_sha256":parent,"reasons":sorted(set(errors))}
def main():
    p=argparse.ArgumentParser();subs=p.add_subparsers(dest="action",required=True)
    c=subs.add_parser("capture")
    for arg in ("db","artifact","trust","urls","retention-records"):
        c.add_argument("--"+arg,type=Path,required=True)
    c.add_argument("--pin",required=True);c.add_argument("--nonce",required=True)
    a=subs.add_parser("audit");a.add_argument("--db",type=Path,required=True)
    a.add_argument("--prefix-seq",type=int);a.add_argument("--prefix-sha256")
    x=p.parse_args()
    try:
        if x.action=="capture":
            result=capture(x.db,x.artifact.read_bytes(),json.loads(x.trust.read_bytes()),
                x.pin,json.loads(x.urls.read_bytes()),json.loads(x.retention_records.read_bytes()),x.nonce)
        else:result=audit(x.db,x.prefix_seq,x.prefix_sha256)
    except (OSError,ValueError,KeyError,TypeError,sqlite3.Error) as exc:
        result={**HOLD,"reasons":["INPUT_REJECTED:"+type(exc).__name__+":"+str(exc)[:100]]}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 1
if __name__=="__main__":raise SystemExit(main())
