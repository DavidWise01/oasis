"""Synthetic Ed25519 witness+meter negative controls; no physical power interruption."""
from __future__ import annotations
import base64
import copy
import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
import uuid
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import witness_attestation as a


class SignedWitnessEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="anny-signed-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.wkey = Ed25519PrivateKey.generate()
        self.mkey = Ed25519PrivateKey.generate()
        self.manifest = {"schema": "anny-powercut-protocol-v1", "run_id": "run-test-signed",
                         "case": "CONFIRM_COMMITTED", "source_sha256": "f" * 64,
                         "expected": ["CONFIRMED", True, 1, "VERIFIED"]}
        self.manifest["manifest_sha256"] = a.digest(a.canonical(self.manifest))
        self.policy = {"schema": a.POLICY_SCHEMA,
            "manifest_sha256": self.manifest["manifest_sha256"],
            "witness": {"device_id": "WITNESS-002", "ed25519_public_key_b64": self.pub(self.wkey)},
            "meter": {"device_id": "METER-001", "ed25519_public_key_b64": self.pub(self.mkey)},
            "voltage_thresholds": {"off_max_v": 5, "on_min_v": 100},
            "max_witness_meter_skew_seconds": 10}
        self.events = {"witness": [], "meter": []}
        base = dt.datetime(2026, 10, 21, 22, 27, tzinfo=dt.timezone.utc)
        for role, key, readings in (("witness", self.wkey, (None, None, None)),
                                    ("meter", self.mkey, (120., 0., 120.))):
            for i, event in enumerate(a.SEQUENCE[role]):
                payload = {"schema": a.SCHEMA, "role": role,
                    "device_id": self.policy[role]["device_id"],
                    "run_id": self.manifest["run_id"],
                    "manifest_sha256": self.manifest["manifest_sha256"],
                    "event": event, "sequence": i+1,
                    "nonce": uuid.uuid4().hex,
                    "observed_utc": (base + dt.timedelta(seconds=i*20)).isoformat()}
                if role == "meter":
                    payload["voltage_v"] = readings[i]
                self.events[role].append(self.sign(key, payload))
        self.write()

    def pub(self, key):
        return base64.b64encode(key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw)).decode()

    def sign(self, key, payload):
        return {"payload": payload, "signature_b64": base64.b64encode(
            key.sign(a.canonical(payload))).decode()}

    def resign(self, role):
        key = {"witness": self.wkey, "meter": self.mkey}[role]
        self.events[role] = [self.sign(key, item["payload"]) for item in self.events[role]]
        self.write()

    def write(self):
        (self.root / "manifest.json").write_text(json.dumps(self.manifest))
        (self.root / "policy.json").write_text(json.dumps(self.policy))
        for role in a.SEQUENCE:
            (self.root / (role + ".jsonl")).write_text("".join(
                json.dumps(x) + "\n" for x in self.events[role]))

    def audit(self, trusted_hash=None):
        return a.authenticate(self.root / "manifest.json", self.root / "policy.json",
            self.root / "witness.jsonl", self.root / "meter.jsonl",
            trusted_hash or a.digest((self.root / "policy.json").read_bytes()))

    def assert_rejected(self, code=None):
        r = self.audit()
        self.assertEqual(r["status"], "NOT_AUTHENTICATED", r)
        self.assertFalse(r["certified"])
        if code:
            self.assertIn(code, r.get("error", ""), r)

    def test_valid_dual_signature_is_candidate_not_certificate(self):
        r = self.audit()
        self.assertEqual(r["status"], "AUTHENTICATED_EVIDENCE_CANDIDATE", r)
        self.assertFalse(r["certified"])
        self.assertFalse(r["independent_electrical_measurement_confirmed"])
        self.assertEqual(r["evidence"]["voltage_values_v"], [120,0,120])

    def test_unsigned_payload_mutation_fails(self):
        self.events["meter"][1]["payload"]["voltage_v"] = 1
        self.write()
        self.assert_rejected("SIGNATURE_INVALID")

    def test_duplicate_meter_event_rejected_even_if_resigned(self):
        self.events["meter"][2]["payload"] = copy.deepcopy(self.events["meter"][1]["payload"])
        self.resign("meter")
        self.assert_rejected("EVENT_ORDER_MISMATCH")

    def test_nonce_replay_with_valid_resign_fails(self):
        self.events["meter"][2]["payload"]["nonce"] = self.events["meter"][0]["payload"]["nonce"]
        self.resign("meter")
        self.assert_rejected("NONCE_REPLAY_OR_MISSING")

    def test_wrong_witness_signer_rejected(self):
        self.events["witness"][1] = self.sign(self.mkey, self.events["witness"][1]["payload"])
        self.write()
        self.assert_rejected("SIGNATURE_INVALID")

    def test_same_public_key_both_sources_rejected(self):
        self.policy["meter"]["ed25519_public_key_b64"] = self.policy["witness"]["ed25519_public_key_b64"]
        self.write()
        self.assert_rejected("DUPLICATE_SIGNER_IDENTITY")

    def test_policy_swap_rejected_against_external_anchor(self):
        trusted = a.digest((self.root / "policy.json").read_bytes())
        self.policy["voltage_thresholds"]["off_max_v"] = 119
        self.write()
        r = self.audit(trusted_hash=trusted)
        self.assertIn("POLICY_ANCHOR_MISMATCH", r.get("error", ""))
        self.assertFalse(r["certified"])

    def test_wrong_run_id_rejected_even_with_valid_signature(self):
        self.events["witness"][0]["payload"]["run_id"] = "run-other"
        self.resign("witness")
        self.assert_rejected("MANIFEST_RUN_MISMATCH")

    def test_absent_zero_voltage_rejected(self):
        self.events["meter"][1]["payload"]["voltage_v"] = 120.
        self.resign("meter")
        self.assert_rejected("METER_TRACE_DOES_NOT_SHOW_CUT")

    def test_missing_event_fails(self):
        self.events["meter"].pop()
        self.write()
        self.assert_rejected("EXPECTED_THREE_EVENTS")

    def test_time_reversal_with_signature_fails(self):
        self.events["meter"][2]["payload"]["observed_utc"] = self.events["meter"][0]["payload"]["observed_utc"]
        self.resign("meter")
        self.assert_rejected("TIME_NOT_INCREASING")

    def test_uncorrelated_witness_and_meter_clocks_rejected(self):
        for event in self.events["meter"]:
            d = dt.datetime.fromisoformat(event["payload"]["observed_utc"])
            event["payload"]["observed_utc"] = (d+dt.timedelta(hours=1)).isoformat()
        self.resign("meter")
        self.assert_rejected("INDEPENDENT_CLOCK_MISMATCH")

    def test_fake_voltage_bool_type_fails(self):
        self.events["meter"][1]["payload"]["voltage_v"] = False
        self.resign("meter")
        self.assert_rejected("VOLTAGE_INVALID")

    def test_wrong_manifest_hash_fails(self):
        self.manifest["case"] = "COMMIT_UNCOMMITTED"
        self.write()
        self.assert_rejected("MANIFEST_DIGEST_BAD")

    def test_no_external_anchor_fails(self):
        r = self.audit(trusted_hash="INVALID")
        self.assertEqual(r["status"], "NOT_AUTHENTICATED")
        self.assertIn("OUT_OF_BAND_POLICY_HASH_REQUIRED", r["error"])

    def test_event_reordering_rejected(self):
        self.events["witness"][1], self.events["witness"][2] = (
            self.events["witness"][2], self.events["witness"][1])
        self.write()
        self.assert_rejected("EVENT_ORDER_MISMATCH")


if __name__ == "__main__":
    unittest.main(verbosity=2)
