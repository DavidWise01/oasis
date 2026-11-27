#!/usr/bin/env python3
"""AETHER-265-RS — three-source raw HTTPS acquisition receipt verifier.

This offline verifier cannot establish custody or independent acquisition by itself.
"""
import argparse
import base64
import hashlib
import ipaddress
import json
import re
from pathlib import Path

SCHEMA="AETHER-265/three-source-receipts-v1"
OBS_SCHEMA="AETHER-264/https-acquisition-v1"
RECEIPT_SCHEMA="AETHER-265/source-receipt-v1"
MAX_RAW=65536
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_qualification_percent":0,"physical_act_allowed":False,
      "independent_custody_verified":False,"independent_acquisition_verified":False}
HEX64=re.compile(r"^[0-9a-f]{64}$")
HEX40=re.compile(r"^[0-9a-f]{40}$")

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),
                      ensure_ascii=True,allow_nan=False).encode("ascii")

def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()

def sha(obj):
    return sha_bytes(canonical(obj))

def verify_ed25519(pem,data,sig):
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key=serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key,Ed25519PublicKey) or len(sig)!=64:
            return False
        key.verify(sig,data)
        return True
    except (ImportError,InvalidSignature,ValueError,TypeError,UnicodeError):
        return False

def validate_observation(obs):
    if not isinstance(obs,dict):
        return ["OBSERVATION_INVALID"]
    required={"schema","requested_url","host","pinned_ip","dns_address_count",
              "tls_hostname_validation","status","elapsed_ms","raw_length",
              "raw_sha256","raw_b64","observation_sha256"}
    if not required.issubset(obs):
        return ["OBSERVATION_SCHEMA_INVALID"]
    problems=[]
    if obs["schema"]!=OBS_SCHEMA or obs["tls_hostname_validation"] is not True or obs["status"] not in (200,206):
        problems.append("OBSERVATION_TRANSPORT_INVALID")
    try:
        peer=ipaddress.ip_address(obs["pinned_ip"])
        if not peer.is_global or peer.is_multicast or peer.is_unspecified:
            problems.append("OBSERVATION_UNSAFE_PEER")
    except (ValueError,TypeError):
        problems.append("OBSERVATION_UNSAFE_PEER")
    try:
        encoded=obs["raw_b64"]
        if not isinstance(encoded,str) or len(encoded)>90000:raise ValueError("ENCODED_OVERSIZE")
        raw=base64.b64decode(encoded,validate=True)
        if len(raw)>MAX_RAW or type(obs["raw_length"]) is not int or obs["raw_length"]!=len(raw):
            problems.append("RAW_LENGTH_MISMATCH")
        if sha_bytes(raw)!=obs["raw_sha256"]:
            problems.append("RAW_SHA256_MISMATCH")
    except (TypeError,ValueError):
        problems.append("RAW_UNDECODABLE")
    bare={k:obs[k] for k in required if k!="observation_sha256"}
    if sha_bytes(canonical(bare))!=obs["observation_sha256"]:
        problems.append("OBSERVATION_SHA256_MISMATCH")
    return problems

def ancestry(root,graph):
    complete=set();active=set()
    def walk(node):
        if not isinstance(node,str) or not node or len(node)>128:
            raise ValueError("ANCESTRY_NAME_INVALID")
        if node in active:raise ValueError("ANCESTRY_CYCLE")
        if node in complete:return
        if node not in graph:raise ValueError("ANCESTRY_NODE_UNAVAILABLE")
        parents=graph[node]
        if not isinstance(parents,list) or len(parents)>16:
            raise ValueError("ANCESTRY_PARENTS_INVALID")
        complete.add(node);active.add(node)
        if len(complete)>256:raise ValueError("ANCESTRY_LIMIT")
        for p in parents:walk(p)
        active.remove(node)
    walk(root)
    return complete

def assess(bundle,signature_check=verify_ed25519):
    problems=[];observed={"sources":[]}
    if not isinstance(bundle,dict):
        return {**HOLD,"reasons":["BUNDLE_INVALID"],"observed":observed}
    challenge=bundle.get("challenge")
    acquisitions=bundle.get("acquisitions")
    pins=bundle.get("public_key_pins")
    graph=bundle.get("source_ancestry")
    consumed=bundle.get("consumed_nonces")
    if not isinstance(challenge,dict) or set(challenge)!={"challenge_id","nonce","run_id","source_commit"}:
        problems.append("CHALLENGE_SCHEMA_INVALID")
        challenge={}
    for field in ("challenge_id","nonce"):
        v=challenge.get(field)
        if not isinstance(v,str) or not v or len(v)>128:
            problems.append("CHALLENGE_FIELD_INVALID")
    if type(challenge.get("run_id")) is not int or challenge["run_id"]<=0:
        problems.append("RUN_ID_INVALID")
    commit=challenge.get("source_commit")
    if not isinstance(commit,str) or not HEX40.fullmatch(commit):
        problems.append("COMMIT_INVALID")
    if not isinstance(consumed,list) or any(not isinstance(n,str) for n in consumed):
        problems.append("CONSUMPTION_LEDGER_INVALID")
        consumed=[]
    if len(consumed)!=len(set(consumed)):
        problems.append("CONSUMED_LEDGER_DUPLICATE")
    if challenge.get("nonce") in consumed:
        problems.append("CHALLENGE_NONCE_REPLAY")
    if not isinstance(pins,dict):
        problems.append("PUBLIC_KEY_PINS_UNAVAILABLE")
        pins={}
    if not isinstance(graph,dict):
        problems.append("SOURCE_ANCESTRY_UNAVAILABLE")
        graph={}
    if not isinstance(acquisitions,list) or len(acquisitions)!=3:
        problems.append("THREE_ACQUISITIONS_REQUIRED")
        acquisitions=[]
    sources=set();keys=set();nonces=set();hosts=set();families=[]
    for item in acquisitions:
        required={"source_id","controller_id","key_id","receipt_nonce","observation",
                  "signature_b64"}
        if not isinstance(item,dict) or set(item)!=required:
            problems.append("ACQUISITION_SCHEMA_INVALID")
            continue
        sid=item["source_id"];controller=item["controller_id"]
        kid=item["key_id"];nonce=item["receipt_nonce"]
        if not isinstance(sid,str) or not sid or sid in sources:
            problems.append("DUPLICATE_SOURCE_OR_INVALID")
        if isinstance(sid,str):sources.add(sid)
        if not isinstance(kid,str) or not kid or kid in keys:
            problems.append("DUPLICATE_KEY_OR_INVALID")
        if isinstance(kid,str):keys.add(kid)
        if not isinstance(nonce,str) or not nonce or nonce in nonces or nonce in consumed or nonce==challenge.get("nonce"):
            problems.append("RECEIPT_NONCE_REPLAY")
        if isinstance(nonce,str):nonces.add(nonce)
        obs=item["observation"]
        problems.extend(validate_observation(obs))
        host=obs.get("host") if isinstance(obs,dict) else None
        if not isinstance(host,str) or not host or host in hosts:
            problems.append("DUPLICATE_OR_MISSING_HOST")
        if isinstance(host,str):hosts.add(host)
        try:
            families.append(ancestry(controller,graph))
        except ValueError as e:problems.append(str(e))
        statement={"schema":RECEIPT_SCHEMA,"challenge":challenge,
                   "source_id":sid,"controller_id":controller,"receipt_nonce":nonce,
                   "observation_sha256":obs.get("observation_sha256") if isinstance(obs,dict) else None,
                   "raw_sha256":obs.get("raw_sha256") if isinstance(obs,dict) else None}
        pin=pins.get(kid)
        if not isinstance(pin,dict) or pin.get("controller_id")!=controller or not isinstance(pin.get("public_key_pem"),str):
            problems.append("PUBLIC_KEY_PIN_MISSING")
            valid=False
        else:
            try:
                sig=base64.b64decode(item["signature_b64"],validate=True)
                valid=bool(signature_check(pin["public_key_pem"],canonical(statement),sig))
            except (ValueError,TypeError,UnicodeError):
                valid=False
            if not valid:problems.append("SIGNATURE_INVALID")
        observed["sources"].append({"source_id":sid,"signature_valid":valid,
                                    "signed_statement_sha256":sha(statement),
                                    "raw_sha256":statement["raw_sha256"]})
    for i,one in enumerate(families):
        for other in families[i+1:]:
            if one.intersection(other):
                problems.append("SHARED_SOURCE_CONTROLLER_ANCESTRY")
    if len(families)!=3:problems.append("THREE_ANCESTRIES_UNAVAILABLE")
    problems += ["ACQUISITION_HOST_ORIGIN_NOT_INDEPENDENTLY_ATTESTED",
                 "EXTERNAL_KEY_AND_ANCESTRY_CUSTODY_UNVERIFIED",
                 "CONSUMED_NONCE_HISTORY_NOT_EXTERNALLY_SEALED"]
    return {**HOLD,"reasons":sorted(set(problems)),"observed":observed}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--bundle",type=Path,required=True)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    try:
        raw=args.bundle.read_bytes()
        if len(raw)>1024*1024:raise ValueError("BUNDLE_OVERSIZE")
        result=assess(json.loads(raw))
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
