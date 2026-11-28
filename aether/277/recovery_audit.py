#!/usr/bin/env python3
"""AETHER-277-RS: read-only key rotation ancestry and restart checkpoint audit.

An in-bundle anchor/key does not demonstrate independent third-party custody.
"""
import argparse,base64,hashlib,json,sqlite3
from pathlib import Path

SCHEMA="AETHER-277/recovery-audit-v1"
ROTATION_SCHEMA="AETHER-276/durable-receipts-v1"
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "external_custody_verified":False,"external_antirollback_verified":False}

def canon(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def sha(v):return hashlib.sha256(canon(v)).hexdigest()
def hash_pem(pem):return hashlib.sha256(pem.encode()).hexdigest()
def hex64(v):return isinstance(v,str) and len(v)==64 and all(x in "0123456789abcdef" for x in v)

def verify(pem,data,signature):
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.exceptions import InvalidSignature
        key=serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key,Ed25519PublicKey):return False
        raw=base64.b64decode(signature,validate=True)
        if len(raw)!=64:return False
        key.verify(raw,canon(data));return True
    except (ImportError,InvalidSignature,ValueError,TypeError,UnicodeError):return False

def read_local(db_path):
    """No PRAGMA journal_mode or schema initialization; read an existing 276 DB."""
    uri=Path(db_path).resolve().as_uri()+"?mode=ro"
    db=sqlite3.connect(uri,uri=True,timeout=5,isolation_level=None)
    try:
        db.execute("BEGIN")
        rows=[dict(zip(("source_id","controller","key_pem","version"),r)) for r in
              db.execute("SELECT source_id,controller,key_pem,version FROM signer ORDER BY source_id")]
        rotations=[dict(zip(("source_id","old_key_sha","new_key_sha","old_sig_b64",
              "new_sig_b64","previous_registry_sha","next_registry_sha"),r)) for r in
              db.execute("SELECT source_id,old_key_sha,new_key_sha,old_sig_b64,new_sig_b64,previous_registry_sha,next_registry_sha FROM rotation ORDER BY id")]
        challenges=db.execute("SELECT COUNT(*) FROM challenge").fetchone()[0]
        receipts=db.execute("SELECT COUNT(*) FROM receipt").fetchone()[0]
        db.commit()
    finally:db.close()
    return {"registry_rows":rows,"rotation_log":rotations,
            "challenges":challenges,"receipts":receipts}

def audit(bundle,local,expected_anchor_digest):
    issues=[];observed={"rotation_signatures":[]}
    if not hex64(expected_anchor_digest):
        return {**HOLD,"reasons":["OUT_OF_BAND_ANCHOR_PIN_REQUIRED"],"observed":observed}
    if not isinstance(bundle,dict) or set(bundle)!={"base_registry","rotation_history",
        "checkpoint","anchor_public_key_pem","anchor_signature_b64"}:
        return {**HOLD,"reasons":["AUDIT_BUNDLE_INVALID"],"observed":observed}
    checkpoint=bundle["checkpoint"]
    required={"schema","base_registry_sha256","head_registry_sha256",
              "rotation_count","minimum_challenges","minimum_receipts","anchor_nonce"}
    if not isinstance(checkpoint,dict) or set(checkpoint)!=required:
        return {**HOLD,"reasons":["CHECKPOINT_SCHEMA_INVALID"],"observed":observed}
    if sha(checkpoint)!=expected_anchor_digest:issues.append("ANCHOR_PIN_MISMATCH")
    if checkpoint["schema"]!=SCHEMA:issues.append("CHECKPOINT_VERSION_INVALID")
    for field in ("rotation_count","minimum_challenges","minimum_receipts"):
        if type(checkpoint[field]) is not int or checkpoint[field]<0:
            issues.append("CHECKPOINT_COUNTER_INVALID")
    if not isinstance(checkpoint["anchor_nonce"],str) or not checkpoint["anchor_nonce"]:
        issues.append("ANCHOR_NONCE_INVALID")
    if not verify(bundle["anchor_public_key_pem"],checkpoint,bundle["anchor_signature_b64"]):
        issues.append("ANCHOR_SIGNATURE_INVALID")
    base=bundle["base_registry"];rotations=bundle["rotation_history"]
    if not isinstance(base,list) or len(base)!=3 or not isinstance(rotations,list) or len(rotations)>128:
        return {**HOLD,"reasons":sorted(set(issues+["ANCESTRY_INPUT_INVALID"])),"observed":observed}
    current={}
    controllers=set()
    for row in base:
        if not isinstance(row,dict) or set(row)!={"source_id","controller","key_pem","version"}:
            issues.append("BASE_ROW_INVALID");continue
        sid=row["source_id"]
        if not isinstance(sid,str) or not sid or sid in current:
            issues.append("BASE_DUPLICATE_SOURCE");continue
        if row["version"]!=1 or not isinstance(row["controller"],str) or not row["controller"] or row["controller"] in controllers or not isinstance(row["key_pem"],str):
            issues.append("BASE_OWNER_OR_VERSION_INVALID")
        controllers.add(row["controller"])
        current[sid]=dict(row)
    def registry_digest():
        return sha([current[s] for s in sorted(current)])
    if len(current)!=3:issues.append("BASE_INCOMPLETE")
    if registry_digest()!=checkpoint["base_registry_sha256"]:
        issues.append("BASE_ANCHOR_MISMATCH")
    chain_log=[]
    for index,transition in enumerate(rotations):
        keys={"source_id","new_key_pem","old_signature_b64","new_signature_b64"}
        if not isinstance(transition,dict) or set(transition)!=keys:
            issues.append("ROTATION_SCHEMA_INVALID");continue
        sid=transition["source_id"]
        old=current.get(sid)
        if not old:issues.append("ROTATION_SOURCE_UNKNOWN");continue
        new_pem=transition["new_key_pem"]
        if not isinstance(new_pem,str) or new_pem==old["key_pem"] or len(new_pem)>4096:
            issues.append("ROTATION_KEY_INVALID");continue
        prev=registry_digest()
        stmt={"schema":ROTATION_SCHEMA,"operation":"ROTATE",
              "source_id":sid,"controller":old["controller"],
              "previous_registry_sha256":prev,
              "old_key_sha256":hash_pem(old["key_pem"]),
              "new_key_sha256":hash_pem(new_pem),
              "next_version":old["version"]+1}
        old_ok=verify(old["key_pem"],stmt,transition["old_signature_b64"])
        new_ok=verify(new_pem,stmt,transition["new_signature_b64"])
        observed["rotation_signatures"].append({"index":index,"old_valid":old_ok,"new_valid":new_ok})
        if not old_ok:issues.append("OLD_ROTATION_SIGNATURE_INVALID")
        if not new_ok:issues.append("NEW_ROTATION_SIGNATURE_INVALID")
        if not (old_ok and new_ok):continue
        current[sid]={**old,"key_pem":new_pem,"version":old["version"]+1}
        after=registry_digest()
        chain_log.append({"source_id":sid,"old_key_sha":stmt["old_key_sha256"],
                          "new_key_sha":stmt["new_key_sha256"],
                          "old_sig_b64":transition["old_signature_b64"],
                          "new_sig_b64":transition["new_signature_b64"],
                          "previous_registry_sha":prev,"next_registry_sha":after})
    if len(rotations)<checkpoint["rotation_count"]:
        issues.append("ROTATION_COUNT_ROLLBACK")
    if registry_digest()!=checkpoint["head_registry_sha256"]:
        issues.append("ANCHORED_HEAD_CONFLICT")
    if not isinstance(local,dict) or set(local)!={"registry_rows","rotation_log","challenges","receipts"}:
        issues.append("LOCAL_READBACK_INVALID")
    else:
        if local["registry_rows"]!=[current[k] for k in sorted(current)]:
            issues.append("RESTART_REGISTRY_MISMATCH")
        if local["rotation_log"]!=chain_log:
            issues.append("RESTART_ROTATION_LOG_MISMATCH")
        if type(local["challenges"]) is not int or local["challenges"]<checkpoint["minimum_challenges"]:
            issues.append("CHALLENGE_COUNT_ROLLBACK")
        if type(local["receipts"]) is not int or local["receipts"]<checkpoint["minimum_receipts"]:
            issues.append("RECEIPT_COUNT_ROLLBACK")
        if type(local["receipts"]) is int and type(local["challenges"]) is int and local["receipts"]!=3*local["challenges"]:
            issues.append("THREE_RECEIPTS_PER_CHALLENGE_VIOLATED")
    issues+=["ANCHOR_PEM_OWNERSHIP_NOT_INDEPENDENTLY_AUTHENTICATED",
             "ANCHOR_CHECKPOINT_NOT_EXTERNALLY_RETAINED",
             "LOCAL_DB_REPLACEMENT_STILL_POSSIBLE"]
    return {**HOLD,"reasons":sorted(set(issues)),"observed":observed}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db",type=Path,required=True)
    p.add_argument("--bundle",type=Path,required=True)
    p.add_argument("--trusted-anchor-sha256",required=True)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    try:
        raw=a.bundle.read_bytes()
        if len(raw)>1024*1024:raise ValueError("BUNDLE_OVERSIZE")
        result=audit(json.loads(raw),read_local(a.db),a.trusted_anchor_sha256)
    except (OSError,ValueError,TypeError,UnicodeError,sqlite3.Error) as error:
        result={**HOLD,"reasons":["INPUT_REJECTED:"+type(error).__name__]}
    output=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(output,encoding="utf-8")
    print(output,end="")
    return 1
if __name__=="__main__":raise SystemExit(main())
