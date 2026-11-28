#!/usr/bin/env python3
"""AETHER-302-RS: signed exact-object binding and retained-byte parity.

The signed statement identifies URI, immutable-version *claim*, length, digest,
source head and receipt. Neither key control nor storage immutability is proven.
"""
import argparse,base64,hashlib,json,sqlite3,sys
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"264"),str(ROOT/"294"),str(ROOT/"292")]
from acquisition import acquire,validate_url
from live_provider_capture import observation
from attestation_audit import verify
SCHEMA="AETHER-302/object-bound-receipt-v1"
JOURNAL="AETHER-302/signed-object-window-v1"
ZERO="0"*64
FIELDS={"schema","custodian_id","receipt_nonce","previous_receipt_sha256",
        "handoff_sha256","source_head_sha256","source_sequence",
        "object_url","object_version","object_sha256","object_length",
        "retained_until_claim","signature_b64"}
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "independent_custodian_ownership_verified":False,
      "immutable_remote_version_verified":False,
      "independent_elapsed_time_verified":False}
def canon(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def digest(x):return hashlib.sha256(x).hexdigest()
def sha(x):return digest(canon(x))
def hex64(x):return isinstance(x,str) and len(x)==64 and all(k in "0123456789abcdef" for k in x)
def urlhost(url):
    if not isinstance(url,str):raise ValueError("URL_INVALID")
    host=urlsplit(url).hostname
    return validate_url(url,[host])[0]
def validate(config,pin):
    required={"schema","receipt_url","object_url","receipt_sha256","object_sha256",
              "object_length","object_version","handoff_sha256","source_head_sha256",
              "source_sequence","key_record","key_pin_sha256"}
    if not isinstance(config,dict) or set(config)!=required or config["schema"]!="AETHER-302/config-v1":
        raise ValueError("CONFIG_SCHEMA_INVALID")
    if not hex64(pin) or sha(config)!=pin:raise ValueError("CONFIG_PIN_INVALID")
    for key in ("receipt_sha256","object_sha256","handoff_sha256","source_head_sha256","key_pin_sha256"):
        if not hex64(config[key]):raise ValueError("CONFIG_HASH_INVALID")
    if type(config["object_length"]) is not int or not 1<=config["object_length"]<=65536:
        raise ValueError("OBJECT_LENGTH_INVALID")
    if (not isinstance(config["object_version"],str) or
        not 1<=len(config["object_version"])<=256 or config["object_version"]=="null"):
        raise ValueError("OBJECT_VERSION_INVALID")
    if type(config["source_sequence"]) is not int or config["source_sequence"]<1:
        raise ValueError("SOURCE_SEQUENCE_INVALID")
    key=config["key_record"]
    if not isinstance(key,dict) or set(key)!={"custodian_id","public_key_pem"} or sha(key)!=config["key_pin_sha256"]:
        raise ValueError("CUSTODIAN_KEY_PIN_INVALID")
    if urlhost(config["receipt_url"])==urlhost(config["object_url"]):
        raise ValueError("SHARED_HOST_ANCESTRY_RISK")
def verify_receipt(raw,config):
    if digest(raw)!=config["receipt_sha256"]:
        raise ValueError("SIGNED_RECEIPT_RAW_CHANGED")
    try:receipt=json.loads(raw)
    except (UnicodeError,ValueError) as e:raise ValueError("RECEIPT_JSON_INVALID") from e
    if not isinstance(receipt,dict) or set(receipt)!=FIELDS or canon(receipt)!=raw or receipt["schema"]!=SCHEMA:
        raise ValueError("RECEIPT_SCHEMA_INVALID")
    for attr in ("custodian_id","receipt_nonce","object_version","retained_until_claim"):
        if not isinstance(receipt[attr],str) or not 1<=len(receipt[attr])<=256:
            raise ValueError("RECEIPT_FIELD_INVALID")
    if not hex64(receipt["previous_receipt_sha256"]):raise ValueError("PREDECESSOR_HASH_INVALID")
    expected={"custodian_id":config["key_record"]["custodian_id"],
              "handoff_sha256":config["handoff_sha256"],
              "source_head_sha256":config["source_head_sha256"],
              "source_sequence":config["source_sequence"],
              "object_url":config["object_url"],"object_version":config["object_version"],
              "object_sha256":config["object_sha256"],"object_length":config["object_length"]}
    for field,value in expected.items():
        if receipt.get(field)!=value:raise ValueError("SIGNED_OBJECT_BINDING_CHANGED:"+field)
    if not verify(config["key_record"]["public_key_pem"],
                  {k:v for k,v in receipt.items() if k!="signature_b64"},
                  receipt["signature_b64"]):
        raise ValueError("RECEIPT_SIGNATURE_INVALID")
    return receipt
def remote(url,collector):
    raw,obs=observation(collector(url,[urlhost(url)]),url)
    if not raw:raise ValueError("EMPTY_REMOTE_RESPONSE")
    return raw,obs
def init(dbpath):
    db=sqlite3.connect(str(dbpath),timeout=10,isolation_level=None)
    try:
        db.execute("PRAGMA journal_mode=WAL");db.execute("PRAGMA synchronous=FULL")
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS window(seq INTEGER PRIMARY KEY,nonce TEXT UNIQUE NOT NULL,previous_head TEXT NOT NULL,head TEXT UNIQUE NOT NULL,config_pin TEXT NOT NULL,manifest TEXT NOT NULL)")
        db.commit()
    except Exception:db.rollback();raise
    finally:db.close()
def capture(dbpath,config,pin,nonce,collector=acquire):
    validate(config,pin)
    if not isinstance(nonce,str) or not 16<=len(nonce)<=128:
        raise ValueError("NONCE_INVALID")
    init(dbpath)
    db=sqlite3.connect(str(dbpath),timeout=10,isolation_level=None)
    try:
        db.execute("PRAGMA busy_timeout=10000");db.execute("BEGIN IMMEDIATE")
        previous=db.execute("SELECT seq,head,config_pin,manifest FROM window ORDER BY seq DESC LIMIT 1").fetchone()
        seq=previous[0]+1 if previous else 1
        if seq>2:raise ValueError("TWO_WINDOWS_ONLY")
        if previous and previous[2]!=pin:raise ValueError("WINDOW_CONFIGURATION_CHANGED")
        if db.execute("SELECT 1 FROM window WHERE nonce=?",(nonce,)).fetchone():raise ValueError("WINDOW_NONCE_REPLAY")
        receipt_raw,receipt_obs=remote(config["receipt_url"],collector)
        receipt=verify_receipt(receipt_raw,config)
        object_raw,object_obs=remote(config["object_url"],collector)
        if digest(object_raw)!=config["object_sha256"] or len(object_raw)!=config["object_length"]:
            raise ValueError("SIGNED_OBJECT_BYTES_CHANGED")
        if previous:
            old=json.loads(previous[3])
            if old["receipt_nonce"]!=receipt["receipt_nonce"] or old["object_version"]!=receipt["object_version"]:
                raise ValueError("SIGNED_RECEIPT_OR_VERSION_CHANGED")
        manifest={"schema":JOURNAL,"seq":seq,"nonce":nonce,
                  "previous_head_sha256":previous[1] if previous else ZERO,
                  "config_sha256":pin,"receipt_observation":receipt_obs,
                  "object_observation":object_obs,"receipt_nonce":receipt["receipt_nonce"],
                  "object_version":receipt["object_version"],
                  "receipt_sha256":digest(receipt_raw),"object_sha256":digest(object_raw),
                  "object_length":len(object_raw)}
        head=sha(manifest)
        db.execute("INSERT INTO window VALUES (?,?,?,?,?,?)",
                   (seq,nonce,manifest["previous_head_sha256"],head,pin,canon(manifest).decode()))
        db.commit()
        return {**HOLD,"window_sequence":seq,"head_sha256":head,
                "signed_object_fields_matched":True,
                "reasons":["KEY_OWNERSHIP_NOT_INDEPENDENTLY_ESTABLISHED",
                           "OBJECT_VERSION_IS_SIGNED_CLAIM_NOT_PROVIDER_IMMUTABILITY",
                           "NO_TRUSTED_ELAPSED_TIME"]}
    except Exception:db.rollback();raise
    finally:db.close()
def audit(dbpath,config,pin,prefix_seq=None,prefix_sha=None):
    validate(config,pin)
    db=sqlite3.connect(Path(dbpath).resolve().as_uri()+"?mode=ro",uri=True,isolation_level=None)
    try:
        db.execute("PRAGMA query_only=ON");db.execute("BEGIN")
        rows=list(db.execute("SELECT seq,nonce,previous_head,head,config_pin,manifest FROM window ORDER BY seq"))
        db.commit()
    finally:db.close()
    faults=[];parent=ZERO;nonces=set()
    for index,(seq,nonce,previous,head,config_pin,raw) in enumerate(rows,1):
        if index!=seq or previous!=parent or nonce in nonces:faults.append("WINDOW_CHAIN_BROKEN")
        nonces.add(nonce)
        try:
            m=json.loads(raw)
            if canon(m).decode()!=raw or sha(m)!=head:faults.append("MANIFEST_SHA_INVALID")
            if (m["schema"]!=JOURNAL or m["seq"]!=seq or m["nonce"]!=nonce or
                m["previous_head_sha256"]!=previous or m["config_sha256"]!=config_pin or config_pin!=pin):
                faults.append("WINDOW_HEADER_INVALID")
            receipt_raw,_=observation(m["receipt_observation"],config["receipt_url"])
            object_raw,_=observation(m["object_observation"],config["object_url"])
            receipt=verify_receipt(receipt_raw,config)
            if (digest(object_raw)!=receipt["object_sha256"] or len(object_raw)!=receipt["object_length"]
                or m["receipt_sha256"]!=digest(receipt_raw) or m["object_sha256"]!=digest(object_raw)
                or m["object_length"]!=len(object_raw) or m["object_version"]!=receipt["object_version"]
                or m["receipt_nonce"]!=receipt["receipt_nonce"]):
                faults.append("RETAINED_OBJECT_OR_RECEIPT_CHANGED")
        except (KeyError,ValueError,TypeError,UnicodeError):
            faults.append("RETAINED_WINDOW_INVALID")
        parent=head
    if len(rows)>2:faults.append("TOO_MANY_WINDOWS")
    if prefix_seq is not None or prefix_sha is not None:
        if type(prefix_seq) is not int or prefix_seq<1 or not hex64(prefix_sha):
            faults.append("HISTORICAL_PIN_INVALID")
        elif len(rows)<prefix_seq:faults.append("HISTORICAL_WINDOW_REMOVED")
        elif rows[prefix_seq-1][3]!=prefix_sha:faults.append("HISTORICAL_WINDOW_REWRITTEN")
    faults+=["REMOTE_VERSION_ENFORCEMENT_NOT_OBSERVED",
             "INDEPENDENT_CUSTODIAN_CONTROL_UNVERIFIED",
             "INDEPENDENT_TIME_UNVERIFIED",
             "LOCAL_ROLLBACK_REMAINS_POSSIBLE"]
    return {**HOLD,"windows":len(rows),"head_sha256":parent,"reasons":sorted(set(faults))}
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="action",required=True)
    c=sub.add_parser("capture")
    c.add_argument("--db",type=Path,required=True);c.add_argument("--config",type=Path,required=True)
    c.add_argument("--pin",required=True);c.add_argument("--nonce",required=True)
    a=sub.add_parser("audit")
    a.add_argument("--db",type=Path,required=True);a.add_argument("--config",type=Path,required=True)
    a.add_argument("--pin",required=True);a.add_argument("--prefix-seq",type=int)
    a.add_argument("--prefix-sha256")
    args=p.parse_args()
    try:
        config=json.loads(args.config.read_bytes())
        result=(capture(args.db,config,args.pin,args.nonce) if args.action=="capture"
                else audit(args.db,config,args.pin,args.prefix_seq,args.prefix_sha256))
    except (OSError,ValueError,KeyError,TypeError,sqlite3.Error) as exc:
        result={**HOLD,"reasons":["REJECTED:"+type(exc).__name__+":"+str(exc)[:100]]}
    print(json.dumps(result,indent=2,sort_keys=True))
    return 1
if __name__=="__main__":raise SystemExit(main())
