#!/usr/bin/env python3
"""AETHER-266-RS: read-only HTTPS session readback and pinned challenge HOLD gate."""
import argparse,base64,hashlib,json,re
from pathlib import Path

SCHEMA="AETHER-266/transport-comparison-v1"
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_qualification_percent":0,"physical_act_allowed":False,
      "external_challenge_custody_verified":False,
      "independent_transport_sessions_verified":False}
H64=re.compile("^[0-9a-f]{64}$")
H40=re.compile("^[0-9a-f]{40}$")
MAX_BODY=65536
def canon(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def hash_bytes(raw):return hashlib.sha256(raw).hexdigest()
def sha(obj):return hash_bytes(canon(obj))
def signature_ok(pem,message,signature):
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key=serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key,Ed25519PublicKey) or len(signature)!=64:return False
        key.verify(signature,message);return True
    except (ImportError,InvalidSignature,TypeError,ValueError,UnicodeError):return False

def check_observation(obs):
    problems=[]
    expected={"schema","requested_url","host","pinned_ip","dns_address_count",
              "tls_hostname_validation","status","elapsed_ms","raw_length",
              "raw_sha256","raw_b64","observation_sha256"}
    if not isinstance(obs,dict) or set(obs)!=expected:return ["OBSERVATION_SCHEMA_INVALID"]
    if obs["schema"]!="AETHER-264/https-acquisition-v1" or obs["tls_hostname_validation"] is not True or obs["status"] not in (200,206):
        problems.append("TRANSPORT_FIELDS_INVALID")
    try:
        import ipaddress
        peer=ipaddress.ip_address(obs["pinned_ip"])
        if not peer.is_global or peer.is_multicast or peer.is_unspecified:problems.append("UNSAFE_PEER")
    except (TypeError,ValueError):problems.append("UNSAFE_PEER")
    try:
        encoded=obs["raw_b64"]
        if not isinstance(encoded,str) or len(encoded)>90000:raise ValueError("ENCODED_LIMIT")
        raw=base64.b64decode(encoded,validate=True)
        if len(raw)>MAX_BODY or type(obs["raw_length"]) is not int or len(raw)!=obs["raw_length"]:
            problems.append("BODY_LENGTH_INVALID")
        if hash_bytes(raw)!=obs["raw_sha256"]:problems.append("BODY_HASH_MISMATCH")
    except (TypeError,ValueError):problems.append("BODY_UNDECODABLE")
    if sha({k:v for k,v in obs.items() if k!="observation_sha256"})!=obs["observation_sha256"]:
        problems.append("OBSERVATION_HASH_MISMATCH")
    return problems

def assess(bundle,verify=signature_ok):
    problems=[];observed={"sessions":[]}
    if not isinstance(bundle,dict):return {**HOLD,"reasons":["BUNDLE_INVALID"],"observed":observed}
    challenge=bundle.get("challenge")
    pin=bundle.get("externally_claimed_challenge_pin")
    sessions=bundle.get("sessions")
    keys=bundle.get("key_pins")
    used=bundle.get("prior_session_nonces")
    if not isinstance(challenge,dict) or set(challenge)!={"challenge_id","nonce","run_id","source_commit","resource_url","expected_body_sha256"}:
        problems.append("CHALLENGE_SCHEMA_INVALID");challenge={}
    for field in ("challenge_id","nonce","resource_url"):
        val=challenge.get(field)
        if not isinstance(val,str) or not val or len(val)>2048:problems.append("CHALLENGE_FIELD_INVALID")
    if type(challenge.get("run_id")) is not int or challenge["run_id"]<=0:problems.append("RUN_INVALID")
    if not isinstance(challenge.get("source_commit"),str) or not H40.fullmatch(challenge["source_commit"]):
        problems.append("SOURCE_COMMIT_INVALID")
    if not isinstance(challenge.get("expected_body_sha256"),str) or not H64.fullmatch(challenge["expected_body_sha256"]):
        problems.append("EXPECTED_BODY_HASH_INVALID")
    if not isinstance(pin,dict) or set(pin)!={"challenge_sha256","pin_source_id","pin_receipt_sha256"}:
        problems.append("CHALLENGE_PIN_SCHEMA_INVALID")
    else:
        if pin["challenge_sha256"]!=sha(challenge):problems.append("CHALLENGE_PIN_MISMATCH")
        if not isinstance(pin["pin_source_id"],str) or not pin["pin_source_id"]:
            problems.append("PIN_SOURCE_INVALID")
        if pin["pin_receipt_sha256"]!=sha({"challenge_sha256":pin["challenge_sha256"],"pin_source_id":pin["pin_source_id"]}):
            problems.append("PIN_RECEIPT_HASH_INVALID")
    if not isinstance(used,list) or any(not isinstance(x,str) for x in used):
        problems.append("NONCE_HISTORY_INVALID");used=[]
    if len(set(used))!=len(used):problems.append("NONCE_HISTORY_DUPLICATED")
    if challenge.get("nonce") in used:problems.append("CHALLENGE_REPLAY")
    if not isinstance(keys,dict):problems.append("KEY_PINS_INVALID");keys={}
    if not isinstance(sessions,list) or len(sessions)!=3:
        problems.append("THREE_SESSIONS_REQUIRED");sessions=[]
    session_ids=set();nonce_ids=set();controllers=set();hosts=set()
    body_hashes=[]
    for session in sessions:
        expected={"session_id","session_nonce","controller_claim","key_id","observation","signature_b64"}
        if not isinstance(session,dict) or set(session)!=expected:
            problems.append("SESSION_SCHEMA_INVALID");continue
        sid=session["session_id"];nonce=session["session_nonce"];controller=session["controller_claim"];kid=session["key_id"]
        if not isinstance(sid,str) or not sid or sid in session_ids:
            problems.append("DUPLICATE_SESSION_ID")
        if isinstance(sid,str):session_ids.add(sid)
        if not isinstance(nonce,str) or not nonce or nonce in nonce_ids or nonce in used or nonce==challenge.get("nonce"):
            problems.append("SESSION_NONCE_REPLAY")
        if isinstance(nonce,str):nonce_ids.add(nonce)
        if not isinstance(controller,str) or not controller or controller in controllers:
            problems.append("DUPLICATE_CONTROLLER_CLAIM")
        if isinstance(controller,str):controllers.add(controller)
        obs=session["observation"]
        problems.extend(check_observation(obs))
        if isinstance(obs,dict):
            body_hashes.append(obs.get("raw_sha256"))
            if obs.get("requested_url")!=challenge.get("resource_url"):
                problems.append("RESOURCE_SUBSTITUTION")
            if obs.get("raw_sha256")!=challenge.get("expected_body_sha256"):
                problems.append("BODY_CONFLICT_WITH_PIN")
            if isinstance(obs.get("host"),str):hosts.add(obs["host"])
        stmt={"schema":SCHEMA,"challenge_sha256":sha(challenge),
              "session_id":sid,"session_nonce":nonce,"controller_claim":controller,
              "observation_sha256":obs.get("observation_sha256") if isinstance(obs,dict) else None}
        key=keys.get(kid)
        if not isinstance(key,dict) or key.get("controller_claim")!=controller or not isinstance(key.get("public_key_pem"),str):
            problems.append("SIGNER_PIN_MISSING");valid=False
        else:
            try:
                signature=base64.b64decode(session["signature_b64"],validate=True)
                valid=bool(verify(key["public_key_pem"],canon(stmt),signature))
            except (TypeError,ValueError,UnicodeError):valid=False
            if not valid:problems.append("SIGNATURE_INVALID")
        observed["sessions"].append({"session_id":sid,"body_sha256":body_hashes[-1] if body_hashes else None,
                                     "signature_valid":valid})
    if len(set(body_hashes))>1:problems.append("INCONSISTENT_READBACK_BODIES")
    observed["distinct_claimed_sessions"]=len(session_ids)
    observed["body_digest_agreement"]=len(body_hashes)==3 and len(set(body_hashes))==1
    problems+=["CHALLENGE_PIN_NOT_INDEPENDENTLY_RETAINED",
               "THREE_TRANSPORT_SESSIONS_NOT_INDEPENDENTLY_ATTESTED",
               "SIGNER_ANCESTRY_AND_KEY_CUSTODY_UNVERIFIED",
               "NONCE_LEDGER_NOT_EXTERNALLY_SEALED"]
    return {**HOLD,"reasons":sorted(set(problems)),"observed":observed}

def main():
    p=argparse.ArgumentParser();p.add_argument("--bundle",type=Path,required=True);p.add_argument("--out",type=Path)
    a=p.parse_args()
    try:
        raw=a.bundle.read_bytes()
        if len(raw)>1024*1024:raise ValueError("INPUT_TOO_LARGE")
        report=assess(json.loads(raw))
    except (OSError,ValueError,TypeError,UnicodeError) as e:
        report={**HOLD,"reasons":["INPUT_REJECTED:"+type(e).__name__]}
    value=json.dumps(report,indent=2,sort_keys=True)+"\n"
    if a.out:a.out.write_text(value,encoding="utf-8")
    print(value,end="");return 1
if __name__=="__main__":raise SystemExit(main())
