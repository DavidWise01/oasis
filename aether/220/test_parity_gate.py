"""AETHER-220 pure parity tests. Synthetic Python fixtures are NOT native Rust runs."""
import hashlib
import json
from pathlib import Path
import unittest
from parity_gate import evaluate, sha256, SCHEMA

FIXTURE = Path(__file__).with_name("synthetic-hold.json")
REFERENCE = Path(__file__).with_name("reference.json")


class ArtifactParityTests(unittest.TestCase):
    def setUp(self):
        self.raw = FIXTURE.read_bytes()
        self.pin = json.loads(REFERENCE.read_text(encoding="utf-8"))

    def check_reject(self, code, *, pin=None, native=None, browser=None, manifest=None):
        result = evaluate(self.pin if pin is None else pin,
                          self.raw if native is None else native,
                          self.raw if browser is None else browser, manifest)
        self.assertEqual(result["verdict"], "REJECT", result)
        self.assertIn(code, result["reasons"])
        self.assertFalse(result["physical_act_allowed"])
        self.assertFalse(result["may_recover"])

    def test_frozen_synthetic_specimen_has_expected_sha(self):
        self.assertEqual(sha256(self.raw), self.pin["artifact_sha256"])

    def test_identical_synthetic_bytes_documentary_only(self):
        result = evaluate(self.pin, self.raw, self.raw)
        self.assertEqual(result["verdict"], "DOCUMENTARY_BYTES_MATCH_ONLY")
        self.assertTrue(result["documentary_byte_parity"])
        self.assertFalse(result["native_execution_proven"])
        self.assertFalse(result["independent_remote_custody_proven"])

    def test_missing_native_rejected(self):
        self.assertEqual(evaluate(self.pin, None, self.raw)["reasons"], ["NATIVE_ARTIFACT_NOT_OBSERVED"])

    def test_missing_browser_rejected(self):
        self.assertEqual(evaluate(self.pin, self.raw, None)["reasons"], ["BROWSER_ARTIFACT_NOT_OBSERVED"])

    def test_one_byte_changed_rejected(self):
        self.check_reject("BROWSER_NATIVE_BYTES_DIVERGE", browser=self.raw + b" ")

    def test_joint_substitution_cannot_bypass_reference_pin(self):
        changed = self.raw.replace(b"SYNTHETIC_ONLY_NOT_NATIVE", b"SYNTHETIC_SWITCHED")
        self.check_reject("ARTIFACT_REFERENCE_PIN_MISMATCH", native=changed, browser=changed)

    def test_missing_reference_pin_rejected(self):
        pin = dict(self.pin)
        pin.pop("artifact_sha256")
        self.check_reject("REFERENCE_SHA256_UNPINNED", pin=pin)

    def test_wrong_reference_schema_rejected(self):
        pin = dict(self.pin)
        pin["schema"] = "FORGED"
        self.check_reject("REFERENCE_SCHEMA_MISMATCH", pin=pin)

    def test_unpinned_source_revision_rejected(self):
        pin = dict(self.pin)
        pin["source_commit"] = "invalid"
        self.check_reject("SOURCE_COMMIT_UNPINNED", pin=pin)

    def test_native_manifest_commit_mismatch_rejected(self):
        self.check_reject("NATIVE_MANIFEST_SOURCE_COMMIT_MISMATCH",
            manifest={"source_commit": "f" * 40, "native_qualification_verified_by_this_manifest": True,
                      "operational_authority": "HOLD", "physical_qualification_percent": 0})

    def test_native_manifest_unverified_rejected(self):
        self.check_reject("NATIVE_QUALIFICATION_NOT_VERIFIED",
            manifest={"source_commit": self.pin["source_commit"], "native_qualification_verified_by_this_manifest": False,
                      "operational_authority": "HOLD", "physical_qualification_percent": 0})

    def test_fake_act_promoting_specimen_with_its_own_digest_rejected(self):
        record = json.loads(self.raw)
        record["physical_act_allowed"] = True
        raw = (json.dumps(record, indent=2) + "\n").encode()
        pin = dict(self.pin)
        pin["artifact_sha256"] = sha256(raw)
        self.check_reject("PINNED_ARTIFACT_PERMISSION_INVALID:physical_act_allowed",
                          native=raw, browser=raw, pin=pin)

    def test_same_repository_digest_is_not_independent_custody(self):
        result = evaluate(self.pin, self.raw, self.raw)
        self.assertFalse(result["independent_remote_custody_proven"])
        self.assertEqual(result["physical_qualification_percent"], 0)
        self.assertEqual(result["operational_authority"], "HOLD")

    def test_pin_was_not_a_rust_execution_proof(self):
        self.assertEqual(self.pin["artifact_kind"], "SYNTHETIC_REFERENCE_ONLY_NOT_RUST_EXECUTION")

    def test_invalid_json_even_when_re_pinned_fails(self):
        raw = b"not json\n"
        pin = dict(self.pin)
        pin["artifact_sha256"] = hashlib.sha256(raw).hexdigest()
        self.check_reject("PINNED_ARTIFACT_NOT_JSON", native=raw, browser=raw, pin=pin)


if __name__ == "__main__":
    unittest.main()
