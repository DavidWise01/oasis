#!/usr/bin/env python3
"""AETHER-298-RS: offline SigV4 oracle and immutable local evidence export.

Only qualifies local evidence integrity. Never grants authority, validates
provider custody, or treats client SigV4 as provider-signed evidence.
"""
import argparse,base64,hashlib,json,os,sqlite3
from pathlib import Path
from urllib.parse import quote
SCHEMA="AETHER-298/offline-qualification-v1"
HOLD={"operational_authority":"HOLD","physical_act_allowed":False,
      "physical_qualification_percent":0,"independent_external_custody_verified":False}
ZERO="0"*64
OPS={"VERSIONING","LOCK_CONFIGURATION","HEAD","RETENTION"}
SAFE_HEADERS={"date","content-type","content-length","x-amz-request-id",
              "x-amz-id-2","x-amz-version-id","x-amz-object-lock-mode",
              "x-amz-object-lock-retain-until-date"}
def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def sha_bytes(value):return hashlib.sha256(value).hexdigest()
def sha(value):return sha_bytes(canonical(value))
def raw_from_record(record):
    if not isinstance(record,dict) or not isinstance(record.get("response_raw_b64"),str):
        raise ValueError("RAW_RESPONSE_MISSING")
    if len(record["response_raw_b64"])>90000:raise ValueError("RESPONSE_BASE64_TOO_LARGE")
    raw=base64.b64decode(record["response_raw_b64"],validate=True)
    if len(raw)>65536 or sha_bytes(raw)!=record.get("response_raw_sha256"):
        raise ValueError("RAW_RESPONSE_DIGEST_MISMATCH")
    return raw
def inspect_evidence(evidence):
    if not isinstance(evidence,dict) or evidence.get("schema")!="AETHER-297/owner-bound-evidence-v1":
        raise ValueError("AETHER297_SCHEMA_INVALID")
    records=evidence.get("records")
    if not isinstance(records,list) or len(records)!=4:raise ValueError("FOUR_RECORDS_REQUIRED")
    ops=set()
    for record in records:
        if not isinstance(record,dict) or record.get("operation") not in OPS:
            raise ValueError("OPERATION_INVALID")
        if record["operation"] in ops:raise ValueError("OPERATION_DUPLICATED")
        ops.add(record["operation"])
        if record.get("method")!=("HEAD" if record["operation"]=="HEAD" else "GET"):
            raise ValueError("READ_ONLY_OPERATION_MISMATCH")
        if record.get("response_status")!=200:raise ValueError("RESPONSE_NOT_SUCCESS")
        if not isinstance(record.get("response_headers"),dict):
            raise ValueError("RESPONSE_HEADERS_INVALID")
        if not set(record["response_headers"]).issubset(SAFE_HEADERS):
            raise ValueError("UNSAFE_HEADER_IN_TRANSCRIPT")
        if not all(isinstance(v,str) and len(v)<=4096 for v in record["response_headers"].values()):
            raise ValueError("RESPONSE_HEADER_VALUE_INVALID")
        if not all(isinstance(record.get(k),str) and len(record[k])==64 for k in ("path_sha256","request_sha256")):
            raise ValueError("REQUEST_PREIMAGE_DIGEST_INVALID")
        raw_from_record(record)
    if ops!=OPS:raise ValueError("MISSING_OPERATION")
    return True
def read_rows(db_path):
    db=sqlite3.connect(Path(db_path).resolve().as_uri()+"?mode=ro",uri=True,isolation_level=None)
    try:
        db.execute("PRAGMA query_only=ON");db.execute("BEGIN")
        rows=list(db.execute("SELECT id,challenge,previous_head,head,manifest FROM evidence ORDER BY id"))
        db.commit()
        return rows
    finally:db.close()
def qualified_history(db_path,expected_seq=None,expected_head=None):
    rows=read_rows(db_path)
    if not rows:raise ValueError("EMPTY_EVIDENCE_JOURNAL")
    prior=ZERO;manifests=[]
    for expected_id,(seq,nonce,parent,head,text) in enumerate(rows,1):
        if seq!=expected_id or parent!=prior:
            raise ValueError("HISTORY_SEQUENCE_OR_PARENT_INVALID")
        manifest=json.loads(text)
        if canonical(manifest).decode()!=text or sha(manifest)!=head:
            raise ValueError("HISTORY_MANIFEST_HASH_INVALID")
        if (manifest.get("schema")!="AETHER-297/owner-bound-evidence-v1" or
            manifest.get("challenge")!=nonce or manifest.get("previous_head_sha256")!=parent):
            raise ValueError("HISTORY_HEADER_INVALID")
        inspect_evidence(manifest.get("evidence"))
        manifests.append(manifest);prior=head
    if expected_seq is not None or expected_head is not None:
        if (type(expected_seq) is not int or expected_seq<1 or
            not isinstance(expected_head,str) or len(expected_head)!=64):
            raise ValueError("EXTERNAL_PREFIX_PIN_INVALID")
        if len(rows)<expected_seq:raise ValueError("PINNED_HISTORY_ROLLED_BACK")
        if rows[expected_seq-1][3]!=expected_head:raise ValueError("PINNED_HISTORY_REWRITTEN")
    return rows,manifests
def qualify_sigv4(case):
    """Independent signing comparison against official botocore library."""
    from botocore.auth import SigV4Auth
    from botocore.awsrequest import AWSRequest
    from botocore.credentials import Credentials
    required={"method","host","path","query","region","access_key",
              "secret_key","session_token","amz_date","expected_owner",
              "candidate_canonical_sha256","candidate_signature"}
    if not isinstance(case,dict) or set(case)!=required:
        raise ValueError("SIGV4_CASE_SCHEMA_INVALID")
    if case["method"] not in ("HEAD","GET"):raise ValueError("SIGV4_METHOD_NOT_READ_ONLY")
    owner=case["expected_owner"]
    if not isinstance(owner,str) or not (len(owner)==12 and owner.isascii() and owner.isdigit()):
        raise ValueError("EXPECTED_BUCKET_OWNER_INVALID")
    query=case["query"]
    if not isinstance(query,dict) or any(not isinstance(k,str) or not isinstance(v,str) for k,v in query.items()):
        raise ValueError("CANONICAL_QUERY_INVALID")
    qs="&".join(quote(k,safe="-_.~")+"="+quote(v,safe="-_.~") for k,v in sorted(query.items()))
    url="https://"+case["host"]+case["path"]+("?" + qs if qs else "")
    headers={"host":case["host"],"x-amz-date":case["amz_date"],
             "x-amz-content-sha256":sha_bytes(b""),
             "x-amz-expected-bucket-owner":owner}
    if case["session_token"]:headers["x-amz-security-token"]=case["session_token"]
    request=AWSRequest(method=case["method"],url=url,data=b"",headers=headers)
    request.context["timestamp"]=case["amz_date"]
    signer=SigV4Auth(Credentials(case["access_key"],case["secret_key"],
                                  case["session_token"] or None),"s3",case["region"])
    cr=signer.canonical_request(request)
    request_hash=sha_bytes(cr.encode())
    reference_signature=signer.signature(signer.string_to_sign(request,cr),request)
    if request_hash!=case["candidate_canonical_sha256"]:
        raise ValueError("SIGV4_CANONICAL_REQUEST_NOT_PARITY")
    if reference_signature!=case["candidate_signature"]:
        raise ValueError("SIGV4_SIGNATURE_NOT_PARITY")
    return {"canonical_request_sha256":request_hash,"signature_equal":True,
            "evidence_only":True,**HOLD}
def freeze_export(db_path,destination,expected_seq,expected_head):
    rows,manifests=qualified_history(db_path,expected_seq,expected_head)
    content={"schema":SCHEMA,"previous_head_sha256":ZERO,
             "source_phase":"AETHER-297","record_count":len(rows),
             "source_head_sha256":rows[-1][3],
             "source_prefix_seq":expected_seq,"source_prefix_sha256":expected_head,
             "source_manifests":manifests,"custody_attested":False,
             "physical_act_allowed":False}
    raw=canonical(content);path=Path(destination)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,"wb") as out:
        out.write(raw);out.flush();os.fsync(out.fileno())
    directory_fd=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(directory_fd)
    finally:os.close(directory_fd)
    if path.read_bytes()!=raw:raise ValueError("EXPORT_READBACK_MISMATCH")
    return {"export_sha256":sha_bytes(raw),"bytes":len(raw),
            "source_head_sha256":rows[-1][3],**HOLD}
def audit_export(export_path,db_path=None):
    raw=Path(export_path).read_bytes()
    if len(raw)>10_000_000:raise ValueError("EXPORT_SIZE_LIMIT")
    manifest=json.loads(raw)
    if raw!=canonical(manifest) or manifest.get("schema")!=SCHEMA:
        raise ValueError("EXPORT_CANONICAL_INVALID")
    if manifest.get("custody_attested") is not False or manifest.get("physical_act_allowed") is not False:
        raise ValueError("AUTHORITY_GATE_CHANGED")
    rows=manifest.get("source_manifests")
    if not isinstance(rows,list) or not rows or manifest.get("record_count")!=len(rows):
        raise ValueError("SOURCE_ROWS_INVALID")
    prev=ZERO
    for entry in rows:
        if entry.get("previous_head_sha256")!=prev or entry.get("schema")!="AETHER-297/owner-bound-evidence-v1":
            raise ValueError("EXPORTED_CHAIN_MISMATCH")
        inspect_evidence(entry["evidence"]);prev=sha(entry)
    if manifest.get("source_head_sha256")!=prev:
        raise ValueError("EXPORTED_HEAD_MISMATCH")
    if db_path:
        qualified_history(db_path,manifest["source_prefix_seq"],manifest["source_prefix_sha256"])
        observed,_=qualified_history(db_path)
        if observed[-1][3]!=manifest["source_head_sha256"]:
            raise ValueError("EXPORT_SOURCE_HEAD_DIVERGENCE")
    return {"export_sha256":sha_bytes(raw),"source_head_sha256":prev,
            "record_count":len(rows),"reasons":["EXPORT_ONLY_LOCAL_CUSTODY",
            "INDEPENDENT_EXTERNAL_RETENTION_NOT_OBSERVED"],**HOLD}
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="operation",required=True)
    q=sub.add_parser("sigv4");q.add_argument("--case",type=Path,required=True)
    x=sub.add_parser("freeze")
    x.add_argument("--db",type=Path,required=True);x.add_argument("--out",type=Path,required=True)
    x.add_argument("--prefix-seq",type=int,required=True);x.add_argument("--prefix-sha256",required=True)
    a=sub.add_parser("audit");a.add_argument("--export",type=Path,required=True)
    a.add_argument("--db",type=Path)
    args=p.parse_args()
    try:
        if args.operation=="sigv4":result=qualify_sigv4(json.loads(args.case.read_bytes()))
        elif args.operation=="freeze":
            result=freeze_export(args.db,args.out,args.prefix_seq,args.prefix_sha256)
        else:result=audit_export(args.export,args.db)
    except (OSError,ValueError,TypeError,KeyError,sqlite3.Error) as e:
        result={**HOLD,"reasons":["REJECTED:"+type(e).__name__+":"+str(e)[:100]]}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 1
if __name__=="__main__":raise SystemExit(main())
