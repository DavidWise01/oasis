#!/usr/bin/env python3
"""AETHER-293-RS: provider-native response preimage & time-chain qualification.

Input is preserved evidence, not an authenticated provider API session.
Caller-supplied provider roots and time roots cannot prove independent custody.
"""
import argparse,base64,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"291"))
sys.path.insert(0,str(ROOT/"292"))
from two_window_readback import read as read_291,audit as audit_291
from attestation_audit import ancestry,verify

VERSION="AETHER-293/provider-object-response-v1"
CLOCK="AETHER-293/signed-time-chain-v1"
ZERO="0"*64
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "provider_api_authentication_verified":False,
      "independent_clock_authority_verified":False,
      "independent_custody_verified":False}
BASE_GAPS={"WINDOW_ORDINAL_NOT_AUTHENTICATED_TIME",
           "REMOTE_IMMUTABILITY_NOT_ESTABLISHED",
           "INDEPENDENT_OPERATOR_CUSTODY_UNVERIFIED",
           "LOCAL_HISTORY_AND_PIN_CAN_ROLL_BACK"}

def canon(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def digest(value):return hashlib.sha256(value).hexdigest()
def sha(value):return digest(canon(value))
def hex64(v):return isinstance(v,str) and len(v)==64 and all(c in "0123456789abcdef" for c in v)
def decode_record(record):
    if not isinstance(record,dict) or set(record)!={"provider_id","window_seq","url","raw_b64","raw_sha256","transport"}:
        raise ValueError("RESPONSE_ENVELOPE_INVALID")
    if not isinstance(record["raw_b64"],str) or len(record["raw_b64"])>90000:
        raise ValueError("RESPONSE_TOO_LARGE")
    raw=base64.b64decode(record["raw_b64"],validate=True)
    if len(raw)>65536 or digest(raw)!=record["raw_sha256"]:
        raise ValueError("RESPONSE_RAW_DIGEST_INVALID")
    response=json.loads(raw)
    if canon(response)!=raw or not isinstance(response,dict):
        raise ValueError("RESPONSE_NOT_CANONICAL")
    fields={"schema","provider_id","window_seq","artifact_sha256","object_key",
            "version_id","lock_mode","retention_until_claim","response_request_id",
            "response_nonce"}
    if set(response)!=fields or response["schema"]!=VERSION:
        raise ValueError("PROVIDER_RESPONSE_SCHEMA_INVALID")
    transport=record["transport"]
    if not isinstance(transport,dict) or set(transport)!={"tls_peer_claim","response_status","request_id","acquisition_observation_sha256"}:
        raise ValueError("TRANSPORT_SCHEMA_INVALID")
    if (transport["tls_peer_claim"] is not True or type(transport["response_status"]) is not int
        or transport["response_status"]!=200 or transport["request_id"]!=response["response_request_id"]
        or not hex64(transport["acquisition_observation_sha256"])):
        raise ValueError("TRANSPORT_CLAIM_INVALID")
    return response

def verify_chain(windows,records,clock_claims,trust,pin):
    problems=[]
    if not isinstance(trust,dict) or set(trust)!={"journal_controller","graph","providers","clock"}:
        return {**HOLD,"reasons":["TRUST_SCHEMA_INVALID"]}
    if not hex64(pin) or sha(trust)!=pin:return {**HOLD,"reasons":["TRUST_ROOT_PIN_MISMATCH"]}
    if not isinstance(windows,list) or len(windows)!=2:
        return {**HOLD,"reasons":["TWO_WINDOWS_REQUIRED"]}
    if not isinstance(records,list) or len(records)!=6 or not isinstance(clock_claims,list) or len(clock_claims)!=2:
        return {**HOLD,"reasons":["SIX_PROVIDER_AND_TWO_CLOCK_RECORDS_REQUIRED"]}
    graph=trust["graph"];providers=trust["providers"];clock=trust["clock"]
    if not isinstance(graph,dict) or not isinstance(providers,dict) or len(providers)!=3 or not isinstance(clock,dict):
        return {**HOLD,"reasons":["TRUST_KEYS_INVALID"]}
    try:
        families=[]
        journal=ancestry(trust["journal_controller"],graph)
        time_family=ancestry(clock["controller_id"],graph)
        if journal & time_family:problems.append("CLOCK_JOURNAL_SHARED_ANCESTRY")
        for kid in sorted(providers):
            fam=ancestry(providers[kid]["controller_id"],graph)
            if fam & journal:problems.append("PROVIDER_JOURNAL_SHARED_ANCESTRY")
            if fam & time_family:problems.append("CLOCK_PROVIDER_SHARED_ANCESTRY")
            if any(fam & other for other in families):problems.append("PROVIDERS_SHARED_ANCESTRY")
            families.append(fam)
    except (KeyError,ValueError,TypeError):
        return {**HOLD,"reasons":["ANCESTRY_GRAPH_INVALID"]}
    object_versions={};source_seen=set();nonce_seen=set()
    for record in records:
        try:
            response=decode_record(record)
            kid=response["provider_id"];seq=response["window_seq"]
            if kid not in providers or type(seq) is not int or seq not in (1,2):
                problems.append("PROVIDER_OR_WINDOW_UNKNOWN");continue
            if record["provider_id"]!=kid or record["window_seq"]!=seq:
                problems.append("RESPONSE_ENVELOPE_BINDING_INVALID")
            if not isinstance(record["url"],str) or not record["url"].startswith("https://"):
                problems.append("SOURCE_URL_INVALID")
            key=(seq,kid)
            if key in source_seen:problems.append("DUPLICATE_PROVIDER_WINDOW")
            source_seen.add(key)
            if response["artifact_sha256"]!=windows[seq-1]["artifact_sha"]:
                problems.append("OBJECT_CONTENT_DIGEST_MISMATCH")
            if not all(isinstance(response[field],str) and 0<len(response[field])<=256 for field in
                       ("object_key","version_id","retention_until_claim","response_request_id","response_nonce")):
                problems.append("PROVIDER_METADATA_INVALID")
            if response["lock_mode"] not in ("COMPLIANCE","GOVERNANCE"):
                problems.append("OBJECT_LOCK_MODE_INVALID")
            if response["response_nonce"] in nonce_seen:
                problems.append("PROVIDER_NONCE_REPLAY")
            nonce_seen.add(response["response_nonce"])
            if key in object_versions:
                problems.append("VERSION_PAIR_REUSED")
            object_versions[key]=(response["object_key"],response["version_id"])
            meta=providers[kid]
            if not isinstance(meta,dict) or set(meta)!={"controller_id","api_origin_claim"}:
                problems.append("PROVIDER_TRUST_ENTRY_INVALID")
            elif response["provider_id"]!=kid or not record["url"].startswith(meta["api_origin_claim"].rstrip("/")+"/"):
                problems.append("PROVIDER_API_ORIGIN_MISMATCH")
        except (ValueError,KeyError,TypeError,UnicodeError):
            problems.append("RETAINED_PROVIDER_RESPONSE_INVALID")
    if source_seen!={(seq,kid) for seq in (1,2) for kid in providers}:
        problems.append("PROVIDER_COVERAGE_INCOMPLETE")
    for kid in providers:
        a=object_versions.get((1,kid));b=object_versions.get((2,kid))
        if a and b and a!=b:problems.append("OBJECT_VERSION_CHANGED_ACROSS_WINDOWS")
    last=ZERO;clock_times=[]
    for seq,claim in enumerate(clock_claims,1):
        required={"schema","controller_id","window_seq","window_head_sha256",
                  "previous_attestation_sha256","unix_ms_claim","nonce","signature_b64"}
        if not isinstance(claim,dict) or set(claim)!=required:
            problems.append("CLOCK_RECORD_SCHEMA_INVALID");continue
        if claim["schema"]!=CLOCK or claim["controller_id"]!=clock.get("controller_id"):
            problems.append("CLOCK_IDENTITY_INVALID")
        statement={k:v for k,v in claim.items() if k!="signature_b64"}
        if not verify(clock.get("public_key_pem",""),statement,claim["signature_b64"]):
            problems.append("CLOCK_SIGNATURE_INVALID")
        if (type(claim["window_seq"]) is not int or claim["window_seq"]!=seq
            or claim["window_head_sha256"]!=windows[seq-1]["head_sha"]):
            problems.append("CLOCK_WINDOW_BINDING_INVALID")
        if claim["previous_attestation_sha256"]!=last:
            problems.append("CLOCK_CHAIN_PREDECESSOR_INVALID")
        last=sha(claim)
        timestamp=claim["unix_ms_claim"]
        if type(timestamp) is not int or timestamp<=0:
            problems.append("CLOCK_TIMESTAMP_INVALID")
        else:clock_times.append(timestamp)
        if not isinstance(claim["nonce"],str) or not claim["nonce"] or claim["nonce"] in nonce_seen:
            problems.append("CLOCK_NONCE_REPLAY")
        nonce_seen.add(claim["nonce"])
    if len(clock_times)==2 and clock_times[1]<=clock_times[0]:
        problems.append("CLOCK_TIME_NONMONOTONIC")
    problems.extend(["PROVIDER_RESPONSE_AUTHENTICITY_UNVERIFIED",
                     "OBJECT_LOCK_POLICY_NOT_INDEPENDENTLY_OBSERVED",
                     "CLOCK_OPERATOR_IDENTITY_UNVERIFIED",
                     "CONTROLLER_GRAPH_SELF_DECLARED",
                     "NO_TRUSTED_ELAPSED_TIME_OR_CUSTODY"])
    return {**HOLD,"reasons":sorted(set(problems)),
            "observed":{"provider_records":len(records),"time_records":len(clock_claims),
                        "clock_claimed_interval_ms":clock_times[1]-clock_times[0] if len(clock_times)==2 else None,
                        "input_claims_consistent":not any(p not in {
                          "PROVIDER_RESPONSE_AUTHENTICITY_UNVERIFIED",
                          "OBJECT_LOCK_POLICY_NOT_INDEPENDENTLY_OBSERVED",
                          "CLOCK_OPERATOR_IDENTITY_UNVERIFIED",
                          "CONTROLLER_GRAPH_SELF_DECLARED",
                          "NO_TRUSTED_ELAPSED_TIME_OR_CUSTODY"} for p in problems)}}
def main():
    parser=argparse.ArgumentParser()
    for field in ("journal","trust","responses","clock-chain"):
        parser.add_argument("--"+field,type=Path,required=True)
    parser.add_argument("--pin",required=True);parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    try:
        baseline=audit_291(args.journal)
        failures=set(baseline["reasons"])-BASE_GAPS
        if failures:raise ValueError("AETHER291_BASELINE_INVALID:"+",".join(sorted(failures)))
        windows,_=read_291(args.journal)
        inputs=[args.trust.read_bytes(),args.responses.read_bytes(),args.clock_chain.read_bytes()]
        if any(len(blob)>1024*1024 for blob in inputs):raise ValueError("INPUT_TOO_LARGE")
        result=verify_chain(windows,json.loads(inputs[1]),json.loads(inputs[2]),json.loads(inputs[0]),args.pin)
    except (OSError,ValueError,TypeError,KeyError) as e:
        result={**HOLD,"reasons":["INPUT_REJECTED:"+type(e).__name__+":"+str(e)[:100]]}
    output=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.out:args.out.write_text(output,encoding="utf-8")
    print(output,end="")
    return 1
if __name__=="__main__":raise SystemExit(main())
