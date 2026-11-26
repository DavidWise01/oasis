#!/usr/bin/env python3
"""AETHER-224 — immutable-intent documentary Phase XVIII freeze evaluator.

A consistent freeze is not evidence of successful CI, independent custody or ACT.
All conclusions fail closed. Only documentary source completeness is evaluated.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

EXPECTED_BOUNDS = ["AETHER-" + str(i) for i in range(217, 225)]
ZERO_FIELDS = (
    "independently_authenticated_external_custodians",
    "independently_authenticated_external_receipts",
    "authenticated_original_hardware_captures",
    "independently_attested_replay_ledgers",
    "independent_remote_checkpoints",
    "physical_qualification_percent",
)
FALSE_FIELDS = (
    "rust_compilation_verified",
    "rust_regressions_executed_verified",
    "python_regressions_executed_verified",
    "github_actions_success_verified",
    "native_execution_artifacts_independently_authenticated",
    "live_pages_deployment_verified",
    "physical_act_allowed",
    "may_recover", "may_repair", "may_reclaim_lock", "may_choose_history",
)
FALSE_CONSTRAINTS = (
    "documentary_source_completion_is_execution_certification",
    "owned_mirrors_are_independent_sources",
    "synthetic_signatures_prove_remote_controller_identity",
    "self_attested_native_reports_prove_execution",
    "byte_digest_equality_proves_physical_origin",
    "nonce_history_is_independently_authenticated",
    "local_stores_are_crash_atomic",
    "joint_rollback_is_defeated_by_external_checkpoint",
    "git_branch_is_technically_immutable",
)
TRUE_CONSTRAINTS = (
    "original_physical_evidence_required_for_act",
    "unresolved_conflicts_remain_visible",
    "new_evidence_requires_separate_subsequent_qualification",
)
DECISION = "DOCUMENTARY_PHASE_XVIII_CLOSED_EXECUTION_EXTERNAL_CUSTODY_AND_PHYSICAL_EVIDENCE_UNQUALIFIED"
SCHEMA = "AETHER-224/phase-xviii-freeze-v1"

def assess(record: dict) -> dict:
    """Fail closed for unexpected authority promotion and absent disclosures."""
    errors: set[str] = set()
    if not isinstance(record, dict):
        record = {}
    if (record.get("schema") != SCHEMA or record.get("bound") != "AETHER-224"
        or record.get("phase") != "XVIII" or record.get("turn") != 8
        or record.get("planned_turns") != 8):
        errors.add("PHASE_FREEZE_IDENTITY_INVALID")
    if (record.get("phase_state") != "CLOSED_DOCUMENTARY_SOFTWARE_PROTOCOL"
        or record.get("documentary_software_progress_percent") != 100):
        errors.add("DOCUMENTARY_PHASE_CLOSURE_INVALID")
    if record.get("completed_bounds") != EXPECTED_BOUNDS:
        errors.add("BOUND_ORDER_OR_COMPLETENESS_MISMATCH")
    scope = record.get("documentary_scope")
    if (not isinstance(scope, list) or len(scope) != 8 or
        any(not isinstance(line, str) or not line.startswith(str(i) + " ")
            for i, line in zip(range(217,225),scope))):
        errors.add("DOCUMENTARY_SCOPE_MISSING_OR_REORDERED")
    if record.get("documentary_implementation_committed") is not True:
        errors.add("DOCUMENTARY_SOURCE_COMMIT_UNVERIFIED")
    for name in ZERO_FIELDS:
        if type(record.get(name)) is not int or record.get(name) != 0:
            errors.add("UNSUPPORTED_EXTERNAL_OR_PHYSICAL_EVIDENCE:" + name)
    for name in FALSE_FIELDS:
        if record.get(name) is not False:
            errors.add("UNSUPPORTED_EXECUTION_OR_AUTHORITY_PROMOTION:" + name)
    if record.get("operational_authority") != "HOLD":
        errors.add("OPERATIONAL_AUTHORITY_NOT_HOLD")
    constraints = record.get("constraints")
    if not isinstance(constraints, dict):
        constraints = {}
    for name in FALSE_CONSTRAINTS:
        if constraints.get(name) is not False:
            errors.add("TRUST_BOUNDARY_INVALID:" + name)
    for name in TRUE_CONSTRAINTS:
        if constraints.get(name) is not True:
            errors.add("TRUST_BOUNDARY_INVALID:" + name)
    unresolved = record.get("unresolved_fail_closed")
    if (not isinstance(unresolved, list) or len(unresolved) != 10
        or len(set(map(str, unresolved))) != 10
        or any(not isinstance(x,str) or not x.strip() for x in unresolved)):
        errors.add("UNRESOLVED_REQUIREMENTS_NOT_PRESERVED")
    if (record.get("previous_phase_freeze") != "../216/decision.json"
        or record.get("previous_bound") != "../223/protocol.json"
        or record.get("watermark") != ".dlw"):
        errors.add("FROZEN_ANCESTRY_OR_WATERMARK_INVALID")
    if record.get("decision") != DECISION:
        errors.add("FREEZE_DECISION_MISMATCH")
    return {
        "schema": "AETHER-224/freeze-assessment-v1",
        "verdict": ("DOCUMENTARY_PHASE_XVIII_FREEZE_CONSISTENT"
                    if not errors else "REJECT"),
        "reasons": sorted(errors),
        "documentary_software_progress_percent": (
            100 if not errors else 0),
        "independently_authenticated_external_custodians": 0,
        "authenticated_original_hardware_captures": 0,
        "physical_qualification_percent": 0,
        "operational_authority": "HOLD",
        "physical_act_allowed": False,
        "may_recover": False,
        "may_repair": False,
        "may_reclaim_lock": False,
        "may_choose_history": False,
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision", type=Path,
                        default=Path(__file__).with_name("decision.json"))
    parser.add_argument("--out", type=Path)
    a = parser.parse_args()
    try:
        record = json.loads(a.decision.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        record = {}
    result = assess(record)
    content = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(content, encoding="utf-8")
    print(content, end="")
    return 0 if result["verdict"] == "DOCUMENTARY_PHASE_XVIII_FREEZE_CONSISTENT" else 1

if __name__ == "__main__":
    sys.exit(main())
