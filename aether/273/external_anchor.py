#!/usr/bin/env python3
"""AETHER-273-RS: offline anchor comparison and raw-transcript readback fencing.

Evidence comes from caller-provided bytes. Successful signature checks are not
proof of independent retrieval, custodian ownership, or operational authority.
"""
import argparse, base64, hashlib, json, re
from pathlib import Path

SCHEMA="AETHER-273/external-anchor-review-v1"
TRANSCRIPT_SCHEMA="AETHER-273/transcript-readback-v1"
ANCHOR_SCHEMA="AETHER-273/anchor-v1"
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "external_anchor_custody_verified":False,"independent_acquisition_verified":False}
H64=re.compile(r"^[0-9a-f]{64}$")
LIMIT=65536

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()

def sha_bytes(raw):
    return hashlib.sha256(raw).hexdigest()

def sha(x):
    return sha_bytes(canonical(x))

def verify_ed25519(pem,message,sig):
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key=serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key,Ed25519PublicKey) or len(sig)!=64:return False
        key.verify(sig,message)
        return True
    except (ImportError,InvalidSignature,ValueError,TypeError,UnicodeError):
        return False

def parse_raw(encoded):
    if not isinstance(encoded,str) or len(encoded)>90000:
        raise ValueError("ENCODED_BODY_INVALID")
    raw=base64.b64decode(encoded,validate=True)
    if len(raw)>LIMIT:
        raise ValueError("BODY_TOO_LARGE")
    return raw

def review(bundle,pinned_anchor_sha256,verify=verify_ed25519):
    errors=[]
    observed={"signed_transcripts":[],"anchor_signature_valid":False}
    if not isinstance(pinned_anchor_sha256,str) or not H64.fullmatch(pinned_anchor_sha256):
        return {**HOLD,"reasons":["OUT_OF_BAND_ANCHOR_DIGEST_REQUIRED"],"observed":observed}
    if not isinstance(bundle,dict) or set(bundle)!={"anchor","anchor_key_pem","registry",
                                                   "readbacks","challenge","previous_challenge_nonces"}:
        return {**HOLD,"reasons":["BUNDLE_INVALID"],"observed":observed}
    anchor=bundle["anchor"];registry=bundle["registry"];challenge=bundle["challenge"]
    history=bundle["previous_challenge_nonces"];reads=bundle["readbacks"]
    if not isinstance(anchor,dict) or set(anchor)!={"statement","signature_b64"}:
        return {**HOLD,"reasons":["ANCHOR_ENVELOPE_INVALID"],"observed":observed}
    statement=anchor["statement"]
    if not isinstance(statement,dict) or set(statement)!={"schema","registry_sha256","epoch",
        "challenge_count_floor","anchor_nonce","controller_claim"}:
        return {**HOLD,"reasons":["ANCHOR_STATEMENT_INVALID"],"observed":observed}
    if sha(statement)!=pinned_anchor_sha256:errors.append("OUT_OF_BAND_ANCHOR_MISMATCH")
    if statement["schema"]!=ANCHOR_SCHEMA:errors.append("ANCHOR_SCHEMA_INVALID")
    if type(statement["epoch"]) is not int or statement["epoch"]<1:
        errors.append("ANCHOR_EPOCH_INVALID")
    if type(statement["challenge_count_floor"]) is not int or statement["challenge_count_floor"]<0:
        errors.append("ANCHOR_FLOOR_INVALID")
    if not isinstance(statement["anchor_nonce"],str) or not statement["anchor_nonce"]:
        errors.append("ANCHOR_NONCE_INVALID")
    if not isinstance(statement["controller_claim"],str) or not statement["controller_claim"]:
        errors.append("ANCHOR_OWNER_INVALID")
    if not isinstance(statement["registry_sha256"],str) or not H64.fullmatch(statement["registry_sha256"]):
        errors.append("ANCHOR_REGISTRY_DIGEST_INVALID")
    try:
        signature=base64.b64decode(anchor["signature_b64"],validate=True)
        if not isinstance(bundle["anchor_key_pem"],str):raise TypeError("BAD_KEY")
        observed["anchor_signature_valid"]=bool(verify(bundle["anchor_key_pem"],canonical(statement),signature))
    except (ValueError,TypeError,UnicodeError):
        pass
    if not observed["anchor_signature_valid"]:errors.append("ANCHOR_SIGNATURE_INVALID")
    if not isinstance(registry,dict) or set(registry)!={"rows","sealed_sha256","challenge_count"}:
        return {**HOLD,"reasons":sorted(set(errors+["REGISTRY_SCHEMA_INVALID"])),"observed":observed}
    rows=registry["rows"]
    if not isinstance(rows,list) or len(rows)!=3:
        errors.append("THREE_SIGNERS_REQUIRED");rows=[]
    seen_keys=set();seen_sources=set();seen_controllers=set();lookup={}
    for row in rows:
        if not isinstance(row,dict) or set(row)!={"key_id","source_id","controller_id","public_key_pem"}:
            errors.append("REGISTRY_ROW_INVALID");continue
        kid=row["key_id"];sid=row["source_id"];owner=row["controller_id"]
        if any(not isinstance(v,str) or not v or len(v)>4096 for v in (kid,sid,owner,row["public_key_pem"])):
            errors.append("REGISTRY_FIELD_INVALID");continue
        if kid in seen_keys or sid in seen_sources or owner in seen_controllers:
            errors.append("REGISTRY_DUPLICATE_IDENTITY")
        seen_keys.add(kid);seen_sources.add(sid);seen_controllers.add(owner);lookup[kid]=row
    if rows!=sorted(rows,key=lambda r:r.get("key_id","") if isinstance(r,dict) else ""):
        errors.append("REGISTRY_ORDER_INVALID")
    if not isinstance(registry["sealed_sha256"],str) or registry["sealed_sha256"]!=sha(rows):
        errors.append("REGISTRY_SEAL_INVALID")
    if registry["sealed_sha256"]!=statement["registry_sha256"]:
        errors.append("REGISTRY_ROLLBACK_OR_SUBSTITUTION")
    if type(registry["challenge_count"]) is not int or registry["challenge_count"]<statement["challenge_count_floor"]:
        errors.append("CHALLENGE_COUNTER_ROLLBACK")
    if not isinstance(challenge,dict) or set(challenge)!={"challenge_id","nonce","source_commit","run_id"}:
        errors.append("CHALLENGE_SCHEMA_INVALID");challenge={}
    if type(challenge.get("run_id")) is not int or challenge["run_id"]<=0:
        errors.append("CHALLENGE_RUN_INVALID")
    if not isinstance(challenge.get("nonce"),str) or not challenge["nonce"]:
        errors.append("CHALLENGE_NONCE_INVALID")
    if not isinstance(history,list) or any(not isinstance(n,str) or not n for n in history):
        errors.append("CHALLENGE_HISTORY_INVALID");history=[]
    if len(history)!=len(set(history)):
        errors.append("CHALLENGE_HISTORY_DUPLICATE")
    if challenge.get("nonce") in history or challenge.get("nonce")==statement["anchor_nonce"]:
        errors.append("CHALLENGE_REPLAY")
    if not isinstance(reads,list) or len(reads)!=3:
        errors.append("THREE_RAW_READBACKS_REQUIRED");reads=[]
    seen_sessions=set();seen_nonce=set();seen_kids=set();body_hashes=[]
    for row in reads:
        required={"session_id","session_nonce","key_id","source_id","controller_id",
                  "requested_url","raw_b64","raw_sha256","signature_b64"}
        if not isinstance(row,dict) or set(row)!=required:
            errors.append("READBACK_SCHEMA_INVALID");continue
        session=row["session_id"];nonce=row["session_nonce"];kid=row["key_id"]
        if not isinstance(session,str) or not session or session in seen_sessions:
            errors.append("DUPLICATE_SESSION")
        if isinstance(session,str):seen_sessions.add(session)
        if not isinstance(nonce,str) or not nonce or nonce in seen_nonce or nonce in history or nonce==challenge.get("nonce"):
            errors.append("READBACK_NONCE_REPLAY")
        if isinstance(nonce,str):seen_nonce.add(nonce)
        if not isinstance(kid,str) or not kid or kid in seen_kids:
            errors.append("DUPLICATE_SIGNER")
        if isinstance(kid,str):seen_kids.add(kid)
        signer=lookup.get(kid)
        if not signer or signer["source_id"]!=row["source_id"] or signer["controller_id"]!=row["controller_id"]:
            errors.append("REGISTRY_SIGNER_MISMATCH")
        if not isinstance(row["requested_url"],str) or not row["requested_url"].startswith("https://"):
            errors.append("READBACK_URL_INVALID")
        try:
            raw=parse_raw(row["raw_b64"])
            measured=sha_bytes(raw)
            if measured!=row["raw_sha256"]:errors.append("RAW_BODY_TAMPER")
            body_hashes.append(measured)
        except (ValueError,TypeError):
            errors.append("RAW_BODY_INVALID")
        signed={"schema":TRANSCRIPT_SCHEMA,"challenge":challenge,
                "registry_sha256":statement["registry_sha256"],
                **{key:row[key] for key in ("session_id","session_nonce","key_id",
                                           "source_id","controller_id","requested_url","raw_sha256")}}
        valid=False
        if signer:
            try:
                signature=base64.b64decode(row["signature_b64"],validate=True)
                valid=bool(verify(signer["public_key_pem"],canonical(signed),signature))
            except (ValueError,TypeError,UnicodeError):pass
        if not valid:errors.append("READBACK_SIGNATURE_INVALID")
        observed["signed_transcripts"].append({"session_id":session,
                                                "signature_valid":valid,"raw_sha256":row["raw_sha256"]})
    if len(body_hashes)==3 and len(set(body_hashes))!=1:
        # A comparison of one claimed immutable resource requires byte agreement.
        errors.append("RAW_READBACK_CONFLICT")
    errors.extend(["ANCHOR_PIN_OWNERSHIP_UNVERIFIED",
                   "HTTP_ACQUISITION_NOT_INDEPENDENTLY_OBSERVED",
                   "EXTERNAL_MONOTONIC_CUSTODY_UNVERIFIED"])
    return {**HOLD,"reasons":sorted(set(errors)),"observed":observed}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--bundle",type=Path,required=True)
    parser.add_argument("--trusted-anchor-sha256",required=True)
    parser.add_argument("--out",type=Path)
    a=parser.parse_args()
    try:
        raw=a.bundle.read_bytes()
        if len(raw)>1024*1024:raise ValueError("BUNDLE_OVERSIZE")
        result=review(json.loads(raw),a.trusted_anchor_sha256)
    except (OSError,ValueError,TypeError,UnicodeError) as e:
        result={**HOLD,"reasons":["INPUT_REJECTED:"+type(e).__name__]}
    output=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(output,encoding="utf-8")
    print(output,end="")
    return 1

if __name__=="__main__":
    raise SystemExit(main())
