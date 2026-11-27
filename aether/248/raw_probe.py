#!/usr/bin/env python3
"""AETHER-248-RS: offline byte-exact capture of externally created probe transcripts."""
import argparse,base64,hashlib,json,re
from pathlib import Path
CATS=("loopback","private","link_local","metadata","redirect","dns_rebind")
HOLD={"operational_authority":"HOLD","physical_act_allowed":False,"physical_qualification_percent":0,
"independent_custody_authenticated":False,"network_isolation_independently_verified":False}
def canon(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
def sha(x):return hashlib.sha256(x).hexdigest()
def capture(spec,folder):
    if not isinstance(spec,dict) or set(spec)!={"source_commit","run_id","challenge_id","files"}:raise ValueError("SPEC_INVALID")
    if type(spec["run_id"]) is not int or spec["run_id"]<=0:raise ValueError("RUN_INVALID")
    if not isinstance(spec["source_commit"],str) or not re.fullmatch("[0-9a-f]{40}",spec["source_commit"]):raise ValueError("COMMIT_INVALID")
    if not isinstance(spec["challenge_id"],str) or not spec["challenge_id"]:raise ValueError("CHALLENGE_INVALID")
    if not isinstance(spec["files"],dict) or set(spec["files"])!=set(CATS):raise ValueError("SIX_FILES_REQUIRED")
    if not folder.is_dir() or folder.is_symlink():raise ValueError("FOLDER_INVALID")
    records=[]
    for category in CATS:
        filename=spec["files"][category]
        if not isinstance(filename,str) or re.fullmatch("[a-zA-Z0-9_.-]{1,100}",filename) is None:raise ValueError("FILENAME_INVALID")
        path=folder/filename
        if path.is_symlink() or not path.is_file():raise ValueError("FILE_INVALID")
        if path.stat().st_size>65536:raise ValueError("FILE_OVERSIZE")
        raw=path.read_bytes()
        if len(raw)>65536:raise ValueError("FILE_OVERSIZE")
        records.append({"category":category,"raw_b64":base64.b64encode(raw).decode(),
                        "raw_sha256":sha(raw),"raw_length":len(raw)})
    result={"schema":"AETHER-248/raw-transcripts-v1","source_commit":spec["source_commit"],
            "run_id":spec["run_id"],"challenge_id":spec["challenge_id"],"records":records}
    result["snapshot_sha256"]=sha(canon(result))
    return result
def review(doc):
    reasons=[];observed=[]
    if not isinstance(doc,dict):return {"verdict":"REJECT_OR_UNVERIFIED","reasons":["DOCUMENT_INVALID"],"observed":[],**HOLD}
    if set(doc)!={"schema","source_commit","run_id","challenge_id","records","snapshot_sha256"}:reasons.append("SCHEMA_INVALID")
    if doc.get("schema")!="AETHER-248/raw-transcripts-v1":reasons.append("VERSION_INVALID")
    if type(doc.get("run_id")) is not int or doc["run_id"]<=0:reasons.append("RUN_INVALID")
    if not isinstance(doc.get("source_commit"),str) or re.fullmatch("[0-9a-f]{40}",doc["source_commit"]) is None:reasons.append("COMMIT_INVALID")
    if not isinstance(doc.get("challenge_id"),str) or not doc["challenge_id"]:reasons.append("CHALLENGE_INVALID")
    records=doc.get("records")
    if not isinstance(records,list) or len(records)!=6:reasons.append("SIX_RECORDS_REQUIRED");records=[]
    seen=set()
    for r in records:
        if not isinstance(r,dict) or set(r)!={"category","raw_b64","raw_sha256","raw_length"}:reasons.append("RECORD_SCHEMA_INVALID");continue
        category=r["category"]
        if not isinstance(category,str) or category not in CATS or category in seen:reasons.append("CATEGORY_INVALID");continue
        seen.add(category)
        try:
            encoded=r["raw_b64"]
            if not isinstance(encoded,str) or len(encoded)>90000:raise ValueError("BASE64_SIZE")
            raw=base64.b64decode(encoded,validate=True)
            if len(raw)>65536:raise ValueError("RAW_SIZE")
            if type(r["raw_length"]) is not int or r["raw_length"]!=len(raw):reasons.append("LENGTH_MISMATCH")
            d=sha(raw)
            if r["raw_sha256"]!=d:reasons.append("RAW_SHA256_MISMATCH")
            observed.append({"category":category,"bytes":len(raw),"sha256":d})
        except (ValueError,TypeError):reasons.append("RAW_UNDECODABLE")
    if seen!=set(CATS):reasons.append("CATEGORY_COVERAGE_INCOMPLETE")
    claimed=doc.get("snapshot_sha256")
    if not isinstance(claimed,str) or re.fullmatch("[0-9a-f]{64}",claimed) is None:reasons.append("SNAPSHOT_DIGEST_INVALID")
    elif sha(canon({k:v for k,v in doc.items() if k!="snapshot_sha256"}))!=claimed:reasons.append("SNAPSHOT_SHA256_MISMATCH")
    reasons+=["TRANSCRIPTS_NOT_AUTHENTICATED_AS_LIVE_NETWORK_PROBES","EXTERNAL_ISOLATION_AND_WITNESSES_UNVERIFIED"]
    return {"verdict":"REJECT_OR_UNVERIFIED","reasons":sorted(set(reasons)),"observed":observed,**HOLD}
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="command",required=True)
    a=sub.add_parser("capture");a.add_argument("--spec",type=Path,required=True);a.add_argument("--folder",type=Path,required=True);a.add_argument("--out",type=Path)
    b=sub.add_parser("review");b.add_argument("--snapshot",type=Path,required=True);b.add_argument("--out",type=Path)
    x=p.parse_args()
    try:
        path=x.spec if x.command=="capture" else x.snapshot
        raw=path.read_bytes()
        if len(raw)>1048576:raise ValueError("INPUT_OVERSIZE")
        doc=json.loads(raw);result=capture(doc,x.folder) if x.command=="capture" else review(doc)
    except (ValueError,OSError,TypeError) as error:
        result={"verdict":"REJECT_OR_UNVERIFIED","reasons":["INPUT_REJECTED:"+type(error).__name__],**HOLD}
    out=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if x.out:x.out.write_text(out,encoding="utf-8")
    print(out,end="");return 1
if __name__=="__main__":raise SystemExit(main())
