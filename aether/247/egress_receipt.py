#!/usr/bin/env python3
"""AETHER-247: offline signed egress-observation adjudicator, no network access."""
import argparse,base64,hashlib,json,re
from pathlib import Path
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
SCHEMA="AETHER-247/egress-receipt-v1"
CATEGORIES={"loopback","private","link_local","metadata","redirect","dns_rebind"}
HOLD={"operational_authority":"HOLD","physical_qualification_percent":0,
"physical_act_allowed":False,"independent_custody_authenticated":False,
"network_isolation_independently_verified":False}
def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def digest(x):return hashlib.sha256(canonical(x)).hexdigest()
def verify_signature(pem,message,sig):
    try:
        key=serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key,Ed25519PublicKey) or len(sig)!=64:return False
        key.verify(sig,message);return True
    except (InvalidSignature,ValueError,TypeError,UnicodeError):return False
def assess(bundle,verifier=verify_signature):
    errors=[];observed=[]
    if not isinstance(bundle,dict):
        return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED","reasons":["BUNDLE_INVALID"],"observed":[],**HOLD}
    measurements=bundle.get("measurements")
    receipts=bundle.get("receipts")
    pins=bundle.get("public_key_pins")
    consumed=bundle.get("consumed_challenges")
    if not isinstance(measurements,list) or len(measurements)!=6:
        errors.append("SIX_MEASUREMENTS_REQUIRED");measurements=[]
    if not isinstance(receipts,list) or len(receipts)!=3:
        errors.append("THREE_SIGNED_RECEIPTS_REQUIRED");receipts=[]
    if not isinstance(pins,dict):errors.append("TRUST_PINS_MISSING");pins={}
    if not isinstance(consumed,list) or any(not isinstance(v,str) for v in consumed):
        errors.append("CONSUMED_LEDGER_INVALID");consumed=[]
    if len(consumed)!=len(set(consumed)):errors.append("CONSUMED_LEDGER_DUPLICATE")
    challenge=bundle.get("challenge_id");run=bundle.get("run_id");head=bundle.get("source_commit")
    if not isinstance(challenge,str) or not challenge or len(challenge)>128:errors.append("CHALLENGE_ID_INVALID")
    if challenge in consumed:errors.append("CHALLENGE_REPLAY")
    if type(run) is not int or run<=0:errors.append("RUN_ID_INVALID")
    if not isinstance(head,str) or re.fullmatch("[0-9a-f]{40}",head) is None:errors.append("SOURCE_COMMIT_INVALID")
    if bundle.get("namespace_separated") is not True:errors.append("NETWORK_NAMESPACE_SEPARATION_NOT_RECORDED")
    if bundle.get("credential_free") is not True:errors.append("CREDENTIAL_FREE_NOT_RECORDED")
    categories=set()
    for m in measurements:
        if not isinstance(m,dict) or set(m)!={"category","outcome","errno","elapsed_ms"}:
            errors.append("MEASUREMENT_SCHEMA_INVALID");continue
        c=m["category"]
        if not isinstance(c,str) or c not in CATEGORIES or c in categories:
            errors.append("CATEGORY_DUPLICATE_OR_INVALID");continue
        categories.add(c)
        if m["outcome"]!="blocked":errors.append("EGRESS_DENIAL_FAILED")
        if type(m["errno"]) is not int or m["errno"]<0:errors.append("ERRNO_INVALID")
        if type(m["elapsed_ms"]) is not int or not 0<=m["elapsed_ms"]<=30000:errors.append("MEASUREMENT_DURATION_INVALID")
    if categories!=CATEGORIES:errors.append("DENIAL_CATEGORY_COVERAGE_INCOMPLETE")
    measurement_hash=digest(measurements)
    roots=set();keys=set();statement_hashes=set()
    for r in receipts:
        if not isinstance(r,dict) or set(r)!={"key_id","statement","signature_b64"}:
            errors.append("RECEIPT_ENVELOPE_INVALID");continue
        kid=r["key_id"];s=r["statement"]
        if not isinstance(kid,str) or not kid or kid in keys:
            errors.append("DUPLICATE_KEY_ID");continue
        keys.add(kid)
        if not isinstance(s,dict) or set(s)!={"schema","controller_root","challenge_id","run_id","source_commit","measurements_sha256","nonce"} or s.get("schema")!="AETHER-247/signed-observation-v1":
            errors.append("STATEMENT_SCHEMA_INVALID");continue
        root=s["controller_root"]
        if not isinstance(root,str) or not root or root in roots:errors.append("CONTROLLER_ROOT_DUPLICATE_OR_INVALID")
        roots.add(root)
        if s["challenge_id"]!=challenge or s["run_id"]!=run or s["source_commit"]!=head:
            errors.append("RECEIPT_RUN_BINDING_MISMATCH")
        if s["measurements_sha256"]!=measurement_hash:errors.append("MEASUREMENT_DIGEST_MISMATCH")
        nonce=s["nonce"]
        if not isinstance(nonce,str) or not nonce or len(nonce)>128 or nonce in consumed:errors.append("NONCE_REPLAY_OR_INVALID")
        sh=digest(s)
        if sh in statement_hashes:errors.append("DUPLICATE_STATEMENT")
        statement_hashes.add(sh)
        pin=pins.get(kid)
        if not isinstance(pin,dict) or pin.get("controller_root")!=root or not isinstance(pin.get("public_key_pem"),str):
            errors.append("TRUST_PIN_UNAVAILABLE");continue
        try:
            sig=base64.b64decode(r["signature_b64"],validate=True)
            good=len(sig)==64 and bool(verifier(pin["public_key_pem"],canonical(s),sig))
        except (ValueError,TypeError,UnicodeError):good=False
        if not good:errors.append("SIGNATURE_INVALID")
        observed.append({"key_id":kid,"controller_root_claim":root,
                         "statement_sha256":sh,"signature_valid":good})
    if len(roots)!=3:errors.append("THREE_ROOTS_NOT_OBSERVED")
    errors+=["SIGNER_CUSTODY_NOT_INDEPENDENTLY_AUTHENTICATED",
             "PROBE_TRANSPORT_AND_NETWORK_ENFORCEMENT_NOT_INDEPENDENTLY_OBSERVED",
             "EXTERNAL_CHALLENGE_LEDGER_NOT_AUTHENTICATED"]
    return {"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED","reasons":sorted(set(errors)),
            "observed":{"measurements_sha256":measurement_hash,"receipts":observed},**HOLD}
def main():
    p=argparse.ArgumentParser();p.add_argument("--bundle",type=Path,required=True);p.add_argument("--out",type=Path);a=p.parse_args()
    try:
        raw=a.bundle.read_bytes()
        if len(raw)>262144:raise ValueError("INPUT_TOO_LARGE")
        result=assess(json.loads(raw))
    except (ValueError,OSError,TypeError,UnicodeError) as e:
        result={"schema":SCHEMA,"verdict":"REJECT_OR_UNVERIFIED","reasons":["INPUT_INVALID:"+type(e).__name__],"observed":{},**HOLD}
    output=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(output,encoding="utf-8")
    print(output,end="");return 1
if __name__=="__main__":raise SystemExit(main())
