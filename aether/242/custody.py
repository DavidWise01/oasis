#!/usr/bin/env python3
"""AETHER-242: read-only external custody/time/nonce claim reconciliation."""
import argparse,hashlib,json,re
from datetime import datetime
from pathlib import Path
SCHEMA="AETHER-242/custody-and-time-v1"
HOLD={"operational_authority":"HOLD","physical_act_allowed":False,
"physical_qualification_percent":0,"independent_custody_authenticated":False}
def canonical(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def sha(x):return hashlib.sha256(canonical(x)).hexdigest()
def instant(x):
    if not isinstance(x,str) or not x.endswith("Z"):raise ValueError("INVALID_UTC")
    t=datetime.fromisoformat(x.replace("Z","+00:00"))
    if t.utcoffset().total_seconds()!=0:raise ValueError("INVALID_OFFSET")
    return t
def assess(b):
    reasons=[];obs={"receipts":[]}
    if not isinstance(b,dict):return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED","reasons":["BUNDLE_INVALID"],"observed":obs,**HOLD}
    keys=b.get("key_custody");times=b.get("time_receipts");nonces=b.get("nonce_consumptions");pin=b.get("pin")
    if not isinstance(keys,list) or len(keys)!=3:reasons.append("THREE_KEY_CUSTODIANS_REQUIRED");keys=[]
    if not isinstance(times,list) or len(times)!=3:reasons.append("THREE_TIME_RECEIPTS_REQUIRED");times=[]
    if not isinstance(nonces,list) or len(nonces)!=3:reasons.append("THREE_NONCE_RECEIPTS_REQUIRED");nonces=[]
    if not isinstance(pin,dict):reasons.append("PIN_MISSING");pin={}
    if not isinstance(pin.get("manifest_sha256"),str) or not re.fullmatch("[0-9a-f]{64}",pin["manifest_sha256"]):reasons.append("PIN_HASH_INVALID")
    if not isinstance(pin.get("source_commit"),str) or not re.fullmatch("[0-9a-f]{40}",pin["source_commit"]):reasons.append("PIN_COMMIT_INVALID")
    if not isinstance(pin.get("challenge_id"),str) or not pin["challenge_id"]:reasons.append("PIN_CHALLENGE_INVALID")
    try:start=instant(pin["run_started_at"])
    except (ValueError,KeyError,TypeError,OverflowError):start=None;reasons.append("RUN_START_TIME_INVALID")
    controllers=set()
    for r in keys:
        if not isinstance(r,dict) or set(r)!={"controller","key_fingerprint_sha256","enrollment_sha256","custody_claim_sha256"}:
            reasons.append("KEY_RECORD_SCHEMA_INVALID");continue
        c=r["controller"]
        if not isinstance(c,str) or not c or len(c)>128:reasons.append("CONTROLLER_INVALID");continue
        if c in controllers:reasons.append("SHARED_CONTROLLER_LABEL")
        controllers.add(c)
        if any(not isinstance(r[k],str) or not re.fullmatch("[0-9a-f]{64}",r[k]) for k in ("key_fingerprint_sha256","enrollment_sha256","custody_claim_sha256")):
            reasons.append("KEY_CUSTODY_HASH_INVALID")
        obs["receipts"].append({"kind":"key","controller":c,"record_sha256":sha(r)})
    time_roots=set()
    for r in times:
        if not isinstance(r,dict) or set(r)!={"controller","challenge_id","manifest_sha256","observed_at","receipt_sha256"}:
            reasons.append("TIME_RECORD_SCHEMA_INVALID");continue
        c=r["controller"]
        if c not in controllers:reasons.append("TIME_CONTROLLER_NOT_ENROLLED")
        if c in time_roots:reasons.append("DUPLICATE_TIME_CONTROLLER")
        time_roots.add(c)
        if r["challenge_id"]!=pin.get("challenge_id") or r["manifest_sha256"]!=pin.get("manifest_sha256"):reasons.append("TIME_BINDING_MISMATCH")
        if r["receipt_sha256"]!=sha({k:v for k,v in r.items() if k!="receipt_sha256"}):reasons.append("TIME_RECEIPT_DIGEST_MISMATCH")
        try:
            t=instant(r["observed_at"])
            if start is not None and t>start:reasons.append("POST_RUN_TIME_CLAIM")
        except (ValueError,TypeError,OverflowError):reasons.append("TIME_CLAIM_INVALID")
        obs["receipts"].append({"kind":"time","controller":c,"record_sha256":sha(r)})
    used=set();nonce_roots=set()
    for r in nonces:
        if not isinstance(r,dict) or set(r)!={"controller","challenge_id","nonce","run_id","previous_head_sha256","new_head_sha256","consumption_sha256"}:
            reasons.append("NONCE_RECORD_SCHEMA_INVALID");continue
        c=r["controller"]
        if c not in controllers:reasons.append("NONCE_CONTROLLER_NOT_ENROLLED")
        if c in nonce_roots:reasons.append("DUPLICATE_NONCE_CONTROLLER")
        nonce_roots.add(c)
        if r["challenge_id"]!=pin.get("challenge_id"):reasons.append("NONCE_CHALLENGE_MISMATCH")
        n=r["nonce"]
        if not isinstance(n,str) or not n or len(n)>128:reasons.append("NONCE_INVALID")
        if n in used:reasons.append("NONCE_REPLAY")
        used.add(n)
        if type(r["run_id"]) is not int or r["run_id"]<=0 or r["run_id"]!=pin.get("run_id"):reasons.append("NONCE_RUN_MISMATCH")
        if any(not isinstance(r[k],str) or not re.fullmatch("[0-9a-f]{64}",r[k]) for k in ("previous_head_sha256","new_head_sha256")):reasons.append("NONCE_HEAD_INVALID")
        if r["consumption_sha256"]!=sha({k:v for k,v in r.items() if k!="consumption_sha256"}):reasons.append("NONCE_RECEIPT_DIGEST_MISMATCH")
        obs["receipts"].append({"kind":"nonce","controller":c,"record_sha256":sha(r)})
    if len(time_roots)!=3:reasons.append("THREE_TIME_CONTROLLERS_NOT_CONFIRMED")
    if len(nonce_roots)!=3:reasons.append("THREE_NONCE_CONTROLLERS_NOT_CONFIRMED")
    reasons.extend(["EXTERNAL_SIGNER_ANCESTRY_AND_TRUSTED_TIME_NOT_AUTHENTICATED","EXTERNAL_IMMUTABLE_NONCE_CUSTODY_NOT_AUTHENTICATED"])
    return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED","reasons":sorted(set(reasons)),"observed":obs,**HOLD}
def main():
    p=argparse.ArgumentParser();p.add_argument("--bundle",type=Path,required=True);p.add_argument("--out",type=Path);a=p.parse_args()
    try:
        raw=a.bundle.read_bytes()
        if len(raw)>1024*1024:raise ValueError("INPUT_TOO_LARGE")
        result=assess(json.loads(raw))
    except (ValueError,OSError,TypeError) as e:
        result={"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED","reasons":["INPUT_INVALID:"+type(e).__name__],"observed":{},**HOLD}
    rendered=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(rendered,encoding="utf-8")
    print(rendered,end="");return 1
if __name__=="__main__":raise SystemExit(main())
