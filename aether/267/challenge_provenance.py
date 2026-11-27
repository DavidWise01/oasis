#!/usr/bin/env python3
"""AETHER-267-RS: challenge provenance, self-issuance and ancestry HOLD gate.

Read-only: verifies supplied evidence, never grants external custody or ACT.
"""
import argparse,base64,hashlib,json,re
from pathlib import Path

SCHEMA="AETHER-267/challenge-provenance-v1"
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "independent_challenge_custody_verified":False,
      "independent_transport_ancestry_verified":False}
H40=re.compile("^[0-9a-f]{40}$")
H64=re.compile("^[0-9a-f]{64}$")

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def sha(x):
    return hashlib.sha256(canon(x)).hexdigest()
def ed25519(pem,msg,sig):
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key=serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key,Ed25519PublicKey) or len(sig)!=64:return False
        key.verify(sig,msg);return True
    except (ImportError,InvalidSignature,TypeError,ValueError,UnicodeError):return False

def ancestors(start,graph):
    seen=set();active=set()
    def walk(n):
        if not isinstance(n,str) or not n or len(n)>128:raise ValueError("ANCESTRY_NAME_INVALID")
        if n in active:raise ValueError("ANCESTRY_CYCLE")
        if n in seen:return
        if n not in graph:raise ValueError("ANCESTRY_NODE_MISSING")
        parents=graph[n]
        if not isinstance(parents,list) or len(parents)>16:raise ValueError("ANCESTRY_PARENTS_INVALID")
        active.add(n);seen.add(n)
        if len(seen)>256:raise ValueError("ANCESTRY_TOO_LARGE")
        for p in parents:walk(p)
        active.remove(n)
    walk(start)
    return seen

def assess(bundle,verify=ed25519):
    issues=[];observed={"transport_signatures":[]}
    if not isinstance(bundle,dict):
        return {**HOLD,"reasons":["BUNDLE_INVALID"],"observed":observed}
    challenge=bundle.get("challenge")
    issuance=bundle.get("issuance_receipt")
    pin=bundle.get("issuance_key_pin")
    transports=bundle.get("transport_receipts")
    graph=bundle.get("controller_ancestry")
    keys=bundle.get("transport_key_pins")
    consumed=bundle.get("previously_consumed_nonces")
    if not isinstance(challenge,dict) or set(challenge)!={"challenge_id","nonce","run_id","source_commit","resource_url","expected_body_sha256"}:
        issues.append("CHALLENGE_SCHEMA_INVALID");challenge={}
    if type(challenge.get("run_id")) is not int or challenge["run_id"]<=0:issues.append("RUN_INVALID")
    if not isinstance(challenge.get("source_commit"),str) or not H40.fullmatch(challenge["source_commit"]):
        issues.append("COMMIT_INVALID")
    if not isinstance(challenge.get("expected_body_sha256"),str) or not H64.fullmatch(challenge["expected_body_sha256"]):
        issues.append("BODY_PIN_INVALID")
    for field in ("challenge_id","nonce","resource_url"):
        v=challenge.get(field)
        if not isinstance(v,str) or not v or len(v)>2048:issues.append("CHALLENGE_FIELD_INVALID")
    if not isinstance(consumed,list) or any(not isinstance(n,str) for n in consumed):
        issues.append("NONCE_HISTORY_INVALID");consumed=[]
    if len(set(consumed))!=len(consumed):issues.append("NONCE_HISTORY_DUPLICATED")
    if challenge.get("nonce") in consumed:issues.append("CHALLENGE_ALREADY_CONSUMED")
    if not isinstance(issuance,dict) or set(issuance)!={"custodian_id","controller_id","key_id","challenge_sha256","issuance_nonce","signature_b64"}:
        issues.append("ISSUANCE_RECEIPT_SCHEMA_INVALID");issuance={}
    if issuance.get("challenge_sha256")!=sha(challenge):
        issues.append("ISSUANCE_CHALLENGE_MISMATCH")
    issue_nonce=issuance.get("issuance_nonce")
    if not isinstance(issue_nonce,str) or not issue_nonce or issue_nonce in consumed or issue_nonce==challenge.get("nonce"):
        issues.append("ISSUANCE_NONCE_REPLAY")
    issue_stmt={"schema":SCHEMA,"custodian_id":issuance.get("custodian_id"),
                "controller_id":issuance.get("controller_id"),
                "challenge_sha256":sha(challenge),"issuance_nonce":issue_nonce}
    if not isinstance(pin,dict) or pin.get("key_id")!=issuance.get("key_id") or pin.get("controller_id")!=issuance.get("controller_id") or not isinstance(pin.get("public_key_pem"),str):
        issues.append("ISSUANCE_PIN_INVALID")
        issue_valid=False
    else:
        try:
            issue_valid=bool(verify(pin["public_key_pem"],canon(issue_stmt),
                                    base64.b64decode(issuance["signature_b64"],validate=True)))
        except (ValueError,TypeError,UnicodeError):issue_valid=False
        if not issue_valid:issues.append("ISSUANCE_SIGNATURE_INVALID")
    observed["issuance_signature_valid"]=issue_valid
    if not isinstance(graph,dict):issues.append("ANCESTRY_GRAPH_INVALID");graph={}
    try:issuer_family=ancestors(issuance.get("controller_id"),graph)
    except ValueError as error:issues.append(str(error));issuer_family=set()
    if not isinstance(keys,dict):issues.append("TRANSPORT_PINS_INVALID");keys={}
    if not isinstance(transports,list) or len(transports)!=3:
        issues.append("THREE_TRANSPORT_RECEIPTS_REQUIRED");transports=[]
    families=[];ids=set();nonces=set();keyids=set()
    for item in transports:
        required={"session_id","session_nonce","source_id","controller_id","key_id",
                  "challenge_sha256","body_sha256","signature_b64"}
        if not isinstance(item,dict) or set(item)!=required:
            issues.append("TRANSPORT_RECEIPT_SCHEMA_INVALID");continue
        sid=item["session_id"];nonce=item["session_nonce"];kid=item["key_id"]
        if not isinstance(sid,str) or not sid or sid in ids:issues.append("SESSION_ID_REPLAY")
        if isinstance(sid,str):ids.add(sid)
        if not isinstance(kid,str) or not kid or kid in keyids or kid==issuance.get("key_id"):
            issues.append("TRANSPORT_SIGNER_KEY_REUSE")
        if isinstance(kid,str):keyids.add(kid)
        if not isinstance(nonce,str) or not nonce or nonce in nonces or nonce in consumed or nonce in (challenge.get("nonce"),issue_nonce):
            issues.append("TRANSPORT_NONCE_REPLAY")
        if isinstance(nonce,str):nonces.add(nonce)
        if item["challenge_sha256"]!=sha(challenge):issues.append("TRANSPORT_CHALLENGE_MISMATCH")
        if item["body_sha256"]!=challenge.get("expected_body_sha256"):issues.append("TRANSPORT_BODY_PIN_MISMATCH")
        try:
            family=ancestors(item["controller_id"],graph)
            families.append(family)
            if issuer_family & family:issues.append("SELF_ISSUED_CHALLENGE_OR_SHARED_CUSTODY")
        except ValueError as error:issues.append(str(error))
        stmt={k:item[k] for k in required if k not in ("signature_b64","key_id")}
        stmt["schema"]=SCHEMA
        entry=keys.get(kid)
        if not isinstance(entry,dict) or entry.get("controller_id")!=item["controller_id"] or not isinstance(entry.get("public_key_pem"),str):
            issues.append("TRANSPORT_PIN_INVALID");valid=False
        else:
            try:valid=bool(verify(entry["public_key_pem"],canon(stmt),base64.b64decode(item["signature_b64"],validate=True)))
            except (TypeError,ValueError,UnicodeError):valid=False
            if not valid:issues.append("TRANSPORT_SIGNATURE_INVALID")
        observed["transport_signatures"].append({"session_id":sid,"signature_valid":valid})
    for i,one in enumerate(families):
        for another in families[i+1:]:
            if one & another:issues.append("TRANSPORT_SHARED_ANCESTRY")
    if len(families)!=3:issues.append("TRANSPORT_ANCESTRIES_INCOMPLETE")
    issues+=["ISSUANCE_KEY_CUSTODY_NOT_EXTERNALLY_ATTESTED",
             "GRAPH_ANCESTRY_NOT_INDEPENDENTLY_AUTHENTICATED",
             "NONCE_CONSUMPTION_NOT_EXTERNALLY_SEALED",
             "TRANSPORT_SESSIONS_NOT_INDEPENDENTLY_ACQUIRED"]
    return {**HOLD,"reasons":sorted(set(issues)),"observed":observed}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--bundle",type=Path,required=True)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        data=args.bundle.read_bytes()
        if len(data)>1024*1024:raise ValueError("INPUT_OVERSIZE")
        result=assess(json.loads(data))
    except (OSError,ValueError,TypeError,UnicodeError) as error:
        result={**HOLD,"reasons":["INPUT_REJECTED:"+type(error).__name__]}
    rendered=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(rendered,encoding="utf-8")
    print(rendered,end="")
    return 1
if __name__=="__main__":
    raise SystemExit(main())
