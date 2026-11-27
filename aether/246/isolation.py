#!/usr/bin/env python3
"""AETHER-246-RS. Offline isolation telemetry review; never certifies custody."""
import argparse,hashlib,ipaddress,json
from pathlib import Path
from urllib.parse import urlsplit
SCHEMA="AETHER-246/egress-isolation-v1"
HOLD={"operational_authority":"HOLD","physical_act_allowed":False,
"physical_qualification_percent":0,"independent_custody_authenticated":False,
"network_isolation_independently_verified":False}
CREDENTIAL_KEYS={"GITHUB_TOKEN","GH_TOKEN","AWS_SECRET_ACCESS_KEY","AWS_ACCESS_KEY_ID","GOOGLE_APPLICATION_CREDENTIALS","AZURE_CLIENT_SECRET","SSH_AUTH_SOCK"}
DENIALS={"loopback","private","link_local","metadata","redirect","dns_rebind"}
def checked_url(raw,hosts):
    if not isinstance(raw,str) or not raw or len(raw)>2048:raise ValueError("URL_INVALID")
    try:
        p=urlsplit(raw);h=p.hostname;port=p.port
    except ValueError as e:raise ValueError("URL_INVALID") from e
    if p.scheme!="https" or not h or p.username or p.password or p.fragment:raise ValueError("URL_NOT_CREDENTIAL_FREE_HTTPS")
    if port not in (None,443) or h.lower() not in hosts:raise ValueError("HOST_OR_PORT_NOT_PINNED")
    try:ip=ipaddress.ip_address(h)
    except ValueError:return h.lower()
    if not ip.is_global:raise ValueError("NONPUBLIC_LITERAL_IP")
    return h.lower()
def assess(bundle):
    reasons=[];observed={"denials":[],"acquisitions":[]}
    if not isinstance(bundle,dict):return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED","reasons":["BUNDLE_INVALID"],"observed":observed,**HOLD}
    hosts=bundle.get("allowed_hosts")
    if not isinstance(hosts,list) or not hosts or any(not isinstance(h,str) or not h or h!=h.lower() for h in hosts) or len(set(hosts))!=len(hosts):
        reasons.append("HOST_LIST_INVALID");hosts=[]
    env=bundle.get("acquirer_environment")
    if not isinstance(env,dict):reasons.append("ENVIRONMENT_MISSING");env={}
    names=set(env)
    if names&CREDENTIAL_KEYS or any(isinstance(k,str) and ("TOKEN" in k.upper() or "SECRET" in k.upper()) for k in names):
        reasons.append("CREDENTIAL_EXPOSURE")
    for k,reason in [("credential_free","CREDENTIAL_FREE_NOT_CONFIRMED"),
                     ("read_only_filesystem","READ_ONLY_FILESYSTEM_NOT_CONFIRMED"),
                     ("isolated_network_namespace","NETWORK_NAMESPACE_NOT_CONFIRMED")]:
        if env.get(k) is not True:reasons.append(reason)
    trials=bundle.get("denial_trials")
    if not isinstance(trials,list) or len(trials)>32:reasons.append("DENIAL_TRIALS_INVALID");trials=[]
    seen=set()
    for t in trials:
        if not isinstance(t,dict) or set(t)!={"category","blocked","observer"}:
            reasons.append("DENIAL_TRIAL_SCHEMA_INVALID");continue
        c=t["category"]
        if not isinstance(c,str) or c in seen:reasons.append("DENIAL_CATEGORY_DUPLICATE_OR_INVALID");continue
        seen.add(c)
        if t["blocked"] is not True:reasons.append("EGRESS_DENIAL_NOT_OBSERVED")
        if not isinstance(t["observer"],str) or not t["observer"]:reasons.append("DENIAL_OBSERVER_MISSING")
        observed["denials"].append({"category":c,"blocked_claim":t["blocked"] is True})
    if not DENIALS.issubset(seen):reasons.append("REQUIRED_DENIAL_TRIALS_MISSING")
    acquisitions=bundle.get("acquisitions")
    if not isinstance(acquisitions,list) or not 1<=len(acquisitions)<=8:reasons.append("ACQUISITION_SET_INVALID");acquisitions=[]
    for a in acquisitions:
        if not isinstance(a,dict) or set(a)!={"url","bytes","sha256"}:reasons.append("ACQUISITION_SCHEMA_INVALID");continue
        try:
            host=checked_url(a["url"],set(hosts))
            if type(a["bytes"]) is not int or not 0<a["bytes"]<=1048576:raise ValueError("ACQUISITION_LENGTH_INVALID")
            v=a["sha256"]
            if not isinstance(v,str) or len(v)!=64 or any(x not in "0123456789abcdef" for x in v):raise ValueError("ACQUISITION_DIGEST_INVALID")
            observed["acquisitions"].append({"host":host,"bytes":a["bytes"],"sha256":v})
        except (ValueError,TypeError,KeyError) as e:reasons.append("ACQUISITION_INVALID:"+str(e))
    reasons+=["NETWORK_TELEMETRY_NOT_INDEPENDENTLY_ATTESTED",
              "DNS_PINNING_AND_EGRESS_ENFORCEMENT_NOT_MEASURED_BY_THIS_TOOL",
              "EXTERNAL_CUSTODY_NOT_AUTHENTICATED"]
    return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
            "reasons":sorted(set(reasons)),"observed":observed,**HOLD}
def main():
    p=argparse.ArgumentParser();p.add_argument("--bundle",type=Path,required=True);p.add_argument("--out",type=Path);a=p.parse_args()
    try:
        raw=a.bundle.read_bytes()
        if len(raw)>262144:raise ValueError("INPUT_TOO_LARGE")
        result=assess(json.loads(raw))
    except (OSError,ValueError,UnicodeError) as e:
        result={"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED","reasons":["INPUT_INVALID:"+type(e).__name__],"observed":{},**HOLD}
    rendered=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(rendered,encoding="utf-8")
    print(rendered,end="");return 1
if __name__=="__main__":raise SystemExit(main())
