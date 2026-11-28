#!/usr/bin/env python3
"""AETHER-296-RS: restricted AWS identity and Object Lock readback; authority HOLD.

SigV4 client authentication and TLS observations do not prove independent
custody, provider-issued signed receipts, or independently held clock keys.
"""
import argparse,base64,datetime,hashlib,hmac,json,os,sys,urllib.parse,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"264"),str(ROOT/"295")]
from acquisition import PinnedHTTPS,resolve_public,public_ip,validate_url
from authenticated_provider import fetch_s3,clock_audit
LIMIT=65536
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "external_custody_verified":False,"independent_clock_authority_verified":False,
      "storage_account_identity_independently_verified":False}
def canon(obj):return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def sha_bytes(raw):return hashlib.sha256(raw).hexdigest()
def hex64(s):return isinstance(s,str) and len(s)==64 and all(c in "0123456789abcdef" for c in s)
def quote(s):return urllib.parse.quote(s,safe="-_.~")
def sign(method,host,path,query,service,region,access,secret,session,now):
    if method!="GET":raise ValueError("GET_ONLY")
    if not isinstance(now,str) or len(now)!=16 or now[8]!="T" or now[-1]!="Z":raise ValueError("DATE_INVALID")
    if not all(isinstance(s,str) and s for s in (access,secret,region,host)):
        raise ValueError("CREDENTIALS_REQUIRED")
    params="&".join(quote(k)+"="+quote(v) for k,v in sorted(query.items()))
    bodyhash=sha_bytes(b"")
    headers={"host":host,"x-amz-date":now,"x-amz-content-sha256":bodyhash}
    if session:headers["x-amz-security-token"]=session
    names=";".join(sorted(headers))
    signed="".join(k+":"+headers[k].strip()+"\n" for k in sorted(headers))
    canonical="\n".join((method,path,params,signed,names,bodyhash))
    scope=now[:8]+"/"+region+"/"+service+"/aws4_request"
    string="\n".join(("AWS4-HMAC-SHA256",now,scope,sha_bytes(canonical.encode())))
    def mac(key,message):return hmac.new(key,message.encode(),hashlib.sha256).digest()
    key=mac(mac(mac(mac(("AWS4"+secret).encode(),now[:8]),region),service),"aws4_request")
    sig=hmac.new(key,string.encode(),hashlib.sha256).hexdigest()
    headers["authorization"]="AWS4-HMAC-SHA256 Credential="+access+"/"+scope+", SignedHeaders="+names+", Signature="+sig
    return headers,params,sha_bytes(canonical.encode())
def endpoint(service,region,bucket=None):
    if not isinstance(region,str) or not region or len(region)>32 or not all(c.isalnum() or c=="-" for c in region):
        raise ValueError("REGION_INVALID")
    if service not in ("sts","s3"):raise ValueError("SERVICE_NOT_ALLOWLISTED")
    host=service+"."+region+".amazonaws.com"
    if service=="s3":
        if not isinstance(bucket,str) or not 3<=len(bucket)<=63 or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789.-" for c in bucket):
            raise ValueError("BUCKET_INVALID")
        if bucket.startswith(".") or bucket.endswith(".") or ".." in bucket:
            raise ValueError("BUCKET_INVALID")
        path="/"+bucket
    else:path="/"
    validate_url("https://"+host+path,[host])
    return host,path
def request(service,region,kind,bucket,access,secret,session,now,
            resolver=resolve_public,factory=PinnedHTTPS):
    if (service,kind) not in (("sts","IDENTITY"),("s3","VERSIONING"),("s3","LOCK_CONFIGURATION")):
        raise ValueError("READ_ONLY_REQUEST_KIND_REQUIRED")
    host,path=endpoint(service,region,bucket)
    query=({"Action":"GetCallerIdentity","Version":"2011-06-15"} if service=="sts"
           else {"versioning":""} if kind=="VERSIONING" else {"object-lock":""})
    headers,qs,request_hash=sign("GET",host,path,query,service,region,access,secret,session,now)
    addresses=resolver(host)
    if (not isinstance(addresses,list) or not 1<=len(addresses)<=16
        or not all(isinstance(ip,str) and public_ip(ip) for ip in addresses)):
        raise ValueError("DNS_UNSAFE_OR_EMPTY")
    conn=factory(host,addresses[0],timeout=3)
    try:
        conn.request("GET",path+"?"+qs,headers={**headers,"Accept-Encoding":"identity","Connection":"close"})
        response=conn.getresponse()
        if response.status!=200:raise ValueError("AWS_RESPONSE_STATUS_REJECTED")
        pairs=response.getheaders()
        if len(pairs)>64 or len({k.lower() for k,_ in pairs})!=len(pairs):
            raise ValueError("DUPLICATE_OR_EXCESS_HEADERS")
        if any(not isinstance(k,str) or not isinstance(v,str) or len(k)>128 or len(v)>4096 for k,v in pairs):
            raise ValueError("RESPONSE_HEADER_INVALID")
        all_headers={k.lower():v for k,v in pairs}
        if all_headers.get("content-encoding","identity").lower()!="identity":
            raise ValueError("ENCODING_NOT_IDENTITY")
        raw=response.read(LIMIT+1)
        if len(raw)>LIMIT:raise ValueError("RAW_RESPONSE_TOO_LARGE")
        # stdlib XML parser; no external entity/network resolution.
        root=ET.fromstring(raw)
        def lookup(name):
            candidates=[n.text for n in root.iter() if n.tag.split("}")[-1]==name]
            return candidates[0] if len(candidates)==1 else None
        if kind=="IDENTITY":
            metadata={"account":lookup("Account"),"arn":lookup("Arn"),"user_id":lookup("UserId")}
            if (not isinstance(metadata["account"],str) or len(metadata["account"])!=12
                or not metadata["account"].isdigit()
                or not isinstance(metadata["arn"],str) or not metadata["arn"].startswith("arn:aws:")
                or not isinstance(metadata["user_id"],str) or not metadata["user_id"]):
                raise ValueError("STS_IDENTITY_RESPONSE_INVALID")
        elif kind=="VERSIONING":
            metadata={"status":lookup("Status"),"mfa_delete":lookup("MFADelete")}
            if metadata["status"]!="Enabled":raise ValueError("VERSIONING_NOT_ENABLED")
        else:
            metadata={"object_lock_enabled":lookup("ObjectLockEnabled"),
                      "default_mode":lookup("Mode"),"default_days":lookup("Days"),
                      "default_years":lookup("Years")}
            if metadata["object_lock_enabled"]!="Enabled":
                raise ValueError("OBJECT_LOCK_NOT_ENABLED")
            if metadata["default_mode"] not in ("COMPLIANCE","GOVERNANCE",None):
                raise ValueError("LOCK_MODE_INVALID")
        safe_headers={k:v for k,v in all_headers.items() if k in ("x-amz-request-id","x-amz-id-2","date","content-type")}
        return {**HOLD,"service":service,"operation":kind,
                "service_host":host,"request_sha256":request_hash,
                "raw_body_sha256":sha_bytes(raw),"raw_body_b64":base64.b64encode(raw).decode(),
                "response_headers":safe_headers,"metadata":metadata,
                "reasons":["CLIENT_SIGV4_NOT_PROVIDER_SIGNED_RESPONSE",
                           "CREDENTIALS_AND_CUSTODIAN_ANCESTRY_NOT_INDEPENDENTLY_VERIFIED"]}
    finally:conn.close()
def correlate(identity,versioning,lock,head,retention,expected_account,expected_version):
    """Only combine compatible observed metadata, never infer ownership or custody."""
    errors=[]
    if not all(isinstance(x,dict) for x in (identity,versioning,lock,head,retention)):
        return {**HOLD,"reasons":["EVIDENCE_TYPE_INVALID"]}
    if (identity.get("operation")!="IDENTITY" or
        versioning.get("operation")!="VERSIONING" or
        lock.get("operation")!="LOCK_CONFIGURATION" or
        head.get("operation")!="HEAD" or retention.get("operation")!="RETENTION"):
        errors.append("OPERATION_KIND_INVALID")
    if not isinstance(expected_account,str) or identity.get("metadata",{}).get("account")!=expected_account:
        errors.append("ACCOUNT_PIN_CONFLICT")
    if not isinstance(expected_version,str) or not expected_version or head.get("object_version")!=expected_version or retention.get("object_version")!=expected_version:
        errors.append("VERSION_PIN_CONFLICT")
    if versioning.get("metadata",{}).get("status")!="Enabled":errors.append("VERSIONING_NOT_ENABLED")
    if lock.get("metadata",{}).get("object_lock_enabled")!="Enabled":errors.append("OBJECT_LOCK_NOT_ENABLED")
    h=head.get("metadata",{});r=retention.get("metadata",{})
    if h.get("lock_mode") not in ("COMPLIANCE","GOVERNANCE") or r.get("lock_mode")!=h.get("lock_mode"):
        errors.append("VERSION_RETENTION_MODE_CONFLICT")
    if not h.get("retain_until") or h.get("retain_until")!=r.get("retain_until"):
        errors.append("VERSION_RETENTION_DATE_CONFLICT")
    if (versioning.get("service_host")!=lock.get("service_host") or
        head.get("url_host")!=versioning.get("service_host") or
        retention.get("url_host")!=versioning.get("service_host")):
        errors.append("PROVIDER_REGION_HOST_CONFLICT")
    errors+=["STS_CLIENT_IDENTITY_IS_NOT_BUCKET_OWNERSHIP_PROOF",
             "TLS_METADATA_NOT_PROVIDER_SIGNED_CUSTODY",
             "CLOCK_CONTROLLER_IDENTITY_UNVERIFIED"]
    return {**HOLD,"reasons":sorted(set(errors)),"metadata_consistent":len(errors)==3}
def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest="mode",required=True)
    r=s.add_parser("aws")
    r.add_argument("--kind",choices=("IDENTITY","VERSIONING","LOCK_CONFIGURATION"),required=True)
    r.add_argument("--region",required=True);r.add_argument("--bucket")
    c=s.add_parser("correlate")
    c.add_argument("--bundle",type=Path,required=True)
    c.add_argument("--expected-account",required=True);c.add_argument("--expected-version",required=True)
    a=p.parse_args()
    try:
        if a.mode=="aws":
            key=os.environ.get("AWS_ACCESS_KEY_ID","")
            secret=os.environ.get("AWS_SECRET_ACCESS_KEY","")
            token=os.environ.get("AWS_SESSION_TOKEN","")
            now=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            result=request("sts" if a.kind=="IDENTITY" else "s3",a.region,a.kind,a.bucket,key,secret,token,now)
        else:
            bundle=json.loads(a.bundle.read_bytes())
            result=correlate(*(bundle[n] for n in ("identity","versioning","lock","head","retention")),
                             a.expected_account,a.expected_version)
    except (OSError,KeyError,ValueError,TypeError,ET.ParseError) as ex:
        result={**HOLD,"reasons":["INPUT_REJECTED:"+type(ex).__name__+":"+str(ex)[:100]]}
    print(json.dumps(result,indent=2,sort_keys=True))
    return 1
if __name__=="__main__":raise SystemExit(main())
