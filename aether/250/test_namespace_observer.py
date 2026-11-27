import base64
import copy
import unittest
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from namespace_observer import collect, adjudicate, canonical

def fixture():
    contents = {
        "/proc/net/route": b"Iface Destination Gateway\n",
        "/proc/net/ipv6_route": b"0000000000\n",
        "/proc/net/dev": b"Inter-| Receive Transmit\n",
    }
    snapshot = collect(read_bytes=lambda p: contents[str(p)],
                       namespace_inode=321, interfaces=["lo"])
    key = Ed25519PrivateKey.generate()
    statement = {"schema": "AETHER-250/observer-receipt-v1",
                 "snapshot_sha256": snapshot["snapshot_sha256"],
                 "source_commit": "a" * 40, "challenge_id": "challenge-01",
                 "observer_id": "observer-1"}
    return {"snapshot": snapshot,
            "receipt": {"key_id": "key-1", "statement": statement,
                        "signature_b64": base64.b64encode(key.sign(canonical(statement))).decode()},
            "out_of_band_public_key": {
                "key_id": "key-1", "observer_id": "observer-1",
                "public_key_pem": key.public_key().public_bytes(
                    serialization.Encoding.PEM,
                    serialization.PublicFormat.SubjectPublicKeyInfo).decode()}}

class Tests(unittest.TestCase):
    def expect(self, transform, reason):
        data = fixture()
        transform(data)
        result = adjudicate(data)
        self.assertIn(reason, result["reasons"], result)
        self.assertEqual(result["operational_authority"], "HOLD")
    def test_valid_local_signature_unqualified(self):
        r = adjudicate(fixture())
        self.assertTrue(r["detail"]["snapshot_valid"])
        self.assertTrue(r["detail"]["signed_receipt_valid"])
        self.assertIn("INDEPENDENT_OBSERVER_KEY_CUSTODY_UNVERIFIED", r["reasons"])
    def test_tampered_raw(self):
        self.expect(lambda b: b["snapshot"]["readings"]["route_v4"].update(
            raw_b64=base64.b64encode(b"altered").decode()), "READING_DIGEST_MISMATCH")
    def test_missing_route(self):
        self.expect(lambda b: b["snapshot"]["readings"].pop("route_v6"), "KERNEL_READINGS_MISSING")
    def test_missing_interface(self):
        self.expect(lambda b: b["snapshot"].update(interfaces=[]), "INTERFACE_SET_INVALID")
    def test_bad_inode(self):
        self.expect(lambda b: b["snapshot"].update(namespace_inode=0), "NAMESPACE_ID_INVALID")
    def test_snapshot_digest(self):
        self.expect(lambda b: b["snapshot"].update(snapshot_sha256="f" * 64), "SNAPSHOT_DIGEST_MISMATCH")
    def test_wrong_receipt_binding(self):
        self.expect(lambda b: b["receipt"]["statement"].update(snapshot_sha256="b" * 64), "RECEIPT_SNAPSHOT_MISMATCH")
    def test_invalid_signature(self):
        self.expect(lambda b: b["receipt"].update(signature_b64=base64.b64encode(b"x" * 64).decode()), "SIGNATURE_INVALID")
    def test_wrong_key(self):
        self.expect(lambda b: b["out_of_band_public_key"].update(key_id="wrong"), "OUT_OF_BAND_KEY_UNAVAILABLE")
    def test_wrong_observer(self):
        self.expect(lambda b: b["receipt"]["statement"].update(observer_id="other"), "OUT_OF_BAND_KEY_UNAVAILABLE")
    def test_bad_commit(self):
        self.expect(lambda b: b["receipt"]["statement"].update(source_commit="bad"), "SOURCE_COMMIT_INVALID")
    def test_no_bundle(self):
        self.assertIn("BUNDLE_INVALID", adjudicate(None)["reasons"])
    def test_capture_overlarge(self):
        with self.assertRaises(ValueError):
            collect(read_bytes=lambda p: b"x" * 65537, namespace_inode=321, interfaces=["lo"])
    def test_capture_bad_inode(self):
        with self.assertRaises(ValueError):
            collect(read_bytes=lambda p: b"", namespace_inode=True, interfaces=["lo"])
    def test_capture_extra_interface(self):
        r = collect(read_bytes=lambda p: b"", namespace_inode=321, interfaces=["lo", "veth0"])
        self.assertIn("veth0", r["interfaces"])
    def test_no_physical_authority(self):
        r = adjudicate(fixture())
        self.assertFalse(r["physical_act_allowed"])
        self.assertFalse(r["kernel_observation_independently_verified"])

if __name__ == "__main__":
    unittest.main()
