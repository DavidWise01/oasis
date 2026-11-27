import base64
import copy
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"268"))
from issuance_pin import consume
from checkpoint_anchor import snapshot,assess,signed_anchor,canonical,sha

def fixture():
    temp=tempfile.TemporaryDirectory()
    path=Path(temp.name)/"local.db"
    consume(path,"n1","a"*64,"b"*64)
    before=snapshot(path)
    consume(path,"n2","c"*64,"d"*64)
    after=snapshot(path)
    temp.cleanup()
    key=Ed25519PrivateKey.generate()
    statement=signed_anchor(before["snapshot_sha256"],before["count"],269,"claimed-external","anchor-nonce")
    signature=base64.b64encode(key.sign(canonical(statement))).decode()
    pin={"controller_id":"claimed-external","public_key_pem":key.public_key().public_bytes(
        serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()}
    return {"anchored_snapshot":before,"recovered_snapshot":after,
            "signed_anchor":{"statement":statement,"signature_b64":signature},"public_key_pin":pin}

class Tests(unittest.TestCase):
    def expect(self,change,reason):
        bundle=fixture();change(bundle);result=assess(bundle)
        self.assertIn(reason,result["reasons"],result)
        self.assertEqual(result["operational_authority"],"HOLD")
    def test_signature_valid_still_hold(self):
        result=assess(fixture())
        self.assertTrue(result["observed"]["signature_valid"])
        self.assertIn("PIN_CUSTODY_NOT_EXTERNALLY_AUTHENTICATED",result["reasons"])
    def test_rollback_to_older_snapshot(self):
        self.expect(lambda b:b.update(recovered_snapshot=copy.deepcopy(b["anchored_snapshot"])),"SIGNED_SNAPSHOT_NOT_EXTERNALLY_RETAINED")
    def test_rollback_to_empty(self):
        def change(b):
            s=b["recovered_snapshot"];s["receipts"]=[];s["count"]=0;s["snapshot_sha256"]=sha({k:v for k,v in s.items() if k!="snapshot_sha256"})
        self.expect(change,"ROLLBACK_COUNT_DECREASED")
    def test_removed_nonce_with_same_count(self):
        def change(b):
            s=b["recovered_snapshot"];s["receipts"][0]["nonce"]="n0"
            s["snapshot_sha256"]=sha({k:v for k,v in s.items() if k!="snapshot_sha256"})
        self.expect(change,"ANCHORED_NONCE_REMOVED")
    def test_substitute_anchored_challenge(self):
        self.expect(lambda b:b["recovered_snapshot"]["receipts"][0].update(challenge_sha256="f"*64),"ANCHORED_NONCE_REWRITTEN")
    def test_signed_before_altered(self):
        self.expect(lambda b:b["anchored_snapshot"].update(snapshot_sha256="f"*64),"SIGNED_ANCHOR_NOT_MATCHING_BEFORE")
    def test_anchor_signature_corrupt(self):
        self.expect(lambda b:b["signed_anchor"].update(signature_b64=base64.b64encode(b"x"*64).decode()),"ANCHOR_SIGNATURE_INVALID")
    def test_pin_substitution(self):
        other=Ed25519PrivateKey.generate().public_key().public_bytes(
            serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()
        self.expect(lambda b:b["public_key_pin"].update(public_key_pem=other),"ANCHOR_SIGNATURE_INVALID")
    def test_wrong_controller(self):
        self.expect(lambda b:b["public_key_pin"].update(controller_id="other"),"PUBLIC_KEY_PIN_UNAVAILABLE")
    def test_wrong_run(self):
        self.expect(lambda b:b["signed_anchor"]["statement"].update(run_id=0),"ANCHOR_RUN_INVALID")
    def test_receipt_hash_mutated(self):
        self.expect(lambda b:b["recovered_snapshot"]["receipts"][0].update(receipt_sha256="f"*64),"AFTER_NONCE_RECEIPT_HASH_INVALID")
    def test_unsorted_nonces(self):
        self.expect(lambda b:b["recovered_snapshot"]["receipts"].reverse(),"AFTER_NONCE_SORT_ORDER_INVALID")
    def test_duplicate_nonce(self):
        self.expect(lambda b:b["recovered_snapshot"]["receipts"][1].update(nonce="n1"),"AFTER_NONCE_DUPLICATE_OR_INVALID")
    def test_snapshot_count_wrong(self):
        self.expect(lambda b:b["recovered_snapshot"].update(count=12),"AFTER_SNAPSHOT_COUNT_INVALID")
    def test_after_snapshot_hash_wrong(self):
        self.expect(lambda b:b["recovered_snapshot"].update(snapshot_sha256="f"*64),"AFTER_SNAPSHOT_DIGEST_INVALID")
    def test_missing_pin(self):
        self.expect(lambda b:b.update(public_key_pin={}),"PUBLIC_KEY_PIN_UNAVAILABLE")
    def test_invalid_bundle(self):
        self.assertIn("BUNDLE_INVALID",assess(None)["reasons"])
    def test_restart_snapshot_persists(self):
        with tempfile.TemporaryDirectory() as t:
            db=Path(t)/"nonce.db"
            consume(db,"one","a"*64,"b"*64)
            a=snapshot(db)
            b=snapshot(db)
            self.assertEqual(a,b)
    def test_never_authorize(self):
        self.assertFalse(assess(fixture())["physical_act_allowed"])

if __name__=="__main__":
    unittest.main()
