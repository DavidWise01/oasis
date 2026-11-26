"""AETHER-222 file-backed documentary original-evidence checks.

These are synthetic byte fixtures, NOT a real remote custodian or physical device.
"""
import copy
import json
import unittest
from original_evidence import evaluate,sha256,SCHEMA

def fixture():
 capture=b"SYNTHETIC CAPTURE BYTES: NOT A PHYSICAL SENSOR\n"
 cap_hash=sha256(capture)
 receipt={
  "enrollment_id":"ENR-222","receipt_id":"REC-222",
  "nonce":"DETERMINISTIC-NONCE-222",
  "holder_key_sha256":"a"*64,"capture_sha256":cap_hash,
  "operational_authority":"HOLD","physical_act_allowed":False
 }
 receipt_bytes=(json.dumps(receipt,sort_keys=True)+"\n").encode()
 r={
  "schema":SCHEMA,
  "enrollment_id":"ENR-222","receipt_id":"REC-222",
  "nonce":"DETERMINISTIC-NONCE-222",
  "holder_key_sha256":"a"*64,
  "receipt_sha256":sha256(receipt_bytes),"capture_sha256":cap_hash,
  "source_root":"ROOT-S","source_operator":"OP-S","source_administrator":"ADMIN-S",
  "holder_root":"ROOT-H","holder_operator":"OP-H","holder_administrator":"ADMIN-H",
  "issuer_root":"ROOT-I","issuer_operator":"OP-I","issuer_administrator":"ADMIN-I",
  "signature_verification":"NOT_PERFORMED",
  "custodian_authentication":"NOT_PERFORMED",
  "original_device_authentication":"NOT_PERFORMED",
  "may_recover":False,"may_repair":False,"physical_act_allowed":False,
  "operational_authority":"HOLD"
 }
 return r,receipt_bytes,capture

class ChallengeTests(unittest.TestCase):
 def reject(self,expected,edit):
  r,b,c=fixture()
  r,b,c=edit(r,b,c)
  decision=evaluate(r,b,c,set())
  self.assertEqual(decision["verdict"],"REJECT",decision)
  self.assertIn(expected,decision["reasons"])
  self.assertFalse(decision["physical_act_allowed"])
  self.assertFalse(decision["may_recover"])
  self.assertEqual(decision["physical_qualification_percent"],0)

 def test_consistent_bytes_are_documentary_only(self):
  r,b,c=fixture()
  d=evaluate(r,b,c,set())
  self.assertEqual(d["verdict"],"DOCUMENTARY_BYTES_AND_BINDINGS_CONSISTENT_ONLY",d)
  self.assertFalse(d["signature_verified"])
  self.assertFalse(d["remote_controller_authenticated"])
  self.assertFalse(d["original_device_authenticated"])

 def test_missing_receipt_bytes(self):
  self.reject("EXTERNAL_RECEIPT_BYTES_UNAVAILABLE",lambda r,b,c:(r,None,c))
 def test_missing_capture_bytes(self):
  self.reject("ORIGINAL_CAPTURE_BYTES_UNAVAILABLE",lambda r,b,c:(r,b,None))
 def test_changed_receipt_byte(self):
  self.reject("EXTERNAL_RECEIPT_DIGEST_MISMATCH",lambda r,b,c:(r,b+b" ",c))
 def test_changed_capture_byte(self):
  self.reject("ORIGINAL_CAPTURE_DIGEST_MISMATCH",lambda r,b,c:(r,b,c+b"!"))
 def test_replaced_receipt_digest(self):
  self.reject("EXTERNAL_RECEIPT_DIGEST_MISMATCH",lambda r,b,c:(dict(r,receipt_sha256="f"*64),b,c))
 def test_swapped_enrollment(self):
  self.reject("RECEIPT_CHALLENGE_BINDING_MISMATCH",lambda r,b,c:(dict(r,enrollment_id="OTHER"),b,c))
 def test_swapped_nonce_binding(self):
  self.reject("RECEIPT_CHALLENGE_BINDING_MISMATCH",lambda r,b,c:(dict(r,nonce="ANOTHER-LONG-VALID-NONCE"),b,c))
 def test_weak_nonce(self):
  self.reject("CHALLENGE_NONCE_INVALID",lambda r,b,c:(dict(r,nonce="old"),b,c))
 def test_shared_root(self):
  self.reject("SHARED_CONTROL_ANCESTRY",lambda r,b,c:(dict(r,holder_root=r["source_root"]),b,c))
 def test_shared_operator(self):
  self.reject("SHARED_CONTROL_ANCESTRY",lambda r,b,c:(dict(r,issuer_operator=r["holder_operator"]),b,c))
 def test_shared_administrator(self):
  self.reject("SHARED_CONTROL_ANCESTRY",lambda r,b,c:(dict(r,issuer_administrator=r["source_administrator"]),b,c))
 def test_missing_holder_key_pin(self):
  self.reject("HOLDER_KEY_PIN_INVALID",lambda r,b,c:(dict(r,holder_key_sha256="short"),b,c))
 def test_missing_receipt_id(self):
  self.reject("RECEIPT_ID_MISSING",lambda r,b,c:(dict(r,receipt_id=""),b,c))
 def test_missing_enrollment_id(self):
  self.reject("ENROLLMENT_BINDING_MISSING",lambda r,b,c:(dict(r,enrollment_id=""),b,c))
 def test_signature_false_claim(self):
  self.reject("SIGNATURE_VERIFICATION_MISREPRESENTED",lambda r,b,c:(dict(r,signature_verification="VERIFIED"),b,c))
 def test_controller_false_claim(self):
  self.reject("CUSTODIAN_AUTHENTICATION_MISREPRESENTED",lambda r,b,c:(dict(r,custodian_authentication="VERIFIED"),b,c))
 def test_physical_device_false_claim(self):
  self.reject("DEVICE_ORIGIN_AUTHENTICATION_MISREPRESENTED",lambda r,b,c:(dict(r,original_device_authentication="VERIFIED"),b,c))
 def test_recovery_promotion(self):
  self.reject("OPERATIONAL_AUTHORITY_PROMOTION",lambda r,b,c:(dict(r,may_recover=True),b,c))
 def test_act_promotion(self):
  self.reject("OPERATIONAL_AUTHORITY_PROMOTION",lambda r,b,c:(dict(r,physical_act_allowed=True),b,c))
 def test_unreadable_json_receipt(self):
  self.reject("RECEIPT_JSON_INVALID",lambda r,b,c:(dict(r,receipt_sha256=sha256(b"not JSON")),b"not JSON",c))
 def test_replayed_nonce(self):
  r,b,c=fixture()
  d=evaluate(r,b,c,{"DETERMINISTIC-NONCE-222"})
  self.assertIn("CHALLENGE_NONCE_REPLAY",d["reasons"])
  self.assertEqual(d["verdict"],"REJECT")
 def test_unobserved_nonce_ledger_is_not_independent(self):
  r,b,c=fixture()
  d=evaluate(r,b,c,None)
  self.assertFalse(d["remote_controller_authenticated"])
  self.assertEqual(d["operational_authority"],"HOLD")
 def test_schema_substitution(self):
  self.reject("CHALLENGE_SCHEMA_INVALID",lambda r,b,c:(dict(r,schema="OTHER"),b,c))

if __name__=="__main__":
 unittest.main()
