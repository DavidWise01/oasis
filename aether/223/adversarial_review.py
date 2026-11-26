#!/usr/bin/env python3
"""AETHER-223: integrated adversarial evidence review, READ-ONLY.

Combines AETHER-221 declared custodian enrollment, AETHER-222 byte/challenge
review and AETHER-218/219 native execution artifacts. Correct self-reported
claims are not external authentication. No outcome grants physical authority.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
HOLD = {
    "independently_authenticated_remote_custodians": 0,
    "authenticated_original_physical_captures": 0,
    "physical_qualification_percent": 0,
    "operational_authority": "HOLD",
    "physical_act_allowed": False,
    "may_repair": False,
    "may_recover": False,
    "may_reclaim_lock": False,
    "may_choose_history": False,
}


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _strings_equal(a: dict, b: dict, pairs: tuple[tuple[str, str], ...]) -> bool:
    return all(a.get(left) == b.get(right) and isinstance(a.get(left), str)
               and bool(a[left]) for left, right in pairs)


def evaluate(enrollment: dict, challenge: dict, owned: dict,
             original: dict, receipt_bytes: bytes | None, capture_bytes: bytes | None,
             prior_nonces: set[str] | None, native_gate: dict | None,
             native_manifest: dict | None) -> dict:
    enroll = load("aether221_enroll", ROOT / "221" / "custodian_enrollment.py")
    original_mod = load("aether222_original", ROOT / "222" / "original_evidence.py")
    ancestry = enroll.evaluate(enrollment, challenge, owned)
    physical = original_mod.evaluate(original, receipt_bytes, capture_bytes, prior_nonces)
    reasons = set()
    if ancestry.get("verdict") != "DOCUMENTARY_ENROLLMENT_CLAIMS_CONSISTENT_ONLY":
        reasons.add("CUSTODIAN_ENROLLMENT_REJECTED")
        reasons.update("ENROLL:" + str(x) for x in ancestry.get("reasons", []))
    if physical.get("verdict") != "DOCUMENTARY_BYTES_AND_BINDINGS_CONSISTENT_ONLY":
        reasons.add("ORIGINAL_EVIDENCE_CHALLENGE_REJECTED")
        reasons.update("CAPTURE:" + str(x) for x in physical.get("reasons", []))
    holder = enrollment.get("custodian")
    if not isinstance(holder, dict):
        holder = {}
    if not _strings_equal(
        original, holder,
        (("holder_root", "controller_root"), ("holder_operator", "operator"),
         ("holder_administrator", "administrator")),
    ):
        reasons.add("HOLDER_CONTROL_ANCESTRY_CROSS_BOUND_MISMATCH")
    issuer = challenge.get("issuer")
    if not isinstance(issuer, dict):
        issuer = {}
    if not _strings_equal(
        original, issuer,
        (("issuer_root", "controller_root"), ("issuer_operator", "operator"),
         ("issuer_administrator", "administrator")),
    ):
        reasons.add("ISSUER_CONTROL_ANCESTRY_CROSS_BOUND_MISMATCH")
    if not _strings_equal(
        original, owned,
        (("source_root", "root"), ("source_operator", "operator"),
         ("source_administrator", "administrator")),
    ):
        reasons.add("SOURCE_CONTROL_ANCESTRY_CROSS_BOUND_MISMATCH")
    if original.get("enrollment_id") != enrollment.get("enrollment_id"):
        reasons.add("ENROLLMENT_ID_CROSS_BOUND_MISMATCH")
    if original.get("nonce") != challenge.get("nonce"):
        reasons.add("CHALLENGE_NONCE_CROSS_BOUND_MISMATCH")
    if original.get("holder_key_sha256") != enrollment.get("public_key_sha256"):
        reasons.add("HOLDER_KEY_CROSS_BOUND_MISMATCH")
    if not isinstance(native_gate, dict):
        reasons.add("OBSERVED_NATIVE_EXECUTION_GATE_MISSING")
    else:
        if native_gate.get("native_qualification_passed") is not True:
            reasons.add("NATIVE_EXECUTION_NOT_VERIFIED")
        if native_gate.get("operational_authority") != "HOLD" or native_gate.get("physical_act_allowed") is not False:
            reasons.add("NATIVE_EXECUTION_AUTHORITY_PROMOTION")
    if not isinstance(native_manifest, dict):
        reasons.add("NATIVE_MANIFEST_MISSING")
    else:
        if native_manifest.get("native_qualification_verified_by_this_manifest") is not True:
            reasons.add("NATIVE_MANIFEST_NOT_VERIFIED")
        if not isinstance(native_gate, dict) or native_manifest.get("source_commit") != native_gate.get("source_commit"):
            reasons.add("NATIVE_SOURCE_REVISION_CONFLICT")
        if native_manifest.get("operational_authority") != "HOLD" or native_manifest.get("physical_qualification_percent") != 0:
            reasons.add("NATIVE_MANIFEST_AUTHORITY_PROMOTION")
    # Even when caller-provided artifacts are internally consistent and say
    # native execution passed, this evaluator cannot authenticate their origin.
    if not reasons:
        reasons.add("INDEPENDENT_ORIGIN_AND_EXECUTION_ATTESTATION_NOT_OBSERVED")
    return {
        "schema": "AETHER-223/adversarial-independent-evidence-v1",
        "verdict": "REJECT" if any(x != "INDEPENDENT_ORIGIN_AND_EXECUTION_ATTESTATION_NOT_OBSERVED" for x in reasons)
                   else "DOCUMENTARY_ENSEMBLE_CONSISTENT_ONLY",
        "reasons": sorted(reasons),
        "enrollment_verdict": ancestry.get("verdict"),
        "capture_verdict": physical.get("verdict"),
        "native_gate_claimed_success": isinstance(native_gate, dict) and native_gate.get("native_qualification_passed") is True,
        "external_signature_verification_performed": False,
        "independent_remote_evidence_retrieved": False,
        "external_replay_ledger_authenticated": False,
        **HOLD,
    }


def _read_json(path: Path | None):
    if path is None:
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (OSError, ValueError, UnicodeError):
        return None


def _bytes(path: Path | None) -> bytes | None:
    if path is None:
        return None
    try:
        if not path.is_file() or path.stat().st_size > 4 * 1024 * 1024:
            return None
        return path.read_bytes()
    except OSError:
        return None


def main() -> int:
    p = argparse.ArgumentParser()
    for field in ("enrollment", "challenge", "owned", "original"):
        p.add_argument("--" + field, type=Path, required=True)
    for field in ("receipt", "capture", "nonce-ledger", "native-gate", "native-manifest", "out"):
        p.add_argument("--" + field, type=Path)
    a = p.parse_args()
    ledger = None
    if a.nonce_ledger is not None:
        try:
            values = json.loads(a.nonce_ledger.read_text(encoding="utf-8"))
            if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
                raise ValueError("invalid nonce ledger")
            ledger = set(values)
        except (OSError, ValueError, UnicodeError):
            ledger = {_read_json(a.original).get("nonce")} if _read_json(a.original) else {"MISSING_NONCE"}
    verdict = evaluate(
        _read_json(a.enrollment) or {}, _read_json(a.challenge) or {},
        _read_json(a.owned) or {}, _read_json(a.original) or {},
        _bytes(a.receipt), _bytes(a.capture), ledger,
        _read_json(a.native_gate), _read_json(a.native_manifest),
    )
    output = json.dumps(verdict, indent=2, sort_keys=True) + "\n"
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if verdict["verdict"] == "DOCUMENTARY_ENSEMBLE_CONSISTENT_ONLY" else 1


if __name__ == "__main__":
    sys.exit(main())
