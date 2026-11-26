#!/usr/bin/env python3
"""AETHER-220: read-only browser/native artifact parity gate.

A matching pair of files is only byte parity. Neither same-repository pins nor
matching synthetic records prove native execution or independent custody.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

SCHEMA = "AETHER-220/artifact-parity-v1"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
FORBIDDEN = ("physical_act_allowed", "may_recover", "may_repair", "may_reclaim_lock", "may_choose_history")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def fail(reason: str, **extra: object) -> dict:
    return dict(schema=SCHEMA, verdict="REJECT", reasons=[reason],
                documentary_byte_parity=False, native_execution_proven=False,
                independent_remote_custody_proven=False, physical_qualification_percent=0,
                operational_authority="HOLD", physical_act_allowed=False,
                may_recover=False, **extra)


def evaluate(reference: dict, native_bytes: bytes | None, browser_bytes: bytes | None,
             native_manifest: dict | None = None) -> dict:
    """Inputs must be supplied independently by caller; never trust self-reported PASS."""
    if reference.get("schema") != "AETHER-220/pinned-reference-v1":
        return fail("REFERENCE_SCHEMA_MISMATCH")
    pinned_sha = reference.get("artifact_sha256")
    pinned_commit = reference.get("source_commit")
    if not isinstance(pinned_sha, str) or not HEX64.fullmatch(pinned_sha):
        return fail("REFERENCE_SHA256_UNPINNED")
    if not isinstance(pinned_commit, str) or not HEX40.fullmatch(pinned_commit):
        return fail("SOURCE_COMMIT_UNPINNED")
    if not isinstance(native_bytes, bytes):
        return fail("NATIVE_ARTIFACT_NOT_OBSERVED")
    if not isinstance(browser_bytes, bytes):
        return fail("BROWSER_ARTIFACT_NOT_OBSERVED")
    native_hash = sha256(native_bytes)
    browser_hash = sha256(browser_bytes)
    if native_hash != browser_hash:
        return fail("BROWSER_NATIVE_BYTES_DIVERGE", native_sha256=native_hash, browser_sha256=browser_hash)
    if native_hash != pinned_sha:
        return fail("ARTIFACT_REFERENCE_PIN_MISMATCH", native_sha256=native_hash, browser_sha256=browser_hash)
    try:
        record = json.loads(native_bytes.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError):
        return fail("PINNED_ARTIFACT_NOT_JSON")
    if not isinstance(record, dict):
        return fail("PINNED_ARTIFACT_NOT_OBJECT")
    if record.get("operational_authority") != "HOLD" or record.get("physical_qualification_percent") != 0:
        return fail("PINNED_ARTIFACT_AUTHORITY_PROMOTION")
    for field in FORBIDDEN:
        if record.get(field) is not False:
            return fail("PINNED_ARTIFACT_PERMISSION_INVALID:" + field)
    if native_manifest is not None:
        if native_manifest.get("source_commit") != pinned_commit:
            return fail("NATIVE_MANIFEST_SOURCE_COMMIT_MISMATCH")
        if native_manifest.get("native_qualification_verified_by_this_manifest") is not True:
            return fail("NATIVE_QUALIFICATION_NOT_VERIFIED")
        if native_manifest.get("operational_authority") != "HOLD" or native_manifest.get("physical_qualification_percent") != 0:
            return fail("NATIVE_MANIFEST_AUTHORITY_PROMOTION")
    return dict(schema=SCHEMA, verdict="DOCUMENTARY_BYTES_MATCH_ONLY",
                reasons=["NATIVE_EXECUTION_AND_INDEPENDENT_REMOTE_CUSTODY_NOT_PROVEN_BY_PARITY"],
                artifact_sha256=pinned_sha, source_commit=pinned_commit,
                documentary_byte_parity=True, native_execution_proven=False,
                independent_remote_custody_proven=False, physical_qualification_percent=0,
                operational_authority="HOLD", physical_act_allowed=False, may_recover=False)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference", type=Path, required=True)
    ap.add_argument("--native", type=Path, required=True)
    ap.add_argument("--browser", type=Path, required=True)
    ap.add_argument("--native-manifest", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    try:
        ref = json.loads(args.reference.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        ref = {}
    def read(path: Path) -> bytes | None:
        try:
            return path.read_bytes()
        except OSError:
            return None
    manifest = None
    if args.native_manifest:
        try:
            manifest = json.loads(args.native_manifest.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            manifest = {"source_commit": None}
    result = evaluate(ref, read(args.native), read(args.browser), manifest)
    output = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if result["documentary_byte_parity"] else 1


if __name__ == "__main__":
    sys.exit(main())
