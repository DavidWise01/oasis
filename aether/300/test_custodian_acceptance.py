import base64,json,sqlite3,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from custodian_acceptance import (record,audit,sha,canon,digest,ZERO,SCHEMA,
                                  validate_pins,verify_receipt)
def pub(key):
    return key.public_key().public_bytes(serialization.Encoding.PEM,
       serialization.PublicFormat.SubjectPublicKeyInfo).decode()
class Tests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.db=Path(t.name)/"accept.sqlite"
        self.source=Path(t.name)/"source.sqlite"
        self.handoff=Path(t.name)/"handoff.json"
        self.signer=Ed25519PrivateKey.generate()
        self.keys={"custodian_id":"external-custodian-300","public_key_pem":pub(self.signer)}
        self.keys_pin=sha(self.keys)
        self.graph={"journal_root":"journal","custodian_root":"custodian",
                    "ancestors":{"journal":["rootA"],"rootA":[],
                                 "custodian":["rootB"],"rootB":[]}}
        self.graph_pin=sha(self.graph)
        self.handoff_obj={"schema":"AETHER-299/highwater-handoff-v1",
            "recipient_claim":self.keys["custodian_id"],
            "source_phase":"AETHER-297","source_sequence":1,
            "source_head_sha256":"a"*64,"anchored_sequence":1,
            "anchored_head_sha256":"a"*64,
            "declared_source_ancestry_sha256":self.graph_pin,
            "independent_custody_verified":False,"physical_act_allowed":False}
        self.handoff.write_bytes(canon(self.handoff_obj))
        self.receipt=self.signed_receipt(ZERO,"nonce-external-300-A")
        self.patch=patch("custodian_acceptance.audit_packet",
                         return_value={"packet_sha256":digest(self.handoff.read_bytes())})
        self.patch.start();self.addCleanup(self.patch.stop)
    def signed_receipt(self,previous,nonce):
        claim={"schema":SCHEMA,"custodian_id":self.keys["custodian_id"],
               "handoff_sha256":digest(self.handoff.read_bytes()),
               "source_head_sha256":self.handoff_obj["source_head_sha256"],
               "source_sequence":self.handoff_obj["source_sequence"],
               "previous_receipt_sha256":previous,
               "receipt_nonce":nonce,"remote_object_id_claim":"object-v1",
               "retained_until_claim":"indefinite-declared"}
        claim["signature_b64"]=base64.b64encode(self.signer.sign(canon(claim))).decode()
        return claim
    def save(self,receipt=None):
        return record(self.db,self.handoff,self.source,receipt or self.receipt,
                      self.keys,self.keys_pin,self.graph,self.graph_pin)
    def test_verified_signature_does_not_grant_custody(self):
        result=self.save()
        self.assertTrue(result["receipt_signature_verified"])
        self.assertFalse(result["independent_external_custody_verified"])
    def test_first_acceptance_is_linked(self):
        self.save()
        self.assertEqual(audit(self.db)["acceptances"],1)
    def test_second_acceptance_hash_chained(self):
        self.save()
        second=self.signed_receipt(sha(self.receipt),"nonce-external-300-B")
        self.assertEqual(self.save(second)["acceptance_sequence"],2)
        self.assertNotIn("RECEIPT_PREDECESSOR_INVALID",audit(self.db)["reasons"])
    def test_duplicate_nonce_rejected(self):
        self.save()
        with self.assertRaises(ValueError):self.save()
    def test_invalid_signature_rejected_atomically(self):
        self.receipt["signature_b64"]="AAAA"
        with self.assertRaisesRegex(ValueError,"RECEIPT_SIGNATURE_INVALID"):self.save()
        self.assertEqual(audit(self.db)["acceptances"],0)
    def test_wrong_handoff_digest(self):
        self.receipt["handoff_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"RECEIPT_BINDING_INVALID"):self.save()
    def test_wrong_source_head(self):
        self.receipt["source_head_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"RECEIPT_BINDING_INVALID"):self.save()
    def test_reused_predecessor_rejected(self):
        self.save()
        second=self.signed_receipt(ZERO,"nonce-external-300-B")
        with self.assertRaisesRegex(ValueError,"RECEIPT_BINDING_INVALID"):self.save(second)
    def test_bad_key_pin_rejected(self):
        with self.assertRaisesRegex(ValueError,"CUSTODIAN_KEY_PIN_MISMATCH"):
            record(self.db,self.handoff,self.source,self.receipt,self.keys,"f"*64,self.graph,self.graph_pin)
    def test_wrong_graph_pin_rejected(self):
        with self.assertRaisesRegex(ValueError,"ANCESTRY_PIN_MISMATCH"):
            record(self.db,self.handoff,self.source,self.receipt,self.keys,self.keys_pin,self.graph,"f"*64)
    def test_common_source_ancestry_rejected(self):
        self.graph["ancestors"]["custodian"]=["rootA"]
        self.graph_pin=sha(self.graph)
        self.handoff_obj["declared_source_ancestry_sha256"]=self.graph_pin
        self.handoff.write_bytes(canon(self.handoff_obj))
        self.receipt=self.signed_receipt(ZERO,"nonce-external-300-A")
        with self.assertRaisesRegex(ValueError,"DECLARED_SHARED_SOURCE_ANCESTRY"):
            self.save()
    def test_wrong_recipient_rejected(self):
        self.handoff_obj["recipient_claim"]="other-recipient"
        self.handoff.write_bytes(canon(self.handoff_obj))
        with self.assertRaisesRegex(ValueError,"HANDOFF_RECIPIENT_DIFFERENT"):self.save()
    def test_receipt_claim_not_independent_ownership(self):
        self.save()
        self.assertIn("INDEPENDENT_CUSTODIAN_OWNERSHIP_UNVERIFIED",audit(self.db)["reasons"])
    def test_external_anchor_matching(self):
        head=self.save()["ledger_head_sha256"]
        self.assertNotIn("EXTERNAL_HIGHWATER_REWRITE",audit(self.db,external_seq=1,external_head=head)["reasons"])
    def test_external_anchor_mismatch(self):
        self.save()
        self.assertIn("EXTERNAL_HIGHWATER_REWRITE",audit(self.db,external_seq=1,external_head="f"*64)["reasons"])
    def test_external_anchor_removed(self):
        self.save()
        self.assertIn("EXTERNAL_HIGHWATER_ROLLBACK",audit(self.db,external_seq=2,external_head="f"*64)["reasons"])
    def test_mutated_stored_hash_detected(self):
        self.save()
        with sqlite3.connect(self.db) as d:d.execute("UPDATE acceptance SET head=?",("f"*64,))
        self.assertIn("ACCEPTANCE_HEAD_INVALID",audit(self.db)["reasons"])
    def test_deleted_row_detected_by_outside_pin(self):
        head=self.save()["ledger_head_sha256"]
        with sqlite3.connect(self.db) as d:d.execute("DELETE FROM acceptance")
        self.assertIn("EXTERNAL_HIGHWATER_ROLLBACK",audit(self.db,external_seq=1,external_head=head)["reasons"])
    def test_source_reconciliation(self):
        self.save()
        self.assertNotIn("HANDOFF_ANCESTRY_DIVERGENCE",
                         audit(self.db,self.handoff,self.source)["reasons"])
    def test_missing_source_does_not_prove_acceptance(self):
        self.save()
        self.assertFalse(audit(self.db)["remote_retention_verified"])
    def test_physical_act_never_promoted(self):
        self.assertFalse(self.save()["physical_act_allowed"])
if __name__=="__main__":unittest.main()
