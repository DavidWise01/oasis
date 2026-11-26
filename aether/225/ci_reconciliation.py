#!/usr/bin/env python3
"""AETHER-225 — read-only GitHub Actions evidence reconciliation.

Input records must be independently fetched before interpretation. This module
does not query GitHub and cannot authenticate the supplied JSON's origin.
A complete synthetic bundle can be documentary-consistent, never independent
runtime attestation or physical authority. Missing evidence is explicit HOLD.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

SCHEMA="AETHER-225/ci-reconciliation-v1"
HEX40=re.compile(r"^[0-9a-f]{40}$")
HEX64=re.compile(r"^[0-9a-f]{64}$")
REQUIRED_STEPS=("Fetch exact repository revision","Install stable Rust toolchain",
                "Record compiler and source revision",
                "Run native Cargo gate and capture failures",
                "Build exact-content evidence manifest, even after Cargo failure")
HOLD={"independently_authenticated_ci_execution":False,
      "independently_authenticated_external_custodians":0,
      "authenticated_original_hardware_captures":0,
      "physical_qualification_percent":0,"operational_authority":"HOLD",
      "may_repair":False,"may_recover":False,"may_reclaim_lock":False,
      "may_choose_history":False,"physical_act_allowed":False}

def sha256(raw:bytes)->str:
    return hashlib.sha256(raw).hexdigest()

def reconcile(target:dict,run:dict|None,jobs:list|None,artifacts:list|None,
              log_bytes:bytes|None,manifest_bytes:bytes|None)->dict:
    issues=set()
    if not isinstance(target,dict) or not HEX40.fullmatch(str(target.get("target_sha",""))):
        issues.add("TARGET_COMMIT_UNPINNED")
    if not isinstance(run,dict):
        issues.add("GITHUB_RUN_NOT_OBSERVED")
        run={}
    else:
        if not isinstance(run.get("id"),int) or run["id"]<=0:
            issues.add("RUN_ID_INVALID")
        if run.get("head_sha")!=target.get("target_sha"):
            issues.add("RUN_SOURCE_COMMIT_MISMATCH")
        if run.get("repository")!="DavidWise01/oasis":
            issues.add("RUN_REPOSITORY_MISMATCH")
        if run.get("status")!="completed" or run.get("conclusion")!="success":
            issues.add("RUN_NOT_COMPLETED_SUCCESSFULLY")
        if run.get("event") not in ("push","workflow_dispatch"):
            issues.add("RUN_TRIGGER_UNEXPECTED")
    if not isinstance(jobs,list) or not jobs:
        issues.add("RUN_JOBS_NOT_OBSERVED")
        jobs=[]
    qualified=[j for j in jobs if isinstance(j,dict) and
               j.get("name")=="Native Rust qualification with captured failure diagnostics"]
    if len(qualified)!=1:
        issues.add("QUALIFICATION_JOB_NOT_UNIQUE")
    for job in qualified:
        if job.get("run_id")!=run.get("id"):
            issues.add("JOB_RUN_ID_MISMATCH")
        if job.get("status")!="completed" or job.get("conclusion")!="success":
            issues.add("JOB_NOT_COMPLETED_SUCCESSFULLY")
        steps=job.get("steps")
        if not isinstance(steps,list):
            issues.add("STEP_HISTORY_MISSING")
            continue
        by_name={s.get("name"):s for s in steps if isinstance(s,dict) and isinstance(s.get("name"),str)}
        for required in REQUIRED_STEPS:
            item=by_name.get(required)
            if item is None:
                issues.add("REQUIRED_STEP_MISSING:"+required)
            elif item.get("conclusion")!="success":
                issues.add("REQUIRED_STEP_NOT_SUCCESSFUL:"+required)
    if not isinstance(artifacts,list) or not artifacts:
        issues.add("RUN_ARTIFACTS_NOT_OBSERVED")
        artifacts=[]
    selected=[a for a in artifacts if isinstance(a,dict) and a.get("name")=="aether218-rust-qualification"]
    if len(selected)!=1:
        issues.add("QUALIFICATION_ARTIFACT_NOT_UNIQUE")
    else:
        a=selected[0]
        if a.get("workflow_run_id")!=run.get("id"):
            issues.add("ARTIFACT_RUN_ID_MISMATCH")
        if a.get("expired") is not False or not isinstance(a.get("size_in_bytes"),int) or a["size_in_bytes"]<=0:
            issues.add("ARTIFACT_EXPIRED_OR_EMPTY")
    if not isinstance(log_bytes,bytes):
        issues.add("RUN_LOG_BYTES_MISSING")
    if not isinstance(manifest_bytes,bytes):
        issues.add("RUN_MANIFEST_BYTES_MISSING")
    else:
        try:
            manifest=json.loads(manifest_bytes)
            if not isinstance(manifest,dict): raise ValueError("manifest not object")
            if manifest.get("source_commit")!=target.get("target_sha"):
                issues.add("MANIFEST_SOURCE_COMMIT_MISMATCH")
            if manifest.get("native_qualification_verified_by_this_manifest") is not True:
                issues.add("NATIVE_GATE_NOT_QUALIFIED")
            if manifest.get("operational_authority")!="HOLD" or manifest.get("physical_qualification_percent")!=0:
                issues.add("MANIFEST_AUTHORITY_PROMOTION")
            for key in ("inputs","evidence"):
                item=manifest.get(key)
                if not isinstance(item,dict) or not item:
                    issues.add("MANIFEST_INVENTORY_MISSING:"+key)
        except (UnicodeError,ValueError):
            issues.add("RUN_MANIFEST_JSON_INVALID")
    if log_bytes is not None and not log_bytes.strip():
        issues.add("RUN_LOG_EMPTY")
    if run.get("html_url") and not str(run["html_url"]).startswith("https://github.com/DavidWise01/oasis/actions/runs/"):
        issues.add("RUN_URL_UNTRUSTED")
    verdict="REJECT" if issues else "DOCUMENTARY_CI_RECORD_CONSISTENT_UNAUTHENTICATED"
    return {"schema":SCHEMA,"verdict":verdict,"reasons":sorted(issues) or
            ["SOURCE_OF_GITHUB_RECORDS_NOT_AUTHENTICATED_BY_THIS_OFFLINE_EVALUATOR"],
            "target_sha":target.get("target_sha"),
            "run_id":run.get("id"),
            "job_count":len(jobs),"artifact_count":len(artifacts),
            "log_sha256":sha256(log_bytes) if log_bytes is not None else None,
            "manifest_sha256":sha256(manifest_bytes) if manifest_bytes is not None else None,
            **HOLD}

def read_json(p:Path|None):
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p else None
    except (OSError,UnicodeError,ValueError):
        return None

def read_bytes(p:Path|None):
    try:
        if p is None or not p.is_file() or p.stat().st_size>16*1024*1024:return None
        return p.read_bytes()
    except OSError:return None

def main()->int:
    p=argparse.ArgumentParser()
    for field in ("target","run","jobs","artifacts","log","manifest"):
        p.add_argument("--"+field,type=Path)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    d=reconcile(read_json(a.target) or {},read_json(a.run),read_json(a.jobs),
                read_json(a.artifacts),read_bytes(a.log),read_bytes(a.manifest))
    report=json.dumps(d,sort_keys=True,indent=2)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(report,encoding="utf-8")
    print(report,end="")
    return 0 if d["verdict"]=="DOCUMENTARY_CI_RECORD_CONSISTENT_UNAUTHENTICATED" else 1

if __name__=="__main__":
    sys.exit(main())
