#!/usr/bin/env python3
"""AETHER-303-RS: custodian registry, dual-key rotation and signed time windows.

Keys and registry roots are supplied pins, not independent identity evidence.
No physical authority, independent elapsed-time, or remote custody is inferred.
"""
import argparse,base64,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"292"))
from attestation_audit import verify as ed_verify, ancestry

HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "independent_custodian_identity_verified":False,
      "independent_clock_custody_verified":False,
      "independent_elapsed_time_verified":False,
      "independent_external_custody_verified":False}
REGISTRY="AETHER-303/registry-attestation-v1"
ROTATION="AETHER-303/dual-signed-rotation-v1"
TIME="AETHER-303/time-window-v1"
ZERO="0"*64
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def sha(v):return hashlib.sha256(canon(v)).hexdigest()
def digest(v):return hashlib.sha256(v).hexdigest()
def hex64(v):return isinstance(v,str) and len(v)==64 and all(c in "0123456789abcdef" for c in v)
def strict(v,fields,label):
    if not isinstance(v,dict) or set(v)!=fields:raise ValueError(label+"_SCHEMA_INVALID")
def verify_signature(key,body,field="signature_b64"):
    if not isinstance(key,dict) or set(key)!={"controller_id","public_key_pem"}:
        raise ValueError("PUBLIC_KEY_RECORD_INVALID")
    unsigned={k:v for k,v in body.items() if k!=field}
    if not ed_verify(key["public_key_pem"],unsigned,body[field]):
        raise ValueError("SIGNATURE_INVALID")
def validate_roots(roots,pin):
    strict(roots,{"registry_key","clock_key","ancestry_graph","source_root","custodian_root",
                  "registry_root","clock_root"},"ROOTS")
    if not hex64(pin) or sha(roots)!=pin:raise ValueError("OUT_OF_BAND_ROOT_PIN_MISMATCH")
    graph=roots["ancestry_graph"]
    if not isinstance(graph,dict):raise ValueError("ANCESTRY_GRAPH_INVALID")
    domains=[]
    for name in ("source_root","custodian_root","registry_root","clock_root"):
        domains.append(ancestry(roots[name],graph))
    for i,source in enumerate(domains):
        if any(source & other for other in domains[i+1:]):
            raise ValueError("DECLARED_CONTROLLERS_SHARE_ANCESTRY")
    return True
def registry_check(statement,roots,expected):
    strict(statement,{"schema","registry_controller_id","custodian_id","key_epoch",
                      "custodian_key_sha256","previous_registry_sha256",
                      "subject_head_sha256","signature_b64"},"REGISTRY")
    if statement["schema"]!=REGISTRY or statement["registry_controller_id"]!=roots["registry_key"]["controller_id"]:
        raise ValueError("REGISTRY_CONTROLLER_INVALID")
    if type(statement["key_epoch"]) is not int or statement["key_epoch"]<1:
        raise ValueError("REGISTRY_EPOCH_INVALID")
    for key,value in expected.items():
        if statement[key]!=value:raise ValueError("REGISTRY_BINDING_INVALID:"+key)
    verify_signature(roots["registry_key"],statement)
    return sha(statement)
def rotation_check(rotation,old_key,new_key,previous_head,epoch,custodian_id,source_head):
    strict(rotation,{"schema","custodian_id","old_key_sha256","new_key_sha256",
                     "from_epoch","to_epoch","previous_rotation_sha256",
                     "source_head_sha256","old_signature_b64",
                     "new_signature_b64"},"ROTATION")
    if rotation["schema"]!=ROTATION or rotation["custodian_id"]!=custodian_id:
        raise ValueError("ROTATION_ID_INVALID")
    if type(epoch) is not int or epoch<1 or rotation["from_epoch"]!=epoch or rotation["to_epoch"]!=epoch+1:
        raise ValueError("ROTATION_EPOCH_INVALID")
    if rotation["old_key_sha256"]!=sha(old_key) or rotation["new_key_sha256"]!=sha(new_key):
        raise ValueError("ROTATION_KEY_SUBSTITUTION")
    if rotation["previous_rotation_sha256"]!=previous_head or rotation["source_head_sha256"]!=source_head:
        raise ValueError("ROTATION_ANCESTRY_INVALID")
    unsigned={k:v for k,v in rotation.items() if not k.endswith("signature_b64")}
    if not ed_verify(old_key["public_key_pem"],unsigned,rotation["old_signature_b64"]):
        raise ValueError("OLD_KEY_SIGNATURE_INVALID")
    if not ed_verify(new_key["public_key_pem"],unsigned,rotation["new_signature_b64"]):
        raise ValueError("NEW_KEY_SIGNATURE_INVALID")
    return sha(rotation)
def time_check(claims,roots,source_head,receipt_head):
    if not isinstance(claims,list) or len(claims)!=2:raise ValueError("TWO_TIME_WINDOWS_REQUIRED")
    last=ZERO;nonces=set();timestamps=[]
    for i,claim in enumerate(claims,1):
        strict(claim,{"schema","clock_controller_id","window_seq","source_head_sha256",
                      "receipt_head_sha256","previous_time_sha256","unix_ms_claim",
                      "nonce","signature_b64"},"TIME")
        if claim["schema"]!=TIME or claim["clock_controller_id"]!=roots["clock_key"]["controller_id"]:
            raise ValueError("CLOCK_CONTROLLER_INVALID")
        if type(claim["window_seq"]) is not int or claim["window_seq"]!=i:
            raise ValueError("TIME_WINDOW_ORDER_INVALID")
        if claim["source_head_sha256"]!=source_head or claim["receipt_head_sha256"]!=receipt_head:
            raise ValueError("TIME_SUBJECT_MISMATCH")
        if claim["previous_time_sha256"]!=last:raise ValueError("TIME_PREDECESSOR_INVALID")
        timestamp=claim["unix_ms_claim"]
        if type(timestamp) is not int or timestamp<=0:raise ValueError("TIME_VALUE_INVALID")
        if not isinstance(claim["nonce"],str) or not 12<=len(claim["nonce"])<=128 or claim["nonce"] in nonces:
            raise ValueError("TIME_NONCE_INVALID_OR_REPLAY")
        verify_signature(roots["clock_key"],claim)
        nonces.add(claim["nonce"]);timestamps.append(timestamp);last=sha(claim)
    if timestamps[1]<=timestamps[0]:raise ValueError("TIME_CLAIM_NOT_INCREASING")
    return {"claimed_elapsed_ms":timestamps[1]-timestamps[0],"chain_head_sha256":last}
def qualify(bundle,roots,pin):
    try:
        validate_roots(roots,pin)
        strict(bundle,{"schema","source_head_sha256","receipt_head_sha256",
                       "custodian_id","old_key","new_key","old_registry",
                       "rotation","new_registry","time_windows"},"BUNDLE")
        if bundle["schema"]!="AETHER-303/qualification-v1":raise ValueError("BUNDLE_VERSION_INVALID")
        source=bundle["source_head_sha256"];receipt=bundle["receipt_head_sha256"]
        if not hex64(source) or not hex64(receipt):raise ValueError("SUBJECT_HEAD_INVALID")
        custodian=bundle["custodian_id"];old=bundle["old_key"];new=bundle["new_key"]
        if not isinstance(custodian,str) or not custodian or old==new:
            raise ValueError("CUSTODIAN_OR_KEY_ID_INVALID")
        old_statement=bundle["old_registry"]
        old_hash=registry_check(old_statement,roots,{
            "custodian_id":custodian,"key_epoch":1,
            "custodian_key_sha256":sha(old),
            "previous_registry_sha256":ZERO,"subject_head_sha256":source})
        rotate_head=rotation_check(bundle["rotation"],old,new,ZERO,1,custodian,source)
        new_hash=registry_check(bundle["new_registry"],roots,{
            "custodian_id":custodian,"key_epoch":2,
            "custodian_key_sha256":sha(new),
            "previous_registry_sha256":old_hash,"subject_head_sha256":source})
        timing=time_check(bundle["time_windows"],roots,source,receipt)
        return {**HOLD,"signature_and_ancestry_claims_consistent":True,
                "registry_chain_head_sha256":new_hash,"rotation_head_sha256":rotate_head,
                "claimed_elapsed_ms":timing["claimed_elapsed_ms"],
                "reasons":["REGISTRY_KEY_CONTROL_NOT_INDEPENDENTLY_OBSERVED",
                           "CLOCK_SOURCE_ACCURACY_NOT_EXTERNALLY_VERIFIED",
                           "DECLARED_GRAPH_NOT_INDEPENDENT_PROVENANCE",
                           "REMOTE_OBJECT_RETENTION_NOT_RETRIEVED"]}
    except (ValueError,TypeError,KeyError,UnicodeError) as exc:
        return {**HOLD,"signature_and_ancestry_claims_consistent":False,
                "reasons":["REJECTED:"+str(exc)[:120]]}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--bundle",type=Path,required=True)
    p.add_argument("--roots",type=Path,required=True)
    p.add_argument("--roots-sha256",required=True)
    args=p.parse_args()
    try:
        data=args.bundle.read_bytes();roots=args.roots.read_bytes()
        if len(data)>256000 or len(roots)>256000:raise ValueError("INPUT_LIMIT")
        result=qualify(json.loads(data),json.loads(roots),args.roots_sha256)
    except (ValueError,OSError,TypeError) as exc:
        result={**HOLD,"reasons":["REJECTED:"+str(exc)[:120]]}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 1
if __name__=="__main__":raise SystemExit(main())
