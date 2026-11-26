"""AETHER-223 cross-protocol documentary tests. All inputs are synthetic."""
import json
import unittest
from pathlib import Path
from adversarial_review import evaluate, HOLD, load, ROOT

enroll = load("aether221_fixture_util", ROOT/"221"/"custodian_enrollment.py")
physical = load("aether222_fixture_util", ROOT/"222"/"original_evidence.py")


def fixture():
    owned={"corpus_id":"ONE-OWNED-CORPUS","root":"SOURCE-ROOT",
           "operator":"SOURCE-OP","administrator":"SOURCE-ADMIN"}
    custodian={"custodian_id":"HOLDER-223","controller_root":"HOLDER-ROOT",
               "operator":"HOLDER-OP","administrator":"HOLDER-ADMIN",
               "host":"HOLDER-HOST","claimed_external_locator":"CLAIMED-REMOTE"}
    issuer={"controller_root":"ISSUER-ROOT","operator":"ISSUER-OP",
            "administrator":"ISSUER-ADMIN"}
    capture=b"SYNTHETIC CAPTURE. NO PHYSICAL DEVICE VERIFIED.\n"
    capture_hash=physical.sha256(capture)
    receipt_obj={
      "enrollment_id":"ENROLL-223","receipt_id":"RECEIPT-223",
      "nonce":"UNIQUE-DOCUMENTARY-NONCE-223","holder_key_sha256":"a"*64,
      "capture_sha256":capture_hash,"operational_authority":"HOLD",
      "physical_act_allowed":False
    }
    receipt=(json.dumps(receipt_obj,sort_keys=True)+"\n").encode()
    challenge={"schema":enroll.CHALLENGE_SCHEMA,"enrollment_id":"ENROLL-223",
      "custodian_id":"HOLDER-223","nonce":receipt_obj["nonce"],
      "public_key_sha256":"a"*64,"evidence_sha256":"b"*64,
      "external_receipt_locator":"CLAIMED-EXTERNAL-NOT-FETCHED",
      "issuer":issuer,
      "replay_checked_out_of_band":True,
      "controller_identity_authenticated_out_of_band":True,
      "receipt_retention_checked_out_of_band":True,
      "operational_authority":"HOLD","physical_act_allowed":False,
      "may_recover":False,"may_repair":False,"may_reclaim_lock":False}
    enrollment={"schema":enroll.SCHEMA,"enrollment_id":"ENROLL-223",
      "source_corpus_id":"ONE-OWNED-CORPUS","custodian":custodian,
      "public_key_sha256":"a"*64,"challenge_nonce":challenge["nonce"],
      "challenge_digest_sha256":enroll.digest(challenge),
      "operational_authority":"HOLD","physical_act_allowed":False,
      "may_recover":False,"may_repair":False,"may_reclaim_lock":False}
    original={"schema":physical.SCHEMA,
      "enrollment_id":"ENROLL-223","receipt_id":"RECEIPT-223","nonce":challenge["nonce"],
      "holder_key_sha256":"a"*64,"receipt_sha256":physical.sha256(receipt),
      "capture_sha256":capture_hash,
      "source_root":"SOURCE-ROOT","source_operator":"SOURCE-OP","source_administrator":"SOURCE-ADMIN",
      "holder_root":"HOLDER-ROOT","holder_operator":"HOLDER-OP","holder_administrator":"HOLDER-ADMIN",
      "issuer_root":"ISSUER-ROOT","issuer_operator":"ISSUER-OP","issuer_administrator":"ISSUER-ADMIN",
      "signature_verification":"NOT_PERFORMED",
      "custodian_authentication":"NOT_PERFORMED",
      "original_device_authentication":"NOT_PERFORMED",
      "operational_authority":"HOLD","physical_act_allowed":False,
      "may_recover":False,"may_repair":False}
    native_gate={"source_commit":"a"*40,"native_qualification_passed":True,
                 "operational_authority":"HOLD","physical_act_allowed":False}
    native_manifest={"source_commit":"a"*40,
       "native_qualification_verified_by_this_manifest":True,
       "operational_authority":"HOLD","physical_qualification_percent":0}
    return [enrollment,challenge,owned,original,receipt,capture,set(),native_gate,native_manifest]


class AdversarialIntegrationTests(unittest.TestCase):
    def evaluate_fixture(self,arr):
        return evaluate(*arr)
    def check_reject(self,reason,edit):
        f=fixture()
        edit(f)
        d=self.evaluate_fixture(f)
        self.assertEqual(d["verdict"],"REJECT",d)
        self.assertIn(reason,d["reasons"],d)
        self.assertEqual(d["operational_authority"],"HOLD")
        self.assertFalse(d["physical_act_allowed"])
        self.assertFalse(d["may_recover"])
        self.assertEqual(d["physical_qualification_percent"],0)

    def test_all_consistent_synthetic_claims_remain_documentary_only(self):
        d=self.evaluate_fixture(fixture())
        self.assertEqual(d["verdict"],"DOCUMENTARY_ENSEMBLE_CONSISTENT_ONLY",d)
        self.assertEqual(d["independently_authenticated_remote_custodians"],0)
        self.assertFalse(d["external_signature_verification_performed"])
        self.assertFalse(d["independent_remote_evidence_retrieved"])

    def test_missing_native_execution(self):
        self.check_reject("OBSERVED_NATIVE_EXECUTION_GATE_MISSING",lambda f:f.__setitem__(7,None))
    def test_native_execution_claim_false(self):
        self.check_reject("NATIVE_EXECUTION_NOT_VERIFIED",lambda f:f[7].update(native_qualification_passed=False))
    def test_native_authority_promoted(self):
        self.check_reject("NATIVE_EXECUTION_AUTHORITY_PROMOTION",lambda f:f[7].update(physical_act_allowed=True))
    def test_missing_manifest(self):
        self.check_reject("NATIVE_MANIFEST_MISSING",lambda f:f.__setitem__(8,None))
    def test_manifest_failure(self):
        self.check_reject("NATIVE_MANIFEST_NOT_VERIFIED",lambda f:f[8].update(native_qualification_verified_by_this_manifest=False))
    def test_manifest_commit_mismatch(self):
        self.check_reject("NATIVE_SOURCE_REVISION_CONFLICT",lambda f:f[8].update(source_commit="b"*40))
    def test_manifest_authority_promoted(self):
        self.check_reject("NATIVE_MANIFEST_AUTHORITY_PROMOTION",lambda f:f[8].update(operational_authority="ACT"))
    def test_enrollment_missing(self):
        self.check_reject("CUSTODIAN_ENROLLMENT_REJECTED",lambda f:f[0].update(enrollment_id="REPLACED"))
    def test_holder_root_shared_with_owned(self):
        self.check_reject("CUSTODIAN_ENROLLMENT_REJECTED",lambda f:f[0]["custodian"].update(controller_root="SOURCE-ROOT"))
    def test_holder_ancestry_cross_bound(self):
        self.check_reject("HOLDER_CONTROL_ANCESTRY_CROSS_BOUND_MISMATCH",lambda f:f[3].update(holder_operator="DIFFERENT"))
    def test_issuer_ancestry_cross_bound(self):
        self.check_reject("ISSUER_CONTROL_ANCESTRY_CROSS_BOUND_MISMATCH",lambda f:f[3].update(issuer_administrator="DIFFERENT"))
    def test_source_ancestry_cross_bound(self):
        self.check_reject("SOURCE_CONTROL_ANCESTRY_CROSS_BOUND_MISMATCH",lambda f:f[3].update(source_root="DIFFERENT"))
    def test_enrollment_id_cross_bound(self):
        self.check_reject("ENROLLMENT_ID_CROSS_BOUND_MISMATCH",lambda f:f[3].update(enrollment_id="OTHER"))
    def test_nonce_cross_bound(self):
        self.check_reject("CHALLENGE_NONCE_CROSS_BOUND_MISMATCH",lambda f:f[3].update(nonce="ANOTHER-CROSS-NONCE"))
    def test_key_cross_bound(self):
        self.check_reject("HOLDER_KEY_CROSS_BOUND_MISMATCH",lambda f:f[3].update(holder_key_sha256="b"*64))
    def test_capture_tamper(self):
        self.check_reject("ORIGINAL_EVIDENCE_CHALLENGE_REJECTED",lambda f:f.__setitem__(5,f[5]+b"TAMPER"))
    def test_receipt_tamper(self):
        self.check_reject("ORIGINAL_EVIDENCE_CHALLENGE_REJECTED",lambda f:f.__setitem__(4,f[4]+b"TAMPER"))
    def test_receipt_missing(self):
        self.check_reject("ORIGINAL_EVIDENCE_CHALLENGE_REJECTED",lambda f:f.__setitem__(4,None))
    def test_capture_missing(self):
        self.check_reject("ORIGINAL_EVIDENCE_CHALLENGE_REJECTED",lambda f:f.__setitem__(5,None))
    def test_nonce_replay(self):
        self.check_reject("ORIGINAL_EVIDENCE_CHALLENGE_REJECTED",lambda f:f[6].add("UNIQUE-DOCUMENTARY-NONCE-223"))
    def test_bogus_signature_verification(self):
        self.check_reject("ORIGINAL_EVIDENCE_CHALLENGE_REJECTED",lambda f:f[3].update(signature_verification="VERIFIED"))
    def test_forged_challenge_issuer(self):
        self.check_reject("CUSTODIAN_ENROLLMENT_REJECTED",lambda f:f[1]["issuer"].update(controller_root="SOURCE-ROOT"))
    def test_repaired_manifest_cannot_grant_act(self):
        d=self.evaluate_fixture(fixture())
        self.assertFalse(d["may_reclaim_lock"])
        self.assertFalse(d["may_choose_history"])
        self.assertFalse(d["original_device_authenticated"] if "original_device_authenticated" in d else False)

if __name__=="__main__":
    unittest.main()
