#!/usr/bin/env python3
"""AETHER-261-RS: offline signed export receipts and restart continuity HOLD gate."""
import argparse,base64,hashlib,json,re
from pathlib import Path

SCHEMA="AETHER-261/receipt-signatures-v1"
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_qualification_percent":0,"physical_act_allowed":False,
      "external_custody_verified":False,"independent_signer_ancestry_verified":False}
HEX64=re.compile(r"^[0-9a-f]{64}$")
HEX40=re.compile(r"^[0-9a-f]{40}$")
def canonical(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def sha(x):return hashlib.sha256(canonical(x)).hexdigest()
def verify_ed25519(public_pem,msg,signature):
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key=serialization.load_pem_public_key(public_pem.encode("ascii"))
        if not isinstance(key,Ed25519PublicKey) or len(signature)!=64:return False
        key.verify(signature,msg);return True
    except (ImportError,InvalidSignature,ValueError,TypeError,UnicodeError):return False
def snapshot_valid(exp):
    if not isinstance(exp,dict) or set(exp)!={"schema","head","events","attempts","export_sha256"}:
        return False
    if exp.get("schema")!="AETHER-260/receipt-export-v1":return False
    if not isinstance(exp.get("export_sha256"),str) or not HEX64.fullmatch(exp["export_sha256"]):return False
    if sha({k:v for k,v in exp.items() if k!="export_sha256"})!=exp["export_sha256"]:return False
    try:
        if not isinstance(exp["head"],dict) or type(exp["head"]["sequence"]) is not int:return False
        if not isinstance(exp["events"],list) or not isinstance(exp["attempts"],list):return False
        if len(exp["events"])>4096 or len(exp["attempts"])>4096:return False
        previous="0"*64
        for index,event in enumerate(exp["events"],1):
            if type(event["sequence"]) is not int or event["sequence"]!=index or event["previous_hash"]!=previous:return False
            previous=event["head_hash"]
        return exp["head"]=={"sequence":len(exp["events"]),"sha256":previous}
    except (KeyError,TypeError,ValueError):return False
def assess(bundle,verify=verify_ed25519):
    problems=[];observed={"verified_signatures":[]}
    if not isinstance(bundle,dict):return {**HOLD,"reasons":["BUNDLE_INVALID"],"observed":observed}
    challenge=bundle.get("challenge");before=bundle.get("before_export");after=bundle.get("after_export")
    receipts=bundle.get("receipts");pins=bundle.get("externally_claimed_key_pins")
    prior=bundle.get("consumed_nonces");seen=bundle.get("seen_export_digests")
    if not isinstance(challenge,dict) or set(challenge)!={"challenge_id","nonce","run_id","source_commit","host_id"}:
        problems.append("CHALLENGE_SCHEMA_INVALID");challenge={}
    for name in ("challenge_id","nonce","host_id"):
        v=challenge.get(name)
        if not isinstance(v,str) or not v or len(v)>128:problems.append("CHALLENGE_FIELD_INVALID")
    if type(challenge.get("run_id")) is not int or challenge["run_id"]<=0:problems.append("RUN_INVALID")
    commit=challenge.get("source_commit")
    if not isinstance(commit,str) or not HEX40.fullmatch(commit):problems.append("COMMIT_INVALID")
    if not isinstance(prior,list) or any(not isinstance(x,str) for x in prior):
        problems.append("NONCE_LEDGER_INVALID");prior=[]
    if not isinstance(seen,list) or any(not isinstance(x,str) for x in seen):
        problems.append("EXPORT_LEDGER_INVALID");seen=[]
    if len(prior)!=len(set(prior)) or len(seen)!=len(set(seen)):problems.append("HISTORY_DUPLICATION")
    if challenge.get("nonce") in prior:problems.append("CHALLENGE_REPLAY")
    if not snapshot_valid(before):problems.append("BEFORE_EXPORT_INVALID")
    if not snapshot_valid(after):problems.append("AFTER_EXPORT_INVALID")
    if snapshot_valid(before) and snapshot_valid(after):
        if len(after["events"])<len(before["events"]) or after["events"][:len(before["events"])]!=before["events"]:
            problems.append("RESTART_HISTORY_REWRITTEN_OR_TRUNCATED")
        if before["export_sha256"]==after["export_sha256"]:
            problems.append("EXPORT_UNCHANGED_ACROSS_RESTART")
    for exp in (before,after):
        if isinstance(exp,dict) and exp.get("export_sha256") in seen:
            problems.append("EXPORT_DIGEST_REPLAY")
    before_hash=before.get("export_sha256") if isinstance(before,dict) else None
    after_hash=after.get("export_sha256") if isinstance(after,dict) else None
    statement={"schema":"AETHER-261/witness-v1","challenge":challenge,
               "before_sha256":before_hash,"after_sha256":after_hash}
    observed["binding_sha256"]=sha(statement)
    if not isinstance(receipts,list) or len(receipts)!=3:
        problems.append("THREE_RECEIPTS_REQUIRED");receipts=[]
    if not isinstance(pins,dict):
        problems.append("PINNED_PUBLIC_KEYS_UNAVAILABLE");pins={}
    roots=set();keys=set();nonces=set()
    for r in receipts:
        if not isinstance(r,dict) or set(r)!={"key_id","controller_claim","nonce","signature_b64"}:
            problems.append("RECEIPT_SCHEMA_INVALID");continue
        kid=r["key_id"];root=r["controller_claim"];nonce=r["nonce"]
        if not isinstance(kid,str) or not kid or kid in keys:
            problems.append("KEY_DUPLICATE_OR_INVALID");continue
        keys.add(kid)
        if not isinstance(root,str) or not root or root in roots:problems.append("CONTROLLER_DUPLICATE_OR_INVALID")
        if isinstance(root,str):roots.add(root)
        if not isinstance(nonce,str) or not nonce or nonce in nonces or nonce in prior or nonce==challenge.get("nonce"):
            problems.append("WITNESS_NONCE_REPLAY")
        if isinstance(nonce,str):nonces.add(nonce)
        pin=pins.get(kid)
        if not isinstance(pin,dict) or pin.get("controller_claim")!=root or not isinstance(pin.get("public_key_pem"),str):
            problems.append("KEY_PIN_MISSING");continue
        signed={**statement,"controller_claim":root,"witness_nonce":nonce}
        try:
            sig=base64.b64decode(r["signature_b64"],validate=True)
            valid=len(sig)==64 and bool(verify(pin["public_key_pem"],canonical(signed),sig))
        except (ValueError,TypeError,UnicodeError):valid=False
        if not valid:problems.append("SIGNATURE_INVALID")
        observed["verified_signatures"].append({"key_id":kid,"controller_claim":root,"valid":valid})
    if len(roots)!=3:problems.append("THREE_DISTINCT_CONTROLLER_LABELS_REQUIRED")
    problems.extend(["KEY_CUSTODY_AND_ANCESTRY_NOT_INDEPENDENTLY_VERIFIED",
                     "EXTERNAL_NONCE_AND_EXPORT_LEDGER_NOT_SEALED",
                     "SIGNED_EXPORTS_NOT_PROOF_OF_EXTERNAL_ATOMICITY"])
    return {**HOLD,"reasons":sorted(set(problems)),"observed":observed}
def main():
    p=argparse.ArgumentParser();p.add_argument("--bundle",type=Path,required=True);p.add_argument("--out",type=Path);args=p.parse_args()
    try:
        raw=args.bundle.read_bytes()
        if len(raw)>4*1024*1024:raise ValueError("OVERSIZE")
        result=assess(json.loads(raw))
    except (OSError,ValueError,TypeError,UnicodeError) as e:
        result={**HOLD,"reasons":["INPUT_REJECTED:"+type(e).__name__]}
    output=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.out:args.out.write_text(output,encoding="utf-8")
    print(output,end="");return 1
if __name__=="__main__":raise SystemExit(main())
