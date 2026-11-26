#!/usr/bin/env python3
"""AETHER-219: deterministic manifest of observed native qualification artifacts.

Only bytes actually present in the current worktree are hashed. Missing inputs
remain visible as missing; a manifest never confers external custody or ACT.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
CRATE = ROOT / "aether" / "rust"
ARTIFACTS = CRATE / "qualification-artifacts"
INPUTS = (
    "aether/rust/Cargo.toml",
    "aether/rust/src/lib.rs",
    "aether/rust/src/bin/aether217_qualification.rs",
    "aether/rust/src/phase_xvii_freeze.rs",
    "aether/216/decision.json",
    "aether/218/qualification_gate.py",
    "aether/219/evidence_manifest.py",
    ".github/workflows/aether217-rust-qualification.yml",
)
EVIDENCE = (
    "commit.txt",
    "rustc-version.txt",
    "cargo-version.txt",
    "cargo_check.log",
    "cargo_test.log",
    "aether217_cli.log",
    "aether217-report.json",
    "aether218-gate.json",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stable_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def observed_bytes(path: Path, base: Path) -> dict:
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(base.resolve(strict=True))
        if not resolved.is_file():
            return {"state": "NOT_A_FILE"}
        data = resolved.read_bytes()
        return {"state": "OBSERVED", "size_bytes": len(data), "sha256": digest(data)}
    except (OSError, ValueError):
        return {"state": "MISSING_OR_UNSAFE"}


def read_git_revision(root: Path) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"], cwd=root,
            check=False, capture_output=True, text=True, timeout=10,
        )
        result = proc.stdout.strip()
        if proc.returncode == 0 and re.fullmatch(r"[0-9a-f]{40}", result):
            return result
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def source_paths(root: Path) -> tuple[str, ...]:
    """Include every Rust module and regression source, not only the CLI entrypoint."""
    names = set(INPUTS)
    crate = root / "aether" / "rust"
    if crate.is_dir():
        for prefix in ("src", "tests"):
            subtree = crate / prefix
            if subtree.is_dir():
                for file in subtree.rglob("*.rs"):
                    if file.is_file() or file.is_symlink():
                        names.add(file.relative_to(root).as_posix())
        for name in ("Cargo.lock", "Cargo.toml"):
            if (crate / name).exists():
                names.add((crate / name).relative_to(root).as_posix())
    return tuple(sorted(names))


def build_manifest(root: Path, artifacts: Path, revision: str | None) -> dict:
    input_items = {
        name: observed_bytes(root / name, root)
        for name in source_paths(root)
    }
    evidence_items = {
        name: observed_bytes(artifacts / name, artifacts)
        for name in EVIDENCE
    }
    errors = []
    if revision is None:
        errors.append("SOURCE_COMMIT_UNVERIFIED")
    if any(v["state"] != "OBSERVED" for v in input_items.values()):
        errors.append("SOURCE_INPUT_MISSING")
    if any(v["state"] != "OBSERVED" for v in evidence_items.values()):
        errors.append("QUALIFICATION_EVIDENCE_MISSING")
    gate_path = artifacts / "aether218-gate.json"
    try:
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        if gate.get("native_qualification_passed") is not True:
            errors.append("NATIVE_QUALIFICATION_NOT_PASSED")
        if gate.get("source_commit") != revision:
            errors.append("GATE_COMMIT_MISMATCH")
        if gate.get("physical_qualification_percent") != 0 or gate.get("operational_authority") != "HOLD":
            errors.append("GATE_AUTHORITY_VIOLATION")
    except (OSError, UnicodeError, json.JSONDecodeError):
        errors.append("GATE_JSON_NOT_READABLE")
    committed = {"source_commit": revision, "inputs": input_items, "evidence": evidence_items}
    # Stable over identical checked-out source and captured evidence; excludes
    # timestamps, hostname, absolute checkout path, manifest's own hash.
    material_digest = digest(stable_json(committed).encode("utf-8"))
    return {
        "schema": "AETHER-219/reproducible-evidence-manifest-v1",
        "bound": "AETHER-219",
        "source_commit": revision,
        "inputs": input_items,
        "evidence": evidence_items,
        "content_digest_sha256": material_digest,
        "native_qualification_verified_by_this_manifest": len(errors) == 0,
        "reasons": sorted(set(errors)),
        "independent_remote_custody_authenticated": False,
        "physical_qualification_percent": 0,
        "operational_authority": "HOLD",
        "may_repair": False,
        "may_recover": False,
        "physical_act_allowed": False,
        "warning": "A local content digest is reproducibility evidence, not independently authenticated custody.",
    }


def compare(first: dict, second: dict) -> dict:
    # Do not compare the self-described booleans alone. Compare actual
    # content hashes, source revision and ordered file metadata instead.
    same = (
        first.get("source_commit") == second.get("source_commit")
        and first.get("inputs") == second.get("inputs")
        and first.get("evidence") == second.get("evidence")
        and first.get("content_digest_sha256") == second.get("content_digest_sha256")
    )
    return {
        "schema": "AETHER-219/manifest-comparison-v1",
        "content_matches": same,
        "physical_qualification_percent": 0,
        "operational_authority": "HOLD",
        "physical_act_allowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--artifacts", type=Path, default=ARTIFACTS)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--compare", nargs=2, type=Path, metavar=("FIRST", "SECOND"))
    args = parser.parse_args()
    if args.compare:
        try:
            first, second = (json.loads(p.read_text(encoding="utf-8")) for p in args.compare)
        except (OSError, ValueError, UnicodeError) as exc:
            print(f"REJECT: MANIFEST_COMPARISON_INPUT_UNREADABLE: {exc}", file=sys.stderr)
            return 2
        result = compare(first, second)
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0 if result["content_matches"] else 1
    root = args.root.resolve()
    artifacts = args.artifacts.resolve()
    result = build_manifest(root, artifacts, read_git_revision(root))
    output = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if result["native_qualification_verified_by_this_manifest"] else 1


if __name__ == "__main__":
    sys.exit(main())
