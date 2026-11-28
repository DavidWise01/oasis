#!/usr/bin/env python3
"""AETHER-301-RS: exact remote receipt/object readback across explicit windows.

Pinned signature verification and two equal reads are not independent custody,
clock authority or remotely enforced retention. Authority remains HOLD.
"""
import argparse,base64,hashlib,json,sqlite3,sys
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"264"),str(ROOT/"294"),str(ROOT/"300")]
from acquisition import acquire,validate_url
from live_provider_capture import observation
from custodian_acceptance import verify_receipt,canon,sha,digest
SCHEMA="AETHER-301/remote-receipt-and-object-v1"
ZERO="0"*64
HOLD={"operational_authority":"HOLD","physical_act_allowed":False,
      "physical_qualification_percent":0,"independent_custody_verified":False,
      "independent_clock_verified":False,"retention_enforced_verified":False}
def hex64(v):return isinstance(v,str) and len(v)==64 and all(c in "0123456789abcdef" for c in v)
def validate_config(config,pin):
    fields={"schema","receipt_url","object_url","receipt_sha256","object_sha256",
            "handoff_sha256","source_head_sha256","source_sequence","key_record","key_sha256"}
    if not isinstance(config,dict) or set(config)!=fields or config["schema"]!="AETHER-301/acquisition-config-v1":
        raise ValueError("CONFIG_SCHEMA_INVALID")
    if not hex64(pin) or sha(config)!=pin:raise ValueError("CONFIG_PIN_INVALID")
    for name in ("receipt_sha256","object_sha256","handoff_sha256","source_head_sha256","key_sha256"):
        if not hex64(config[name]):raise ValueError("DIGEST_INVALID:"+name)
    if not isinstance(config["source_sequence"],int) or isinstance(config["source_sequence"],bool) or config["source_sequence"]<1:
        raise ValueError("SOURCE_SEQUENCE_INVALID")
    key=config["key_record"]
    if not isinstance(key,dict) or set(key)!={"custodian_id","public_key_pem"} or sha(key)!=config["key_sha256"]:
        raise ValueError("CUSTODIAN_KEY_PIN_INVALID")
    hosts=set()
    for field in ("receipt_url","object_url"):
        url=config[field]
        if not isinstance(url,str):raise ValueError("URL_INVALID")
        host,_=validate_url(url,[urlsplit(url).hostname])
        if host in hosts:raise ValueError("RECEIPT_AND_OBJECT_SAME_HOST")
        hosts.add(host)
    return True
def remote_read(url,collector):
    host,_=validate_url(url,[urlsplit(url).hostname])
    raw,obs=observation(collector(url,[host]),url)
    if not raw:raise ValueError("EMPTY_REMOTE_RESPONSE")
    return raw,obs
def receipt_check(raw,config):
    if digest(raw)!=config["receipt_sha256"]:raise ValueError("REMOTE_RECEIPT_BYTES_CHANGED")
    try:receipt=json.loads(raw)
    except (UnicodeError,ValueError) as e:raise ValueError("REMOTE_RECEIPT_JSON_INVALID") from e
    if not isinstance(receipt,dict) or canon(receipt)!=raw:
        raise ValueError("REMOTE_RECEIPT_NONCANONICAL")
    verify_receipt(receipt,config["key_record"],{
        "handoff_sha256":config["handoff_sha256"],
        "source_head_sha256":config["source_head_sha256"],
        "source_sequence":config["source_sequence"]})
    return receipt
def init(path):
    db=sqlite3.connect(str(path),isolation_level=None,timeout=10)
    try:
        db.execute("PRAGMA journal_mode=WAL");db.execute("PRAGMA synchronous=FULL")
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS window (seq INTEGER PRIMARY KEY,nonce TEXT NOT NULL UNIQUE,previous_head TEXT NOT NULL,head TEXT NOT NULL UNIQUE,config_pin TEXT NOT NULL,manifest TEXT NOT NULL)")
        db.commit()
    except Exception:db.rollback();raise
    finally:db.close()
def capture(path,config,pin,nonce,collector=acquire):
    validate_config(config,pin)
    if not isinstance(nonce,str) or not 16<=len(nonce)<=128:
        raise ValueError("FRESH_WINDOW_NONCE_REQUIRED")
    init(path)
    db=sqlite3.connect(str(path),timeout=10,isolation_level=None)
    try:
        db.execute("PRAGMA busy_timeout=10000");db.execute("BEGIN IMMEDIATE")
        prev=db.execute("SELECT seq,head,config_pin FROM window ORDER BY seq DESC LIMIT 1").fetchone()
        seq=prev[0]+1 if prev else 1
        if seq>2:raise ValueError("TWO_WINDOWS_ALREADY_CAPTURED")
        if db.execute("SELECT 1 FROM window WHERE nonce=?",(nonce,)).fetchone():
            raise ValueError("WINDOW_REPLAY")
        if prev and prev[2]!=pin:raise ValueError("SOURCE_CONFIGURATION_CHANGED")
        receipt_raw,receipt_obs=remote_read(config["receipt_url"],collector)
        receipt=receipt_check(receipt_raw,config)
        object_raw,object_obs=remote_read(config["object_url"],collector)
        if digest(object_raw)!=config["object_sha256"]:
            raise ValueError("REMOTE_OBJECT_BYTES_CHANGED")
        manifest={"schema":SCHEMA,"window_seq":seq,"window_nonce":nonce,
                  "previous_head_sha256":prev[1] if prev else ZERO,
                  "config_sha256":pin,"receipt_observation":receipt_obs,
                  "object_observation":object_obs,"receipt_sha256":digest(receipt_raw),
                  "object_sha256":digest(object_raw),
                  "source_head_sha256":config["source_head_sha256"],
                  "source_sequence":config["source_sequence"],
                  "custodian_id":receipt["custodian_id"]}
        head=sha(manifest)
        db.execute("INSERT INTO window VALUES (?,?,?,?,?,?)",
                   (seq,nonce,manifest["previous_head_sha256"],head,pin,canon(manifest).decode()))
        db.commit()
        return {**HOLD,"window_sequence":seq,"journal_head_sha256":head,
                "exact_receipt_and_object_bytes_matched":True,
                "receipt_signature_valid":True,
                "reasons":["TWO_FETCHES_DO_NOT_PROVE_RETENTION_OR_ELAPSED_TIME",
                           "EXTERNALLY_PINNED_KEY_OWNERSHIP_UNVERIFIED",
                           "DISTINCT_HOSTS_NOT_INDEPENDENT_ANCESTRY"]}
    except Exception:db.rollback();raise
    finally:db.close()
def audit(path,config,pin,prefix_seq=None,prefix_head=None):
    validate_config(config,pin)
    db=sqlite3.connect(Path(path).resolve().as_uri()+"?mode=ro",uri=True,isolation_level=None)
    try:
        db.execute("PRAGMA query_only=ON");db.execute("BEGIN")
        rows=list(db.execute("SELECT seq,nonce,previous_head,head,config_pin,manifest FROM window ORDER BY seq"))
        db.commit()
    finally:db.close()
    faults=[];prev=ZERO;seen=set()
    for index,(seq,nonce,parent,head,pinrow,raw) in enumerate(rows,1):
        if index!=seq or parent!=prev or nonce in seen:
            faults.append("WINDOW_SEQUENCE_OR_NONCE_BROKEN")
        seen.add(nonce)
        try:
            m=json.loads(raw)
            if canon(m).decode()!=raw or sha(m)!=head or m["schema"]!=SCHEMA:
                faults.append("WINDOW_MANIFEST_HEAD_INVALID")
            if (m["window_seq"]!=seq or m["window_nonce"]!=nonce or
                m["previous_head_sha256"]!=parent or m["config_sha256"]!=pinrow
                or pinrow!=pin):
                faults.append("WINDOW_BINDING_INVALID")
            receipt_raw,receipt_obs=observation(m["receipt_observation"],config["receipt_url"])
            object_raw,object_obs=observation(m["object_observation"],config["object_url"])
            receipt=receipt_check(receipt_raw,config)
            if digest(object_raw)!=config["object_sha256"] or m["object_sha256"]!=digest(object_raw):
                faults.append("OBJECT_RETAINED_BYTES_INVALID")
            if m["receipt_sha256"]!=digest(receipt_raw) or m["custodian_id"]!=receipt["custodian_id"]:
                faults.append("RECEIPT_RETAINED_BYTES_INVALID")
            if (m["source_head_sha256"]!=config["source_head_sha256"] or
                m["source_sequence"]!=config["source_sequence"]):
                faults.append("SOURCE_HIGHWATER_CHANGED")
        except (ValueError,KeyError,TypeError,UnicodeError):
            faults.append("RETAINED_OBSERVATION_INVALID")
        prev=head
    if len(rows)>2:faults.append("TOO_MANY_WINDOWS")
    if prefix_seq is not None or prefix_head is not None:
        if type(prefix_seq) is not int or prefix_seq<1 or not hex64(prefix_head):
            faults.append("EXTERNAL_PREFIX_FORMAT_INVALID")
        elif len(rows)<prefix_seq:faults.append("EXTERNALLY_ANCHORED_WINDOW_REMOVED")
        elif rows[prefix_seq-1][3]!=prefix_head:faults.append("EXTERNALLY_ANCHORED_WINDOW_CHANGED")
    faults+=["NO_INDEPENDENT_STORAGE_OWNERSHIP",
             "NO_AUTHENTICATED_ELAPSED_TIME","NO_IMMUTABLE_REMOTE_RETENTION_PROOF",
             "LOCAL_HISTORY_AND_PIN_CAN_ROLL_BACK"]
    return {**HOLD,"windows":len(rows),"latest_head_sha256":prev,
            "reasons":sorted(set(faults))}
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="op",required=True)
    c=sub.add_parser("capture")
    for name in ("db","config"):c.add_argument("--"+name,type=Path,required=True)
    c.add_argument("--pin",required=True);c.add_argument("--nonce",required=True)
    a=sub.add_parser("audit")
    for name in ("db","config"):a.add_argument("--"+name,type=Path,required=True)
    a.add_argument("--pin",required=True);a.add_argument("--prefix-seq",type=int)
    a.add_argument("--prefix-head")
    args=p.parse_args()
    try:
        config=json.loads(args.config.read_bytes())
        result=capture(args.db,config,args.pin,args.nonce) if args.op=="capture" else audit(
            args.db,config,args.pin,args.prefix_seq,args.prefix_head)
    except (OSError,ValueError,KeyError,TypeError,sqlite3.Error) as exc:
        result={**HOLD,"reasons":["REJECTED:"+type(exc).__name__+":"+str(exc)[:100]]}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 1
if __name__=="__main__":raise SystemExit(main())
