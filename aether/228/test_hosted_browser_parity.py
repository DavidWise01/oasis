"""AETHER-228 synthetic hosted/browser evidence parity tests.

Fixtures are not actual downloaded GitHub Actions archives or trusted pins.
"""
import unittest
from hosted_browser_parity import evaluate,digest

SHA="a"*40
PAYLOAD=b"SYNTHETIC GITHUB-HOSTED ARCHIVE PLACEHOLDER; NOT REAL EVIDENCE.\n"

def fixture():
    reference={"schema":"AETHER-228/expected-hosted-archive-v1","sha256":digest(PAYLOAD),
               "source_commit":SHA,"run_id":228001,
               "origin_type":"GITHUB_HOSTED_ARTIFACT_DOWNLOADED"}
    run={"id":228001,"head_sha":SHA,"repository":"DavidWise01/oasis",
         "status":"completed","conclusion":"success",
         "artifact_name":"aether218-rust-qualification","artifact_expired":False}
    inventory={"schema":"AETHER-227/archive-inventory-v1",
               "source_commit":SHA,"verdict":"DOCUMENTARY_ARCHIVE_BYTES_CONSISTENT_ONLY",
               "operational_authority":"HOLD","physical_qualification_percent":0}
    return [reference,PAYLOAD,PAYLOAD,inventory,run]

class HostedBrowserTests(unittest.TestCase):
    def reject(self,code,edit):
        parts=fixture()
        edit(parts)
        result=evaluate(*parts)
        self.assertEqual(result["verdict"],"REJECT_OR_UNVERIFIED",result)
        self.assertIn(code,result["reasons"])
        self.assertEqual(result["operational_authority"],"HOLD")
        self.assertFalse(result["physical_act_allowed"])
        self.assertFalse(result["independently_authenticated_hosted_artifact"])

    def test_consistent_fake_bytes_are_documentary_only(self):
        result=evaluate(*fixture())
        self.assertEqual(result["verdict"],"DOCUMENTARY_HOSTED_BROWSER_BYTES_MATCH_ONLY")
        self.assertFalse(result["independently_authenticated_hosted_artifact"])
        self.assertEqual(result["physical_qualification_percent"],0)
    def test_missing_reference_pin(self):
        self.reject("EXTERNAL_DIGEST_PIN_MISSING",lambda x:x[0].pop("sha256"))
    def test_bad_reference_schema(self):
        self.reject("REFERENCE_SCHEMA_INVALID",lambda x:x[0].update(schema="BAD"))
    def test_missing_source_sha(self):
        self.reject("SOURCE_REVISION_PIN_MISSING",lambda x:x[0].update(source_commit="bad"))
    def test_run_pin_missing(self):
        self.reject("RUN_ID_PIN_MISSING",lambda x:x[0].update(run_id=0))
    def test_origin_not_declared(self):
        self.reject("HOSTED_ORIGIN_NOT_DECLARED",lambda x:x[0].update(origin_type="LOCAL_ZIP"))
    def test_missing_hosted_bytes(self):
        self.reject("HOSTED_BYTES_NOT_OBSERVED",lambda x:x.__setitem__(1,None))
    def test_missing_browser_bytes(self):
        self.reject("BROWSER_BYTES_NOT_OBSERVED",lambda x:x.__setitem__(2,None))
    def test_browser_mutation(self):
        self.reject("HOSTED_BROWSER_BYTES_DIVERGE",lambda x:x.__setitem__(2,PAYLOAD+b"tamper"))
    def test_joint_file_substitution_against_pin(self):
        def change(x):
            x[1]=x[2]=b"both substituted"
        self.reject("HOSTED_DIGEST_PIN_MISMATCH",change)
    def test_replaced_pin_against_browser_bytes(self):
        self.reject("BROWSER_DIGEST_PIN_MISMATCH",lambda x:x[0].update(sha256="b"*64))
    def test_missing_run_record(self):
        self.reject("RUN_RECORD_NOT_OBSERVED",lambda x:x.__setitem__(4,None))
    def test_swapped_run_id(self):
        self.reject("RUN_ID_MISMATCH",lambda x:x[4].update(id=900))
    def test_swapped_source(self):
        self.reject("RUN_SOURCE_COMMIT_MISMATCH",lambda x:x[4].update(head_sha="b"*40))
    def test_mirror_repository(self):
        self.reject("RUN_REPOSITORY_MISMATCH",lambda x:x[4].update(repository="owned/mirror"))
    def test_incomplete_run(self):
        self.reject("RUN_NOT_SUCCESSFULLY_COMPLETED",lambda x:x[4].update(status="in_progress"))
    def test_failed_run(self):
        self.reject("RUN_NOT_SUCCESSFULLY_COMPLETED",lambda x:x[4].update(conclusion="failure"))
    def test_wrong_artifact_name(self):
        self.reject("RUN_ARTIFACT_NAME_MISMATCH",lambda x:x[4].update(artifact_name="other"))
    def test_expired_artifact(self):
        self.reject("RUN_ARTIFACT_EXPIRED",lambda x:x[4].update(artifact_expired=True))
    def test_missing_inventory(self):
        self.reject("ARTIFACT_INVENTORY_NOT_OBSERVED",lambda x:x.__setitem__(3,None))
    def test_inventory_wrong_source(self):
        self.reject("INVENTORY_SOURCE_REVISION_MISMATCH",lambda x:x[3].update(source_commit="b"*40))
    def test_inventory_false_pass(self):
        self.reject("INVENTORY_QUALIFICATION_NOT_CONSISTENT",lambda x:x[3].update(verdict="REJECT"))
    def test_inventory_act_promotion(self):
        self.reject("INVENTORY_AUTHORITY_PROMOTION",lambda x:x[3].update(operational_authority="ACT"))
    def test_inventory_wrong_schema(self):
        self.reject("INVENTORY_SCHEMA_INVALID",lambda x:x[3].update(schema="BAD"))
    def test_exact_digest_same_bytes(self):
        self.assertEqual(digest(PAYLOAD),digest(PAYLOAD))

if __name__=="__main__":
    unittest.main()
