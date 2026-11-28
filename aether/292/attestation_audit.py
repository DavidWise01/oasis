#!/usr/bin/env python3
"""AETHER-292-RS: signed object-version and observation-time qualifications.

Verifies pinned claims, not actual provider API control, trusted clocks,
operator independence, remote immutability, or operational ACT.
"""
import argparse,base64,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"291"))
from two_window_readback import read as read_291, audit as audit_291
SCHEMA="AETHER-292/qualified-object-v1"
VERSION_SCHEMA="AETHER-292/provider-version-v1"
CLOCK_SCHEMA="AETHER-292/time-witness-v1"
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "independent_elapsed_time_verified":False,
      "independent_external_custody_verified":False,
      "remote_immutability_verified":False}
BASELINE_GAPS={"WINDOW_ORDINAL_NOT_AUTHENTICATED_TIME",
 "REMOTE_IMMUTABILITY_NOT_ESTABLISHED","INDEPENDENT_OPERATOR_CUSTODY_UNVERIFIED",
 "LOCAL_HISTORY_AND_PIN_CAN_ROLL_BACK"}
def canon(obj):return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def sha(obj):return hashlib.sha256(canon(obj)).hexdigest()
def ishash(x):return isinstance(x,str) and len(x)==64 and all(c in "0123456789abcdef" for c in x)
def verify(pem,obj,b64):
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key=serialization.load_pem_public_key(pem.encode("ascii"))
        signature=base64.b64decode(b64,validate=True)
        if not isinstance(key,Ed25519PublicKey) or len(signature)!=64:return False
        key.verify(signature,canon(obj))
        return True
    except (ImportError,InvalidSignature,TypeError,ValueError,UnicodeError):
        return False
def ancestry(name,graph):
    seen=set();active=set()
    def visit(node):
        if not isinstance(node,str) or not node or len(node)>128 or node not in graph:
            raise ValueError("ANCESTRY_NODE_UNKNOWN")
        if node in active:raise ValueError("ANCESTRY_CYCLE")
        if node in seen:return
        parents=graph[node]
        if not isinstance(parents,list) or len(parents)>16:raise ValueError("ANCESTRY_EDGES_INVALID")
        active.add(node);seen.add(node)
        if len(seen)>256:raise ValueError("ANCESTRY_TOO_LARGE")
        for parent in parents:visit(parent)
        active.remove(node)
    visit(name)
    return seen
def ensure_canonical(doc,fields):
    if not isinstance(doc,dict) or set(doc)!=fields:raise ValueError("ATTESTATION_SCHEMA_INVALID")
    return doc
def attested(body,key,pin,signature_schema):
    if not isinstance(key,dict) or set(key)!={"controller_id","public_key_pem"}:
        raise ValueError("ATTESTOR_KEY_INVALID")
    if body["schema"]!=signature_schema or body["controller_id"]!=key["controller_id"]:
        raise ValueError("ATTESTATION_IDENTITY_CONFLICT")
    statement={k:v for k,v in body.items() if k!="signature_b64"}
    if not verify(key["public_key_pem"],statement,body["signature_b64"]):
        raise ValueError("ATTESTATION_SIGNATURE_INVALID")
def qualify(windows,nonces,trust,pin,versions,times):
    problems=[]
    if not ishash(pin) or not isinstance(trust,dict) or sha(trust)!=pin:
        return {**HOLD,"reasons":["OUT_OF_BAND_TRUST_PIN_MISMATCH"]}
    if set(trust)!={"journal_controller","graph","providers","clock"} or not isinstance(trust["graph"],dict):
        return {**HOLD,"reasons":["TRUST_SCHEMA_INVALID"]}
    if not isinstance(windows,list) or len(windows)!=2 or not isinstance(nonces,list) or len(nonces)!=6:
        return {**HOLD,"reasons":["TWO_COMPLETE_WINDOWS_REQUIRED"]}
    if not isinstance(versions,list) or len(versions)!=6 or not isinstance(times,list) or len(times)!=2:
        return {**HOLD,"reasons":["SIX_VERSION_AND_TWO_CLOCK_ATTESTATIONS_REQUIRED"]}
    graph=trust["graph"]
    try:
        root=ancestry(trust["journal_controller"],graph)
        clock=trust["clock"]
        if not isinstance(clock,dict):raise ValueError("CLOCK_KEY_INVALID")
        clock_family=ancestry(clock["controller_id"],graph)
        if clock_family & root:problems.append("CLOCK_JOURNAL_SHARED_ANCESTRY")
    except (ValueError,KeyError,TypeError) as exc:
        return {**HOLD,"reasons":["TRUST_ANCESTRY_INVALID:"+str(exc)[:80]]}
    providers=trust["providers"]
    if not isinstance(providers,dict) or len(providers)!=3:
        return {**HOLD,"reasons":["THREE_PROVIDER_KEYS_REQUIRED"]}
    families=[]
    for kid,info in sorted(providers.items()):
        try:
            fam=ancestry(info["controller_id"],graph)
            if fam & root:problems.append("PROVIDER_JOURNAL_SHARED_ANCESTRY")
            if fam & clock_family:problems.append("CLOCK_PROVIDER_SHARED_ANCESTRY")
            if any(fam & x for x in families):problems.append("PROVIDER_SHARED_ANCESTRY")
            families.append(fam)
        except (ValueError,KeyError,TypeError):
            problems.append("PROVIDER_ANCESTRY_INVALID")
    version_index={};times_by_seq={};seen_nonces=set()
    version_fields={"schema","controller_id","provider_id","window_seq","artifact_sha256",
                    "object_key","object_version","object_lock_mode","retention_until_claim",
                    "nonce","signature_b64"}
    clock_fields={"schema","controller_id","window_seq","window_head_sha256",
                  "observed_unix_ms_claim","nonce","signature_b64"}
    for v in versions:
        try:
            ensure_canonical(v,version_fields)
            kid=v["provider_id"];seq=v["window_seq"];key=(seq,kid)
            if key in version_index:problems.append("VERSION_ATTESTATION_DUPLICATE")
            version_index[key]=v
            if kid not in providers or type(seq) is not int or seq not in (1,2):
                problems.append("VERSION_ATTESTATION_SOURCE_INVALID");continue
            attested(v,providers[kid],pin,VERSION_SCHEMA)
            if not all(isinstance(v[k],str) and 0<len(v[k])<=512 for k in
                       ("object_key","object_version","retention_until_claim")):
                problems.append("PROVIDER_OBJECT_METADATA_INVALID")
            if v["object_lock_mode"] not in ("COMPLIANCE","GOVERNANCE"):
                problems.append("PROVIDER_OBJECT_LOCK_NOT_ASSERTED")
            if not ishash(v["artifact_sha256"]) or v["artifact_sha256"]!=windows[seq-1]["artifact_sha"]:
                problems.append("PROVIDER_OBJECT_DIGEST_DIVERGENCE")
            nonce=v["nonce"]
            if not isinstance(nonce,str) or not nonce or nonce in seen_nonces:
                problems.append("ATTESTATION_NONCE_REUSE")
            seen_nonces.add(nonce)
        except (ValueError,TypeError,KeyError,UnicodeError):
            problems.append("VERSION_ATTESTATION_INVALID")
    for t in times:
        try:
            ensure_canonical(t,clock_fields)
            seq=t["window_seq"]
            if type(seq) is not int or seq not in (1,2):
                problems.append("CLOCK_WINDOW_INVALID");continue
            if seq in times_by_seq:problems.append("CLOCK_DUPLICATE_WINDOW")
            times_by_seq[seq]=t
            attested(t,clock,pin,CLOCK_SCHEMA)
            if t["window_head_sha256"]!=windows[seq-1]["head_sha"]:
                problems.append("CLOCK_WINDOW_HEAD_DIVERGENCE")
            if type(t["observed_unix_ms_claim"]) is not int or t["observed_unix_ms_claim"]<1:
                problems.append("CLOCK_TIMESTAMP_INVALID")
            nonce=t["nonce"]
            if not isinstance(nonce,str) or not nonce or nonce in seen_nonces:
                problems.append("ATTESTATION_NONCE_REUSE")
            seen_nonces.add(nonce)
        except (ValueError,TypeError,KeyError,UnicodeError):
            problems.append("CLOCK_ATTESTATION_INVALID")
    if len(version_index)!=6:problems.append("VERSION_COVERAGE_INCOMPLETE")
    if set(times_by_seq)!={1,2}:problems.append("CLOCK_COVERAGE_INCOMPLETE")
    else:
        first=times_by_seq[1]["observed_unix_ms_claim"]
        second=times_by_seq[2]["observed_unix_ms_claim"]
        if type(first) is int and type(second) is int and second<=first:
            problems.append("CLOCK_WINDOW_NOT_INCREASING")
    for kid in providers:
        first=version_index.get((1,kid));second=version_index.get((2,kid))
        if first and second and (first["object_key"]!=second["object_key"] or
                                 first["object_version"]!=second["object_version"]):
            problems.append("PROVIDER_OBJECT_VERSION_CHANGED")
    for seq,row in enumerate(windows,1):
        try:
            manifest=json.loads(row["manifest_json"])
            reading_ids={v["endpoint_id"] for v in manifest["readings"]}
            if reading_ids!=set(providers) or len(manifest["readings"])!=3:
                problems.append("PROVIDER_WINDOW_SOURCE_MISMATCH")
            if manifest["artifact_sha256"]!=row["artifact_sha"] or
               manifest["window_nonce"]!=row["window_nonce"]:
                problems.append("WINDOW_PREIMAGE_CONFLICT")
        except (ValueError,KeyError,TypeError):
            problems.append("WINDOW_PREIMAGE_INVALID")
    problems+=["PROVIDER_ATTESTATION_NOT_AUTHENTICATED_WITH_PROVIDER_API",
               "CLOCK_ROOT_NOT_EXTERNALLY_ATTESTED",
               "CONTROLLER_GRAPH_SELF_DECLARED",
               "REMOTE_OBJECT_LOCK_NOT_INDEPENDENTLY_OBSERVED",
               "LOCAL_DATABASE_AND_PINS_ROLLBACK_POSSIBLE"]
    return {**HOLD,"reasons":sorted(set(problems)),
            "observed":{"windows":len(windows),"version_attestations":len(versions),
                        "clock_attestations":len(times),
                        "matching_local_claims":not any(reason not in {
                          "PROVIDER_ATTESTATION_NOT_AUTHENTICATED_WITH_PROVIDER_API",
                          "CLOCK_ROOT_NOT_EXTERNALLY_ATTESTED","CONTROLLER_GRAPH_SELF_DECLARED",
                          "REMOTE_OBJECT_LOCK_NOT_INDEPENDENTLY_OBSERVED",
                          "LOCAL_DATABASE_AND_PINS_ROLLBACK_POSSIBLE"} for reason in problems)}}
def main():
    p=argparse.ArgumentParser()
    for name in ("db","trust","versions","times"):
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--trust-sha256",required=True)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        windows,nonces=read_291(args.db)
        baseline=audit_291(args.db)
        failures=set(baseline["reasons"])-{
            "WINDOW_ORDINAL_NOT_AUTHENTICATED_TIME",
            "REMOTE_IMMUTABILITY_NOT_ESTABLISHED",
            "INDEPENDENT_OPERATOR_CUSTODY_UNVERIFIED",
            "LOCAL_HISTORY_AND_PIN_CAN_ROLL_BACK"}
        if failures:raise ValueError("BASELINE_291_INVALID:"+",".join(sorted(failures)))
        raw=[args.trust.read_bytes(),args.versions.read_bytes(),args.times.read_bytes()]
        if any(len(data)>1_000_000 for data in raw):raise ValueError("INPUT_LIMIT")
        result=qualify(windows,nonces,*(json.loads(x) for x in (raw[0],)),args.trust_sha256,
                       json.loads(raw[1]),json.loads(raw[2]))
    except (OSError,ValueError,KeyError,TypeError) as e:
        result={**HOLD,"reasons":["INPUT_REJECTED:"+type(e).__name__+":"+str(e)[:100]]}
    output=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.out:
        args.out.write_text(output,encoding="utf-8")
    print(output,end="")
    return 1
if __name__=="__main__":raise SystemExit(main())
