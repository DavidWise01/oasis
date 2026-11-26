#!/usr/bin/env python3
"""AETHER-243: read-only external evidence byte acquisition; never certifies custody."""
import argparse,hashlib,ipaddress,json
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request,build_opener,HTTPRedirectHandler
SCHEMA="AETHER-243/external-acquisition-v1"
HOLD={"operational_authority":"HOLD","physical_qualification_percent":0,"physical_act_allowed":False,"independent_custody_authenticated":False}
MAX_BYTES=1048576
def sha(b):return hashlib.sha256(b).hexdigest()
def locator(url,hosts):
    if not isinstance(url,str) or len(url)>2048:raise ValueError("URL_INVALID")
    p=urlsplit(url);host=(p.hostname or "").lower()
    if p.scheme!="https" or host not in hosts or not host:raise ValueError("HOST_NOT_PINNED")
    if p.username or p.password or p.fragment or p.port not in (None,443):raise ValueError("URL_AUTH_OR_PORT")
    try:
        ip=ipaddress.ip_address(host)
        if not ip.is_global:raise ValueError("NONPUBLIC_IP")
    except ValueError as e:
        if str(e)=="NONPUBLIC_IP":raise
    return host
class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,url):
        raise ValueError("REDIRECT_REQUIRES_NEW_PIN")
def retrieve(url):
    opener=build_opener(NoRedirect)
    req=Request(url,headers={"User-Agent":"AETHER-243-read-only","Accept":"application/octet-stream"})
    with opener.open(req,timeout=12) as response:
        if response.geturl()!=url:raise ValueError("URL_CHANGED")
        length=response.headers.get("Content-Length")
        if length is not None and int(length)>MAX_BYTES:raise ValueError("SIZE_LIMIT")
        result=response.read(MAX_BYTES+1)
    if len(result)>MAX_BYTES:raise ValueError("SIZE_LIMIT")
    return result
def assess(config,fetch=retrieve):
    observed=[];reasons=[]
    if not isinstance(config,dict):return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED","reasons":["CONFIG_INVALID"],"observed":observed,**HOLD}
    hosts=config.get("allowed_hosts");sources=config.get("sources")
    if not isinstance(hosts,list) or not hosts or any(not isinstance(h,str) or not h or h!=h.lower() for h in hosts):
        reasons.append("HOST_PINS_INVALID");hosts=[]
    if not isinstance(sources,list) or not 1<=len(sources)<=8:
        reasons.append("SOURCE_SET_INVALID");sources=[]
    ids=set();controllers=set();hashes=set()
    for s in sources:
        if not isinstance(s,dict) or set(s)!={"source_id","url","controller_claim","expected_sha256"}:
            reasons.append("SOURCE_SCHEMA_INVALID");continue
        sid=s["source_id"];controller=s["controller_claim"]
        if not isinstance(sid,str) or not sid or sid in ids:
            reasons.append("SOURCE_ID_DUPLICATE_OR_INVALID");continue
        ids.add(sid)
        if not isinstance(controller,str) or not controller:
            reasons.append("CONTROLLER_CLAIM_INVALID");continue
        if controller in controllers:reasons.append("SHARED_DECLARED_CONTROLLER")
        controllers.add(controller)
        try:
            host=locator(s["url"],set(hosts))
            expected=s["expected_sha256"]
            if not isinstance(expected,str) or len(expected)!=64 or any(c not in "0123456789abcdef" for c in expected):
                raise ValueError("DIGEST_INVALID")
            raw=fetch(s["url"])
            if not isinstance(raw,bytes) or len(raw)>MAX_BYTES:raise ValueError("BODY_INVALID")
            actual=sha(raw)
            if actual!=expected:reasons.append("RESPONSE_DIGEST_MISMATCH")
            if actual in hashes:reasons.append("DUPLICATE_EVIDENCE_BYTES")
            hashes.add(actual)
            observed.append({"source_id":sid,"host":host,"controller_claim":controller,
                             "response_sha256":actual,"response_bytes":len(raw),"digest_match":actual==expected})
        except Exception as e:
            reasons.append("FETCH_OR_VALIDATION_FAILED:"+type(e).__name__)
            observed.append({"source_id":sid,"state":"UNVERIFIED"})
    if len(controllers)<3:reasons.append("THREE_CLAIMED_CONTROLLERS_NOT_OBSERVED")
    reasons+=["CONTROLLER_ANCESTRY_AND_EXTERNAL_CUSTODY_UNAUTHENTICATED",
              "REMOTE_CLOCK_AND_PHYSICAL_ORIGIN_UNAUTHENTICATED"]
    return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
            "reasons":sorted(set(reasons)),"observed":observed,**HOLD}
def main():
    p=argparse.ArgumentParser();p.add_argument("--config",type=Path,required=True);p.add_argument("--out",type=Path);a=p.parse_args()
    try:
        raw=a.config.read_bytes()
        if len(raw)>65536:raise ValueError("CONFIG_TOO_LARGE")
        result=assess(json.loads(raw))
    except (OSError,ValueError,UnicodeError) as e:
        result={"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
                "reasons":["CONFIG_UNAVAILABLE:"+type(e).__name__],"observed":[],**HOLD}
    output=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(output,encoding="utf-8")
    print(output,end="");return 1
if __name__=="__main__":raise SystemExit(main())
