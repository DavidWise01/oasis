"""AETHER-219 reproducibility invariants; Python only, not Rust qualification."""
from pathlib import Path
import tempfile
import unittest
from evidence_manifest import build_manifest, compare, digest, stable_json, observed_bytes, INPUTS, EVIDENCE


class EvidenceManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.artifacts = self.root / "aether" / "rust" / "qualification-artifacts"
        self.artifacts.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def create_sources(self):
        for name in INPUTS:
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(("source:" + name).encode("utf-8"))

    def create_evidence(self, good=False):
        import json
        for name in EVIDENCE:
            p = self.artifacts / name
            p.write_bytes(("evidence:" + name).encode("utf-8"))
        self.artifacts.joinpath("aether218-gate.json").write_text(json.dumps({
            "native_qualification_passed": good,
            "source_commit": "a" * 40,
            "physical_qualification_percent": 0,
            "operational_authority": "HOLD",
        }), encoding="utf-8")

    def test_empty_inputs_hold(self):
        r = build_manifest(self.root, self.artifacts, None)
        self.assertFalse(r["native_qualification_verified_by_this_manifest"])
        self.assertIn("SOURCE_INPUT_MISSING", r["reasons"])
        self.assertEqual(r["physical_qualification_percent"], 0)

    def test_same_bytes_same_hash(self):
        self.assertEqual(digest(b"abc"), digest(b"abc"))

    def test_byte_change_changes_hash(self):
        self.assertNotEqual(digest(b"abc"), digest(b"abd"))

    def test_json_deterministic_key_order(self):
        self.assertEqual(stable_json({"b": 1, "a": 2}), stable_json({"a": 2, "b": 1}))

    def test_source_missing_fails_even_with_fake_native_success(self):
        self.create_evidence(good=True)
        r = build_manifest(self.root, self.artifacts, "a" * 40)
        self.assertFalse(r["native_qualification_verified_by_this_manifest"])

    def test_evidence_missing_fails(self):
        self.create_sources()
        r = build_manifest(self.root, self.artifacts, "a" * 40)
        self.assertIn("QUALIFICATION_EVIDENCE_MISSING", r["reasons"])

    def test_existing_full_fixture_is_classification_only(self):
        self.create_sources()
        self.create_evidence(good=True)
        r = build_manifest(self.root, self.artifacts, "a" * 40)
        self.assertTrue(r["native_qualification_verified_by_this_manifest"])
        self.assertFalse(r["independent_remote_custody_authenticated"])
        self.assertEqual(r["operational_authority"], "HOLD")

    def test_native_gate_failure_stays_rejected(self):
        self.create_sources()
        self.create_evidence(good=False)
        r = build_manifest(self.root, self.artifacts, "a" * 40)
        self.assertIn("NATIVE_QUALIFICATION_NOT_PASSED", r["reasons"])

    def test_mismatched_commit_rejected(self):
        self.create_sources()
        self.create_evidence(good=True)
        r = build_manifest(self.root, self.artifacts, "b" * 40)
        self.assertIn("GATE_COMMIT_MISMATCH", r["reasons"])

    def test_identical_bundle_compares_equal(self):
        self.create_sources()
        self.create_evidence(good=True)
        r = build_manifest(self.root, self.artifacts, "a" * 40)
        self.assertTrue(compare(r, r)["content_matches"])

    def test_changed_fixture_compares_unequal(self):
        self.create_sources()
        self.create_evidence(good=True)
        first = build_manifest(self.root, self.artifacts, "a" * 40)
        p = self.root / INPUTS[0]
        p.write_bytes(b"tampered")
        second = build_manifest(self.root, self.artifacts, "a" * 40)
        self.assertFalse(compare(first, second)["content_matches"])

    def test_changed_log_compares_unequal(self):
        self.create_sources()
        self.create_evidence(good=True)
        first = build_manifest(self.root, self.artifacts, "a" * 40)
        self.artifacts.joinpath("cargo_test.log").write_bytes(b"modified")
        second = build_manifest(self.root, self.artifacts, "a" * 40)
        self.assertFalse(compare(first, second)["content_matches"])

    def test_missing_file_is_not_observed(self):
        r = observed_bytes(self.root / "missing", self.root)
        self.assertEqual(r["state"], "MISSING_OR_UNSAFE")

    def test_symlink_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as external:
            outside = Path(external) / "secret"
            outside.write_text("not ours", encoding="utf-8")
            link = self.root / "escape"
            link.symlink_to(outside)
            self.assertEqual(observed_bytes(link, self.root)["state"], "MISSING_OR_UNSAFE")

    def test_path_independent_source_digest(self):
        self.create_sources()
        self.create_evidence(good=True)
        r = build_manifest(self.root, self.artifacts, "a" * 40)
        self.assertEqual(len(r["content_digest_sha256"]), 64)
        self.assertNotIn(str(self.root), stable_json(r))

if __name__ == "__main__":
    unittest.main()
