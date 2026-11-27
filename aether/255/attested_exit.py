#!/usr/bin/env python3
"""AETHER-255-RS: offline attestation of pidfd-exit transcript provenance.

Cryptographic statements are checked; externally independent custody is NOT inferred.
No process control, network access, lock reclaim or ACT authorization.
"""
import argparse
import base64
import hashlib
import json
import re
from pathlib import Path

SCHEMA = "AETHER-255/pidfd-attestation-v1"
HOLD = {"operational_authority": "HOLD", "physical_qualification_percent": 0,
        "physical_act_allowed": False, "external_custody_authenticated": False,
        "live_pidfd_exit_independently_attested": False}
H40 = re.compile(r"^[0-9a-f]{40}$")
H64 = re.compile(r"^[0-9a-f]{64}$")
CHILD_CODE = "import os,sys; sys.stdin.buffer.read(1); os._exit(7)"

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")

def sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()

def verified(pem, message, sig):
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key = serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key, Ed25519PublicKey) or len(sig) != 64:
            return False
        key.verify(sig, message)
        return True
    except (ImportError, InvalidSignature, ValueError, TypeError, UnicodeError):
        return False

def assess(bundle, verify=verified):
    issues = []
    observations = {"signatures": []}
    if not isinstance(bundle, dict):
        return {"schema": SCHEMA, "verdict": "REJECT_OR_UNVERIFIED",
                "reasons": ["BUNDLE_INVALID"], "observed": observations, **HOLD}
    challenge = bundle.get("challenge")
    transcript = bundle.get("pidfd_transcript")
    receipts = bundle.get("witness_receipts")
    trust = bundle.get("out_of_band_key_pins")
    used_nonces = bundle.get("previously_consumed_nonces")
    used_transcripts = bundle.get("previously_seen_transcripts")
    if not isinstance(challenge, dict) or set(challenge) != {
        "challenge_id", "nonce", "run_id", "source_commit", "host_id", "boot_id"}:
        issues.append("CHALLENGE_SCHEMA_INVALID")
        challenge = {}
    for k in ("challenge_id", "nonce", "host_id", "boot_id"):
        if not isinstance(challenge.get(k), str) or not challenge[k] or len(challenge[k]) > 128:
            issues.append("CHALLENGE_FIELD_INVALID")
    if type(challenge.get("run_id")) is not int or challenge["run_id"] <= 0:
        issues.append("RUN_ID_INVALID")
    commit = challenge.get("source_commit")
    if not isinstance(commit, str) or not H40.fullmatch(commit):
        issues.append("SOURCE_COMMIT_INVALID")
    if not isinstance(used_nonces, list) or any(not isinstance(x, str) for x in used_nonces):
        issues.append("NONCE_HISTORY_INVALID")
        used_nonces = []
    if not isinstance(used_transcripts, list) or any(not isinstance(x, str) for x in used_transcripts):
        issues.append("TRANSCRIPT_HISTORY_INVALID")
        used_transcripts = []
    if len(used_nonces) != len(set(used_nonces)) or len(used_transcripts) != len(set(used_transcripts)):
        issues.append("REPLAY_HISTORY_DUPLICATE")
    if challenge.get("nonce") in used_nonces:
        issues.append("CHALLENGE_NONCE_REPLAY")
    if not isinstance(transcript, dict) or set(transcript) != {
        "schema", "observation", "transcript_sha256", "operational_authority",
        "physical_qualification_percent", "physical_act_allowed",
        "external_custody_authenticated", "live_os_exit_authenticated_externally"}:
        issues.append("PIDFD_TRANSCRIPT_SCHEMA_INVALID")
        transcript = {}
    obs = transcript.get("observation")
    if transcript.get("schema") != "AETHER-254/pidfd-exit-v1":
        issues.append("PIDFD_VERSION_INVALID")
    if not isinstance(obs, dict):
        issues.append("PIDFD_OBSERVATION_INVALID")
        obs = {}
    expected_transcript_hash = sha({k:v for k,v in transcript.items() if k != "transcript_sha256"})
    claimed_transcript_hash = transcript.get("transcript_sha256")
    if not isinstance(claimed_transcript_hash, str) or not H64.fullmatch(claimed_transcript_hash):
        issues.append("PIDFD_TRANSCRIPT_HASH_INVALID")
    elif claimed_transcript_hash != expected_transcript_hash:
        issues.append("PIDFD_TRANSCRIPT_HASH_MISMATCH")
    if claimed_transcript_hash in used_transcripts:
        issues.append("TRANSCRIPT_REPLAY")
    if (transcript.get("operational_authority") != "HOLD" or
        transcript.get("physical_qualification_percent") != 0 or
        transcript.get("physical_act_allowed") is not False):
        issues.append("PIDFD_AUTHORITY_FIELDS_TAMPERED")
    if obs:
        if type(obs.get("pid")) is not int or obs["pid"] <= 0:
            issues.append("PID_INVALID")
        if type(obs.get("start_ticks")) is not int or obs["start_ticks"] < 0:
            issues.append("START_TICKS_INVALID")
        if type(obs.get("namespace_inode")) is not int or obs["namespace_inode"] <= 0:
            issues.append("NAMESPACE_INVALID")
        if obs.get("pidfd_readable") is not True:
            issues.append("PIDFD_READINESS_MISSING")
        if obs.get("waitid_pid") != obs.get("pid"):
            issues.append("WAITID_PROCESS_MISMATCH")
        if (obs.get("waitid_code") != 1 or obs.get("waitid_status") != 7 or
            obs.get("wait_returncode") != 7):
            issues.append("EXIT_STATUS_MISMATCH")
        if obs.get("child_script_sha256") != hashlib.sha256(CHILD_CODE.encode()).hexdigest():
            issues.append("CHILD_ANCESTRY_SCRIPT_MISMATCH")
        if obs.get("boot_id") != challenge.get("boot_id"):
            issues.append("HOST_BOOT_ID_MISMATCH")
    statement = {"schema": "AETHER-255/witness-statement-v1",
                 "challenge": challenge,
                 "transcript_sha256": claimed_transcript_hash}
    observations["binding_sha256"] = sha(statement)
    if not isinstance(receipts, list) or len(receipts) != 3:
        issues.append("THREE_WITNESSES_REQUIRED")
        receipts = []
    if not isinstance(trust, dict):
        issues.append("TRUST_ROOTS_MISSING")
        trust = {}
    controllers = set()
    keys = set()
    witness_nonces = set()
    for item in receipts:
        if not isinstance(item, dict) or set(item) != {
            "key_id", "controller_claim", "witness_nonce", "signature_b64"}:
            issues.append("RECEIPT_SCHEMA_INVALID")
            continue
        kid = item["key_id"]
        controller = item["controller_claim"]
        nonce = item["witness_nonce"]
        if not isinstance(kid, str) or not kid or kid in keys:
            issues.append("KEY_REUSE_OR_INVALID")
            continue
        keys.add(kid)
        if not isinstance(controller, str) or not controller or controller in controllers:
            issues.append("CONTROLLER_DUPLICATE_OR_INVALID")
        if isinstance(controller, str):
            controllers.add(controller)
        if (not isinstance(nonce, str) or not nonce or nonce in witness_nonces or
            nonce in used_nonces or nonce == challenge.get("nonce")):
            issues.append("WITNESS_NONCE_REPLAY")
        if isinstance(nonce, str):
            witness_nonces.add(nonce)
        key = trust.get(kid)
        if not isinstance(key, dict) or key.get("controller_claim") != controller or not isinstance(key.get("public_key_pem"), str):
            issues.append("KEY_PIN_UNAVAILABLE")
            continue
        signed = {**statement, "controller_claim": controller, "witness_nonce": nonce}
        try:
            sig = base64.b64decode(item["signature_b64"], validate=True)
            good = len(sig) == 64 and bool(verify(key["public_key_pem"], canonical(signed), sig))
        except (ValueError, TypeError, UnicodeError):
            good = False
        if not good:
            issues.append("SIGNATURE_INVALID")
        observations["signatures"].append({"key_id": kid, "controller_claim": controller,
                                           "signature_valid": good, "signed_sha256": sha(signed)})
    if len(controllers) != 3:
        issues.append("THREE_CONTROLLER_LABELS_MISSING")
    issues += ["EXTERNAL_SIGNER_ANCESTRY_AND_CUSTODY_UNAUTHENTICATED",
               "FRESH_CHALLENGE_AND_NONCE_CONSUMPTION_NOT_EXTERNALLY_SEALED",
               "HOST_AND_PIDFD_ORIGIN_NOT_INDEPENDENTLY_OBSERVED"]
    return {"schema": SCHEMA, "verdict": "REJECT_OR_UNVERIFIED",
            "reasons": sorted(set(issues)), "observed": observations, **HOLD}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        raw = args.bundle.read_bytes()
        if len(raw) > 512 * 1024:
            raise ValueError("INPUT_TOO_LARGE")
        result = assess(json.loads(raw))
    except (OSError, ValueError, TypeError, UnicodeError) as error:
        result = {"schema": SCHEMA, "verdict": "REJECT_OR_UNVERIFIED",
                  "reasons": ["INPUT_INVALID:" + type(error).__name__], **HOLD}
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
