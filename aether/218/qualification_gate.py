#!/usr/bin/env python3
"""AETHER-218: fail-closed native Rust qualification runner.

Runs only inside the current checked-out worktree. No fabricated PASS if Cargo,
Rust, sources, freeze records, or test evidence are unavailable.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
CRATE = ROOT / "rust"
ARTIFACTS = CRATE / "qualification-artifacts"
CHECKS = (
    ("cargo_check", ("cargo", "check", "--all-targets")),
    ("cargo_test", ("cargo", "test", "--all-targets", "--", "--nocapture")),
    ("aether217_cli", ("cargo", "run", "--quiet", "--bin", "aether217_qualification")),
)
EXPECTED_SOURCE = "AETHER-216"
EXPECTED_BOUND = "AETHER-218"


def classify(results: dict, report: dict | None) -> dict:
    """Pure gate: success requires THREE actual native command results."""
    failures = []
    for name, _ in CHECKS:
        result = results.get(name)
        if not isinstance(result, dict) or result.get("executed") is not True:
            failures.append("EXECUTION_NOT_OBSERVED:" + name)
        elif result.get("returncode") != 0:
            failures.append("NATIVE_COMMAND_FAILED:" + name)
    if report is None:
        failures.append("QUALIFICATION_JSON_MISSING_OR_INVALID")
    else:
        if report.get("source_freeze") != EXPECTED_SOURCE or report.get("documentary_decision_consistent") is not True:
            failures.append("FROZEN_DECISION_NOT_VERIFIED")
        if report.get("physical_qualification_percent") != 0 or report.get("operational_authority") != "HOLD":
            failures.append("PHYSICAL_AUTHORITY_BOUNDARY_FAILED")
        for field in ("physical_act_allowed", "may_repair", "may_recover", "may_reclaim_lock", "may_choose_history"):
            if report.get(field) is not False:
                failures.append("AUTHORITY_FLAG_MISMATCH:" + field)
    return {
        "schema": "AETHER-218/native-qualification-v1",
        "bound": EXPECTED_BOUND,
        "native_qualification_passed": not failures,
        "reasons": failures,
        "physical_qualification_percent": 0,
        "independent_remote_custody_authenticated": False,
        "operational_authority": "HOLD",
        "physical_act_allowed": False,
        "may_recover": False,
        "source_only_does_not_mean_executed": True,
    }


def run(name: str, args: tuple[str, ...]) -> dict:
    logfile = ARTIFACTS / f"{name}.log"
    if shutil.which(args[0]) is None:
        logfile.write_text(f"NOT EXECUTED: executable unavailable: {args[0]}\n", encoding="utf-8")
        return {"executed": False, "returncode": None, "command": list(args), "log": logfile.name}
    try:
        with logfile.open("w", encoding="utf-8") as output:
            child = subprocess.run(args, cwd=CRATE, text=True, stdout=output, stderr=subprocess.STDOUT, check=False)
        return {"executed": True, "returncode": child.returncode, "command": list(args), "log": logfile.name}
    except OSError as exc:
        logfile.write_text(f"NOT EXECUTED: {exc}\n", encoding="utf-8")
        return {"executed": False, "returncode": None, "command": list(args), "log": logfile.name}


def main() -> int:
    parser = argparse.ArgumentParser(description="AETHER-218 fail-closed native qualification")
    parser.add_argument("--self-test", action="store_true", help="test pure rejection logic without Cargo")
    args = parser.parse_args()
    if args.self_test:
        blank = classify({}, None)
        assert not blank["native_qualification_passed"]
        assert blank["operational_authority"] == "HOLD"
        synthetic = {name: {"executed": True, "returncode": 0} for name, _ in CHECKS}
        false_physical = classify(synthetic, {
            "source_freeze": EXPECTED_SOURCE,
            "documentary_decision_consistent": True,
            "physical_qualification_percent": 100,
            "operational_authority": "ACT",
            "physical_act_allowed": True,
        })
        assert not false_physical["native_qualification_passed"]
        print("PASS: AETHER-218 synthetic fail-closed rejection checks (NOT native Rust tests)")
        return 0
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=CRATE, capture_output=True, text=True, check=False)
    revision = commit.stdout.strip() if commit.returncode == 0 else "UNVERIFIED"
    results = {}
    for name, command in CHECKS:
        result = run(name, command)
        results[name] = result
        print(f"{name}: {'exit='+str(result['returncode']) if result['executed'] else 'NOT EXECUTED'}", flush=True)
        # Never attempt a downstream command if a prior gate was not passed.
        if not result["executed"] or result["returncode"] != 0:
            break
    cli_report = None
    if results.get("aether217_cli", {}).get("returncode") == 0:
        log = (ARTIFACTS / "aether217_cli.log").read_text(encoding="utf-8")
        try:
            cli_report = json.loads(log)
            (ARTIFACTS / "aether217-report.json").write_text(
                json.dumps(cli_report, indent=2) + "\n", encoding="utf-8"
            )
        except json.JSONDecodeError:
            pass
    assessment = classify(results, cli_report)
    assessment["source_commit"] = revision
    assessment["observed_utc"] = timestamp
    assessment["commands"] = results
    (ARTIFACTS / "aether218-gate.json").write_text(
        json.dumps(assessment, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(assessment, indent=2), flush=True)
    return 0 if assessment["native_qualification_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
