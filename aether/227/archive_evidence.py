#!/usr/bin/env python3
"""AETHER-227 — content-addressed archive export and independent-byte review.

Export a canonical ZIP of locally observed CI evidence; verify an externally
provided ZIP without extraction. A local archive is NOT the GitHub Actions
artifact ZIP, and successful byte parity is NOT independently authenticated
CI execution, original device evidence or external custody.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import zipfile

SCHEMA="AETHER-227/archive-inventory-v1"
SHA40=re.compile(r"^[0-9a-f]{40}$")
REQUIRED=("commit.txt","rustc-version.txt","cargo-version.txt","cargo_check.log",
          "cargo_test.log","aether217_cli.log","aether217-report.json",
          "aether218-gate.json","aether219-manifest.json")
HOLD={"native_ci_execution_independently_authenticated":False,
      "github_artifact_remote_retention_authenticated":False,
      "authenticated_original_physical_captures":0,
      "independent_external_custodians":0,
      "physical_qualification_percent":0,"operational_authority":"HOLD",
      "physical_act_allowed":False,"may_recover":False,"may_repair":False,
      "may_reclaim_lock":False,"may_choose_history":False}

def digest(raw:bytes)->str:
    return hashlib.sha256(raw).hexdigest()

def canonical(v:object)->bytes:
    return (json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()

def safe_name(name:str)->bool:
    if not isinstance(name,str) or not name or "\\" in name or "\x00" in name or name.startswith("/"):
        return False
    path=PurePosixPath(name)
    return not path.is_absolute() and all(x not in ("..",".") for x in name.split("/")) and not name.endswith("/")

def inspect_zip(raw:bytes,expected_commit:str,max_files:int=256,max_file_size:int=8*1024*1024)->dict:
    errors=set()
    items={}
    if not isinstance(expected_commit,str) or not SHA40.fullmatch(expected_commit):
        errors.add("EXPECTED_SOURCE_COMMIT_UNPINNED")
    if not isinstance(raw,bytes):
        return report(errors|{"ARCHIVE_BYTES_MISSING"},items,None,expected_commit)
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            infos=z.infolist()
            if len(infos)>max_files:errors.add("ARCHIVE_ENTRY_COUNT_EXCEEDED")
            seen=set()
            for info in infos:
                name=info.filename
                if name in seen:errors.add("DUPLICATE_ARCHIVE_ENTRY")
                seen.add(name)
                if not safe_name(name):
                    errors.add("UNSAFE_ARCHIVE_PATH")
                    continue
                mode=info.external_attr>>16
                if stat.S_IFMT(mode)==stat.S_IFLNK:
                    errors.add("SYMLINK_ARCHIVE_ENTRY")
                    continue
                if info.is_dir():
                    errors.add("DIRECTORY_ENTRY_NOT_EXPECTED")
                    continue
                if info.file_size>max_file_size:
                    errors.add("ARCHIVE_FILE_SIZE_EXCEEDED")
                    continue
                try:
                    data=z.read(info)
                except (OSError,RuntimeError,zipfile.BadZipFile):
                    errors.add("CORRUPT_ARCHIVE_ENTRY")
                    continue
                if len(data)!=info.file_size or len(data)>max_file_size:
                    errors.add("ARCHIVE_UNCOMPRESSED_SIZE_MISMATCH")
                    continue
                items[name]={"bytes":len(data),"sha256":digest(data)}
            missing=set(REQUIRED)-set(items)
            if missing:errors.add("REQUIRED_EVIDENCE_MISSING")
            if "commit.txt" in items:
                commit_data=z.read("commit.txt").strip().decode("utf-8",errors="replace")
                if commit_data!=expected_commit:errors.add("SOURCE_COMMIT_MISMATCH")
            if "aether218-gate.json" in items:
                try:
                    gate=json.loads(z.read("aether218-gate.json"))
                    if gate.get("source_commit")!=expected_commit:errors.add("NATIVE_GATE_SOURCE_MISMATCH")
                    if gate.get("native_qualification_passed") is not True:
                        errors.add("NATIVE_EXECUTION_NOT_QUALIFIED")
                    if gate.get("operational_authority")!="HOLD" or gate.get("physical_qualification_percent")!=0:
                        errors.add("GATE_AUTHORITY_PROMOTION")
                except (ValueError,UnicodeError):
                    errors.add("GATE_JSON_INVALID")
            if "aether219-manifest.json" in items:
                try:
                    manifest=json.loads(z.read("aether219-manifest.json"))
                    if manifest.get("source_commit")!=expected_commit:errors.add("MANIFEST_SOURCE_MISMATCH")
                    if manifest.get("operational_authority")!="HOLD" or manifest.get("physical_qualification_percent")!=0:
                        errors.add("MANIFEST_AUTHORITY_PROMOTION")
                    if manifest.get("native_qualification_verified_by_this_manifest") is not True:
                        errors.add("MANIFEST_NATIVE_QUALIFICATION_NOT_PASSED")
                except (ValueError,UnicodeError):
                    errors.add("MANIFEST_JSON_INVALID")
    except (OSError,ValueError,zipfile.BadZipFile,zipfile.LargeZipFile):
        errors.add("ARCHIVE_CORRUPT_OR_UNREADABLE")
    return report(errors,items,digest(raw),expected_commit)

def report(errors:set[str],items:dict,zip_hash:str|None,commit:str)->dict:
    stable={"source_commit":commit,"files":items}
    return {"schema":SCHEMA,
        "verdict":"DOCUMENTARY_ARCHIVE_BYTES_CONSISTENT_ONLY" if not errors else "REJECT",
        "reasons":sorted(errors) if errors else ["ARCHIVE_ORIGIN_AND_REMOTE_RETENTION_NOT_INDEPENDENTLY_AUTHENTICATED"],
        "source_commit":commit,"archive_sha256":zip_hash,
        "inventory_sha256":digest(canonical(stable)),"entry_count":len(items),
        "entries":dict(sorted(items.items())),**HOLD}

def export(directory:Path,source_commit:str)->bytes:
    if not SHA40.fullmatch(source_commit):raise ValueError("Unpinned commit")
    names=sorted(x.name for x in directory.iterdir() if x.is_file() and x.name in REQUIRED)
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,"w",compression=zipfile.ZIP_STORED,allowZip64=False) as z:
        for name in names:
            data=(directory/name).read_bytes()
            if len(data)>8*1024*1024:raise ValueError("File too large")
            info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_STORED
            info.external_attr=(stat.S_IFREG|0o644)<<16
            z.writestr(info,data)
    return stream.getvalue()

def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-sha",required=True)
    parser.add_argument("--directory",type=Path)
    parser.add_argument("--archive",type=Path)
    parser.add_argument("--out",type=Path)
    parser.add_argument("--export",dest="export_path",type=Path)
    a=parser.parse_args()
    if a.export_path is not None:
        if a.directory is None:
            print("REJECT: source evidence directory required",file=sys.stderr)
            return 2
        try:
            raw=export(a.directory,a.source_sha)
            a.export_path.parent.mkdir(parents=True,exist_ok=True)
            a.export_path.write_bytes(raw)
        except (OSError,ValueError) as e:
            print("REJECT: "+str(e),file=sys.stderr)
            return 2
    else:
        try:
            raw=a.archive.read_bytes() if a.archive else None
        except OSError:
            raw=None
    result=inspect_zip(raw,a.source_sha)
    output=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(output,encoding="utf-8")
    print(output,end="")
    return 0 if result["verdict"]=="DOCUMENTARY_ARCHIVE_BYTES_CONSISTENT_ONLY" else 1

if __name__=="__main__":
    sys.exit(main())
