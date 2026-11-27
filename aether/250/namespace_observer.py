#!/usr/bin/env python3
"""AETHER-250-RS: read-only Linux namespace observation and Ed25519 evidence gate.

No network connections, no state changes, and no operational authority.
"""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path

SCHEMA = "AETHER-250/namespace-observation-v1"
MAX_FILE = 65536
HOLD = {"operational_authority": "HOLD", "physical_qualification_percent": 0,
        "physical_act_allowed": False, "independent_custody_authenticated": False,
        "kernel_observation_independently_verified": False}

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("utf-8")

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def collect(read_bytes=None, namespace_inode=None, interfaces=None):
    """Capture kernel-interface bytes without invoking external commands or sockets."""
    if read_bytes is None:
        read_bytes = Path.read_bytes
    if namespace_inode is None:
        namespace_inode = os.stat("/proc/self/ns/net").st_ino
    if type(namespace_inode) is not int or namespace_inode <= 0:
        raise ValueError("NAMESPACE_ID_INVALID")
    if interfaces is None:
        interfaces = sorted(p.name for p in Path("/sys/class/net").iterdir())
    if not isinstance(interfaces, list) or not interfaces or len(interfaces) > 32:
        raise ValueError("INTERFACE_SET_INVALID")
    if any(not isinstance(x, str) or not x or len(x) > 32 for x in interfaces):
        raise ValueError("INTERFACE_NAME_INVALID")
    readings = {}
    for label, pathname in (("route_v4", "/proc/net/route"),
                            ("route_v6", "/proc/net/ipv6_route"),
                            ("net_dev", "/proc/net/dev")):
        raw = read_bytes(Path(pathname))
        if not isinstance(raw, bytes) or len(raw) > MAX_FILE:
            raise ValueError("KERNEL_SNAPSHOT_LIMIT")
        readings[label] = {"sha256": sha(raw), "length": len(raw),
                           "raw_b64": base64.b64encode(raw).decode("ascii")}
    snapshot = {"schema": SCHEMA, "namespace_inode": namespace_inode,
                "interfaces": interfaces, "readings": readings}
    snapshot["snapshot_sha256"] = sha(canonical(snapshot))
    return snapshot

def verify_ed25519(pem, message, signature):
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key = serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key, Ed25519PublicKey) or len(signature) != 64:
            return False
        key.verify(signature, message)
        return True
    except (ImportError, ValueError, TypeError, UnicodeError, InvalidSignature):
        return False

def adjudicate(bundle, verifier=verify_ed25519):
    problems = []
    detail = {"snapshot_valid": False, "signed_receipt_valid": False}
    if not isinstance(bundle, dict):
        return {"verdict": "REJECT_OR_UNVERIFIED", "reasons": ["BUNDLE_INVALID"],
                "detail": detail, **HOLD}
    snapshot = bundle.get("snapshot")
    receipt = bundle.get("receipt")
    pin = bundle.get("out_of_band_public_key")
    if not isinstance(snapshot, dict) or set(snapshot) != {
        "schema", "namespace_inode", "interfaces", "readings", "snapshot_sha256"}:
        problems.append("SNAPSHOT_SCHEMA_INVALID")
    else:
        if snapshot["schema"] != SCHEMA:
            problems.append("VERSION_INVALID")
        if type(snapshot["namespace_inode"]) is not int or snapshot["namespace_inode"] <= 0:
            problems.append("NAMESPACE_ID_INVALID")
        interfaces = snapshot["interfaces"]
        if not isinstance(interfaces, list) or not interfaces or len(interfaces) > 32 or len(set(interfaces)) != len(interfaces):
            problems.append("INTERFACE_SET_INVALID")
        readings = snapshot["readings"]
        if not isinstance(readings, dict) or set(readings) != {"route_v4", "route_v6", "net_dev"}:
            problems.append("KERNEL_READINGS_MISSING")
        else:
            for k, r in readings.items():
                if not isinstance(r, dict) or set(r) != {"sha256", "length", "raw_b64"}:
                    problems.append("READING_SCHEMA_INVALID")
                    continue
                try:
                    encoded = r["raw_b64"]
                    if not isinstance(encoded, str) or len(encoded) > 90000:
                        raise ValueError("ENCODED_SIZE")
                    raw = base64.b64decode(encoded, validate=True)
                    if len(raw) > MAX_FILE or type(r["length"]) is not int or r["length"] != len(raw):
                        problems.append("READING_LENGTH_MISMATCH")
                    if r["sha256"] != sha(raw):
                        problems.append("READING_DIGEST_MISMATCH")
                except (ValueError, TypeError):
                    problems.append("READING_UNDECODABLE")
        expected = sha(canonical({k: v for k, v in snapshot.items() if k != "snapshot_sha256"}))
        if snapshot["snapshot_sha256"] != expected:
            problems.append("SNAPSHOT_DIGEST_MISMATCH")
        detail["snapshot_valid"] = len(problems) == 0
    if not isinstance(receipt, dict) or set(receipt) != {"key_id", "statement", "signature_b64"}:
        problems.append("RECEIPT_SCHEMA_INVALID")
    else:
        statement = receipt["statement"]
        if not isinstance(statement, dict) or set(statement) != {
            "schema", "snapshot_sha256", "source_commit", "challenge_id", "observer_id"}:
            problems.append("SIGNED_STATEMENT_SCHEMA_INVALID")
        else:
            if statement["schema"] != "AETHER-250/observer-receipt-v1":
                problems.append("RECEIPT_VERSION_INVALID")
            if not isinstance(snapshot, dict) or statement["snapshot_sha256"] != snapshot.get("snapshot_sha256"):
                problems.append("RECEIPT_SNAPSHOT_MISMATCH")
            if (not isinstance(statement["source_commit"], str) or
                len(statement["source_commit"]) != 40 or
                any(x not in "0123456789abcdef" for x in statement["source_commit"])):
                problems.append("SOURCE_COMMIT_INVALID")
            if not all(isinstance(statement[k], str) and statement[k] for k in ("challenge_id", "observer_id")):
                problems.append("OBSERVER_BINDING_INVALID")
            if not isinstance(pin, dict) or pin.get("key_id") != receipt["key_id"] or pin.get("observer_id") != statement["observer_id"] or not isinstance(pin.get("public_key_pem"), str):
                problems.append("OUT_OF_BAND_KEY_UNAVAILABLE")
            else:
                try:
                    sig = base64.b64decode(receipt["signature_b64"], validate=True)
                    valid = verifier(pin["public_key_pem"], canonical(statement), sig)
                except (ValueError, TypeError, UnicodeError):
                    valid = False
                detail["signed_receipt_valid"] = bool(valid)
                if not valid:
                    problems.append("SIGNATURE_INVALID")
    problems.extend(["INDEPENDENT_OBSERVER_KEY_CUSTODY_UNVERIFIED",
                     "NAMESPACE_AND_KERNEL_ORIGIN_NOT_INDEPENDENTLY_ATTESTED",
                     "NETWORK_EGRESS_ENFORCEMENT_NOT_PROVEN"])
    return {"verdict": "REJECT_OR_UNVERIFIED", "reasons": sorted(set(problems)),
            "detail": detail, **HOLD}

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sample = sub.add_parser("collect")
    sample.add_argument("--out", type=Path, required=True)
    review = sub.add_parser("review")
    review.add_argument("--bundle", type=Path, required=True)
    review.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "collect":
            result = collect()
        else:
            raw = args.bundle.read_bytes()
            if len(raw) > 512 * 1024:
                raise ValueError("BUNDLE_TOO_LARGE")
            result = adjudicate(json.loads(raw))
    except (OSError, ValueError, TypeError) as error:
        result = {"verdict": "REJECT_OR_UNVERIFIED",
                  "reasons": ["INPUT_OR_COLLECTION_FAILURE:" + type(error).__name__], **HOLD}
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
