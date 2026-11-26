#!/usr/bin/env python3
"""AETHER-236: bounded authenticated-transport GitHub commit-DAG observation.

GitHub REST JSON is transport-observed, NOT raw Git-object verification,
independent custody, or proof of when a commit was made.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import sys
from collections import deque
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPO="DavidWise01/oasis"
SCHEMA="AETHER-236/commit-dag-readback-v1"
SHA40=re.compile(r"^[0-9a-f]{40}$")
MAX_NODES=256
MAX_DEPTH=128
MAX_BYTES=1024*1024
HOLD={"operational_authority":"HOLD","physical_qualification_percent":0,
      "independent_custody_authenticated":False,"physical_act_allowed":False}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def outcome(pin,head,reasons,observed):
    reasons=sorted(set(reasons))
    return {"schema":SCHEMA,"repository":REPO,"pin_commit":pin,"run_head":head,
            "dag_result":"STRICT_ANCESTOR_OBSERVED_UNQUALIFIED" if not reasons else "REJECT_OR_UNVERIFIED",
            "reasons":reasons or ["API_COMMIT_GRAPH_DOES_NOT_AUTHENTICATE_ORIGINAL_GIT_OBJECT_OR_CUSTODY"],
            "observed":observed,**HOLD}

def walk(pin,head,fetch):
    observed=[]
    issues=[]
    if not isinstance(pin,str) or not SHA40.fullmatch(pin):
        issues.append("PIN_SHA_INVALID")
    if not isinstance(head,str) or not SHA40.fullmatch(head):
        issues.append("RUN_HEAD_SHA_INVALID")
    if issues:return outcome(pin,head,issues,observed)
    if pin==head:return outcome(pin,head,["PIN_NOT_STRICT_ANCESTOR"],observed)
    queue=deque([(head,0)])
    seen=set()
    found=False
    while queue and len(seen)<MAX_NODES:
        commit,depth=queue.popleft()
        if commit in seen:continue
        seen.add(commit)
        try:
            raw=fetch(commit)
            if not isinstance(raw,bytes) or len(raw)>MAX_BYTES:
                raise ValueError("RESPONSE_SIZE_OR_TYPE")
            doc=json.loads(raw)
            if not isinstance(doc,dict) or doc.get("sha")!=commit:
                raise ValueError("COMMIT_SHA_BINDING")
            parents=doc.get("parents")
            if not isinstance(parents,list) or len(parents)>16:
                raise ValueError("PARENTS_MALFORMED")
            parent_shas=[]
            for item in parents:
                s=item.get("sha") if isinstance(item,dict) else None
                if not isinstance(s,str) or not SHA40.fullmatch(s):
                    raise ValueError("PARENT_SHA_INVALID")
                if s==commit or s in parent_shas:
                    raise ValueError("PARENT_EDGE_INVALID")
                parent_shas.append(s)
            observed.append({"commit":commit,"depth":depth,
                             "response_sha256":sha(raw),"response_bytes":len(raw),
                             "parents":parent_shas})
            if pin in parent_shas:
                found=True
                break
            if depth>=MAX_DEPTH:
                if parent_shas:issues.append("DEPTH_BOUND_EXCEEDED")
                continue
            for p in parent_shas:
                if p not in seen:queue.append((p,depth+1))
        except (ValueError,TypeError,UnicodeError,OSError) as e:
            issues.append("COMMIT_READ_FAILED:"+type(e).__name__)
            break
    if queue and not found:issues.append("NODE_BOUND_EXCEEDED")
    if not found:issues.append("STRICT_ANCESTRY_NOT_ESTABLISHED")
    return outcome(pin,head,issues,observed)

def github_fetch(token):
    def get(commit):
        if not SHA40.fullmatch(commit):raise ValueError("INVALID_SHA")
        url="https://api.github.com/repos/"+REPO+"/git/commits/"+commit
        headers={"Accept":"application/vnd.github+json",
                 "X-GitHub-Api-Version":"2022-11-28",
                 "User-Agent":"AETHER-236-read-only"}
        if token:headers["Authorization"]="Bearer "+token
        request=Request(url,headers=headers,method="GET")
        with urlopen(request,timeout=15) as response:
            if response.geturl()!=url:raise ValueError("UNEXPECTED_REDIRECT")
            raw=response.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES:raise ValueError("RESPONSE_TOO_LARGE")
        return raw
    return get

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pin-commit",required=True)
    p.add_argument("--run-head",required=True)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    result=walk(a.pin_commit,a.run_head,github_fetch(os.environ.get("GITHUB_TOKEN","")))
    rendered=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(rendered,encoding="utf-8")
    print(rendered,end="")
    return 0 if result["dag_result"]=="STRICT_ANCESTOR_OBSERVED_UNQUALIFIED" else 1

if __name__=="__main__":
    sys.exit(main())
