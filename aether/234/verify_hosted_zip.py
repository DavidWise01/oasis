#!/usr/bin/env python3
"""AETHER-234-RS: fail-closed hosted ZIP member verification.

Read-only. The expected manifest must be independently pinned by the caller.
This tool never grants physical or operational authority.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import re
import stat
import sys
import zipfile
from pathlib import PurePosixPath

SCHEMA="AETHER-234/hosted-zip-member-adjudication-v1"
MAX_ZIP=16*1024*1024
MAX_FILE=4*1024*1024
MAX_TOTAL=32*1024*1024
MAX_MEMBERS=128
SHA256=re.compile(r"^[0-9a-f]{64}$")
HOLD={"operational_authority":"HOLD","physical_qualification_percent":0,
      "independent_custody_authenticated":False,"physical_act_allowed":False}

def digest(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def clean_name(name:str)->bool:
    if not name or name.startswith("/") or "\\" in name or ":" in name or "\x00" in name:
        return False
    p=PurePosixPath(name)
    return all(part not in ("", ".", "..") for part in name.split("/")) and str(p)==name

def report(reasons,observed):
    return {"schema":SCHEMA,
            "verdict":"MEMBERS_MATCH_PINNED_MANIFEST_UNQUALIFIED" if not reasons else "REJECT_OR_UNVERIFIED",
            "reasons":sorted(set(reasons)) if reasons else
                 ["MANIFEST_PROVENANCE_AND_INDEPENDENT_CUSTODY_NOT_AUTHENTICATED"],
            "observed":observed,**HOLD}

def verify(archive:bytes, expected:dict)->dict:
    reasons=[]
    observed={"archive_sha256":digest(archive),"archive_bytes":len(archive),"members":[]}
    if not isinstance(expected,dict) or not expected or any(
        not isinstance(k,str) or not clean_name(k) or not isinstance(v,str)
        or SHA256.fullmatch(v) is None for k,v in expected.items()):
        return report(["PINNED_MANIFEST_INVALID"],observed)
    if not archive or len(archive)>MAX_ZIP:
        return report(["ARCHIVE_EMPTY_OR_OVERSIZE"],observed)
    try:
        z=zipfile.ZipFile(io.BytesIO(archive))
        infos=z.infolist()
        if len(infos)>MAX_MEMBERS: reasons.append("TOO_MANY_MEMBERS")
        names=[i.filename for i in infos]
        if len(names)!=len(set(names)):reasons.append("DUPLICATE_MEMBER")
        total=0
        actual={}
        for i in infos:
            name=i.filename
            if not clean_name(name) or name.endswith("/"):
                reasons.append("UNSAFE_OR_DIRECTORY_MEMBER")
                continue
            mode=(i.external_attr>>16)
            if stat.S_IFMT(mode) not in (0,stat.S_IFREG):
                reasons.append("NONREGULAR_MEMBER")
                continue
            if i.flag_bits & 1:
                reasons.append("ENCRYPTED_MEMBER")
                continue
            if i.file_size>MAX_FILE or i.compress_size>MAX_ZIP:
                reasons.append("MEMBER_SIZE_LIMIT")
                continue
            total+=i.file_size
            if total>MAX_TOTAL:
                reasons.append("TOTAL_EXPANDED_LIMIT")
                break
            if i.compress_size==0 and i.file_size>0:
                reasons.append("SUSPICIOUS_COMPRESSION")
                continue
            if i.compress_size and i.file_size>1000*i.compress_size:
                reasons.append("EXPANSION_RATIO_LIMIT")
                continue
            with z.open(i,"r") as f:
                raw=f.read(MAX_FILE+1)
            if len(raw)!=i.file_size:
                reasons.append("MEMBER_LENGTH_MISMATCH")
                continue
            actual[name]=digest(raw)
            observed["members"].append({"name":name,"bytes":len(raw),"sha256":actual[name]})
        if set(actual)!=set(expected):
            reasons.append("MEMBER_SET_MISMATCH")
        for name in set(actual)&set(expected):
            if actual[name]!=expected[name]:
                reasons.append("MEMBER_DIGEST_MISMATCH")
        z.close()
    except (zipfile.BadZipFile,zipfile.LargeZipFile,RuntimeError,EOFError,OSError,ValueError) as e:
        reasons.append("ZIP_READ_FAILED:"+type(e).__name__)
    return report(reasons,observed)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip",required=True,help="Previously acquired hosted ZIP bytes")
    p.add_argument("--manifest",required=True,help="Independently pinned JSON map of filename to sha256")
    p.add_argument("--out")
    args=p.parse_args()
    try:
        with open(args.zip,"rb") as f:archive=f.read(MAX_ZIP+1)
        with open(args.manifest,"rb") as f:expected=json.loads(f.read(65537))
        result=verify(archive,expected)
    except (OSError,ValueError,UnicodeError) as e:
        result=report(["INPUT_READ_FAILED:"+type(e).__name__],{})
    rendered=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.out:
        with open(args.out,"w",encoding="utf-8") as f:f.write(rendered)
    print(rendered,end="")
    return 0 if result["verdict"]=="MEMBERS_MATCH_PINNED_MANIFEST_UNQUALIFIED" else 1

if __name__=="__main__":
    sys.exit(main())
