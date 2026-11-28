#!/usr/bin/env python3
"""AETHER-287-RS: byte-exact manifest export and signed custody-claim readback.

External custody remains unproven until identity, ancestry, and independent
archival retention are independently established. Operational ACT stays HOLD.
"""
import argparse,base64,hashlib,json,os,sqlite3,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"286"))
from atomic_manifest import readback,audit_rows,sha,canonical,ZERO

SCHEMA="AETHER-287/export-v1"
ACK_SCHEMA="AETHER-287/acknowledgment-v1"
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "independent_external_custody_verified":False,
      "externally_anchored_rollback_resistance":False}

def hex64(x):
    return isinstance(x,str) and len(x)==64 and all(c in "0123456789abcdef" for c in x)

def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()

def verify(pem,statement,b64):
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        pub=serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(pub,Ed25519PublicKey):return False
        raw=base64.b64decode(b64,validate=True)
        if len(raw)!=64:return False
        pub.verify(raw,canonical(statement))
        return True
    except (ImportError,InvalidSignature,ValueError,TypeError,UnicodeError):
        return False

def make_export(rows,nonces,seq):
    """Reproduce recorded manifest preimages; do not manufacture missing bytes."""
    faults=audit_rows(rows,nonces)
    if faults:raise ValueError("LOCAL_JOURNAL_INVALID:"+",".join(faults))
    if type(seq) is not int or not 1<=seq<=len(rows):
        raise ValueError("EXPORT_SEQUENCE_INVALID")
    row=rows[seq-1]
    if row["id"]!=seq:raise ValueError("EXPORT_SEQUENCE_CONFLICT")
    manifest_text=row["manifest_json"]
    if not isinstance(manifest_text,str):raise ValueError("MANIFEST_NOT_RETAINED")
    manifest=json.loads(manifest_text)
    raw=manifest_text.encode("utf-8")
    if canonical(manifest)!=raw or sha_bytes(raw)!=row["head_sha"]:
        raise ValueError("MANIFEST_PREIMAGE_CONFLICT")
    batch_nonces=sorted([n for n in nonces if n["batch_id"]==seq],
                        key=lambda n:(n["key_id"],n["nonce"]))
    artifact={"schema":SCHEMA,"batch_id":seq,"head_sha256":row["head_sha"],
              "previous_head_sha256":row["previous_sha"],
              "trust_sha256":row["trust_sha"],
              "manifest_bytes_b64":base64.b64encode(raw).decode("ascii"),
              "nonce_rows":batch_nonces}
    artifact["artifact_sha256"]=sha(artifact)
    return artifact

def export(path,seq,destination):
    rows,nonces=readback(path)
    artifact=make_export(rows,nonces,seq)
    output=canonical(artifact)
    # Refuse overwrite. fsync file and parent directory on POSIX.
    destination=Path(destination)
    if destination.is_symlink():raise ValueError("EXPORT_SYMLINK_REJECTED")
    fd=os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        with os.fdopen(fd,"wb") as out:
            out.write(output)
            out.flush()
            os.fsync(out.fileno())
    except BaseException:
        try:destination.unlink()
        except OSError:pass
        raise
    if os.name=="posix":
        dfd=os.open(destination.parent,os.O_RDONLY)
        try:os.fsync(dfd)
        finally:os.close(dfd)
    return {**HOLD,"batch_id":seq,"artifact_sha256":artifact["artifact_sha256"],
            "export_bytes_sha256":sha_bytes(output),
            "reasons":["EXPORT_NOT_YET_INDEPENDENTLY_RETAINED"]}

def ancestry(controller,graph):
    seen=set();active=set()
    def visit(node):
        if not isinstance(node,str) or not node or len(node)>128:
            raise ValueError("ANCESTRY_NODE_INVALID")
        if node in active:raise ValueError("ANCESTRY_CYCLE")
        if node in seen:return
        if node not in graph:raise ValueError("ANCESTRY_MISSING")
        parents=graph[node]
        if not isinstance(parents,list) or len(parents)>16:
            raise ValueError("ANCESTRY_PARENTS_INVALID")
        active.add(node);seen.add(node)
        if len(seen)>256:raise ValueError("ANCESTRY_LIMIT")
        for parent in parents:visit(parent)
        active.remove(node)
    visit(controller)
    return seen

def verify_export(artifact,rows,nonces):
    errors=[]
    required={"schema","batch_id","head_sha256","previous_head_sha256",
              "trust_sha256","manifest_bytes_b64","nonce_rows","artifact_sha256"}
    if not isinstance(artifact,dict) or set(artifact)!=required:
        return ["EXPORT_SCHEMA_INVALID"]
    if artifact["schema"]!=SCHEMA:errors.append("EXPORT_VERSION_INVALID")
    if type(artifact["batch_id"]) is not int or not 1<=artifact["batch_id"]<=len(rows):
        return errors+["EXPORT_BATCH_MISSING"]
    try:
        original=make_export(rows,nonces,artifact["batch_id"])
    except (KeyError,ValueError,TypeError) as e:
        return errors+["LOCAL_JOURNAL_INVALID:"+str(e)[:80]]
    if artifact!=original:errors.append("EXPORT_PREIMAGE_OR_NONCE_MISMATCH")
    if not hex64(artifact["artifact_sha256"]) or sha({k:v for k,v in artifact.items() if k!="artifact_sha256"})!=artifact["artifact_sha256"]:
        errors.append("EXPORT_ARTIFACT_DIGEST_INVALID")
    return errors

def audit(db_path,artifact,witness_bundle,trust_pin):
    errors=[]
    try:
        rows,nonces=readback(db_path)
        errors.extend(verify_export(artifact,rows,nonces))
    except (OSError,sqlite3.Error,ValueError,KeyError,TypeError) as e:
        return {**HOLD,"reasons":["LOCAL_READBACK_INVALID:"+type(e).__name__]}
    observed={"signature_checks":[],"retained_head":artifact.get("head_sha256") if isinstance(artifact,dict) else None}
    if not hex64(trust_pin):
        errors.append("OUT_OF_BAND_TRUST_ROOT_REQUIRED")
    if not isinstance(witness_bundle,dict) or set(witness_bundle)!={"trust","acknowledgments","consumed_nonces"}:
        return {**HOLD,"reasons":sorted(set(errors+["ACKNOWLEDGMENT_BUNDLE_INVALID"])),"observed":observed}
    trust=witness_bundle["trust"]
    if not isinstance(trust,dict) or set(trust)!={"journal_controller","controllers","custodians"}:
        return {**HOLD,"reasons":sorted(set(errors+["ACKNOWLEDGMENT_TRUST_INVALID"])),"observed":observed}
    if hex64(trust_pin) and sha(trust)!=trust_pin:errors.append("TRUST_ROOT_PIN_CONFLICT")
    graph=trust["controllers"];custodians=trust["custodians"]
    acks=witness_bundle["acknowledgments"];consumed=witness_bundle["consumed_nonces"]
    if not isinstance(graph,dict) or not isinstance(custodians,dict):
        return {**HOLD,"reasons":sorted(set(errors+["CONTROLLER_TRUST_INVALID"])),"observed":observed}
    if not isinstance(acks,list) or len(acks)!=3:
        return {**HOLD,"reasons":sorted(set(errors+["THREE_ACKNOWLEDGMENTS_REQUIRED"])),"observed":observed}
    if not isinstance(consumed,list) or any(not isinstance(n,str) for n in consumed):
        errors.append("NONCE_HISTORY_INVALID");consumed=[]
    if len(consumed)!=len(set(consumed)):errors.append("NONCE_HISTORY_DUPLICATED")
    try:journal_family=ancestry(trust["journal_controller"],graph)
    except ValueError as e:errors.append(str(e));journal_family=set()
    keys=set();nonce_set=set();families=[];ack_heads=[]
    for ack in acks:
        fields={"custodian_id","controller_id","nonce","batch_id",
                "artifact_sha256","head_sha256","signature_b64"}
        if not isinstance(ack,dict) or set(ack)!=fields:
            errors.append("ACK_SCHEMA_INVALID");continue
        kid=ack["custodian_id"];controller=ack["controller_id"];nonce=ack["nonce"]
        if not isinstance(kid,str) or kid in keys:errors.append("ACK_CUSTODIAN_DUPLICATE")
        if isinstance(kid,str):keys.add(kid)
        if not isinstance(nonce,str) or not nonce or nonce in nonce_set or nonce in consumed:
            errors.append("ACK_NONCE_REPLAY")
        if isinstance(nonce,str):nonce_set.add(nonce)
        pinned=custodians.get(kid)
        valid=False
        statement={"schema":ACK_SCHEMA,**{k:v for k,v in ack.items() if k!="signature_b64"}}
        if not isinstance(pinned,dict) or set(pinned)!={"controller_id","public_key_pem"} or pinned["controller_id"]!=controller:
            errors.append("ACK_KEY_PIN_MISMATCH")
        else:
            valid=verify(pinned["public_key_pem"],statement,ack["signature_b64"])
            if not valid:errors.append("ACK_SIGNATURE_INVALID")
        observed["signature_checks"].append({"custodian_id":kid,"valid":valid})
        if (not isinstance(artifact,dict) or ack["artifact_sha256"]!=artifact.get("artifact_sha256") or
            ack["head_sha256"]!=artifact.get("head_sha256") or
            ack["batch_id"]!=artifact.get("batch_id")):
            errors.append("ACK_EXPORT_SUBSTITUTION")
        ack_heads.append((ack["artifact_sha256"],ack["head_sha256"]))
        try:
            family=ancestry(controller,graph);families.append(family)
            if family & journal_family:errors.append("JOURNAL_ACK_SHARED_ANCESTRY")
        except ValueError as e:errors.append(str(e))
    if len(set(ack_heads))>1:errors.append("ACK_HEAD_CONFLICT")
    for i,f in enumerate(families):
        for other in families[i+1:]:
            if f & other:errors.append("ACK_SHARED_CONTROLLER_ANCESTRY")
    errors.extend(["CUSTODIAN_KEYS_AND_GRAPH_SELF_DECLARED",
                   "EXTERNAL_RAW_ACK_RETRIEVAL_NOT_PERFORMED",
                   "EXTERNAL_RETENTION_NOT_OBSERVED",
                   "NONCE_HISTORY_NOT_EXTERNALLY_SEALED"])
    return {**HOLD,"reasons":sorted(set(errors)),"observed":observed}

def main():
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="action",required=True)
    e=sub.add_parser("export")
    e.add_argument("--db",type=Path,required=True)
    e.add_argument("--batch",type=int,required=True)
    e.add_argument("--out",type=Path,required=True)
    a=sub.add_parser("audit")
    a.add_argument("--db",type=Path,required=True)
    a.add_argument("--export",type=Path,required=True)
    a.add_argument("--acknowledgments",type=Path,required=True)
    a.add_argument("--trusted-root-sha256",required=True)
    args=p.parse_args()
    try:
        if args.action=="export":
            result=export(args.db,args.batch,args.out)
        else:
            raw=[args.export.read_bytes(),args.acknowledgments.read_bytes()]
            if any(len(b)>1024*1024 for b in raw):raise ValueError("INPUT_TOO_LARGE")
            artifact=json.loads(raw[0])
            if canonical(artifact)!=raw[0]:raise ValueError("EXPORT_NOT_CANONICAL")
            result=audit(args.db,artifact,json.loads(raw[1]),args.trusted_root_sha256)
    except (OSError,ValueError,TypeError,KeyError,sqlite3.Error) as e:
        result={**HOLD,"reasons":["INPUT_REJECTED:"+type(e).__name__+":"+str(e)[:100]]}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 1
if __name__=="__main__":raise SystemExit(main())
