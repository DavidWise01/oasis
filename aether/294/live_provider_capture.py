#!/usr/bin/env python3
"""AETHER-294-RS: bounded live HTTPS capture of provider and time evidence.

This opt-in public GET collector does NOT authenticate cloud API accounts,
metadata ownership, external clock authority, or independently held custody.
"""
import argparse,base64,hashlib,json,sqlite3,sys
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"264"))
from acquisition import acquire,validate_url
SCHEMA="AETHER-294/acquired-evidence-v1"
OBS_FIELDS=("schema","requested_url","host","pinned_ip","dns_address_count",
            "tls_hostname_validation","status","elapsed_ms","raw_length",
            "raw_sha256","raw_b64")
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "provider_identity_verified":False,"trusted_time_verified":False,
      "independent_custody_verified":False}
ZERO="0"*64
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def sha(v):return hashlib.sha256(canon(v)).hexdigest()
def digest(raw):return hashlib.sha256(raw).hexdigest()
def ishash(x):return isinstance(x,str) and len(x)==64 and all(c in "0123456789abcdef" for c in x)
def observation(record,url):
    if not isinstance(record,dict) or any(k not in record for k in OBS_FIELDS):
        raise ValueError("OBSERVATION_FIELDS_MISSING")
    host,_=validate_url(url,[urlsplit(url).hostname])
    core={k:record[k] for k in OBS_FIELDS}
    if (core["schema"]!="AETHER-264/https-acquisition-v1" or
        core["requested_url"]!=url or core["host"]!=host or
        core["tls_hostname_validation"] is not True or
        type(core["status"]) is not int or core["status"]!=200):
        raise ValueError("OBSERVATION_TRANSPORT_MISMATCH")
    if not isinstance(core["raw_b64"],str) or len(core["raw_b64"])>90000:
        raise ValueError("RAW_BASE64_TOO_LARGE")
    try:raw=base64.b64decode(core["raw_b64"],validate=True)
    except (TypeError,ValueError) as e:raise ValueError("BASE64_INVALID") from e
    if (len(raw)>65536 or type(core["raw_length"]) is not int or
        len(raw)!=core["raw_length"] or digest(raw)!=core["raw_sha256"]):
        raise ValueError("RAW_DIGEST_OR_LENGTH_INVALID")
    if record.get("observation_sha256")!=sha(core):
        raise ValueError("OBSERVATION_PREIMAGE_HASH_INVALID")
    return raw,{**core,"observation_sha256":record["observation_sha256"]}
def validate_plan(plan):
    if not isinstance(plan,dict) or set(plan)!={"schema","provider_urls","clock_urls","artifact_sha256","window_heads"}:
        raise ValueError("PLAN_SCHEMA_INVALID")
    if plan["schema"]!="AETHER-294/acquisition-plan-v1" or not ishash(plan["artifact_sha256"]):
        raise ValueError("PLAN_FIELDS_INVALID")
    providers=plan["provider_urls"];clocks=plan["clock_urls"];heads=plan["window_heads"]
    if (not isinstance(providers,dict) or set(providers)!={"provider0","provider1","provider2"} or
        not isinstance(clocks,dict) or set(clocks)!={"clock0"} or
        not isinstance(heads,list) or len(heads)!=2 or not all(ishash(h) for h in heads)):
        raise ValueError("PLAN_SOURCE_COUNTS_INVALID")
    hosts=set()
    for endpoint in list(providers.values())+list(clocks.values()):
        if not isinstance(endpoint,list) or len(endpoint)!=2:raise ValueError("TWO_WINDOW_URLS_REQUIRED")
        for url in endpoint:
            if not isinstance(url,str):raise ValueError("URL_INVALID")
            host,_=validate_url(url,[urlsplit(url).hostname])
            if host in hosts:continue
            hosts.add(host)
    owners=[]
    for endpoint in list(providers.values())+list(clocks.values()):
        host0=urlsplit(endpoint[0]).hostname
        host1=urlsplit(endpoint[1]).hostname
        if host0!=host1:raise ValueError("SOURCE_HOST_CHANGED")
        owners.append(host0)
    if len(set(owners))!=4:raise ValueError("SHARED_HOST_BETWEEN_SOURCES")
def dbopen(path):
    db=sqlite3.connect(str(path),isolation_level=None,timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=10000")
    return db
def initialize(path):
    db=dbopen(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS acquisition(id INTEGER PRIMARY KEY AUTOINCREMENT,challenge_nonce TEXT NOT NULL UNIQUE,previous_sha TEXT NOT NULL,head_sha TEXT NOT NULL UNIQUE,plan_sha TEXT NOT NULL,manifest_json TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS source_observation(id TEXT NOT NULL,acquisition_id INTEGER NOT NULL REFERENCES acquisition(id),observation_sha TEXT NOT NULL,PRIMARY KEY(id,acquisition_id))")
        db.commit()
    except Exception:db.rollback();raise
    finally:db.close()
def check_payload(kind,kid,window,raw,plan):
    # The body is a canonical preservation envelope, not vendor-authenticated API evidence.
    try:value=json.loads(raw)
    except (UnicodeError,ValueError) as e:raise ValueError("BODY_NOT_JSON") from e
    if not isinstance(value,dict) or canon(value)!=raw:
        raise ValueError("BODY_NONCANONICAL")
    if kind=="provider":
        required={"schema","provider_id","window_seq","artifact_sha256",
                  "object_key","version_id","lock_mode","retention_until_claim",
                  "response_request_id","response_nonce"}
        if set(value)!=required or value["schema"]!="AETHER-293/provider-object-response-v1":
            raise ValueError("PROVIDER_BODY_SCHEMA_INVALID")
        if (value["provider_id"]!=kid or type(value["window_seq"]) is not int or
            value["window_seq"]!=window or value["artifact_sha256"]!=plan["artifact_sha256"]):
            raise ValueError("PROVIDER_BODY_BINDING_INVALID")
        if not all(isinstance(value[k],str) and 0<len(value[k])<=256 for k in
                   ("object_key","version_id","retention_until_claim","response_request_id","response_nonce")):
            raise ValueError("PROVIDER_METADATA_INVALID")
        if value["lock_mode"] not in ("COMPLIANCE","GOVERNANCE"):
            raise ValueError("PROVIDER_LOCK_CLAIM_INVALID")
    else:
        required={"schema","controller_id","window_seq","window_head_sha256",
                  "previous_attestation_sha256","unix_ms_claim","nonce","signature_b64"}
        if set(value)!=required or value["schema"]!="AETHER-293/signed-time-chain-v1":
            raise ValueError("CLOCK_BODY_SCHEMA_INVALID")
        if (type(value["window_seq"]) is not int or value["window_seq"]!=window or
            value["window_head_sha256"]!=plan["window_heads"][window-1] or
            type(value["unix_ms_claim"]) is not int or value["unix_ms_claim"]<=0):
            raise ValueError("CLOCK_BODY_BINDING_INVALID")
    return value
def capture(path,plan,plan_pin,nonce,collector=acquire):
    validate_plan(plan)
    if not ishash(plan_pin) or sha(plan)!=plan_pin:raise ValueError("PLAN_PIN_MISMATCH")
    if not isinstance(nonce,str) or not 16<=len(nonce)<=128:
        raise ValueError("FRESH_CHALLENGE_REQUIRED")
    initialize(path);db=dbopen(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM acquisition WHERE challenge_nonce=?",(nonce,)).fetchone():
            raise ValueError("CAPTURE_NONCE_REPLAY")
        previous=db.execute("SELECT head_sha FROM acquisition ORDER BY id DESC LIMIT 1").fetchone()
        head0=previous[0] if previous else ZERO
        sources=[];claim_nonces=set();object_versions={}
        clock_claims=[]
        for kind,urls in (("provider",plan["provider_urls"]),("clock",plan["clock_urls"])):
            for kid in sorted(urls):
                for window,url in enumerate(urls[kid],1):
                    host,_=validate_url(url,[urlsplit(url).hostname])
                    raw,obs=observation(collector(url,[host]),url)
                    value=check_payload(kind,kid,window,raw,plan)
                    n=value["response_nonce"] if kind=="provider" else value["nonce"]
                    if n in claim_nonces or not isinstance(n,str) or not n:
                        raise ValueError("SOURCE_NONCE_DUPLICATE")
                    claim_nonces.add(n)
                    if kind=="provider":object_versions[(kid,window)]=(value["object_key"],value["version_id"])
                    else:clock_claims.append(value)
                    sources.append({"kind":kind,"source_id":kid,"window_seq":window,
                                    "url":url,"observation":obs})
        for kid in plan["provider_urls"]:
            if object_versions[(kid,1)]!=object_versions[(kid,2)]:
                raise ValueError("PROVIDER_VERSION_CHANGED")
        if len(clock_claims)!=2 or clock_claims[1]["unix_ms_claim"]<=clock_claims[0]["unix_ms_claim"]:
            raise ValueError("CLOCK_CLAIM_NOT_INCREASING")
        if clock_claims[0]["previous_attestation_sha256"]!=ZERO or clock_claims[1]["previous_attestation_sha256"]!=sha(clock_claims[0]):
            raise ValueError("CLOCK_CLAIM_CHAIN_INVALID")
        manifest={"schema":SCHEMA,"challenge_nonce":nonce,
                  "previous_sha256":head0,"plan_sha256":plan_pin,"sources":sources}
        head=sha(manifest)
        db.execute("INSERT INTO acquisition(challenge_nonce,previous_sha,head_sha,plan_sha,manifest_json) VALUES (?,?,?,?,?)",
                   (nonce,head0,head,plan_pin,canon(manifest).decode()))
        ident=db.execute("SELECT last_insert_rowid()").fetchone()[0]
        for entry in sources:
            slot=f'{entry["kind"]}:{entry["source_id"]}:{entry["window_seq"]}'
            db.execute("INSERT INTO source_observation VALUES (?,?,?)",
                       (slot,ident,entry["observation"]["observation_sha256"]))
        db.commit()
        return {**HOLD,"acquisition_id":ident,"head_sha256":head,"raw_records_retained":len(sources),
                "reasons":["HTTPS_TRANSPORT_NOT_PROVIDER_ACCOUNT_AUTHENTICATION",
                           "CLOCK_SOURCE_IDENTITY_AND_SIGNATURE_UNVERIFIED",
                           "TWO_FETCHES_DO_NOT_PROVE_ELAPSED_TIME"]}
    except Exception:db.rollback();raise
    finally:db.close()
def audit(path):
    db=sqlite3.connect(Path(path).resolve().as_uri()+"?mode=ro",uri=True,isolation_level=None)
    try:
        db.execute("PRAGMA query_only=ON");db.execute("BEGIN")
        batches=[dict(zip(("id","challenge_nonce","previous_sha","head_sha","plan_sha","manifest_json"),r))
                 for r in db.execute("SELECT id,challenge_nonce,previous_sha,head_sha,plan_sha,manifest_json FROM acquisition ORDER BY id")]
        slots=[dict(zip(("id","acquisition_id","observation_sha"),r)) for r in
               db.execute("SELECT id,acquisition_id,observation_sha FROM source_observation ORDER BY acquisition_id,id")]
        db.commit()
    finally:db.close()
    errors=[];previous=ZERO
    for i,row in enumerate(batches,1):
        if row["id"]!=i or row["previous_sha"]!=previous:errors.append("CHAIN_SEQUENCE_BROKEN")
        try:
            manifest=json.loads(row["manifest_json"])
            if canon(manifest).decode()!=row["manifest_json"] or sha(manifest)!=row["head_sha"]:
                errors.append("BATCH_HASH_INVALID")
            if (manifest["challenge_nonce"]!=row["challenge_nonce"] or
                manifest["previous_sha256"]!=row["previous_sha"] or
                manifest["plan_sha256"]!=row["plan_sha"]):
                errors.append("BATCH_HEADER_CHANGED")
            seen=set()
            for item in manifest["sources"]:
                raw,obs=observation(item["observation"],item["url"])
                name=f'{item["kind"]}:{item["source_id"]}:{item["window_seq"]}'
                seen.add((name,obs["observation_sha256"]))
                if digest(raw)!=obs["raw_sha256"]:errors.append("RETAINED_RAW_CHANGED")
            stored={(v["id"],v["observation_sha"]) for v in slots if v["acquisition_id"]==i}
            if len(seen)!=8 or stored!=seen:errors.append("OBSERVATION_SET_DIVERGENCE")
        except (ValueError,TypeError,KeyError,UnicodeError):
            errors.append("RETAINED_MANIFEST_INVALID")
        previous=row["head_sha"]
    if len(slots)!=8*len(batches):errors.append("GLOBAL_OBSERVATION_CONSERVATION_FAILED")
    errors+=["PROVIDER_API_IDENTITY_NOT_ESTABLISHED","CLOCK_AUTHORITY_UNVERIFIED",
             "LOCAL_DATABASE_ROLLBACK_POSSIBLE"]
    return {**HOLD,"acquisitions":len(batches),"observations":len(slots),
            "latest_head_sha256":previous,"reasons":sorted(set(errors))}
def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest="mode",required=True)
    c=s.add_parser("capture")
    c.add_argument("--db",type=Path,required=True)
    c.add_argument("--plan",type=Path,required=True)
    c.add_argument("--plan-sha256",required=True)
    c.add_argument("--nonce",required=True)
    a=s.add_parser("audit");a.add_argument("--db",type=Path,required=True)
    opts=p.parse_args()
    try:
        result=(capture(opts.db,json.loads(opts.plan.read_bytes()),opts.plan_sha256,opts.nonce)
                if opts.mode=="capture" else audit(opts.db))
    except (OSError,ValueError,KeyError,TypeError,sqlite3.Error) as e:
        result={**HOLD,"reasons":["REJECTED:"+type(e).__name__+":"+str(e)[:100]]}
    print(json.dumps(result,indent=2,sort_keys=True))
    return 1
if __name__=="__main__":raise SystemExit(main())
