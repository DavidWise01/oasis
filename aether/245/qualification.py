#!/usr/bin/env python3
"""AETHER-245: offline signature qualification. No networking or ACT authority."""
import argparse, base64, hashlib, json, re
from pathlib import Path
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

HOLD={"operational_authority":"HOLD","physical_act_allowed":False,
      "physical_qualification_percent":0,"independent_custody_authenticated":False,
      "network_isolation_measured":False}
SCHEMA="AETHER-245/offline-qualification-v1"

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()

def verify_signature(pem,message,signature):
    try:
        key=serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key,Ed25519PublicKey):return False
        key.verify(signature,message)
        return True
    except (InvalidSignature,ValueError,TypeError,UnicodeError):
        return False

def assess(bundle):
    reasons=[];observed=[]
    if not isinstance(bundle,dict):
        return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED","reasons":["BUNDLE_INVALID"],"observed":[],**HOLD}
    records=bundle.get("artifacts");keys=bundle.get("independently_pinned_keys")
    consumed=bundle.get("consumed_nonces");challenge=bundle.get("challenge")
    if not isinstance(records,list) or len(records)!=3:
        reasons.append("EXACT_THREE_ARTIFACTS_REQUIRED");records=[]
    if not isinstance(keys,dict):reasons.append("PUBLIC_KEY_PINS_MISSING");keys={}
    if not isinstance(consumed,list) or any(not isinstance(n,str) for n in consumed):
        reasons.append("NONCE_LEDGER_INVALID");consumed=[]
    if not isinstance(challenge,dict):reasons.append("CHALLENGE_MISSING");challenge={}
    nonces=set();controllers=set();key_ids=set();body_hashes=set();bindings=set()
    expected={"schema","challenge_id","run_id","source_commit","nonce",
              "controller_claim","body_sha256","source_id"}
    for r in records:
        if not isinstance(r,dict) or set(r)!={"body_b64","statement","signature_b64","key_id"}:
            reasons.append("ENVELOPE_INVALID");continue
        s=r["statement"];kid=r["key_id"]
        if not isinstance(s,dict) or set(s)!=expected or s.get("schema")!="AETHER-245/signed-byte-statement-v1":
            reasons.append("STATEMENT_SCHEMA_INVALID");continue
        if not isinstance(kid,str) or not kid or kid in key_ids:reasons.append("KEY_REUSED_OR_INVALID")
        key_ids.add(kid)
        c=s["controller_claim"];n=s["nonce"]
        if not isinstance(c,str) or not c or c in controllers:reasons.append("CONTROLLER_REUSED_OR_INVALID")
        if isinstance(c,str):controllers.add(c)
        if not isinstance(n,str) or not n or n in nonces or n in consumed:reasons.append("NONCE_REPLAY_OR_INVALID")
        if isinstance(n,str):nonces.add(n)
        if s["challenge_id"]!=challenge.get("challenge_id") or s["run_id"]!=challenge.get("run_id") or s["source_commit"]!=challenge.get("source_commit"):
            reasons.append("CHALLENGE_BINDING_MISMATCH")
        if type(s["run_id"]) is not int or s["run_id"]<=0 or not isinstance(s["source_commit"],str) or not re.fullmatch("[0-9a-f]{40}",s["source_commit"]):
            reasons.append("RUN_OR_SOURCE_INVALID")
        bindings.add((str(s["challenge_id"]),str(s["run_id"]),str(s["source_commit"])))
        try:
            body=base64.b64decode(r["body_b64"],validate=True)
            sig=base64.b64decode(r["signature_b64"],validate=True)
            if len(body)>1048576 or len(sig)!=64:raise ValueError("SIZE")
            body_hash=hashlib.sha256(body).hexdigest()
            if body_hash!=s["body_sha256"]:reasons.append("BODY_DIGEST_MISMATCH")
            if body_hash in body_hashes:reasons.append("DUPLICATE_BODY")
            body_hashes.add(body_hash)
        except (ValueError,TypeError):
            reasons.append("BODY_OR_SIGNATURE_INVALID");continue
        k=keys.get(kid)
        if not isinstance(k,dict) or k.get("controller_claim")!=c or not isinstance(k.get("public_key_pem"),str):
            reasons.append("PUBLIC_KEY_NOT_PINNED");continue
        valid=verify_signature(k["public_key_pem"],canonical(s),sig)
        if not valid:reasons.append("SIGNATURE_INVALID")
        observed.append({"source_id":s["source_id"],"key_id":kid,"signature_valid":valid,
                         "body_sha256":body_hash,"body_bytes":len(body),
                         "statement_sha256":hashlib.sha256(canonical(s)).hexdigest()})
    if len(bindings)!=1:reasons.append("CROSS_SOURCE_BINDING_MISMATCH")
    if len(controllers)<3:reasons.append("THREE_CONTROLLER_LABELS_NOT_PRESENT")
    reasons+=["EXTERNAL_KEY_CUSTODY_UNAUTHENTICATED",
              "NETWORK_ISOLATION_NOT_MEASURED","EXTERNAL_NONCE_LEDGER_UNAUTHENTICATED"]
    return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
            "reasons":sorted(set(reasons)),"observed":observed,**HOLD}
def main():
    p=argparse.ArgumentParser();p.add_argument("--snapshot",type=Path,required=True)
    p.add_argument("--out",type=Path);a=p.parse_args()
    try:
        raw=a.snapshot.read_bytes()
        if len(raw)>4*1048576:raise ValueError("INPUT_TOO_LARGE")
        result=assess(json.loads(raw))
    except (ValueError,OSError,TypeError) as e:
        result={"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED",
                "reasons":["INPUT_INVALID:"+type(e).__name__],"observed":[],**HOLD}
    output=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if a.out:a.out.write_text(output,encoding="utf-8")
    print(output,end="");return 1
if __name__=="__main__":raise SystemExit(main())
