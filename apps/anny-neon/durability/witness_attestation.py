#!/usr/bin/env python3
"""ANNY signed, dual-source witness/meter evidence gate, OFFLINE and read-only.

This gate authenticates signed *claims* against an independently pinned public
key policy and checks a distinct signed meter trace. It never controls power,
never generates signatures, and never calls a claim a physical certification.

Dependencies: cryptography>=42.0 (Ed25519 verification only).
Usage: python witness_attestation.py verify --manifest path.json --policy policy.json
       --trusted-policy-sha256 <OUT-OF-BAND-TRUSTED-HASH> \
       --witness witness.jsonl --meter meter.jsonl --report result.json
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

SCHEMA = "anny-signed-witness-v1"
POLICY_SCHEMA = "anny-witness-trust-policy-v1"
SEQUENCE = {
    "witness": ("REGISTER", "OFF_OBSERVED", "ON_OBSERVED"),
    "meter": ("BASELINE_VOLTAGE", "ZERO_VOLTAGE", "RESTORED_VOLTAGE"),
}


def canonical(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def timestamp(value: str) -> dt.datetime:
    if not isinstance(value, str):
        raise ValueError("TIMESTAMP_FORMAT")
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("TIMESTAMP_MISSING_ZONE")
    return parsed.astimezone(dt.timezone.utc)


def read_lines(path):
    raw = Path(path).read_bytes()
    if not raw or len(raw) > 1_000_000:
        raise ValueError("EVIDENCE_SIZE_BOUNDS")
    lines = raw.decode("utf-8").splitlines()
    if len(lines) != 3:
        raise ValueError("EXPECTED_THREE_EVENTS")
    return [json.loads(line) for line in lines], digest(raw)


def decode_key(key_b64: str):
    if not isinstance(key_b64, str):
        raise ValueError("PUBLIC_KEY_MISSING")
    raw = base64.b64decode(key_b64, validate=True)
    if len(raw) != 32:
        raise ValueError("ED25519_KEY_LENGTH")
    return Ed25519PublicKey.from_public_bytes(raw)


def check_stream(path, role, config, policy, manifest):
    items, filehash = read_lines(path)
    public_key = decode_key(config["ed25519_public_key_b64"])
    serial = config["device_id"]
    if not isinstance(serial, str) or not serial.strip():
        raise ValueError("EMPTY_DEVICE_ID")
    prior = None
    prev_sequence = 0
    seen_nonces = set()
    readings = []
    for i, entry in enumerate(items):
        if not isinstance(entry, dict) or set(entry) != {"payload", "signature_b64"}:
            raise ValueError("BAD_SIGNED_ENVELOPE")
        payload = entry["payload"]
        if not isinstance(payload, dict):
            raise ValueError("BAD_SIGNED_PAYLOAD")
        signature = base64.b64decode(entry["signature_b64"], validate=True)
        if len(signature) != 64:
            raise ValueError("INVALID_SIGNATURE_LENGTH")
        try:
            public_key.verify(signature, canonical(payload))
        except InvalidSignature as exc:
            raise ValueError("SIGNATURE_INVALID") from exc
        if payload.get("schema") != SCHEMA or payload.get("role") != role:
            raise ValueError("ROLE_OR_SCHEMA_MISMATCH")
        if payload.get("device_id") != serial:
            raise ValueError("DEVICE_ID_MISMATCH")
        if payload.get("run_id") != manifest.get("run_id") or \
                payload.get("manifest_sha256") != manifest.get("manifest_sha256"):
            raise ValueError("MANIFEST_RUN_MISMATCH")
        if payload.get("event") != SEQUENCE[role][i]:
            raise ValueError("EVENT_ORDER_MISMATCH")
        number = payload.get("sequence")
        if type(number) is not int or number != prev_sequence + 1:
            raise ValueError("SEQUENCE_REPLAY")
        prev_sequence = number
        nonce = payload.get("nonce")
        if not isinstance(nonce, str) or len(nonce) < 16 or nonce in seen_nonces:
            raise ValueError("NONCE_REPLAY_OR_MISSING")
        seen_nonces.add(nonce)
        time = timestamp(payload.get("observed_utc"))
        if prior is not None and time <= prior:
            raise ValueError("TIME_NOT_INCREASING")
        prior = time
        if role == "meter":
            voltage = payload.get("voltage_v")
            if type(voltage) not in (float, int) or not (0 <= voltage <= 1000):
                raise ValueError("VOLTAGE_INVALID")
            readings.append(float(voltage))
    return {"file_sha256": filehash,
            "times": [timestamp(x["payload"]["observed_utc"]) for x in items],
            "readings": readings, "events": len(items), "device": serial}


def authenticate(manifest_path, policy_path, witness_path, meter_path,
                 trusted_policy_sha256):
    """Returns a candidate or fail-closed report; never 'certified'."""
    checks = {}
    report = {"schema": SCHEMA, "status": "NOT_AUTHENTICATED",
              "certified": False, "independent_electrical_measurement_confirmed": False,
              "checks": checks, "evidence_class": "SIGNED_DUAL_SOURCE_CLAIMS"}
    try:
        if not isinstance(trusted_policy_sha256, str) or \
                len(trusted_policy_sha256) != 64 or \
                any(ch not in "0123456789abcdef" for ch in trusted_policy_sha256):
            raise ValueError("OUT_OF_BAND_POLICY_HASH_REQUIRED")
        pbytes = Path(policy_path).read_bytes()
        checks["out_of_band_policy_anchor"] = digest(pbytes) == trusted_policy_sha256
        if not checks["out_of_band_policy_anchor"]:
            raise ValueError("POLICY_ANCHOR_MISMATCH")
        policy = json.loads(pbytes)
        manifest = json.loads(Path(manifest_path).read_bytes())
        checks["policy_and_manifest_schema"] = (policy.get("schema") == POLICY_SCHEMA
            and manifest.get("schema") == "anny-powercut-protocol-v1"
            and isinstance(manifest.get("manifest_sha256"), str)
            and len(manifest["manifest_sha256"]) == 64)
        if not checks["policy_and_manifest_schema"]:
            raise ValueError("POLICY_OR_MANIFEST_SCHEMA")
        core = {k: v for k, v in manifest.items() if k != "manifest_sha256"}
        checks["manifest_digest"] = digest(canonical(core)) == manifest["manifest_sha256"]
        if not checks["manifest_digest"]:
            raise ValueError("MANIFEST_DIGEST_BAD")
        checks["policy_binds_manifest"] = policy.get("manifest_sha256") == manifest["manifest_sha256"]
        if not checks["policy_binds_manifest"]:
            raise ValueError("POLICY_MANIFEST_MISMATCH")
        w, m = policy["witness"], policy["meter"]
        checks["independent_public_keys"] = (
            w["ed25519_public_key_b64"] != m["ed25519_public_key_b64"]
            and w["device_id"] != m["device_id"])
        if not checks["independent_public_keys"]:
            raise ValueError("DUPLICATE_SIGNER_IDENTITY")
        witness = check_stream(witness_path, "witness", w, policy, manifest)
        meter = check_stream(meter_path, "meter", m, policy, manifest)
        checks["both_streams_signed_and_ordered"] = True
        threshold = policy.get("voltage_thresholds", {})
        off, on = threshold.get("off_max_v"), threshold.get("on_min_v")
        if type(off) not in (float, int) or type(on) not in (float, int) or \
                not (0 <= off < on <= 1000):
            raise ValueError("INVALID_VOLTAGE_POLICY")
        v = meter["readings"]
        checks["meter_readings_cross_thresholds"] = (
            v[0] >= on and v[1] <= off and v[2] >= on)
        if not checks["meter_readings_cross_thresholds"]:
            raise ValueError("METER_TRACE_DOES_NOT_SHOW_CUT")
        # Signed event times must agree within a policy-prescribed bound.
        drift = policy.get("max_witness_meter_skew_seconds", 30)
        if type(drift) not in (float, int) or not (0 < drift <= 300):
            raise ValueError("SKEW_POLICY_INVALID")
        diffs = [abs((a - b).total_seconds()) for a, b in
                 zip(witness["times"], meter["times"])]
        checks["witness_meter_times_correlate"] = all(d <= drift for d in diffs)
        if not checks["witness_meter_times_correlate"]:
            raise ValueError("INDEPENDENT_CLOCK_MISMATCH")
        report["status"] = "AUTHENTICATED_EVIDENCE_CANDIDATE"
        report["independent_electrical_measurement_confirmed"] = False
        report["evidence"] = {
            "witness_sha256": witness["file_sha256"],
            "meter_sha256": meter["file_sha256"],
            "policy_sha256": trusted_policy_sha256,
            "voltage_values_v": v,
            "witness_meter_skew_seconds": diffs,
        }
    except (OSError, TypeError, KeyError, ValueError, UnicodeDecodeError,
            OverflowError, json.JSONDecodeError) as exc:
        report["error"] = str(exc)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("verify")
    v.add_argument("--manifest", required=True)
    v.add_argument("--policy", required=True)
    v.add_argument("--trusted-policy-sha256", required=True)
    v.add_argument("--witness", required=True)
    v.add_argument("--meter", required=True)
    v.add_argument("--report", required=True)
    x = p.parse_args()
    report = authenticate(x.manifest, x.policy, x.witness, x.meter,
                          x.trusted_policy_sha256)
    Path(x.report).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"status": report["status"], "certified": False,
                      "report": x.report}))
    return 0 if report["status"] == "AUTHENTICATED_EVIDENCE_CANDIDATE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
