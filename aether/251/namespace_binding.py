#!/usr/bin/env python3
"""AETHER-251-RS — fail-closed supervisor/worker namespace challenge review."""
import argparse
import base64
import hashlib
import json
import re
from pathlib import Path

SCHEMA = "AETHER-251/namespace-binding-v1"
HOLD = {"operational_authority": "HOLD", "physical_qualification_percent": 0,
        "physical_act_allowed": False, "independent_custody_authenticated": False,
        "network_isolation_independently_verified": False}

def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("ascii")

def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()

def signature_ok(pem, message, signature):
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key = serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key, Ed25519PublicKey) or len(signature) != 64:
            return False
        key.verify(signature, message)
        return True
    except (ImportError, InvalidSignature, ValueError, TypeError, UnicodeError):
        return False

def assess(bundle, verify=signature_ok):
    errors = []
    seen = {"receipts": []}
    if not isinstance(bundle, dict):
        return {"schema": SCHEMA, "verdict": "REJECT_OR_UNVERIFIED",
                "reasons": ["BUNDLE_INVALID"], "observed": seen, **HOLD}
    challenge = bundle.get("challenge")
    supervisor = bundle.get("supervisor")
    worker = bundle.get("worker")
    receipts = bundle.get("receipts")
    keys = bundle.get("out_of_band_public_keys")
    consumed = bundle.get("previously_consumed_nonces")
    if not isinstance(challenge, dict) or set(challenge) != {
        "challenge_id", "run_id", "source_commit", "nonce"}:
        errors.append("CHALLENGE_SCHEMA_INVALID"); challenge = {}
    if (not isinstance(challenge.get("challenge_id"), str) or
        not challenge["challenge_id"] or len(challenge["challenge_id"]) > 128):
        errors.append("CHALLENGE_ID_INVALID")
    if type(challenge.get("run_id")) is not int or challenge["run_id"] <= 0:
        errors.append("RUN_ID_INVALID")
    commit = challenge.get("source_commit")
    if not isinstance(commit, str) or re.fullmatch("[0-9a-f]{40}", commit) is None:
        errors.append("SOURCE_COMMIT_INVALID")
    nonce = challenge.get("nonce")
    if not isinstance(nonce, str) or not nonce or len(nonce) > 128:
        errors.append("CHALLENGE_NONCE_INVALID")
    if not isinstance(consumed, list) or any(not isinstance(x, str) for x in consumed):
        errors.append("NONCE_LEDGER_INVALID"); consumed = []
    if len(consumed) != len(set(consumed)):
        errors.append("NONCE_LEDGER_DUPLICATE")
    if nonce in consumed:
        errors.append("CHALLENGE_REPLAY")
    required = {"role", "namespace_inode", "process_id", "challenge_id",
                "run_id", "source_commit", "snapshot_sha256"}
    observations = []
    for role, record in (("supervisor", supervisor), ("worker", worker)):
        if not isinstance(record, dict) or set(record) != required:
            errors.append(role.upper() + "_SCHEMA_INVALID")
            continue
        if record["role"] != role:
            errors.append("ROLE_SUBSTITUTION")
        if type(record["namespace_inode"]) is not int or record["namespace_inode"] <= 0:
            errors.append("NAMESPACE_INODE_INVALID")
        if type(record["process_id"]) is not int or record["process_id"] <= 0:
            errors.append("PROCESS_ID_INVALID")
        if not isinstance(record["snapshot_sha256"], str) or re.fullmatch(
            "[0-9a-f]{64}", record["snapshot_sha256"]) is None:
            errors.append("SNAPSHOT_DIGEST_INVALID")
        if any(record.get(k) != challenge.get(k) for k in
               ("challenge_id", "run_id", "source_commit")):
            errors.append("OBSERVATION_CHALLENGE_MISMATCH")
        observations.append(record)
    if len(observations) == 2:
        if observations[0]["namespace_inode"] == observations[1]["namespace_inode"]:
            errors.append("NAMESPACE_NOT_SEPARATED")
        if observations[0]["process_id"] == observations[1]["process_id"]:
            errors.append("PROCESS_ID_REUSED")
    pair = {"challenge": challenge, "supervisor": supervisor, "worker": worker}
    pair_digest = digest(pair)
    seen["pair_sha256"] = pair_digest
    if not isinstance(receipts, list) or len(receipts) != 3:
        errors.append("THREE_SIGNED_WITNESS_RECEIPTS_REQUIRED"); receipts = []
    if not isinstance(keys, dict):
        errors.append("PUBLIC_KEYS_MISSING"); keys = {}
    controllers = set()
    key_ids = set()
    witness_nonces = set()
    for envelope in receipts:
        if not isinstance(envelope, dict) or set(envelope) != {
            "key_id", "statement", "signature_b64"}:
            errors.append("RECEIPT_ENVELOPE_INVALID"); continue
        statement = envelope["statement"]
        kid = envelope["key_id"]
        if not isinstance(kid, str) or not kid or kid in key_ids:
            errors.append("KEY_ID_DUPLICATE_OR_INVALID"); continue
        key_ids.add(kid)
        expected = {"schema", "controller_claim", "pair_sha256", "challenge_id",
                    "run_id", "source_commit", "witness_nonce"}
        if not isinstance(statement, dict) or set(statement) != expected or (
            statement.get("schema") != "AETHER-251/witness-v1"):
            errors.append("WITNESS_STATEMENT_SCHEMA_INVALID"); continue
        controller = statement["controller_claim"]
        if not isinstance(controller, str) or not controller or controller in controllers:
            errors.append("WITNESS_CONTROLLER_DUPLICATE_OR_INVALID")
        if isinstance(controller, str):
            controllers.add(controller)
        witness_nonce = statement["witness_nonce"]
        if (not isinstance(witness_nonce, str) or not witness_nonce or
            witness_nonce in witness_nonces or witness_nonce in consumed or
            witness_nonce == nonce):
            errors.append("WITNESS_NONCE_REPLAY")
        if isinstance(witness_nonce, str):
            witness_nonces.add(witness_nonce)
        if statement["pair_sha256"] != pair_digest:
            errors.append("SUPERVISOR_WORKER_DIGEST_MISMATCH")
        if any(statement.get(k) != challenge.get(k) for k in
               ("challenge_id", "run_id", "source_commit")):
            errors.append("WITNESS_CHALLENGE_MISMATCH")
        key = keys.get(kid)
        if not isinstance(key, dict) or (
            key.get("controller_claim") != controller or
            not isinstance(key.get("public_key_pem"), str)):
            errors.append("KEY_PIN_MISSING_OR_MISMATCHED"); continue
        try:
            raw = base64.b64decode(envelope["signature_b64"], validate=True)
            valid = len(raw) == 64 and bool(verify(
                key["public_key_pem"], canonical(statement), raw))
        except (TypeError, ValueError, UnicodeError):
            valid = False
        if not valid:
            errors.append("SIGNATURE_INVALID")
        seen["receipts"].append({"key_id": kid,
                                 "controller_claim": controller,
                                 "signature_valid": valid,
                                 "statement_sha256": digest(statement)})
    if len(controllers) != 3:
        errors.append("THREE_DISTINCT_CONTROLLER_LABELS_MISSING")
    # These independent evidence properties are NOT established by the inputs.
    errors += ["WITNESS_CONTROLLER_ANCESTRY_NOT_AUTHENTICATED",
               "NONCE_CONSUMPTION_NOT_EXTERNALLY_SEALED",
               "NAMESPACE_ORIGIN_NOT_INDEPENDENTLY_MEASURED"]
    return {"schema": SCHEMA, "verdict": "REJECT_OR_UNVERIFIED",
            "reasons": sorted(set(errors)), "observed": seen, **HOLD}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bundle", type=Path, required=True)
    p.add_argument("--out", type=Path)
    args = p.parse_args()
    try:
        raw = args.bundle.read_bytes()
        if len(raw) > 512 * 1024:
            raise ValueError("INPUT_TOO_LARGE")
        result = assess(json.loads(raw))
    except (ValueError, OSError, TypeError, UnicodeError) as error:
        result = {"schema": SCHEMA, "verdict": "REJECT_OR_UNVERIFIED",
                  "reasons": ["INPUT_UNAVAILABLE:" + type(error).__name__], **HOLD}
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
