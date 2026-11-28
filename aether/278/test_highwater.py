import base64,sqlite3,tempfile,unittest
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from highwater import append,inspect,audit,sha,canon,SCHEMA

def anchor(seq,head,challenges,receipts,rotations,run):
    statement={"schema":SCHEMA,"min_seq":seq,"min_challenges":challenges,
               "min_receipts":receipts,"min_rotations":rotations,"min_run_id":run,
               "anchored_head_sha256":head,"controller_claim":"claimed-external-custodian"}
    private=Ed25519PrivateKey.generate()
    return ({"statement":statement,
             "public_key_pem":private.public_key().public_bytes(
                serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode(),
             "signature_b64":base64.b64encode(private.sign(canon(statement))).decode()},
            sha(statement))

class Tests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.db=Path(t.name)/"highwater.db"
        self.h0="0"*64
    def push(self,challenges=1,receipts=3,rotations=0,run=278,head=None,registry=None):
        return append(self.db,registry or "a"*64,challenges,receipts,rotations,run,
                      self.h0 if head is None else head)
    def test_initial_checkpoint(self):
        result=self.push()
        self.assertEqual(result["sequence"],1)
        self.assertEqual(inspect(self.db)["validation_errors"],[])
    def test_restart_monotonic(self):
        first=self.push();second=self.push(2,6,0,279,first["head_sha256"])
        self.assertEqual(second["sequence"],2)
    def test_replay_stale_head(self):
        first=self.push()
        with self.assertRaisesRegex(ValueError,"STALE_OR_SUBSTITUTED_HEAD"):
            self.push(2,6,0,279,self.h0)
    def test_count_decrease(self):
        first=self.push(2,6)
        with self.assertRaisesRegex(ValueError,"MONOTONIC_INSERT_REJECTED"):
            self.push(1,3,0,279,first["head_sha256"])
    def test_receipt_conservation(self):
        with self.assertRaisesRegex(ValueError,"THREE_RECEIPTS_PER_CHALLENGE"):
            self.push(1,2)
    def test_registry_change_without_rotation(self):
        first=self.push()
        with self.assertRaisesRegex(ValueError,"REGISTRY_CHANGE_WITHOUT_ROTATION"):
            self.push(2,6,0,279,first["head_sha256"],"b"*64)
    def test_registry_change_with_rotation(self):
        first=self.push()
        second=self.push(2,6,1,279,first["head_sha256"],"b"*64)
        self.assertEqual(second["sequence"],2)
    def test_recovery_to_older_db(self):
        first=self.push();second=self.push(2,6,0,279,first["head_sha256"])
        evidence,pin=anchor(2,second["head_sha256"],2,6,0,279)
        with sqlite3.connect(self.db) as db:
            db.execute("DELETE FROM checkpoint WHERE seq=2")
        result=audit(self.db,evidence,pin)
        self.assertIn("ANCHORED_HEAD_MISSING",result["reasons"])
    def test_historical_head_substitution(self):
        first=self.push()
        evidence,pin=anchor(1,first["head_sha256"],1,3,0,278)
        with sqlite3.connect(self.db) as db:
            db.execute("UPDATE checkpoint SET head_sha=? WHERE seq=1",("f"*64,))
        result=audit(self.db,evidence,pin)
        self.assertIn("ANCHORED_HISTORICAL_HEAD_REWRITTEN",result["reasons"])
    def test_invalid_chain_digest(self):
        self.push()
        with sqlite3.connect(self.db) as db:
            db.execute("UPDATE checkpoint SET previous_sha=? WHERE seq=1",("f"*64,))
        self.assertIn("PREVIOUS_CHAIN_DIGEST_MISMATCH",inspect(self.db)["validation_errors"])
    def test_anchor_signature_corrupt(self):
        first=self.push();record,pin=anchor(1,first["head_sha256"],1,3,0,278)
        record["signature_b64"]="AAAA"
        self.assertIn("EXTERNAL_ANCHOR_SIGNATURE_INVALID",audit(self.db,record,pin)["reasons"])
    def test_anchor_digest_substituted(self):
        first=self.push();record,pin=anchor(1,first["head_sha256"],1,3,0,278)
        self.assertIn("EXTERNAL_ANCHOR_DIGEST_MISMATCH",audit(self.db,record,"f"*64)["reasons"])
    def test_pin_required(self):
        first=self.push();record,pin=anchor(1,first["head_sha256"],1,3,0,278)
        self.assertIn("OUT_OF_BAND_ANCHOR_DIGEST_REQUIRED",audit(self.db,record,None)["reasons"])
    def test_cryptographic_validity_still_hold(self):
        first=self.push();record,pin=anchor(1,first["head_sha256"],1,3,0,278)
        result=audit(self.db,record,pin)
        self.assertFalse(result["physical_act_allowed"])
        self.assertIn("REMOTE_CUSTODIAN_HIGHWATER_NOT_OBSERVED",result["reasons"])
    def test_no_act_on_inspect(self):
        self.push()
        self.assertEqual(inspect(self.db)["validation_errors"],[])
if __name__=="__main__":
    unittest.main()
