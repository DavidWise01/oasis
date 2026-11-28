#!/usr/bin/env python3
"""AETHER-283-RS: retained-journal recovery and claimed external prefix witness.

Caller-supplied witness records, keys and ancestry cannot prove independence.
"""
import argparse,base64,hashlib,json,sqlite3,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"282"))
from retained_journal import examine,sha,canon

SCHEMA="AETHER-283/prefix-witness-v1"
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "independent_prefix_custody_verified":False,"external_antirollback_verified":False}

def hex64(v):
    return isinstance(v,str) and len(v)==64 and all(x in "0123456789abcdef" for x in v)

def verify(pem,statement,signature_b64):
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key=serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key,Ed25519PublicKey):return False
        signature=base64.b64decode(signature_b64,validate=True)
        if len(signature)!=64:return False
        key.verify(signature,canon(statement))
        return True
    except (ImportError,InvalidSignature,TypeError,ValueError,UnicodeError):
        return False

def heads(path):
    """Use a read-only query against the historical, signed-challenge journal."""
    uri=Path(path).resolve().as_uri()+"?mode=ro"
    db=sqlite3.connect(uri,uri=True,isolation_level=None,timeout=5)
    try:
        db.execute("PRAGMA query_only=ON")
        db.execute("BEGIN")
        result=[{"seq":r[0],"head_sha256":r[1],"previous_sha256":r[2]}
                for r in db.execute("SELECT seq,head_sha,previous_sha FROM head ORDER BY seq")]
        db.commit()
        return result
    finally:
        db.close()

def assess(path,bundle,trust_digest):
    observations={"witness_signatures":[]}
    if not hex64(trust_digest):
        return {**HOLD,"reasons":["OUT_OF_BAND_TRUST_DIGEST_REQUIRED"],"observed":observations}
    if not isinstance(bundle,dict) or set(bundle)!={"trust_record","witnesses","previous_witness_nonces"}:
        return {**HOLD,"reasons":["BUNDLE_SCHEMA_INVALID"],"observed":observations}
    trust=bundle["trust_record"]
    if not isinstance(trust,dict) or set(trust)!={"witness_keys","controller_ancestry","journal_controller"}:
        return {**HOLD,"reasons":["TRUST_RECORD_SCHEMA_INVALID"],"observed":observations}
    problems=[]
    if sha(trust)!=trust_digest:problems.append("OUT_OF_BAND_TRUST_DIGEST_MISMATCH")
    witness_keys=trust["witness_keys"]
    graph=trust["controller_ancestry"]
    if not isinstance(witness_keys,dict) or not isinstance(graph,dict):
        return {**HOLD,"reasons":["TRUST_FIELDS_INVALID"],"observed":observations}
    witnesses=bundle["witnesses"]
    history=bundle["previous_witness_nonces"]
    if not isinstance(witnesses,list) or len(witnesses)!=3:
        problems.append("THREE_PREFIX_WITNESSES_REQUIRED");witnesses=[]
    if not isinstance(history,list) or len(history)>4096 or any(not isinstance(n,str) for n in history):
        problems.append("WITNESS_HISTORY_INVALID");history=[]
    if len(history)!=len(set(history)):problems.append("WITNESS_HISTORY_DUPLICATE")
    def ancestry(node):
        visited=set();active=set()
        def visit(n):
            if not isinstance(n,str) or not n or len(n)>128:raise ValueError("CONTROLLER_NODE_INVALID")
            if n in active:raise ValueError("CONTROLLER_CYCLE")
            if n in visited:return
            if n not in graph:raise ValueError("CONTROLLER_GRAPH_INCOMPLETE")
            parents=graph[n]
            if not isinstance(parents,list) or len(parents)>16:raise ValueError("CONTROLLER_PARENTS_INVALID")
            active.add(n);visited.add(n)
            if len(visited)>256:raise ValueError("CONTROLLER_GRAPH_BOUNDS")
            for p in parents:visit(p)
            active.remove(n)
        visit(node);return visited
    try:journal_family=ancestry(trust["journal_controller"])
    except ValueError as e:problems.append(str(e));journal_family=set()
    local_heads=heads(path)
    recovered=examine(path)
    problems.extend("JOURNAL_"+reason for reason in recovered["reasons"]
                    if reason not in {"EXTERNAL_PREFIX_CUSTODY_UNVERIFIED",
                                      "CONTROLLER_INDEPENDENCE_UNVERIFIED",
                                      "LOCAL_DATABASE_REPLACEMENT_POSSIBLE"})
    keys_seen=set();controllers=[];nonce_seen=set();claims=[]
    for witness in witnesses:
        required={"key_id","controller_id","witness_nonce","prefix_seq",
                  "prefix_sha256","run_id","signature_b64"}
        if not isinstance(witness,dict) or set(witness)!=required:
            problems.append("WITNESS_SCHEMA_INVALID");continue
        key=witness["key_id"];controller=witness["controller_id"]
        nonce=witness["witness_nonce"]
        if not isinstance(key,str) or key in keys_seen:problems.append("WITNESS_KEY_REUSE")
        if isinstance(key,str):keys_seen.add(key)
        if not isinstance(nonce,str) or not nonce or nonce in nonce_seen or nonce in history:
            problems.append("WITNESS_NONCE_REPLAY")
        if isinstance(nonce,str):nonce_seen.add(nonce)
        if type(witness["prefix_seq"]) is not int or witness["prefix_seq"]<1 or not hex64(witness["prefix_sha256"]):
            problems.append("PREFIX_FORMAT_INVALID")
        elif witness["prefix_seq"]>len(local_heads):
            problems.append("ANCHORED_PREFIX_REMOVED")
        elif local_heads[witness["prefix_seq"]-1]["head_sha256"]!=witness["prefix_sha256"]:
            problems.append("ANCHORED_PREFIX_REWRITTEN")
        if type(witness["run_id"]) is not int or witness["run_id"]<1:
            problems.append("WITNESS_RUN_INVALID")
        try:
            family=ancestry(controller)
            controllers.append(family)
            if family & journal_family:problems.append("SELF_ISSUED_OR_SHARED_JOURNAL_ANCESTRY")
        except ValueError as e:problems.append(str(e))
        statement={"schema":SCHEMA,**{k:witness[k] for k in required if k!="signature_b64"}}
        pinned=witness_keys.get(key)
        valid=False
        if not isinstance(pinned,dict) or set(pinned)!={"controller_id","public_key_pem"} or pinned["controller_id"]!=controller:
            problems.append("WITNESS_KEY_PIN_MISMATCH")
        else:
            valid=verify(pinned["public_key_pem"],statement,witness["signature_b64"])
            if not valid:problems.append("WITNESS_SIGNATURE_INVALID")
        claims.append((witness["prefix_seq"],witness["prefix_sha256"]))
        observations["witness_signatures"].append({"key_id":key,"valid":valid})
    for i,family in enumerate(controllers):
        for other in controllers[i+1:]:
            if family & other:problems.append("WITNESS_SHARED_CONTROLLER_ANCESTRY")
    if len(set(claims))>1:problems.append("WITNESS_PREFIX_CLAIM_CONFLICT")
    problems+=["WITNESS_PUBLIC_KEY_CUSTODY_UNVERIFIED",
               "CLAIMED_CONTROLLER_GRAPH_NOT_INDEPENDENTLY_ATTESTED",
               "WITNESS_HISTORY_NOT_EXTERNALLY_PERSISTED",
               "LOCAL_JOURNAL_CAN_BE_REPLACED"]
    observations["local_heads"]=len(local_heads)
    observations["recovery"]=recovered["observed"]
    return {**HOLD,"reasons":sorted(set(problems)),"observed":observations}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db",type=Path,required=True)
    p.add_argument("--witness-bundle",type=Path,required=True)
    p.add_argument("--trusted-record-sha256",required=True)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    try:
        raw=a.witness_bundle.read_bytes()
        if len(raw)>1024*1024:raise ValueError("BUNDLE_TOO_LARGE")
        report=assess(a.db,json.loads(raw),a.trusted_record_sha256)
    except (OSError,ValueError,TypeError,KeyError,sqlite3.Error) as exc:
        report={**HOLD,"reasons":["INPUT_REJECTED:"+type(exc).__name__]}
    result=json.dumps(report,indent=2,sort_keys=True)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(result,encoding="utf-8")
    print(result,end="")
    return 1
if __name__=="__main__":raise SystemExit(main())
