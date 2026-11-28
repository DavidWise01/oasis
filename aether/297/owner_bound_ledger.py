#!/usr/bin/env python3
"""AETHER-297-RS: expected-owner-bound S3 metadata + redacted atomic ledger.

No write HTTP verbs. No AWS secrets, session tokens, or Authorization in ledger.
A successful expected-owner request is NOT independent custody attestation.
"""
import argparse,base64,datetime,hashlib,hmac,json,os,sqlite3,sys,urllib.parse,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"264"))
from acquisition import PinnedHTTPS,resolve_public,public_ip,validate_url
SCHEMA="AETHER-297/owner-bound-evidence-v1"
ZERO="0"*64
LIMIT=65536
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "independent_external_custody_verified":False,
      "provider_signed_storage_receipt_verified":False}
SAFE_HEADERS={"date","content-type","content-length","x-amz-request-id","x-amz-id-2",
              "x-amz-version-id","x-amz-object-lock-mode",
              "x-amz-object-lock-retain-until-date"}
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def sha(v):return digest(canon(v))
def q(s):return urllib.parse.quote(s,safe="-_.~")
def validate_owner(owner):
    if not isinstance(owner,str) or len(owner)!=12 or not owner.isascii() or not owner.isdigit():
        raise ValueError("EXPECTED_OWNER_12_DIGITS_REQUIRED")
def validate_target(region,bucket,key,version,owner):
    validate_owner(owner)
    if not isinstance(region,str) or not 1<=len(region)<=32 or any(not(c.islower() or c.isdigit() or c=="-") for c in region):
        raise ValueError("REGION_INVALID")
    if not isinstance(bucket,str) or not 3<=len(bucket)<=63 or any(not(c.islower() or c.isdigit() or c in ".-") for c in bucket) or ".." in bucket or bucket.startswith((".", "-")) or bucket.endswith((".", "-")):
        raise ValueError("BUCKET_INVALID")
    if not isinstance(key,str) or not key or len(key)>1024 or key.startswith("/"):
        raise ValueError("OBJECT_KEY_INVALID")
    if not isinstance(version,str) or not version or len(version)>256 or version=="null":
        raise ValueError("EXPLICIT_NON_NULL_VERSION_REQUIRED")
    host="s3."+region+".amazonaws.com"
    validate_url("https://"+host+"/",[host])
    return host
def sign(method,host,path,query,region,owner,access,secret,session,now):
    if method not in ("GET","HEAD"):raise ValueError("READ_ONLY_METHODS_ONLY")
    validate_owner(owner)
    if not isinstance(now,str) or len(now)!=16 or now[8]!="T" or not now.endswith("Z"):
        raise ValueError("DATE_FORMAT_INVALID")
    if not all(isinstance(x,str) and x for x in (access,secret,region,host)):
        raise ValueError("CREDENTIALS_REQUIRED")
    if not path.startswith("/") or "?" in path:raise ValueError("CANONICAL_PATH_INVALID")
    querystring="&".join(q(k)+"="+q(v) for k,v in sorted(query.items()))
    headers={"host":host,"x-amz-content-sha256":digest(b""),
             "x-amz-date":now,"x-amz-expected-bucket-owner":owner}
    if session:headers["x-amz-security-token"]=session
    headernames=";".join(sorted(headers))
    canonicalheaders="".join(k+":"+headers[k].strip()+"\n" for k in sorted(headers))
    request="\n".join((method,path,querystring,canonicalheaders,headernames,digest(b"")))
    scope=now[:8]+"/"+region+"/s3/aws4_request"
    tosign="\n".join(("AWS4-HMAC-SHA256",now,scope,digest(request.encode())))
    def mac(key,s):return hmac.new(key,s.encode(),hashlib.sha256).digest()
    key=mac(mac(mac(mac(("AWS4"+secret).encode(),now[:8]),region),"s3"),"aws4_request")
    signature=hmac.new(key,tosign.encode(),hashlib.sha256).hexdigest()
    headers["authorization"]="AWS4-HMAC-SHA256 Credential="+access+"/"+scope+", SignedHeaders="+headernames+", Signature="+signature
    return headers,querystring,digest(request.encode())
def targets(bucket,key,version):
    base="/"+q(bucket)
    objectpath=base+"/"+"/".join(q(part) for part in key.split("/"))
    return [("VERSIONING","GET",base,{"versioning":""}),
            ("LOCK_CONFIGURATION","GET",base,{"object-lock":""}),
            ("HEAD","HEAD",objectpath,{"versionId":version}),
            ("RETENTION","GET",objectpath,{"retention":"","versionId":version})]
def live(method,host,requestpath,headers):
    addresses=resolve_public(host)
    if not isinstance(addresses,list) or not 1<=len(addresses)<=16 or not all(isinstance(ip,str) and public_ip(ip) for ip in addresses):
        raise ValueError("UNSAFE_DNS")
    conn=PinnedHTTPS(host,addresses[0],timeout=3)
    try:
        conn.request(method,requestpath,headers={**headers,"Accept-Encoding":"identity","Connection":"close"})
        response=conn.getresponse()
        if response.status!=200:raise ValueError("S3_RESPONSE_NOT_SUCCESS")
        pairs=response.getheaders()
        if len(pairs)>64:raise ValueError("RESPONSE_HEADERS_TOO_MANY")
        names=[k.lower() for k,v in pairs]
        if len(names)!=len(set(names)):raise ValueError("DUPLICATE_RESPONSE_HEADERS")
        if any(not isinstance(k,str) or not isinstance(v,str) or len(k)>128 or len(v)>4096 for k,v in pairs):
            raise ValueError("RESPONSE_HEADER_TOO_LARGE")
        info={k.lower():v for k,v in pairs}
        if info.get("content-encoding","identity").lower()!="identity":
            raise ValueError("COMPRESSED_RESPONSE_REJECTED")
        length=info.get("content-length")
        if length is not None and (not length.isdigit() or int(length)>LIMIT):
            raise ValueError("CONTENT_LENGTH_INVALID")
        raw=response.read(LIMIT+1)
        if len(raw)>LIMIT or length is not None and len(raw)!=int(length):
            raise ValueError("BODY_INCOMPLETE_OR_TOO_LARGE")
        return 200,info,raw
    finally:conn.close()
def metadata(kind,headers,raw,version):
    if kind=="HEAD":
        if raw:raise ValueError("HEAD_BODY_NOT_EMPTY")
        if headers.get("x-amz-version-id")!=version:raise ValueError("VERSION_ID_CHANGED")
        mode=headers.get("x-amz-object-lock-mode")
        date=headers.get("x-amz-object-lock-retain-until-date")
        if mode not in ("COMPLIANCE","GOVERNANCE") or not date:
            raise ValueError("HEAD_LOCK_METADATA_MISSING")
        return {"version":version,"mode":mode,"until":date}
    if not raw or len(raw)>LIMIT:raise ValueError("XML_RESPONSE_MISSING")
    try:root=ET.fromstring(raw)
    except ET.ParseError as exc:raise ValueError("XML_RESPONSE_INVALID") from exc
    def one(name):
        values=[v.text for v in root.iter() if v.tag.split("}")[-1]==name]
        return values[0] if len(values)==1 else None
    if kind=="VERSIONING":
        if root.tag.split("}")[-1]!="VersioningConfiguration" or one("Status")!="Enabled":
            raise ValueError("BUCKET_VERSIONING_DISABLED")
        return {"status":"Enabled"}
    if kind=="LOCK_CONFIGURATION":
        if root.tag.split("}")[-1]!="ObjectLockConfiguration" or one("ObjectLockEnabled")!="Enabled":
            raise ValueError("BUCKET_OBJECT_LOCK_DISABLED")
        return {"enabled":True}
    if kind=="RETENTION":
        if root.tag.split("}")[-1]!="Retention":raise ValueError("RETENTION_ROOT_INVALID")
        mode=one("Mode");date=one("RetainUntilDate")
        if mode not in ("COMPLIANCE","GOVERNANCE") or not date:raise ValueError("RETENTION_DATA_INVALID")
        return {"mode":mode,"until":date}
    raise ValueError("OPERATION_UNSUPPORTED")
def snapshot(region,bucket,key,version,owner,access,secret,session,now,transport=live):
    host=validate_target(region,bucket,key,version,owner)
    records=[];results={}
    for kind,method,path,query in targets(bucket,key,version):
        headers,querystring,requesthash=sign(method,host,path,query,region,owner,access,secret,session,now)
        status,pairs,raw=transport(method,host,path+"?"+querystring,headers)
        if status!=200:raise ValueError("STATUS_REJECTED")
        if not isinstance(pairs,dict) or len(pairs)>64 or any(not isinstance(k,str) or not isinstance(v,str) for k,v in pairs.items()):
            raise ValueError("RESPONSE_HEADERS_INVALID")
        normalized={k.lower():v for k,v in pairs.items()}
        if any(len(k)>128 or len(v)>4096 for k,v in normalized.items()):
            raise ValueError("RESPONSE_HEADERS_TOO_LONG")
        if len(raw)>LIMIT:raise ValueError("RAW_BODY_TOO_LARGE")
        if normalized.get("content-encoding","identity").lower()!="identity":
            raise ValueError("ENCODING_UNSUPPORTED")
        response_meta=metadata(kind,normalized,raw,version)
        results[kind]=response_meta
        records.append({"operation":kind,"method":method,"host":host,
                        "path_sha256":digest((path+"?"+querystring).encode()),
                        "request_sha256":requesthash,"response_status":status,
                        "response_headers":{k:v for k,v in normalized.items() if k in SAFE_HEADERS},
                        "response_raw_sha256":digest(raw),
                        "response_raw_b64":base64.b64encode(raw).decode("ascii"),
                        "parsed":response_meta})
    if results["HEAD"]["mode"]!=results["RETENTION"]["mode"] or results["HEAD"]["until"]!=results["RETENTION"]["until"]:
        raise ValueError("VERSION_SPECIFIC_RETENTION_CONFLICT")
    return {"schema":SCHEMA,"region":region,"bucket":bucket,"key_sha256":digest(key.encode()),
            "version":version,"expected_bucket_owner":owner,
            "records":records}
def open_db(path):
    db=sqlite3.connect(str(path),isolation_level=None,timeout=10)
    db.execute("PRAGMA journal_mode=WAL");db.execute("PRAGMA synchronous=FULL")
    db.execute("PRAGMA busy_timeout=10000");db.execute("PRAGMA foreign_keys=ON")
    return db
def init(path):
    db=open_db(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS evidence (id INTEGER PRIMARY KEY AUTOINCREMENT,challenge TEXT NOT NULL UNIQUE,previous_head TEXT NOT NULL,head TEXT NOT NULL UNIQUE,manifest TEXT NOT NULL)")
        db.commit()
    except Exception:db.rollback();raise
    finally:db.close()
def append(path,evidence,challenge):
    if not isinstance(challenge,str) or not 16<=len(challenge)<=128:
        raise ValueError("CHALLENGE_REQUIRED")
    if evidence.get("schema")!=SCHEMA or len(evidence.get("records",[]))!=4:
        raise ValueError("EVIDENCE_INCOMPLETE")
    init(path);db=open_db(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM evidence WHERE challenge=?",(challenge,)).fetchone():
            raise ValueError("CHALLENGE_REPLAY")
        prior=db.execute("SELECT head FROM evidence ORDER BY id DESC LIMIT 1").fetchone()
        parent=prior[0] if prior else ZERO
        manifest={"schema":SCHEMA,"challenge":challenge,"previous_head_sha256":parent,"evidence":evidence}
        head=sha(manifest)
        db.execute("INSERT INTO evidence(challenge,previous_head,head,manifest) VALUES (?,?,?,?)",
                   (challenge,parent,head,canon(manifest).decode()))
        seq=db.execute("SELECT last_insert_rowid()").fetchone()[0]
        db.commit()
        return {**HOLD,"sequence":seq,"head_sha256":head,"transcripts":4,
                "reasons":["EXPECTED_OWNER_RESPONSE_CONSISTENT_NOT_INDEPENDENT_CUSTODY",
                           "LOCAL_LEDGER_ROLLBACK_POSSIBLE"]}
    except Exception:db.rollback();raise
    finally:db.close()
def audit(path,prefix_seq=None,prefix_sha=None):
    db=sqlite3.connect(Path(path).resolve().as_uri()+"?mode=ro",uri=True,isolation_level=None)
    try:
        db.execute("PRAGMA query_only=ON");db.execute("BEGIN")
        rows=list(db.execute("SELECT id,challenge,previous_head,head,manifest FROM evidence ORDER BY id"))
        db.commit()
    finally:db.close()
    faults=[];parent=ZERO
    for i,(seq,challenge,previous,head,raw) in enumerate(rows,1):
        if seq!=i or previous!=parent:faults.append("HISTORY_GAP_OR_PARENT_CHANGED")
        try:
            manifest=json.loads(raw)
            if canon(manifest).decode()!=raw or sha(manifest)!=head:faults.append("HISTORY_HASH_CHANGED")
            if manifest["challenge"]!=challenge or manifest["previous_head_sha256"]!=previous:
                faults.append("HISTORY_HEADER_CHANGED")
            e=manifest["evidence"]
            if e["schema"]!=SCHEMA or len(e["records"])!=4:faults.append("EVIDENCE_INCOMPLETE")
            kinds=set()
            for r in e["records"]:
                kinds.add(r["operation"])
                body=base64.b64decode(r["response_raw_b64"],validate=True)
                if digest(body)!=r["response_raw_sha256"]:faults.append("RAW_EVIDENCE_SUBSTITUTED")
                if any("authorization" in k.lower() or "token" in k.lower() or "secret" in k.lower() for k in r["response_headers"]):
                    faults.append("CREDENTIAL_BEARING_HEADER_PRESENT")
            if kinds!={"VERSIONING","LOCK_CONFIGURATION","HEAD","RETENTION"}:
                faults.append("OPERATION_SET_INVALID")
        except (KeyError,ValueError,TypeError,UnicodeError):
            faults.append("MANIFEST_UNREADABLE")
        parent=head
    if prefix_seq is not None or prefix_sha is not None:
        if type(prefix_seq) is not int or prefix_seq<1 or not isinstance(prefix_sha,str) or len(prefix_sha)!=64:
            faults.append("PREFIX_FORMAT_INVALID")
        elif len(rows)<prefix_seq:faults.append("HISTORICAL_PREFIX_REMOVED")
        elif rows[prefix_seq-1][3]!=prefix_sha:faults.append("HISTORICAL_PREFIX_REWRITTEN")
    faults+=["WHOLE_LEDGER_ROLLBACK_POSSIBLE","SOURCE_ACCOUNT_ANCESTRY_NOT_INDEPENDENTLY_OBSERVED"]
    return {**HOLD,"batches":len(rows),"latest_head_sha256":parent,
            "reasons":sorted(set(faults))}
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="action",required=True)
    c=sub.add_parser("capture")
    c.add_argument("--db",type=Path,required=True);c.add_argument("--region",required=True)
    c.add_argument("--bucket",required=True);c.add_argument("--key",required=True)
    c.add_argument("--version",required=True);c.add_argument("--expected-owner",required=True)
    c.add_argument("--nonce",required=True)
    a=sub.add_parser("audit");a.add_argument("--db",type=Path,required=True)
    a.add_argument("--prefix-seq",type=int);a.add_argument("--prefix-sha256")
    args=p.parse_args()
    try:
        if args.action=="capture":
            date=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            evidence=snapshot(args.region,args.bucket,args.key,args.version,args.expected_owner,
                 os.environ.get("AWS_ACCESS_KEY_ID",""),os.environ.get("AWS_SECRET_ACCESS_KEY",""),
                 os.environ.get("AWS_SESSION_TOKEN",""),date)
            result=append(args.db,evidence,args.nonce)
        else:result=audit(args.db,args.prefix_seq,args.prefix_sha256)
    except (OSError,ValueError,KeyError,TypeError,sqlite3.Error) as exc:
        result={**HOLD,"reasons":["REJECTED:"+type(exc).__name__+":"+str(exc)[:100]]}
    print(json.dumps(result,indent=2,sort_keys=True))
    return 1
if __name__=="__main__":raise SystemExit(main())
