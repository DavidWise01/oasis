import base64
import copy
import hashlib
import unittest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from attested_exit import assess, canonical, sha, CHILD_CODE

def fixture():
    boot = "11111111-2222-3333-4444-555555555555"
    observation = {"pid": 123, "start_ticks": 445, "boot_id": boot,
                   "namespace_inode": 987, "stat_sha256": "a"*64,
                   "pidfd_readable": True, "waitid_pid": 123,
                   "waitid_code": 1, "waitid_status": 7, "wait_returncode": 7,
                   "elapsed_ms": 14,
                   "child_script_sha256": hashlib.sha256(CHILD_CODE.encode()).hexdigest()}
    transcript = {"schema": "AETHER-254/pidfd-exit-v1", "observation": observation,
                  "operational_authority": "HOLD", "physical_qualification_percent": 0,
                  "physical_act_allowed": False, "external_custody_authenticated": False,
                  "live_os_exit_authenticated_externally": False}
    transcript["transcript_sha256"] = sha(transcript)
    challenge = {"challenge_id": "fresh-1", "nonce": "nonce-1", "run_id": 77,
                 "source_commit": "b"*40, "host_id": "machine-1", "boot_id": boot}
    statement = {"schema": "AETHER-255/witness-statement-v1",
                 "challenge": challenge, "transcript_sha256": transcript["transcript_sha256"]}
    receipts = []
    pins = {}
    for i in range(3):
        key = Ed25519PrivateKey.generate()
        kid = "key" + str(i)
        controller = "root" + str(i)
        witness_nonce = "w-nonce-" + str(i)
        signed = {**statement, "controller_claim": controller, "witness_nonce": witness_nonce}
        receipts.append({"key_id": kid, "controller_claim": controller,
                         "witness_nonce": witness_nonce,
                         "signature_b64": base64.b64encode(key.sign(canonical(signed))).decode()})
        pins[kid] = {"controller_claim": controller, "public_key_pem": key.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()}
    return {"challenge": challenge, "pidfd_transcript": transcript, "witness_receipts": receipts,
            "out_of_band_key_pins": pins, "previously_consumed_nonces": [],
            "previously_seen_transcripts": []}

class Tests(unittest.TestCase):
    def expect(self, change, reason):
        value = fixture()
        change(value)
        result = assess(value)
        self.assertIn(reason, result["reasons"], result)
        self.assertEqual(result["operational_authority"], "HOLD")
    def test_three_genuine_signatures_still_hold(self):
        result = assess(fixture())
        self.assertEqual(sum(x["signature_valid"] for x in result["observed"]["signatures"]), 3)
        self.assertIn("EXTERNAL_SIGNER_ANCESTRY_AND_CUSTODY_UNAUTHENTICATED", result["reasons"])
    def test_replayed_challenge(self):
        self.expect(lambda b:b["previously_consumed_nonces"].append("nonce-1"), "CHALLENGE_NONCE_REPLAY")
    def test_replayed_transcript(self):
        self.expect(lambda b:b["previously_seen_transcripts"].append(b["pidfd_transcript"]["transcript_sha256"]), "TRANSCRIPT_REPLAY")
    def test_duplicate_witness_nonce(self):
        self.expect(lambda b:b["witness_receipts"][1].update(witness_nonce="w-nonce-0"), "WITNESS_NONCE_REPLAY")
    def test_replayed_witness_nonce(self):
        self.expect(lambda b:b["previously_consumed_nonces"].append("w-nonce-0"), "WITNESS_NONCE_REPLAY")
    def test_changed_host_boot(self):
        self.expect(lambda b:b["challenge"].update(boot_id="other-boot"), "HOST_BOOT_ID_MISMATCH")
    def test_substituted_transcript_bytes(self):
        self.expect(lambda b:b["pidfd_transcript"]["observation"].update(pid=125), "PIDFD_TRANSCRIPT_HASH_MISMATCH")
    def test_changed_wait_pid(self):
        self.expect(lambda b:b["pidfd_transcript"]["observation"].update(waitid_pid=999), "WAITID_PROCESS_MISMATCH")
    def test_changed_exit_status(self):
        self.expect(lambda b:b["pidfd_transcript"]["observation"].update(waitid_status=0), "EXIT_STATUS_MISMATCH")
    def test_changed_script(self):
        self.expect(lambda b:b["pidfd_transcript"]["observation"].update(child_script_sha256="0"*64), "CHILD_ANCESTRY_SCRIPT_MISMATCH")
    def test_corrupted_signature(self):
        self.expect(lambda b:b["witness_receipts"][0].update(signature_b64=base64.b64encode(b"x"*64).decode()), "SIGNATURE_INVALID")
    def test_wrong_pin(self):
        self.expect(lambda b:b["out_of_band_key_pins"]["key0"].update(
            public_key_pem=b["out_of_band_key_pins"]["key1"]["public_key_pem"]), "SIGNATURE_INVALID")
    def test_duplicate_root(self):
        self.expect(lambda b:b["witness_receipts"][1].update(controller_claim="root0"), "CONTROLLER_DUPLICATE_OR_INVALID")
    def test_missing_witness(self):
        self.expect(lambda b:b["witness_receipts"].pop(), "THREE_WITNESSES_REQUIRED")
    def test_invalid_run(self):
        self.expect(lambda b:b["challenge"].update(run_id=True), "RUN_ID_INVALID")
    def test_invalid_source_commit(self):
        self.expect(lambda b:b["challenge"].update(source_commit="not-a-commit"), "SOURCE_COMMIT_INVALID")
    def test_authority_tamper(self):
        self.expect(lambda b:b["pidfd_transcript"].update(operational_authority="ACT"), "PIDFD_AUTHORITY_FIELDS_TAMPERED")
    def test_missing_transcript(self):
        self.expect(lambda b:b.pop("pidfd_transcript"), "PIDFD_TRANSCRIPT_SCHEMA_INVALID")
    def test_invalid_bundle(self):
        self.assertIn("BUNDLE_INVALID", assess(None)["reasons"])
    def test_hold_guarantee(self):
        result = assess(fixture())
        self.assertFalse(result["physical_act_allowed"])
        self.assertFalse(result["live_pidfd_exit_independently_attested"])

if __name__ == "__main__":
    unittest.main()
