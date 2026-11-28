#!/usr/bin/env python3
"""AETHER-299-RS: actual AETHER-297 signer parity and atomic external-handoff packet.

This never authenticates independent external custody; every verdict stays HOLD.
"""
import argparse,base64,hashlib,json,os,sqlite3,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"297"),str(ROOT/"298")]
from owner_bound_ledger import sign as actual_sign
from qualification import qualified_history,canonical,sha_bytes,sha
HOLD={"verdict":"REJECT_OR_UNVERIFIED","operational_authority":"HOLD",
      "physical_act_allowed":False,"physical_qualification_percent":0,
      "independent_external_custody_verified":False}
SCHEMA="AETHER-299/highwater-handoff-v1"
def sigv4_parity(host,path,query,region,owner,access,secret,token,now,method="GET"):
    """Check actual AETHER-297 signed headers against botocore, not duplicated logic."""
    from botocore.auth import SigV4Auth
    from botocore.awsrequest import AWSRequest
    from botocore.credentials import Credentials
    from urllib.parse import quote
    if method not in ("HEAD","GET"):raise ValueError("READ_ONLY_METHOD_REQUIRED")
    signed,qs,actual_hash=actual_sign(method,host,path,query,region,owner,
                                      access,secret,token,now)
    safe_headers={k:v for k,v in signed.items() if k!="authorization"}
    url="https://"+host+path+("?" + qs if qs else "")
    request=AWSRequest(method=method,url=url,data=b"",headers=safe_headers)
    request.context["timestamp"]=now
    signer=SigV4Auth(Credentials(access,secret,token or None),"s3",region)
    canon_request=signer.canonical_request(request)
    oracle_hash=sha_bytes(canon_request.encode())
    oracle_signature=signer.signature(signer.string_to_sign(request,canon_request),request)
    actual_signature=signed["authorization"].rsplit("Signature=",1)[-1]
    if oracle_hash!=actual_hash:raise ValueError("ACTUAL_SIGV4_CANONICAL_PARITY_FAILED")
    if oracle_signature!=actual_signature:raise ValueError("ACTUAL_SIGV4_SIGNATURE_PARITY_FAILED")
    return {**HOLD,"request_sha256":actual_hash,"signature_parity":True,
            "reasons":["SIGV4_CLIENT_PARITY_NOT_PROVIDER_CUSTODY"]}
def handoff_preimage(db,seq,head,recipient,ancestry_pin):
    """No claim of external acceptance: emit local packet for an out-of-band custodian."""
    if not isinstance(recipient,str) or not 1<=len(recipient)<=128:
        raise ValueError("RECIPIENT_ID_REQUIRED")
    if not isinstance(ancestry_pin,str) or len(ancestry_pin)!=64 or any(c not in "0123456789abcdef" for c in ancestry_pin):
        raise ValueError("OUT_OF_BAND_ANCESTRY_PIN_REQUIRED")
    rows,_=qualified_history(db,seq,head)
    return {"schema":SCHEMA,"recipient_claim":recipient,
            "source_phase":"AETHER-297","source_sequence":len(rows),
            "source_head_sha256":rows[-1][3],"anchored_sequence":seq,
            "anchored_head_sha256":head,"declared_source_ancestry_sha256":ancestry_pin,
            "independent_custody_verified":False,
            "physical_act_allowed":False}
def durable_write(path,raw,fail_at=None):
    """Create-only output, followed by fsync and readback. Never replace a prior packet."""
    dest=Path(path)
    fd=os.open(dest,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    try:
        with os.fdopen(fd,"wb") as stream:
            stream.write(raw);stream.flush()
            if fail_at=="before_fsync":raise RuntimeError("INJECTED_PRE_FSYNC")
            os.fsync(stream.fileno())
            if fail_at=="after_fsync":raise RuntimeError("INJECTED_POST_FSYNC")
        parent=os.open(dest.parent,os.O_RDONLY)
        try:os.fsync(parent)
        finally:os.close(parent)
        if fail_at=="before_readback":raise RuntimeError("INJECTED_PRE_READBACK")
        if dest.read_bytes()!=raw:raise ValueError("DURABLE_READBACK_MISMATCH")
    except BaseException:
        # Preserve partial file for forensics. Do not replace/remove on recovery.
        raise
    return sha_bytes(raw)
def export_handoff(db,dest,seq,head,recipient,ancestry_pin,fail_at=None):
    obj=handoff_preimage(db,seq,head,recipient,ancestry_pin)
    raw=canonical(obj)
    result=durable_write(dest,raw,fail_at)
    return {**HOLD,"handoff_sha256":result,"bytes":len(raw),"reasons":[
        "PACKET_NOT_EXTERNALLY_ACKNOWLEDGED","CUSTODIAN_IDENTITY_SELF_DECLARED"]}
def audit_packet(path,db=None,pin=None):
    raw=Path(path).read_bytes()
    if len(raw)>4096:raise ValueError("HANDOFF_PACKET_TOO_LARGE")
    obj=json.loads(raw)
    fields={"schema","recipient_claim","source_phase","source_sequence",
            "source_head_sha256","anchored_sequence","anchored_head_sha256",
            "declared_source_ancestry_sha256","independent_custody_verified","physical_act_allowed"}
    if not isinstance(obj,dict) or set(obj)!=fields or canonical(obj)!=raw or obj["schema"]!=SCHEMA:
        raise ValueError("HANDOFF_PACKET_NONCANONICAL")
    if obj["independent_custody_verified"] is not False or obj["physical_act_allowed"] is not False:
        raise ValueError("FORBIDDEN_AUTHORITY_PROMOTION")
    if pin is not None and pin!=sha_bytes(raw):raise ValueError("HANDOFF_DIGEST_PIN_CONFLICT")
    if db is not None:
        rows,_=qualified_history(db,obj["anchored_sequence"],obj["anchored_head_sha256"])
        if len(rows)<obj["source_sequence"] or rows[obj["source_sequence"]-1][3]!=obj["source_head_sha256"]:
            raise ValueError("HANDOFF_SOURCE_ROLLBACK")
    return {**HOLD,"packet_sha256":sha_bytes(raw),"reasons":[
        "INDEPENDENT_EXTERNAL_RETENTION_UNOBSERVED","NO_SIGNED_REMOTE_ACCEPTANCE"]}
def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest="op",required=True)
    v=s.add_parser("parity")
    v.add_argument("--fixture",type=Path,required=True)
    x=s.add_parser("handoff")
    x.add_argument("--db",type=Path,required=True);x.add_argument("--out",type=Path,required=True)
    x.add_argument("--seq",type=int,required=True);x.add_argument("--head",required=True)
    x.add_argument("--recipient",required=True);x.add_argument("--ancestry-pin",required=True)
    a=s.add_parser("audit")
    a.add_argument("--packet",type=Path,required=True);a.add_argument("--db",type=Path)
    a.add_argument("--pin")
    o=p.parse_args()
    try:
        if o.op=="parity":
            data=json.loads(o.fixture.read_bytes())
            result=sigv4_parity(**data)
        elif o.op=="handoff":
            result=export_handoff(o.db,o.out,o.seq,o.head,o.recipient,o.ancestry_pin)
        else:result=audit_packet(o.packet,o.db,o.pin)
    except (ValueError,TypeError,KeyError,OSError,sqlite3.Error,RuntimeError) as err:
        result={**HOLD,"reasons":["REJECTED:"+type(err).__name__+":"+str(err)[:100]]}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 1
if __name__=="__main__":raise SystemExit(main())
