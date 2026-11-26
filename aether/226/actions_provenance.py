#!/usr/bin/env python3
"""AETHER-226 — authenticated GitHub Actions provenance *observation*.

Fetches one explicitly selected GitHub workflow run via GitHub's API using a
token from the environment. The same token and repository controller do NOT
provide independent physical or external custody attestation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPO="DavidWise01/oasis"
WORKFLOW="aether217-rust-qualification.yml"
SHA40=re.compile(r"^[0-9a-f]{40}$")
HOLD={"independent_external_custodians":0,"physical_qualification_percent":0,
      "operational_authority":"HOLD","physical_act_allowed":False,
      "may_recover":False,"may_repair":False,"may_reclaim_lock":False}
BASE="https://api.github.com/repos/"+REPO

def sha(raw:bytes)->str:
    return hashlib.sha256(raw).hexdigest()

def observe(run_id:int,expected_sha:str,fetch):
    """fetch(path)->(decoded JSON, exact response bytes); injected in tests."""
    issues=set()
    if not isinstance(run_id,int) or isinstance(run_id,bool) or run_id<1:
        issues.add("RUN_ID_INVALID")
    if not isinstance(expected_sha,str) or not SHA40.fullmatch(expected_sha):
        issues.add("EXPECTED_COMMIT_UNPINNED")
    if issues:
        return outcome(run_id,expected_sha,issues,{})
    seen={}
    endpoints={
        "run":f"/actions/runs/{run_id}",
        "jobs":f"/actions/runs/{run_id}/jobs?per_page=100",
        "artifacts":f"/actions/runs/{run_id}/artifacts?per_page=100",
    }
    records={}
    for label,path in endpoints.items():
        try:
            data,raw=fetch(path)
            if not isinstance(data,dict) or not isinstance(raw,bytes):
                raise ValueError("Invalid response envelope")
            seen[label]={"path":path,"sha256":sha(raw),"bytes":len(raw)}
            records[label]=data
        except (OSError,ValueError,KeyError,TypeError) as e:
            issues.add("API_READBACK_UNAVAILABLE:"+label)
            seen[label]={"path":path,"state":"UNVERIFIED","reason":type(e).__name__}
    run=records.get("run",{})
    jobs=records.get("jobs",{}).get("jobs",[])
    artifacts=records.get("artifacts",{}).get("artifacts",[])
    if run:
        if run.get("id")!=run_id: issues.add("RUN_ID_MISMATCH")
        if run.get("head_sha")!=expected_sha: issues.add("RUN_COMMIT_MISMATCH")
        if run.get("path") not in (".github/workflows/"+WORKFLOW,WORKFLOW):
            issues.add("WORKFLOW_IDENTITY_MISMATCH")
        full_name=run.get("repository",{}).get("full_name") if isinstance(run.get("repository"),dict) else None
        if full_name!=REPO: issues.add("REPOSITORY_MISMATCH")
        if run.get("event") not in ("push","workflow_dispatch"): issues.add("TRIGGER_UNEXPECTED")
        if run.get("status")!="completed" or run.get("conclusion")!="success":
            issues.add("RUN_NOT_SUCCESSFULLY_COMPLETED")
    if not isinstance(jobs,list) or not jobs:
        issues.add("JOBS_NOT_OBSERVED")
        jobs=[]
    if not isinstance(artifacts,list):
        issues.add("ARTIFACT_LIST_INVALID")
        artifacts=[]
    if records.get("jobs",{}).get("total_count",len(jobs))>len(jobs):
        issues.add("JOBS_PAGINATED_INCOMPLETE")
    if records.get("artifacts",{}).get("total_count",len(artifacts))>len(artifacts):
        issues.add("ARTIFACTS_PAGINATED_INCOMPLETE")
    candidates=[j for j in jobs if isinstance(j,dict) and
                j.get("name")=="Native Rust qualification with captured failure diagnostics"]
    if len(candidates)!=1:issues.add("QUALIFICATION_JOB_NOT_UNIQUE")
    else:
        job=candidates[0]
        if job.get("run_id")!=run_id:issues.add("JOB_RUN_MISMATCH")
        if job.get("conclusion")!="success" or job.get("status")!="completed":
            issues.add("QUALIFICATION_JOB_NOT_SUCCESSFUL")
        steps=job.get("steps")
        if not isinstance(steps,list) or not steps:issues.add("JOB_STEPS_NOT_OBSERVED")
        elif not all(isinstance(s,dict) and s.get("conclusion")=="success" for s in steps):
            issues.add("JOB_STEP_NOT_SUCCESSFUL")
    if not any(isinstance(a,dict) and a.get("name")=="aether218-rust-qualification"
               and a.get("expired") is False and a.get("size_in_bytes",0)>0
               and isinstance(a.get("workflow_run"),dict)
               and a["workflow_run"].get("id")==run_id
               for a in artifacts):
        issues.add("RUN_BOUND_QUALIFICATION_ARTIFACT_NOT_OBSERVED")
    # JSON readback from GitHub is evidence of an API response when the actual
    # transport is authenticated; not independently retained logs or physical data.
    return outcome(run_id,expected_sha,issues,seen)

def outcome(run_id,expected_sha,issues,responses):
    return {"schema":"AETHER-226/github-run-provenance-v1",
            "run_id":run_id,"expected_source_sha":expected_sha,
            "verdict":"DOCUMENTARY_GITHUB_API_METADATA_CONSISTENT"
                      if not issues else "REJECT_OR_UNVERIFIED",
            "reasons":sorted(issues) or
                ["API_METADATA_ALONE_DOES_NOT_AUTHENTICATE_EXECUTABLE_LOGS_OR_EXTERNAL_CUSTODY"],
            "api_response_digests":responses,
            "source_authenticated_independently":False,
            "runner_binary_or_logs_independently_authenticated":False,
            **HOLD}

def api_fetch(token:str,path:str):
    if not path.startswith("/actions/runs/") or ".." in path:
        raise ValueError("disallowed GitHub API path")
    req=Request(BASE+path,headers={"Accept":"application/vnd.github+json",
                "Authorization":"Bearer "+token,
                "X-GitHub-Api-Version":"2022-11-28","User-Agent":"AETHER-226-readonly"})
    with urlopen(req,timeout=12) as res:
        raw=res.read(8*1024*1024+1)
    if len(raw)>8*1024*1024: raise ValueError("API response exceeded 8 MB")
    return json.loads(raw),raw

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--run-id",type=int,required=True)
    p.add_argument("--source-sha",required=True)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    token=os.environ.get("GITHUB_TOKEN","")
    if not token:
        result=outcome(a.run_id,a.source_sha,{"GITHUB_TOKEN_UNAVAILABLE"},{})
    else:
        result=observe(a.run_id,a.source_sha,lambda path:api_fetch(token,path))
    out=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(out,encoding="utf-8")
    print(out,end="")
    return 0 if result["verdict"]=="DOCUMENTARY_GITHUB_API_METADATA_CONSISTENT" else 1

if __name__=="__main__":
    sys.exit(main())
