#!/usr/bin/env python3
"""AETHER-271-RS: raw readback -> checkpoint -> out-of-band pin digest gate.

The independently supplied digest is an explicit trust prerequisite, not
proof of independent ownership. No network activity or authority is granted.
"""
import argparse,base64,hashlib,json,re
from pathlib import Path

SCHEMA="AETHER-271/raw-readback-pin-v1"
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "independent_acquisition_verified":False,
      "independent_pin_owner_authenticated":False}
HEX64=re.compile(r"^[0-9a-f]{64}$")
MAX_BYTES=65536

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False,ensure_ascii=True).encode()

def sha_bytes(value):return hashlib.sha256(value).hexdigest()
def sha(value):return sha_bytes(canonical(value))

def verify_signature(pem,payload,signature):
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key=serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key,Ed25519PublicKey) or len(signature)!=64:return False
        key.verify(signature,payload)
        return True
    except (ImportError,InvalidSignature,ValueError,TypeError,UnicodeError):return False

def lineage(name,graph):
    done=set();active=set()
    def visit(node):
        if not isinstance(node,str) or not node or len(node)>128:raise ValueError("LINEAGE_NODE_INVALID")
        if node in active:raise ValueError("LINEAGE_CYCLE")
        if node in done:return
        if node not in graph:raise ValueError("LINEAGE_MISSING")
        parents=graph[node]
        if not isinstance(parents,list) or len(parents)>16:raise ValueError("LINEAGE_PARENTS_INVALID")
        active.add(node);done.add(node)
        if len(done)>256:raise ValueError("LINEAGE_TOO_LARGE")
        for p in parents:visit(p)
        active.remove(node)
    visit(name)
    return done

def checkpoint_ok(c):
    if not isinstance(c,dict) or set(c)!={"schema","count","receipts","snapshot_sha256"}:
        return False
    if c["schema"]!="AETHER-269/nonce-anchor-v1" or not isinstance(c["receipts"],list) or len(c["receipts"])>4096:
        return False
    if type(c["count"]) is not int or c["count"]!=len(c["receipts"]):return False
    if not isinstance(c["snapshot_sha256"],str) or not HEX64.fullmatch(c["snapshot_sha256"]):return False
    if c["snapshot_sha256"]!=sha({k:v for k,v in c.items() if k!="snapshot_sha256"}):return False
    prior=""
    for entry in c["receipts"]:
        if not isinstance(entry,dict) or set(entry)!={"nonce","challenge_sha256","issuance_sha256","receipt_sha256"}:return False
        nonce=entry["nonce"]
        if not isinstance(nonce,str) or not nonce or nonce<=prior or len(nonce)>128:return False
        if any(not isinstance(entry[k],str) or not HEX64.fullmatch(entry[k]) for k in ("challenge_sha256","issuance_sha256","receipt_sha256")):return False
        receipt={"schema":"AETHER-268/pinned-issuance-nonce-v1","nonce":nonce,
                 "challenge_sha256":entry["challenge_sha256"],"issuance_sha256":entry["issuance_sha256"]}
        if sha(receipt)!=entry["receipt_sha256"]:return False
        prior=nonce
    return True

def assess(bundle,expected_pin_sha256,signature_verify=verify_signature):
    reasons=[];observed={"readbacks":[]}
    if not isinstance(expected_pin_sha256,str) or not HEX64.fullmatch(expected_pin_sha256):
        return {**HOLD,"reasons":["OUT_OF_BAND_PIN_REQUIRED"],"observed":observed}
    if not isinstance(bundle,dict) or set(bundle)!={"trust_record","expected_checkpoint_sha256","readbacks","challenge_nonce"}:
        return {**HOLD,"reasons":["BUNDLE_INVALID"],"observed":observed}
    trust=bundle["trust_record"]
    reads=bundle["readbacks"]
    nonce=bundle["challenge_nonce"]
    expected=bundle["expected_checkpoint_sha256"]
    if not isinstance(trust,dict) or set(trust)!={"issuer_controller","public_keys","source_controllers","ancestry"}:
        return {**HOLD,"reasons":["TRUST_RECORD_INVALID"],"observed":observed}
    if sha(trust)!=expected_pin_sha256:reasons.append("OUT_OF_BAND_TRUST_PIN_MISMATCH")
    if not isinstance(expected,str) or not HEX64.fullmatch(expected):reasons.append("CHECKPOINT_PIN_INVALID")
    if not isinstance(nonce,str) or not nonce or len(nonce)>128:reasons.append("CHALLENGE_NONCE_INVALID")
    if not isinstance(reads,list) or len(reads)!=3:
        reasons.append("THREE_READBACKS_REQUIRED");reads=[]
    keys=trust["public_keys"];controllers=trust["source_controllers"];graph=trust["ancestry"]
    if not all(isinstance(x,dict) for x in (keys,controllers,graph)):
        return {**HOLD,"reasons":["TRUST_RECORD_FIELDS_INVALID"],"observed":observed}
    families=[];source_ids=set();session_ids=set();receipt_nonces=set()
    try:issuer_family=lineage(trust["issuer_controller"],graph)
    except ValueError as e:reasons.append(str(e));issuer_family=set()
    seen_snapshots=[]
    for row in reads:
        needed={"source_id","session_id","receipt_nonce","raw_b64","raw_sha256",
                "controller_id","key_id","signature_b64"}
        if not isinstance(row,dict) or set(row)!=needed:
            reasons.append("READBACK_SCHEMA_INVALID");continue
        sid=row["source_id"];session=row["session_id"];rnonce=row["receipt_nonce"]
        controller=row["controller_id"];keyid=row["key_id"]
        if not isinstance(sid,str) or not sid or sid in source_ids:reasons.append("DUPLICATE_SOURCE")
        if isinstance(sid,str):source_ids.add(sid)
        if not isinstance(session,str) or not session or session in session_ids:reasons.append("DUPLICATE_SESSION")
        if isinstance(session,str):session_ids.add(session)
        if not isinstance(rnonce,str) or not rnonce or rnonce in receipt_nonces or rnonce==nonce:
            reasons.append("READBACK_NONCE_REPLAY")
        if isinstance(rnonce,str):receipt_nonces.add(rnonce)
        if controllers.get(sid)!=controller:reasons.append("SOURCE_CONTROLLER_PIN_MISMATCH")
        try:
            family=lineage(controller,graph)
            families.append(family)
            if family & issuer_family:reasons.append("SELF_ISSUED_OR_SHARED_ISSUER_ANCESTRY")
        except ValueError as e:reasons.append(str(e))
        raw=None;parsed=None
        try:
            encoded=row["raw_b64"]
            if not isinstance(encoded,str) or len(encoded)>90000:raise ValueError("BODY_OVERSIZE")
            raw=base64.b64decode(encoded,validate=True)
            if len(raw)>MAX_BYTES:raise ValueError("BODY_OVERSIZE")
            parsed=json.loads(raw)
        except (TypeError,ValueError,UnicodeError,json.JSONDecodeError):
            reasons.append("RAW_READBACK_UNDECODABLE")
        if raw is not None and sha_bytes(raw)!=row["raw_sha256"]:
            reasons.append("RAW_READBACK_HASH_MISMATCH")
        if not checkpoint_ok(parsed):reasons.append("RAW_CHECKPOINT_INVALID")
        else:
            seen_snapshots.append(parsed)
            if parsed["snapshot_sha256"]!=expected:reasons.append("CHECKPOINT_DIGEST_CONFLICT")
        statement={"schema":SCHEMA,"source_id":sid,"session_id":session,
                   "receipt_nonce":rnonce,"challenge_nonce":nonce,
                   "raw_sha256":row["raw_sha256"],"checkpoint_sha256":expected}
        pinned_key=keys.get(keyid)
        if (not isinstance(pinned_key,dict) or pinned_key.get("controller_id")!=controller
            or not isinstance(pinned_key.get("public_key_pem"),str)):
            reasons.append("SIGNER_NOT_IN_PINNED_TRUST_RECORD");valid=False
        else:
            try:
                sig=base64.b64decode(row["signature_b64"],validate=True)
                valid=bool(signature_verify(pinned_key["public_key_pem"],canonical(statement),sig))
            except (TypeError,ValueError,UnicodeError):valid=False
            if not valid:reasons.append("SIGNATURE_INVALID")
        observed["readbacks"].append({"source_id":sid,"signature_valid":valid,
                                      "raw_sha256":row["raw_sha256"]})
    for index,one in enumerate(families):
        for other in families[index+1:]:
            if one & other:reasons.append("SHARED_SOURCE_ANCESTRY")
    if len(seen_snapshots)==3 and len({sha(c) for c in seen_snapshots})!=1:
        reasons.append("SPLIT_CHECKPOINT_READBACK")
    if len(families)!=3:reasons.append("THREE_VALID_ANCESTRIES_REQUIRED")
    reasons+=["TRUST_PIN_ORIGIN_NOT_INDEPENDENTLY_ATTESTED",
              "READBACK_TRANSPORT_NOT_INDEPENDENTLY_ACQUIRED",
              "SIGNER_OWNER_NOT_INDEPENDENTLY_VERIFIED"]
    return {**HOLD,"reasons":sorted(set(reasons)),"observed":observed}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--bundle",type=Path,required=True)
    p.add_argument("--trusted-pin-sha256",required=True)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    try:
        raw=a.bundle.read_bytes()
        if len(raw)>1024*1024:raise ValueError("BUNDLE_TOO_LARGE")
        result=assess(json.loads(raw),a.trusted_pin_sha256)
    except (OSError,ValueError,TypeError,UnicodeError) as e:
        result={**HOLD,"reasons":["INPUT_REJECTED:"+type(e).__name__]}
    value=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(value,encoding="utf-8")
    print(value,end="")
    return 1

if __name__=="__main__":raise SystemExit(main())
