#!/usr/bin/env python3
"""Validate full AI Space discovery catalog; fail closed, no network."""
import json
from pathlib import Path
from collections import Counter
import sys
p=Path("worlds/ai-space/github-discovery-full.json")
try:
    raw=p.read_bytes()
    data=json.loads(raw)
    rows=data["repositories"]
    assert isinstance(rows,list) and rows,"missing/empty repositories"
    assert data.get("discovered_count")==len(rows),"declared count differs from entries"
    ids=[str(r["id"]) for r in rows]
    names=[r["repository"].lower() for r in rows]
    assert len(set(ids))==len(ids),"duplicate numeric IDs"
    assert len(set(names))==len(names),"duplicate full names"
    assert all(n.startswith("davidwise01/") for n in names),"unexpected repository owner"
    assert all(r.get("url","").startswith("https://github.com/DavidWise01/") for r in rows),"invalid repository URL"
    assert all(r.get("connection")=="discovered_not_connected" for r in rows),"unreviewed repo marked connected"
    assert all(r.get("classification")=="unreviewed" for r in rows),"unreviewed repo assigned an unverified class"
    declared=data.get("profile_public_repos")
    assert declared is None or declared==len(rows),"profile count mismatch"
    result={"status":"PASS","catalog_count":len(rows),"file_bytes":len(raw),"unique_ids":len(set(ids)),"unique_repositories":len(set(names)),"profile_public_repos":declared,"first_repo":names[0],"last_repo":names[-1]}
except (OSError,UnicodeError,ValueError,KeyError,AssertionError,TypeError) as e:
    result={"status":"FAIL","reason":str(e)}
out=Path("worlds/ai-space/catalog-validation.json")
out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2))
sys.exit(0 if result["status"]=="PASS" else 1)
