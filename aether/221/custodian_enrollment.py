#!/usr/bin/env python3
"""AETHER-221: fail-closed custodian enrollment and external ancestry review.

Only checks documentary structure and cross-record identity. This program
cannot verify a remote controller, cryptographic signature, out-of-band source
or physical capture. No remote custodian becomes authenticated by this gate.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

SCHEMA = "AETHER-221/enrollment-v1"
CHALLENGE_SCHEMA = "AETHER-221/external-challenge-v1"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN = ("physical_act_allowed", "may_recover", "may_repair", "may_reclaim_lock")


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def evaluate(enrollment: dict, challenge: dict, owned: dict) -> dict:
    problems: set[str] = set()
    if enrollment.get("schema") != SCHEMA or challenge.get("schema") != CHALLENGE_SCHEMA:
        problems.add("SCHEMA_INVALID")
    if not isinstance(owned, dict) or not all(isinstance(owned.get(x), str) and owned[x] for x in ("corpus_id","root","operator","administrator")):
        problems.add("OWNED_SOURCE_ANCESTRY_MISSING")
    identity = enrollment.get("custodian", {})
    if not isinstance(identity, dict):
        identity = {}
    fields = ("custodian_id","controller_root","operator","administrator","host","claimed_external_locator")
    if not all(isinstance(identity.get(x), str) and identity[x].strip() for x in fields):
        problems.add("CUSTODIAN_IDENTITY_MISSING")
    issuer = challenge.get("issuer", {})
    if not isinstance(issuer, dict):
        issuer = {}
    if not all(isinstance(issuer.get(x), str) and issuer[x].strip() for x in ("controller_root","operator","administrator")):
        problems.add("CHALLENGE_ISSUER_ANCESTRY_MISSING")
    if not isinstance(owned, dict):
        owned = {}
    for field, owned_field in (("controller_root","root"),("operator","operator"),("administrator","administrator")):
        if identity.get(field) and identity.get(field) == owned.get(owned_field):
            problems.add("CUSTODIAN_MIRRORS_OWNED_SOURCE")
        if issuer.get(field) and issuer.get(field) == owned.get(owned_field):
            problems.add("ISSUER_MIRRORS_OWNED_SOURCE")
        if issuer.get(field) and issuer.get(field) == identity.get(field):
            problems.add("ISSUER_SHARES_CUSTODIAN_CONTROL")
    if enrollment.get("source_corpus_id") != owned.get("corpus_id"):
        problems.add("SOURCE_CORPUS_BINDING_MISMATCH")
    key = enrollment.get("public_key_sha256")
    if not isinstance(key, str) or not HEX64.fullmatch(key):
        problems.add("CUSTODIAN_KEY_FINGERPRINT_INVALID")
    if enrollment.get("enrollment_id") != challenge.get("enrollment_id"):
        problems.add("CHALLENGE_ENROLLMENT_MISMATCH")
    if identity.get("custodian_id") != challenge.get("custodian_id"):
        problems.add("CHALLENGE_CUSTODIAN_MISMATCH")
    if enrollment.get("challenge_nonce") != challenge.get("nonce") or not isinstance(challenge.get("nonce"), str) or len(challenge.get("nonce")) < 16:
        problems.add("CHALLENGE_NONCE_MISMATCH_OR_WEAK")
    if enrollment.get("public_key_sha256") != challenge.get("public_key_sha256"):
        problems.add("CHALLENGE_KEY_BINDING_MISMATCH")
    expected = challenge.get("evidence_sha256")
    if not isinstance(expected, str) or not HEX64.fullmatch(expected):
        problems.add("CHALLENGE_EVIDENCE_DIGEST_MISSING")
    if enrollment.get("challenge_digest_sha256") != digest(challenge):
        problems.add("CHALLENGE_RECORD_DIGEST_MISMATCH")
    if not isinstance(challenge.get("external_receipt_locator"), str) or not challenge.get("external_receipt_locator"):
        problems.add("EXTERNAL_RECEIPT_LOCATOR_MISSING")
    if issuer.get("controller_root") == "owned":
        problems.add("SELF_ISSUED_CHALLENGE")
    if challenge.get("replay_checked_out_of_band") is not True:
        problems.add("REPLAY_NOT_INDEPENDENTLY_CHECKED")
    if challenge.get("controller_identity_authenticated_out_of_band") is not True:
        problems.add("CONTROLLER_AUTHENTICATION_UNVERIFIED")
    if challenge.get("receipt_retention_checked_out_of_band") is not True:
        problems.add("EXTERNAL_RETENTION_UNVERIFIED")
    for field in FORBIDDEN:
        if enrollment.get(field) is not False or challenge.get(field) is not False:
            problems.add("OPERATIONAL_PERMISSION_INVALID:" + field)
    if enrollment.get("operational_authority") != "HOLD" or challenge.get("operational_authority") != "HOLD":
        problems.add("AUTHORITY_HOLD_INVALID")
    # Critical trust limit: all supplied booleans and apparent source-root
    # distinctions are merely caller claims, including when the checks agree.
    issues = sorted(problems)
    return {
        "schema": "AETHER-221/enrollment-assessment-v1",
        "verdict": "REJECT" if issues else "DOCUMENTARY_ENROLLMENT_CLAIMS_CONSISTENT_ONLY",
        "reasons": issues or ["EXTERNAL_ORIGIN_AND_CONTROL_NOT_INDEPENDENTLY_OBSERVED"],
        "enrollment_sha256": digest(enrollment),
        "challenge_sha256": digest(challenge),
        "independently_authenticated_custodians": 0,
        "independent_original_captures": 0,
        "original_evidence_authenticated": False,
        "physical_qualification_percent": 0,
        "may_repair": False, "may_recover": False,
        "may_reclaim_lock": False, "physical_act_allowed": False,
        "operational_authority": "HOLD",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--enrollment", type=Path, required=True)
    parser.add_argument("--challenge", type=Path, required=True)
    parser.add_argument("--owned", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        enrollment = json.loads(args.enrollment.read_text(encoding="utf-8"))
        challenge = json.loads(args.challenge.read_text(encoding="utf-8"))
        owned = json.loads(args.owned.read_text(encoding="utf-8"))
        if not all(isinstance(v, dict) for v in (enrollment, challenge, owned)):
            raise ValueError("Input JSON objects required")
        result = evaluate(enrollment, challenge, owned)
    except (OSError, UnicodeError, ValueError) as exc:
        result = {
            "schema": "AETHER-221/enrollment-assessment-v1",
            "verdict": "REJECT", "reasons": ["EVIDENCE_INPUT_UNREADABLE:" + str(exc)],
            "independently_authenticated_custodians": 0,
            "physical_qualification_percent": 0,
            "may_recover": False, "physical_act_allowed": False, "operational_authority": "HOLD",
        }
    output = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if result["verdict"] == "DOCUMENTARY_ENROLLMENT_CLAIMS_CONSISTENT_ONLY" else 1


if __name__ == "__main__":
    sys.exit(main())
