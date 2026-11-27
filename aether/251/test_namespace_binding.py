import base64
import unittest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from namespace_binding import assess, canonical, digest

def fixture():
    challenge = {"challenge_id": "fresh-17", "run_id": 77,
                 "source_commit": "a" * 40, "nonce": "nonce-fresh-17"}
    sup = {"role": "supervisor", "namespace_inode": 1001, "process_id": 401,
           "snapshot_sha256": "b" * 64,
           **{k: challenge[k] for k in ("challenge_id", "run_id", "source_commit")}}
    worker = {"role": "worker", "namespace_inode": 2002, "process_id": 402,
              "snapshot_sha256": "c" * 64,
              **{k: challenge[k] for k in ("challenge_id", "run_id", "source_commit")}}
    pair = digest({"challenge": challenge, "supervisor": sup, "worker": worker})
    receipts = []
    keys = {}
    for i in range(3):
        priv = Ed25519PrivateKey.generate()
        s = {"schema": "AETHER-251/witness-v1", "controller_claim": "root" + str(i),
             "pair_sha256": pair, "witness_nonce": "witness-nonce-" + str(i),
             **{k: challenge[k] for k in ("challenge_id", "run_id", "source_commit")}}
        receipts.append({"key_id": "key" + str(i), "statement": s,
                         "signature_b64": base64.b64encode(priv.sign(canonical(s))).decode()})
        keys["key" + str(i)] = {"controller_claim": "root" + str(i),
            "public_key_pem": priv.public_key().public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo).decode()}
    return {"challenge": challenge, "supervisor": sup, "worker": worker,
            "receipts": receipts, "out_of_band_public_keys": keys,
            "previously_consumed_nonces": []}

class Tests(unittest.TestCase):
    def expect(self, mutate, reason):
        b = fixture()
        mutate(b)
        result = assess(b)
        self.assertIn(reason, result["reasons"], result)
        self.assertEqual(result["operational_authority"], "HOLD")
    def test_real_crypto_signatures_but_hold(self):
        result = assess(fixture())
        self.assertEqual(sum(x["signature_valid"] for x in result["observed"]["receipts"]), 3)
        self.assertIn("WITNESS_CONTROLLER_ANCESTRY_NOT_AUTHENTICATED", result["reasons"])
    def test_same_namespace(self):
        self.expect(lambda b: b["worker"].update(namespace_inode=1001), "NAMESPACE_NOT_SEPARATED")
    def test_same_process(self):
        self.expect(lambda b: b["worker"].update(process_id=401), "PROCESS_ID_REUSED")
    def test_role_swap(self):
        self.expect(lambda b: b["worker"].update(role="supervisor"), "ROLE_SUBSTITUTION")
    def test_worker_challenge_substituted(self):
        self.expect(lambda b: b["worker"].update(challenge_id="other"), "OBSERVATION_CHALLENGE_MISMATCH")
    def test_worker_source_substituted(self):
        self.expect(lambda b: b["worker"].update(source_commit="d" * 40), "OBSERVATION_CHALLENGE_MISMATCH")
    def test_replay_challenge(self):
        self.expect(lambda b: b["previously_consumed_nonces"].append("nonce-fresh-17"), "CHALLENGE_REPLAY")
    def test_replay_witness_nonce(self):
        self.expect(lambda b: b["previously_consumed_nonces"].append("witness-nonce-0"), "WITNESS_NONCE_REPLAY")
    def test_duplicate_witness_nonce(self):
        self.expect(lambda b: b["receipts"][1]["statement"].update(witness_nonce="witness-nonce-0"), "WITNESS_NONCE_REPLAY")
    def test_wrong_pair_hash(self):
        self.expect(lambda b: b["receipts"][0]["statement"].update(pair_sha256="f" * 64), "SUPERVISOR_WORKER_DIGEST_MISMATCH")
    def test_signature_corrupted(self):
        self.expect(lambda b: b["receipts"][0].update(signature_b64=base64.b64encode(b"x" * 64).decode()), "SIGNATURE_INVALID")
    def test_wrong_key(self):
        self.expect(lambda b: b["out_of_band_public_keys"]["key0"].update(public_key_pem=b["out_of_band_public_keys"]["key1"]["public_key_pem"]), "SIGNATURE_INVALID")
    def test_duplicate_controller(self):
        self.expect(lambda b: b["receipts"][1]["statement"].update(controller_claim="root0"), "WITNESS_CONTROLLER_DUPLICATE_OR_INVALID")
    def test_missing_receipt(self):
        self.expect(lambda b: b["receipts"].pop(), "THREE_SIGNED_WITNESS_RECEIPTS_REQUIRED")
    def test_wrong_run(self):
        self.expect(lambda b: b["receipts"][0]["statement"].update(run_id=78), "WITNESS_CHALLENGE_MISMATCH")
    def test_missing_supervisor(self):
        self.expect(lambda b: b.pop("supervisor"), "SUPERVISOR_SCHEMA_INVALID")
    def test_invalid_run_type(self):
        self.expect(lambda b: b["challenge"].update(run_id=True), "RUN_ID_INVALID")
    def test_none(self):
        self.assertIn("BUNDLE_INVALID", assess(None)["reasons"])
    def test_no_authority(self):
        r = assess(fixture())
        self.assertFalse(r["physical_act_allowed"])
        self.assertFalse(r["network_isolation_independently_verified"])

if __name__ == "__main__":
    unittest.main()
