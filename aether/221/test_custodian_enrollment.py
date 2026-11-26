"""AETHER-221 documentary enrollment regression tests; not remote authentication."""
import copy
import unittest
from custodian_enrollment import evaluate, digest, SCHEMA, CHALLENGE_SCHEMA


def fixture():
    owned = {"corpus_id": "OWNED-GITHUB-AND-0ROOT", "root": "OWNED-ROOT",
             "operator": "OWNED-OP", "administrator": "OWNED-ADMIN"}
    custodian = {"custodian_id": "OUTSIDE-1", "controller_root": "OTHER-ROOT",
                 "operator": "OTHER-OP", "administrator": "OTHER-ADMIN",
                 "host": "OUTSIDE-HOST", "claimed_external_locator": "external-custody-claim"}
    challenge = {
        "schema": CHALLENGE_SCHEMA, "enrollment_id": "ENROLL-221",
        "custodian_id": "OUTSIDE-1", "nonce": "UNREPEATED-CHALLENGE-221",
        "public_key_sha256": "a" * 64, "evidence_sha256": "b" * 64,
        "external_receipt_locator": "external-claim-not-fetched",
        "issuer": {"controller_root": "THIRD-ROOT", "operator": "THIRD-OP",
                   "administrator": "THIRD-ADMIN"},
        "replay_checked_out_of_band": True,
        "controller_identity_authenticated_out_of_band": True,
        "receipt_retention_checked_out_of_band": True,
        "operational_authority": "HOLD", "physical_act_allowed": False,
        "may_recover": False, "may_repair": False, "may_reclaim_lock": False,
    }
    enrollment = {
        "schema": SCHEMA, "enrollment_id": "ENROLL-221",
        "source_corpus_id": owned["corpus_id"], "custodian": custodian,
        "public_key_sha256": "a" * 64, "challenge_nonce": challenge["nonce"],
        "challenge_digest_sha256": digest(challenge),
        "operational_authority": "HOLD", "physical_act_allowed": False,
        "may_recover": False, "may_repair": False, "may_reclaim_lock": False,
    }
    return enrollment, challenge, owned


class EnrollmentTests(unittest.TestCase):
    def reject(self, reason, edit):
        e, c, o = fixture()
        edit(e, c, o)
        result = evaluate(e, c, o)
        self.assertIn(reason, result["reasons"], result)
        self.assertEqual(result["verdict"], "REJECT")
        self.assertFalse(result["physical_act_allowed"])
        self.assertFalse(result["may_recover"])
        self.assertEqual(result["independently_authenticated_custodians"], 0)

    def test_synthetic_consistency_only(self):
        e, c, o = fixture()
        result = evaluate(e, c, o)
        self.assertEqual(result["verdict"], "DOCUMENTARY_ENROLLMENT_CLAIMS_CONSISTENT_ONLY", result)
        self.assertEqual(result["independently_authenticated_custodians"], 0)
        self.assertFalse(result["original_evidence_authenticated"])

    def test_owned_source_mirror(self):
        self.reject("CUSTODIAN_MIRRORS_OWNED_SOURCE", lambda e,c,o: e["custodian"].update(controller_root=o["root"]))

    def test_shared_operator_with_owned(self):
        self.reject("CUSTODIAN_MIRRORS_OWNED_SOURCE", lambda e,c,o: e["custodian"].update(operator=o["operator"]))

    def test_shared_admin_with_owned(self):
        self.reject("CUSTODIAN_MIRRORS_OWNED_SOURCE", lambda e,c,o: e["custodian"].update(administrator=o["administrator"]))

    def test_issuer_same_controller(self):
        self.reject("ISSUER_SHARES_CUSTODIAN_CONTROL", lambda e,c,o: c["issuer"].update(controller_root=e["custodian"]["controller_root"]))

    def test_issuer_owned_source(self):
        self.reject("ISSUER_MIRRORS_OWNED_SOURCE", lambda e,c,o: c["issuer"].update(operator=o["operator"]))

    def test_bad_enrollment_identity(self):
        self.reject("CHALLENGE_ENROLLMENT_MISMATCH", lambda e,c,o: e.update(enrollment_id="SWITCHED"))

    def test_custodian_identity_substitution(self):
        self.reject("CHALLENGE_CUSTODIAN_MISMATCH", lambda e,c,o: c.update(custodian_id="SWITCHED"))

    def test_nonce_replay_or_substitution(self):
        self.reject("CHALLENGE_NONCE_MISMATCH_OR_WEAK", lambda e,c,o: c.update(nonce="old"))

    def test_key_substitution(self):
        self.reject("CHALLENGE_KEY_BINDING_MISMATCH", lambda e,c,o: c.update(public_key_sha256="f"*64))

    def test_source_corpus_mismatch(self):
        self.reject("SOURCE_CORPUS_BINDING_MISMATCH", lambda e,c,o: e.update(source_corpus_id="OTHER"))

    def test_challenge_digest_substitution(self):
        self.reject("CHALLENGE_RECORD_DIGEST_MISMATCH", lambda e,c,o: c.update(evidence_sha256="f"*64))

    def test_missing_external_receipt(self):
        self.reject("EXTERNAL_RECEIPT_LOCATOR_MISSING", lambda e,c,o: c.update(external_receipt_locator=""))

    def test_missing_challenge_replay_check(self):
        self.reject("REPLAY_NOT_INDEPENDENTLY_CHECKED", lambda e,c,o: c.update(replay_checked_out_of_band=False))

    def test_missing_external_authentication(self):
        self.reject("CONTROLLER_AUTHENTICATION_UNVERIFIED", lambda e,c,o: c.update(controller_identity_authenticated_out_of_band=False))

    def test_missing_external_retention(self):
        self.reject("EXTERNAL_RETENTION_UNVERIFIED", lambda e,c,o: c.update(receipt_retention_checked_out_of_band=False))

    def test_missing_key_fingerprint(self):
        self.reject("CUSTODIAN_KEY_FINGERPRINT_INVALID", lambda e,c,o: e.update(public_key_sha256=""))

    def test_act_promotion_on_enrollment(self):
        self.reject("OPERATIONAL_PERMISSION_INVALID:physical_act_allowed", lambda e,c,o: e.update(physical_act_allowed=True))

    def test_recovery_promotion_on_challenge(self):
        self.reject("OPERATIONAL_PERMISSION_INVALID:may_recover", lambda e,c,o: c.update(may_recover=True))

    def test_challenge_is_not_self_issued(self):
        self.reject("SELF_ISSUED_CHALLENGE", lambda e,c,o: c["issuer"].update(controller_root="owned"))

    def test_same_claimed_host_is_not_remote_proof(self):
        e,c,o=fixture()
        result=evaluate(e,c,o)
        self.assertEqual(result["physical_qualification_percent"],0)
        self.assertEqual(result["operational_authority"],"HOLD")


if __name__ == "__main__":
    unittest.main()
