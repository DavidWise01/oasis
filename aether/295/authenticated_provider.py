#!/usr/bin/env python3
"""AETHER-295-RS: opt-in AWS S3 SigV4 read-only evidence and pinned clock checks.

SigV4 authenticates the CLIENT request, not the provider's independent custody.
TLS response checks do not replace provider-issued signed receipts.
"""
import argparse,base64,datetime,hashlib,hmac,json,os,sys,urllib.parse,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"264"),str(ROOT/"292")]
from acquisition import PinnedHTTPS,resolve_public,validate_url
from attestation_audit import verify as ed_verify
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "provider_custody_independent":False,"trusted_clock_independent":False}
CLOCK_SCHEMA="AETHER-295/clock-link-v1"
LIMIT=65536
def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def sha(o):return digest(canon(o))
def valid_sha(s):return isinstance(s,str) and len(s)==64 and all(c in "0123456789abcdef" for c in s)
def q(s):return urllib.parse.quote(s,safe="-_.~")
def signed_headers(method,host,path,query,region,access,secret,session,now):
    """AWS Signature Version 4; only GET/HEAD, no payload or write operations."""
    if method not in ("GET","HEAD"):raise ValueError("READ_ONLY_METHOD_REQUIRED")
    if (not isinstance(now,str) or len(now)!=16 or not now.endswith("Z")
        or not now[:8].isdigit() or now[8]!="T" or not now[9:15].isdigit()):
        raise ValueError("AMZ_DATE_INVALID")
    if not all(isinstance(v,str) and v for v in (host,region,access,secret)):
        raise ValueError("CREDENTIAL_FIELDS_MISSING")
    if not path.startswith("/") or "?" in path or "#" in path:raise ValueError("PATH_INVALID")
    if not isinstance(query,dict) or any(not isinstance(k,str) or not isinstance(v,str) for k,v in query.items()):
        raise ValueError("QUERY_INVALID")
    canonical_query="&".join(q(k)+"="+q(v) for k,v in sorted(query.items()))
    headers={"host":host,"x-amz-content-sha256":digest(b""),"x-amz-date":now}
    if session:headers["x-amz-security-token"]=session
    names=";".join(sorted(headers))
    canonical_headers="".join(k+":"+headers[k].strip()+"\n" for k in sorted(headers))
    canonical_request=("\n".join([method,path,canonical_query,canonical_headers,names,digest(b"")])).encode()
    scope=now[:8]+"/"+region+"/s3/aws4_request"
    string_to_sign="\n".join(["AWS4-HMAC-SHA256",now,scope,digest(canonical_request)])
    def mac(k,m):return hmac.new(k,m.encode(),hashlib.sha256).digest()
    key=mac(mac(mac(mac(("AWS4"+secret).encode(),now[:8]),region),"s3"),"aws4_request")
    signature=hmac.new(key,string_to_sign.encode(),hashlib.sha256).hexdigest()
    auth=("AWS4-HMAC-SHA256 Credential="+access+"/"+scope+
          ", SignedHeaders="+names+", Signature="+signature)
    return {**headers,"authorization":auth},canonical_query,digest(canonical_request)
def validate_target(host,key,version,region,kind):
    if kind not in ("HEAD","RETENTION"):raise ValueError("ONLY_OBJECT_METADATA_ALLOWED")
    if not isinstance(region,str) or not region or len(region)>32:raise ValueError("REGION_INVALID")
    if not isinstance(key,str) or not key or len(key)>1024:raise ValueError("OBJECT_KEY_INVALID")
    if not isinstance(version,str) or not version or len(version)>256:raise ValueError("VERSION_REQUIRED")
    expected=("s3."+region+".amazonaws.com")
    if host!=expected:raise ValueError("AWS_SERVICE_HOST_NOT_PINNED")
    validate_url("https://"+host+"/",[host])
    path="/"+"/".join(q(p) for p in key.split("/"))
    if not path.startswith("/") or "//" in path:raise ValueError("OBJECT_PATH_INVALID")
    query={"versionId":version}
    if kind=="RETENTION":query["retention"]=""
    return path,query
def fetch_s3(host,key,version,region,kind,access,secret,session,now,
             resolver=resolve_public,factory=PinnedHTTPS):
    path,query=validate_target(host,key,version,region,kind)
    method="HEAD" if kind=="HEAD" else "GET"
    headers,query_string,request_digest=signed_headers(method,host,path,query,region,access,secret,session,now)
    addresses=resolver(host)
    if not isinstance(addresses,list) or not addresses or len(addresses)>16:
        raise ValueError("DNS_UNAVAILABLE")
    from acquisition import public_ip
    if not all(isinstance(ip,str) and public_ip(ip) for ip in addresses):
        raise ValueError("DNS_NOT_PUBLIC")
    conn=factory(host,addresses[0],timeout=3)
    try:
        conn.request(method,path+"?"+query_string,headers={**headers,"Accept-Encoding":"identity","Connection":"close"})
        result=conn.getresponse()
        if result.status!=200:raise ValueError("AWS_STATUS_NOT_OK")
        all_headers={k.lower():v for k,v in result.getheaders()}
        if all_headers.get("content-encoding","identity").lower()!="identity":
            raise ValueError("COMPRESSED_BODY_REJECTED")
        if len(all_headers)>64:raise ValueError("HEADER_COUNT_LIMIT")
        if any(len(k)>128 or len(v)>4096 for k,v in all_headers.items()):
            raise ValueError("HEADER_LIMIT")
        payload=result.read(LIMIT+1)
        if len(payload)>LIMIT:raise ValueError("RESPONSE_SIZE_LIMIT")
        if kind=="HEAD" and payload:raise ValueError("UNEXPECTED_HEAD_BODY")
        if kind=="HEAD":
            observed=all_headers.get("x-amz-version-id")
            if observed!=version:raise ValueError("VERSION_ID_DIVERGENCE")
            meta={"version_id":observed,
                  "lock_mode":all_headers.get("x-amz-object-lock-mode"),
                  "retain_until":all_headers.get("x-amz-object-lock-retain-until-date")}
        else:
            root=ET.fromstring(payload)
            if root.tag.split("}")[-1]!="Retention":raise ValueError("RETENTION_XML_ROOT_INVALID")
            values={element.tag.split("}")[-1]:element.text for element in root}
            if values.get("Mode") not in ("GOVERNANCE","COMPLIANCE") or not values.get("RetainUntilDate"):
                raise ValueError("RETENTION_NOT_ESTABLISHED")
            meta={"lock_mode":values["Mode"],"retain_until":values["RetainUntilDate"]}
        # Credential, token and Authorization never appear in the result.
        return {**HOLD,"provider":"AWS_S3","operation":kind,"request_sha256":request_digest,
                "url_host":host,"object_version":version,"response_sha256":digest(payload),
                "raw_response_b64":base64.b64encode(payload).decode(),
                "headers":{k:v for k,v in all_headers.items() if k.startswith("x-amz-")},
                "metadata":meta,
                "reasons":["SIGNED_CLIENT_REQUEST_NOT_PROVIDER_SIGNATURE",
                           "ACCOUNT_OWNERSHIP_AND_EXTERNAL_CUSTODY_UNVERIFIED"]}
    finally:conn.close()
def clock_audit(claims,pem,pinned_pem_sha,window_heads):
    """Verify a clock's *signature* and chained windows; never infer accuracy."""
    failures=[]
    if (not isinstance(pem,str) or digest(pem.encode())!=pinned_pem_sha):
        return {**HOLD,"reasons":["PINNED_CLOCK_KEY_REQUIRED"]}
    if not isinstance(claims,list) or len(claims)!=2 or not isinstance(window_heads,list) or len(window_heads)!=2:
        return {**HOLD,"reasons":["TWO_CLOCK_WINDOWS_REQUIRED"]}
    prev="0"*64;times=[];nonces=set()
    fields={"schema","window_seq","window_head_sha256","previous_attestation_sha256",
            "unix_ms_claim","nonce","signature_b64"}
    for i,claim in enumerate(claims,1):
        if not isinstance(claim,dict) or set(claim)!=fields:
            failures.append("CLOCK_CLAIM_SCHEMA_INVALID");continue
        statement={k:v for k,v in claim.items() if k!="signature_b64"}
        if claim["schema"]!=CLOCK_SCHEMA or claim["window_seq"]!=i or claim["window_head_sha256"]!=window_heads[i-1]:
            failures.append("CLOCK_WINDOW_MISMATCH")
        if claim["previous_attestation_sha256"]!=prev:failures.append("CLOCK_CHAIN_BROKEN")
        if not ed_verify(pem,statement,claim["signature_b64"]):failures.append("CLOCK_SIGNATURE_INVALID")
        if type(claim["unix_ms_claim"]) is not int or claim["unix_ms_claim"]<=0:
            failures.append("CLOCK_TIMESTAMP_INVALID")
        else:times.append(claim["unix_ms_claim"])
        if not isinstance(claim["nonce"],str) or not claim["nonce"] or claim["nonce"] in nonces:
            failures.append("CLOCK_NONCE_REPLAY")
        nonces.add(claim["nonce"]);prev=sha(claim)
    if len(times)==2 and times[1]<=times[0]:failures.append("CLOCK_TIME_NONMONOTONIC")
    failures+=["CLOCK_KEY_CONTROLLER_NOT_INDEPENDENTLY_IDENTIFIED",
               "CLOCK_TIME_NOT_PROVIDER_ATTESTED","CLOCK_ELAPSED_INTERVAL_UNVERIFIED"]
    return {**HOLD,"reasons":sorted(set(failures)),
            "claimed_delta_ms":times[1]-times[0] if len(times)==2 else None}
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="task",required=True)
    a=sub.add_parser("aws")
    for n in ("host","key","version","region"):a.add_argument("--"+n,required=True)
    a.add_argument("--kind",required=True,choices=["HEAD","RETENTION"])
    c=sub.add_parser("clock")
    for n in ("claims","clock-pem","heads"):c.add_argument("--"+n,type=Path,required=True)
    c.add_argument("--pinned-key-sha256",required=True)
    opts=p.parse_args()
    try:
        if opts.task=="aws":
            access=os.environ.get("AWS_ACCESS_KEY_ID","")
            secret=os.environ.get("AWS_SECRET_ACCESS_KEY","")
            session=os.environ.get("AWS_SESSION_TOKEN","")
            now=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            result=fetch_s3(opts.host,opts.key,opts.version,opts.region,opts.kind,access,secret,session,now)
        else:
            pem=opts.clock_pem.read_text(encoding="utf-8")
            result=clock_audit(json.loads(opts.claims.read_bytes()),pem,
                               opts.pinned_key_sha256,json.loads(opts.heads.read_bytes()))
    except (OSError,ValueError,TypeError,KeyError,ET.ParseError) as e:
        result={**HOLD,"reasons":["INPUT_REJECTED:"+type(e).__name__+":"+str(e)[:80]]}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 1
if __name__=="__main__":raise SystemExit(main())
