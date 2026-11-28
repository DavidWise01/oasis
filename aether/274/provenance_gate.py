#!/usr/bin/env python3
"""AETHER-274-RS: authenticated-by-pinned-key acquisition transcript review.

Distinguishes byte-level consistency and signed claims from independent
observation. No live network collection, third-party custody, or ACT.
"""
import argparse
import base64
import hashlib
import ipaddress
import json
from pathlib import Path
from urllib.parse import urlsplit

SCHEMA="AETHER-274/acquisition-provenance-v1"
OBS_SCHEMA="AETHER-264/https-acquisition-v1"
MAX_BODY=65536
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "live_transport_observed":False,"independent_custody_verified":False}

def canon(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),
                      ensure_ascii=True,allow_nan=False).encode("ascii")

def sha_bytes(blob):
    return hashlib.sha256(blob).hexdigest()

def sha(obj):
    return sha_bytes(canon(obj))

def hex64(value):
    return isinstance(value,str) and len(value)==64 and all(c in "0123456789abcdef" for c in value)

def ed25519(pem,message,signature):
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key=serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key,Ed25519PublicKey) or len(signature)!=64:
            return False
        key.verify(signature,message)
        return True
    except (ImportError,InvalidSignature,ValueError,TypeError,UnicodeError):
        return False

def verify_observation(obs):
    fields={"schema","requested_url","host","pinned_ip","dns_address_count",
            "tls_hostname_validation","status","elapsed_ms","raw_length",
            "raw_sha256","raw_b64","observation_sha256"}
    if not isinstance(obs,dict) or set(obs)!=fields:
        return ["OBSERVATION_SCHEMA_INVALID"]
    faults=[]
    if obs["schema"]!=OBS_SCHEMA or obs["tls_hostname_validation"] is not True or type(obs["status"]) is not int or obs["status"] not in (200,206):
        faults.append("TRANSPORT_CLAIM_INVALID")
    try:
        parsed=urlsplit(obs["requested_url"])
        if (parsed.scheme!="https" or parsed.username or parsed.password or parsed.fragment or
            parsed.port not in (None,443) or parsed.hostname!=obs["host"]):
            faults.append("TRANSPORT_URL_INVALID")
        ip=ipaddress.ip_address(obs["pinned_ip"])
        if not ip.is_global or ip.is_multicast or ip.is_unspecified:
            faults.append("PEER_NOT_PUBLIC")
    except (ValueError,TypeError,AttributeError):
        faults.append("TRANSPORT_ADDRESS_INVALID")
    try:
        if not isinstance(obs["raw_b64"],str) or len(obs["raw_b64"])>90000:
            raise ValueError("ENCODED_LIMIT")
        raw=base64.b64decode(obs["raw_b64"],validate=True)
        if len(raw)>MAX_BODY or type(obs["raw_length"]) is not int or len(raw)!=obs["raw_length"]:
            faults.append("RAW_BODY_LENGTH_MISMATCH")
        if sha_bytes(raw)!=obs["raw_sha256"]:
            faults.append("RAW_BODY_SHA256_MISMATCH")
    except (ValueError,TypeError):
        faults.append("RAW_BODY_UNDECODABLE")
    bare={k:v for k,v in obs.items() if k!="observation_sha256"}
    if sha(bare)!=obs["observation_sha256"]:
        faults.append("OBSERVATION_RECORD_TAMPER")
    return faults

def lineage(node,graph):
    found=set();active=set()
    def visit(current):
        if not isinstance(current,str) or not current or len(current)>128:
            raise ValueError("CONTROLLER_NODE_INVALID")
        if current in active:raise ValueError("CONTROLLER_CYCLE")
        if current in found:return
        if current not in graph:raise ValueError("CONTROLLER_ANCESTRY_MISSING")
        parents=graph[current]
        if not isinstance(parents,list) or len(parents)>16:
            raise ValueError("CONTROLLER_PARENTS_INVALID")
        found.add(current);active.add(current)
        if len(found)>256:raise ValueError("CONTROLLER_GRAPH_LIMIT")
        for parent in parents:visit(parent)
        active.remove(current)
    visit(node)
    return found

def assess(bundle,pinned_registry_sha256,signature_check=ed25519):
    issues=[];observed={"signatures":[]}
    if not hex64(pinned_registry_sha256):
        return {**HOLD,"reasons":["OUT_OF_BAND_REGISTRY_DIGEST_REQUIRED"],"observed":observed}
    if not isinstance(bundle,dict) or set(bundle)!={"registry","challenge","previous_session_nonces","acquisitions"}:
        return {**HOLD,"reasons":["BUNDLE_SCHEMA_INVALID"],"observed":observed}
    registry=bundle["registry"]
    challenge=bundle["challenge"]
    history=bundle["previous_session_nonces"]
    acquisitions=bundle["acquisitions"]
    if not isinstance(registry,dict) or set(registry)!={"sources","controllers","issuer_controller"}:
        return {**HOLD,"reasons":["REGISTRY_INVALID"],"observed":observed}
    if sha(registry)!=pinned_registry_sha256:
        issues.append("REGISTRY_DIGEST_SUBSTITUTION")
    sources=registry["sources"];graph=registry["controllers"]
    if not isinstance(sources,dict) or not isinstance(graph,dict):
        return {**HOLD,"reasons":["REGISTRY_FIELDS_INVALID"],"observed":observed}
    if not isinstance(challenge,dict) or set(challenge)!={"challenge_id","nonce","run_id","expected_raw_sha256","url"}:
        issues.append("CHALLENGE_INVALID");challenge={}
    for key in ("challenge_id","nonce","url"):
        value=challenge.get(key)
        if not isinstance(value,str) or not value or len(value)>2048:
            issues.append("CHALLENGE_FIELDS_INVALID")
    if not hex64(challenge.get("expected_raw_sha256")):
        issues.append("EXPECTED_RAW_DIGEST_INVALID")
    if type(challenge.get("run_id")) is not int or challenge["run_id"]<1:
        issues.append("CHALLENGE_RUN_INVALID")
    if not isinstance(history,list) or len(history)>4096 or any(not isinstance(x,str) for x in history):
        issues.append("NONCE_HISTORY_INVALID");history=[]
    if len(set(history))!=len(history):issues.append("HISTORY_HAS_DUPLICATE_NONCE")
    if challenge.get("nonce") in history:issues.append("CHALLENGE_NONCE_REPLAY")
    if not isinstance(acquisitions,list) or len(acquisitions)!=3:
        issues.append("THREE_ACQUISITIONS_REQUIRED");acquisitions=[]
    try:issuer_family=lineage(registry["issuer_controller"],graph)
    except ValueError as e:issues.append(str(e));issuer_family=set()
    ids=set();sessions=set();nonces=set();keys=set();families=[];digests=[]
    for item in acquisitions:
        required={"source_id","controller_id","key_id","session_id","session_nonce",
                  "observation","signed_receipt_b64"}
        if not isinstance(item,dict) or set(item)!=required:
            issues.append("ACQUISITION_SCHEMA_INVALID");continue
        source=item["source_id"];controller=item["controller_id"];kid=item["key_id"]
        sid=item["session_id"];nonce=item["session_nonce"]
        for label,value,seen in (("SOURCE",source,ids),("SESSION",sid,sessions),("NONCE",nonce,nonces),("KEY",kid,keys)):
            if not isinstance(value,str) or not value or len(value)>128 or value in seen:
                issues.append(label+"_REPLAY_OR_INVALID")
            if isinstance(value,str):seen.add(value)
        if nonce==challenge.get("nonce") or nonce in history:
            issues.append("SESSION_NONCE_CONSUMED")
        source_entry=sources.get(source)
        if (not isinstance(source_entry,dict) or
            set(source_entry)!={"controller_id","key_id","public_key_pem","hostname"} or
            source_entry.get("controller_id")!=controller or source_entry.get("key_id")!=kid):
            issues.append("SOURCE_REGISTRY_PIN_MISMATCH")
            source_entry=None
        try:
            family=lineage(controller,graph)
            families.append(family)
            if family & issuer_family:issues.append("SELF_ISSUED_OR_SHARED_ISSUER_ANCESTRY")
        except ValueError as e:issues.append(str(e))
        obs=item["observation"]
        issues.extend(verify_observation(obs))
        if isinstance(obs,dict):
            if obs.get("requested_url")!=challenge.get("url"):
                issues.append("ACQUISITION_URL_SUBSTITUTION")
            if obs.get("raw_sha256")!=challenge.get("expected_raw_sha256"):
                issues.append("PINNED_RAW_BYTES_CONFLICT")
            if source_entry and obs.get("host")!=source_entry["hostname"]:
                issues.append("SOURCE_HOSTNAME_PIN_MISMATCH")
            digests.append(obs.get("raw_sha256"))
        statement={"schema":SCHEMA,"challenge":challenge,
                   "source_id":source,"controller_id":controller,
                   "key_id":kid,"session_id":sid,"session_nonce":nonce,
                   "observation_sha256":obs.get("observation_sha256") if isinstance(obs,dict) else None}
        valid=False
        if source_entry:
            try:
                signature=base64.b64decode(item["signed_receipt_b64"],validate=True)
                valid=bool(signature_check(source_entry["public_key_pem"],canon(statement),signature))
            except (ValueError,TypeError,UnicodeError):pass
        if not valid:issues.append("SIGNED_RECEIPT_INVALID")
        observed["signatures"].append({"source_id":source,"valid":valid,
                                       "record_digest":sha(statement)})
    for i,f in enumerate(families):
        for other in families[i+1:]:
            if f & other:issues.append("SHARED_ACQUISITION_ANCESTRY")
    if len(digests)==3 and len(set(digests))>1:
        issues.append("CONFLICTING_ACQUIRED_BODY_DIGESTS")
    issues.extend(["RAW_OBSERVATIONS_SUPPLIED_NOT_LIVE_ACQUIRED",
                   "TRUST_REGISTRY_ORIGIN_UNVERIFIED",
                   "CONTROLLER_ANCESTRY_SELF_DECLARED",
                   "NONCE_HISTORY_NOT_EXTERNALLY_SEALED"])
    return {**HOLD,"reasons":sorted(set(issues)),"observed":observed}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--bundle",type=Path,required=True)
    parser.add_argument("--trusted-registry-sha256",required=True)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    try:
        raw=args.bundle.read_bytes()
        if len(raw)>1024*1024:raise ValueError("INPUT_TOO_LARGE")
        result=assess(json.loads(raw),args.trusted_registry_sha256)
    except (OSError,ValueError,TypeError,UnicodeError) as e:
        result={**HOLD,"reasons":["INPUT_REJECTED:"+type(e).__name__]}
    output=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(output,encoding="utf-8")
    print(output,end="")
    return 1

if __name__=="__main__":
    raise SystemExit(main())
