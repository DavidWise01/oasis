#!/usr/bin/env python3
"""AETHER-233 — live read-only GitHub Actions evidence acquisition.

A user-specified completed run is fetched via GitHub's authenticated REST API.
Actual returned byte streams are SHA-256-hashed, never confused with a synthetic
run, and never treated as independent custody or physical ACT qualification.
No data is written back to GitHub; JSON report contains no token or logs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.request import HTTPRedirectHandler, Request, build_opener
from urllib.parse import urlsplit

REPO="DavidWise01/oasis"
BASE="https://api.github.com/repos/"+REPO
SCHEMA="AETHER-233/live-execution-acquisition-v1"
SHA40=re.compile(r"^[a-f0-9]{40}$")
MAX_BYTES=16*1024*1024
HOLD={"independently_authenticated_execution":False,
      "authenticated_external_custodians":0,
      "authenticated_original_physical_captures":0,
      "physical_qualification_percent":0,"operational_authority":"HOLD",
      "physical_act_allowed":False,"may_repair":False,"may_recover":False,
      "may_reclaim_lock":False,"may_choose_history":False}

def sha(raw:bytes)->str:
    return hashlib.sha256(raw).hexdigest()

def read_api(token:str,path:str,raw:bool=False):
    if not token:raise ValueError("GITHUB_TOKEN_MISSING")
    if (not re.fullmatch(r"/actions/(?:runs/[0-9]+(?:/(?:jobs|artifacts)\\?per_page=100)?|jobs/[0-9]+/logs|artifacts/[0-9]+/zip)",path)) or ".." in path):
        raise ValueError("UNSAFE_API_ENDPOINT")
    headers={"Accept":"application/vnd.github+json",
             "Authorization":"Bearer "+token,
             "X-GitHub-Api-Version":"2022-11-28",
             "User-Agent":"AETHER-233-read-only"}
    req=Request(BASE+path,headers=headers)
    class NoTokenOnRedirect(HTTPRedirectHandler):
        def redirect_request(self,request,fp,code,msg,headers,newurl):
            forwarded=super().redirect_request(request,fp,code,msg,headers,newurl)
            if forwarded is not None and urlsplit(newurl).hostname!="api.github.com":
                for key in list(forwarded.headers):
                    if key.lower()=="authorization":
                        del forwarded.headers[key]
            return forwarded
    opener=build_opener(NoTokenOnRedirect())
    with opener.open(req,timeout=18) as response:
        content=response.read(MAX_BYTES+1)
    if len(content)>MAX_BYTES:raise ValueError("API_BYTE_LIMIT_EXCEEDED")
    return content

def acquire(run_id:int,expected_sha:str,fetch):
    problems=set()
    observed={}
    if type(run_id) is not int or run_id<=0:problems.add("RUN_ID_NOT_PINNED")
    if not isinstance(expected_sha,str) or SHA40.fullmatch(expected_sha) is None:
        problems.add("SOURCE_COMMIT_NOT_PINNED")
    if problems:return result(run_id,expected_sha,problems,observed)
    paths={"run":f"/actions/runs/{run_id}",
           "jobs":f"/actions/runs/{run_id}/jobs?per_page=100",
           "artifacts":f"/actions/runs/{run_id}/artifacts?per_page=100"}
    data={}
    for label,path in paths.items():
        try:
            blob=fetch(path,False)
            if not isinstance(blob,(dict,bytes)):raise ValueError("API_RESPONSE_INVALID")
            if isinstance(blob,bytes):
                raw=blob
                value=json.loads(raw)
            else:
                value=blob
                raw=json.dumps(blob,sort_keys=True,separators=(",",":")).encode()
            if not isinstance(value,dict):raise ValueError("API_RESPONSE_NOT_OBJECT")
            observed[label]={"sha256":sha(raw),"bytes":len(raw),"api_path":path}
            data[label]=value
        except (OSError,ValueError,UnicodeError,TypeError,KeyError) as err:
            problems.add("API_READBACK_UNAVAILABLE:"+label)
            observed[label]={"state":"UNVERIFIED","error":type(err).__name__}
    run=data.get("run",{})
    if run:
        if run.get("id")!=run_id:problems.add("RUN_ID_MISMATCH")
        if run.get("head_sha")!=expected_sha:problems.add("RUN_SOURCE_SHA_MISMATCH")
        if run.get("repository",{}).get("full_name")!=REPO:problems.add("REPOSITORY_MISMATCH")
        if run.get("path")!=".github/workflows/aether217-rust-qualification.yml":
            problems.add("WORKFLOW_MISMATCH")
        if run.get("status")!="completed":problems.add("RUN_NOT_TERMINAL")
        if run.get("conclusion")!="success":problems.add("RUN_NOT_SUCCESS")
    jobs=data.get("jobs",{}).get("jobs")
    if not isinstance(jobs,list):
        jobs=[]
        problems.add("JOBS_NOT_OBSERVED")
    if data.get("jobs",{}).get("total_count",len(jobs))>len(jobs):
        problems.add("JOBS_PAGE_INCOMPLETE")
    matched=[j for j in jobs if isinstance(j,dict)
             and j.get("name")=="Native Rust qualification with captured failure diagnostics"]
    if len(matched)!=1:
        problems.add("QUALIFICATION_JOB_NOT_UNIQUE")
    else:
        job=matched[0]
        if job.get("run_id")!=run_id:problems.add("JOB_RUN_ID_MISMATCH")
        if job.get("status")!="completed" or job.get("conclusion")!="success":
            problems.add("QUALIFICATION_JOB_NOT_SUCCESS")
        steps=job.get("steps")
        if not isinstance(steps,list) or not steps:problems.add("JOB_STEPS_UNOBSERVED")
        elif any(not isinstance(s,dict) or s.get("conclusion")!="success" for s in steps):
            problems.add("JOB_STEP_FAILURE")
        job_id=job.get("id")
        if type(job_id) is int and job_id>0:
            try:
                log=fetch(f"/actions/jobs/{job_id}/logs",True)
                if not isinstance(log,bytes) or not log:raise ValueError("EMPTY_JOB_LOG")
                observed["job_log"]={"sha256":sha(log),"bytes":len(log),"job_id":job_id}
            except (OSError,ValueError,TypeError) as err:
                problems.add("ACTUAL_JOB_LOG_NOT_OBSERVED")
                observed["job_log"]={"state":"UNVERIFIED","error":type(err).__name__}
        else:problems.add("JOB_ID_UNPINNED")
    artifacts=data.get("artifacts",{}).get("artifacts")
    if not isinstance(artifacts,list):
        artifacts=[]
        problems.add("ARTIFACT_LIST_NOT_OBSERVED")
    if data.get("artifacts",{}).get("total_count",len(artifacts))>len(artifacts):
        problems.add("ARTIFACTS_PAGE_INCOMPLETE")
    candidates=[a for a in artifacts if isinstance(a,dict)
                and a.get("name")=="aether218-rust-qualification"]
    if len(candidates)!=1:problems.add("QUALIFICATION_ARTIFACT_NOT_UNIQUE")
    else:
        a=candidates[0]
        if a.get("expired") is not False:problems.add("QUALIFICATION_ARTIFACT_EXPIRED")
        if a.get("workflow_run",{}).get("id")!=run_id:
            problems.add("QUALIFICATION_ARTIFACT_RUN_MISMATCH")
        artifact_id=a.get("id")
        if type(artifact_id) is int and artifact_id>0 and not a.get("expired"):
            try:
                archive=fetch(f"/actions/artifacts/{artifact_id}/zip",True)
                if not isinstance(archive,bytes) or not archive:raise ValueError("EMPTY_HOSTED_ZIP")
                observed["hosted_artifact_zip"]={"sha256":sha(archive),"bytes":len(archive),"artifact_id":artifact_id}
            except (OSError,ValueError,TypeError) as err:
                problems.add("HOSTED_ARCHIVE_BYTES_NOT_OBSERVED")
                observed["hosted_artifact_zip"]={"state":"UNVERIFIED","error":type(err).__name__}
        else:problems.add("ARTIFACT_ID_UNPINNED_OR_EXPIRED")
    return result(run_id,expected_sha,problems,observed)

def result(run_id,commit,problems,observed):
    return {"schema":SCHEMA,"run_id":run_id,"source_commit":commit,
            "verdict":"LIVE_API_BYTES_OBSERVED_UNQUALIFIED" if not problems else "REJECT_OR_UNVERIFIED",
            "reasons":sorted(problems) if problems else
               ["API_OBSERVATIONS_DO_NOT_INDEPENDENTLY_AUTHENTICATE_RUNNER_OR_PHYSICAL_ORIGIN"],
            "observed":observed,**HOLD}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--run-id",type=int,required=True)
    p.add_argument("--source-sha",required=True)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    token=os.environ.get("GITHUB_TOKEN","")
    if not token:
        report=result(a.run_id,a.source_sha,{"GITHUB_TOKEN_NOT_AVAILABLE"},{})
    else:
        report=acquire(a.run_id,a.source_sha,lambda path,raw:read_api(token,path,raw))
    rendered=json.dumps(report,sort_keys=True,indent=2)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(rendered,encoding="utf-8")
    print(rendered,end="")
    return 0 if report["verdict"]=="LIVE_API_BYTES_OBSERVED_UNQUALIFIED" else 1

if __name__=="__main__":
    sys.exit(main())
