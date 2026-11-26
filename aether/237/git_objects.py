#!/usr/bin/env python3
"""AETHER-237-RS: reconstruct Git tree and blob object IDs from API payloads.

Read-only, bounded and fail-closed. GitHub API transport is not external custody.
The path is read at a *specific pinned commit*, never at the moving branch head.
"""
from __future__ import annotations
import argparse
import base64
import binascii
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen

REPO="DavidWise01/oasis"
SCHEMA="AETHER-237/git-tree-blob-readback-v1"
HEX40=re.compile(r"^[0-9a-f]{40}$")
HEX64=re.compile(r"^[0-9a-f]{64}$")
MAX_RESPONSE=2*1024*1024
MAX_BLOB=1024*1024
MAX_ENTRIES=2048
MAX_DEPTH=16
HOLD={"operational_authority":"HOLD","physical_qualification_percent":0,
      "independent_custody_authenticated":False,"physical_act_allowed":False}

def object_id(kind: str,content: bytes) -> str:
    if kind not in ("blob","tree"):raise ValueError("INVALID_GIT_OBJECT_TYPE")
    return hashlib.sha1(kind.encode()+b" "+str(len(content)).encode()+bytes([0])+content).hexdigest()

def tree_bytes(entries):
    if not isinstance(entries,list) or len(entries)>MAX_ENTRIES:
        raise ValueError("TREE_ENTRIES_INVALID")
    seen=set()
    rows=[]
    for entry in entries:
        if not isinstance(entry,dict):raise ValueError("TREE_ENTRY_INVALID")
        name=entry.get("path")
        mode=entry.get("mode")
        kind=entry.get("type")
        oid=entry.get("sha")
        if not isinstance(name,str) or not name or name in (".","..") or "/" in name or "\\ " in name or "\x00" in name or "\\" in name:
            raise ValueError("TREE_NAME_INVALID")
        if name in seen:raise ValueError("TREE_DUPLICATE_ENTRY")
        seen.add(name)
        if kind=="tree":
            if mode!="040000":raise ValueError("TREE_MODE_INVALID")
        elif kind=="blob":
            if mode not in ("100644","100755","120000"):raise ValueError("BLOB_MODE_INVALID")
        else:
            raise ValueError("UNSUPPORTED_GIT_ENTRY")
        if not isinstance(oid,str) or not HEX40.fullmatch(oid):
            raise ValueError("ENTRY_SHA_INVALID")
        git_mode="40000" if mode=="040000" else mode
        raw_name=name.encode("utf-8")
        rows.append((raw_name+(b"/" if kind=="tree" else b""),git_mode.encode()+b" "+raw_name+bytes([0])+bytes.fromhex(oid)))
    return b"".join(row for _,row in sorted(rows,key=lambda item:item[0]))

def parse_json(raw,expected_sha=None):
    if not isinstance(raw,bytes) or not raw or len(raw)>MAX_RESPONSE:
        raise ValueError("API_PAYLOAD_INVALID")
    value=json.loads(raw)
    if not isinstance(value,dict):
        raise ValueError("API_JSON_INVALID")
    if expected_sha is not None and value.get("sha")!=expected_sha:
        raise ValueError("RESPONSE_SHA_MISMATCH")
    return value

def check_path(path):
    return isinstance(path,str) and bool(path) and len(path)<1024 and all(
        x not in ("",".","..") and "\x00" not in x and "\\" not in x
        for x in path.split("/")) and len(path.split("/"))<=MAX_DEPTH

def verify(pin_commit,path,expected_sha256,fetch):
    reasons=[]
    seen=[]
    payload={"schema":SCHEMA,"pin_commit":pin_commit,"path":path,
             "verdict":"REJECT_OR_UNVERIFIED","reasons":reasons,
             "observed":seen,**HOLD}
    if not isinstance(pin_commit,str) or not HEX40.fullmatch(pin_commit):
        reasons.append("PIN_COMMIT_INVALID")
    if not check_path(path):
        reasons.append("PATH_INVALID")
    if not isinstance(expected_sha256,str) or not HEX64.fullmatch(expected_sha256):
        reasons.append("EXPECTED_DIGEST_INVALID")
    if reasons:return payload
    try:
        raw=fetch("commits",pin_commit)
        commit=parse_json(raw,pin_commit)
        seen.append({"kind":"commit_api","sha":pin_commit,"response_sha256":hashlib.sha256(raw).hexdigest()})
        root=commit.get("tree",{}).get("sha")
        if not isinstance(root,str) or not HEX40.fullmatch(root):
            raise ValueError("COMMIT_TREE_MISSING")
        current=root
        names=path.split("/")
        for index,part in enumerate(names):
            raw=fetch("trees",current)
            value=parse_json(raw,current)
            if value.get("truncated") is True:raise ValueError("TREE_TRUNCATED")
            entries=value.get("tree")
            reconstructed=object_id("tree",tree_bytes(entries))
            if reconstructed!=current:raise ValueError("TREE_OBJECT_ID_MISMATCH")
            seen.append({"kind":"tree","sha":current,"response_sha256":hashlib.sha256(raw).hexdigest(),
                         "entry_count":len(entries),"reconstructed_sha1":reconstructed})
            matches=[e for e in entries if e["path"]==part]
            if len(matches)!=1:raise ValueError("PATH_COMPONENT_NOT_UNIQUE_OR_ABSENT")
            found=matches[0]
            if index<len(names)-1:
                if found["type"]!="tree":raise ValueError("INTERMEDIATE_NOT_TREE")
                current=found["sha"]
            else:
                if found["type"]!="blob" or found["mode"] not in ("100644","100755"):
                    raise ValueError("TARGET_NOT_REGULAR_BLOB")
                blob_id=found["sha"]
                raw=fetch("blobs",blob_id)
                blob=parse_json(raw,blob_id)
                if blob.get("encoding")!="base64" or not isinstance(blob.get("content"),str):
                    raise ValueError("BLOB_ENCODING_INVALID")
                data=base64.b64decode(blob["content"],validate=False)
                if len(data)>MAX_BLOB or blob.get("size")!=len(data):
                    raise ValueError("BLOB_SIZE_MISMATCH")
                if object_id("blob",data)!=blob_id:
                    raise ValueError("BLOB_OBJECT_ID_MISMATCH")
                actual=hashlib.sha256(data).hexdigest()
                seen.append({"kind":"blob","sha":blob_id,"bytes":len(data),
                             "response_sha256":hashlib.sha256(raw).hexdigest(),
                             "content_sha256":actual})
                if actual!=expected_sha256:
                    raise ValueError("PINNED_CONTENT_DIGEST_MISMATCH")
        payload["verdict"]="OBJECT_IDENTITIES_MATCH_UNQUALIFIED"
        reasons.append("API_OBJECT_ID_PARITY_IS_NOT_INDEPENDENT_CUSTODY_OR_PRERUN_TIMING")
    except (ValueError,TypeError,KeyError,UnicodeError,binascii.Error,OSError) as e:
        reasons.append("OBJECT_READ_FAILED:"+str(e) if isinstance(e,ValueError)
                       else "OBJECT_READ_FAILED:"+type(e).__name__)
    return payload

def api_fetch(kind,oid):
    if kind not in ("commits","trees","blobs") or not HEX40.fullmatch(oid):
        raise ValueError("API_ROUTE_INVALID")
    url="https://api.github.com/repos/"+REPO+"/git/"+kind+"/"+oid
    request=Request(url,headers={"Accept":"application/vnd.github+json",
        "X-GitHub-Api-Version":"2022-11-28","User-Agent":"AETHER-237-read-only"})
    with urlopen(request,timeout=15) as response:
        if response.geturl()!=url:raise ValueError("UNEXPECTED_REDIRECT")
        raw=response.read(MAX_RESPONSE+1)
    return raw

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pin-commit",required=True)
    p.add_argument("--path",required=True)
    p.add_argument("--sha256",required=True)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    report=verify(a.pin_commit,a.path,a.sha256,api_fetch)
    rendered=json.dumps(report,indent=2,sort_keys=True)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(rendered,encoding="utf-8")
    print(rendered,end="")
    return 0 if report["verdict"]=="OBJECT_IDENTITIES_MATCH_UNQUALIFIED" else 1

if __name__=="__main__":
    sys.exit(main())
