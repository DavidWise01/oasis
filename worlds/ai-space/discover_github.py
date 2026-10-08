#!/usr/bin/env python3
"""Discover all public repositories owned by DavidWise01 with GitHub REST pagination.

This avoids GitHub Search's 1,000-result ceiling. Classification is conservative:
repositories are candidates, never assumed to contain runnable agents.
"""
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request

OWNER = os.getenv("OASIS_DISCOVERY_OWNER", "DavidWise01")
OUT = Path(os.getenv("OASIS_DISCOVERY_OUTPUT", "worlds/ai-space/github-discovery-full.json"))

def github(path):
    request=urllib.request.Request(
        "https://api.github.com"+path,
        headers={
            "Accept":"application/vnd.github+json",
            "User-Agent":"oasis-ai-space-discovery/0.2",
            **({"Authorization":"Bearer "+os.environ["GITHUB_TOKEN"]} if os.getenv("GITHUB_TOKEN") else {})
        }
    )
    with urllib.request.urlopen(request,timeout=30) as resp:
        return json.load(resp)

def main():
    profile=github("/users/"+urllib.parse.quote(OWNER))
    expected=profile.get("public_repos")
    repos=[]
    page=1
    while True:
        path="/users/"+urllib.parse.quote(OWNER)+"/repos?per_page=100&page="+str(page)+"&type=owner&sort=full_name&direction=asc"
        rows=github(path)
        if not isinstance(rows,list):
            raise RuntimeError("Unexpected GitHub API response")
        for row in rows:
            if row.get("owner",{}).get("login","").lower()!=OWNER.lower():
                continue
            repos.append({
                "id":row["id"],
                "name":row["name"],
                "repository":row["full_name"],
                "url":row["html_url"],
                "default_branch":row.get("default_branch"),
                "description":row.get("description"),
                "archived":row.get("archived",False),
                "fork":row.get("fork",False),
                "visibility":row.get("visibility","public"),
                "classification":"unreviewed",
                "connection":"discovered_not_connected"
            })
        if len(rows)<100:break
        page+=1
        if page>1000:raise RuntimeError("Safety page bound reached")
    unique={r["id"]:r for r in repos}
    if len(unique)!=len(repos):
        raise RuntimeError("Duplicates detected during pagination; retry with stable snapshot")
    if expected is not None and expected!=len(repos):
        raise RuntimeError(f"Incomplete crawl: profile public_repos={expected}, collected={len(repos)}")
    catalog={
        "schema":"oasis/agent-discovery/v0.2",
        "source":"GitHub REST /users/{owner}/repos (paginated)",
        "owner":OWNER,
        "profile_public_repos":expected,
        "discovered_count":len(repos),
        "classification_policy":"unreviewed; no remote code is executed",
        "external_site":{"url":"https://0root.ai","status":"separate crawl required"},
        "repositories":sorted(repos,key=lambda r:r["repository"].lower())
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"PASS: {len(repos)} repositories inventoried across {page} pages")
    return 0

if __name__=="__main__":
    try:sys.exit(main())
    except (urllib.error.URLError,RuntimeError,KeyError) as exc:
        print("BLOCKED:",exc,file=sys.stderr)
        sys.exit(1)
