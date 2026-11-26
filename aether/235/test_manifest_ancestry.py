import copy
import hashlib
import pathlib
import sys
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from manifest_ancestry import review,canonical

def fixture():
    source="b"*40
    pin_commit="a"*40
    manifest={"source_commit":source,"files":{"qualification.json":"c"*64}}
    return {
      "manifest":manifest,
      "pin":{"commit_sha":pin_commit,"manifest_sha256":hashlib.sha256(canonical(manifest)).hexdigest(),
             "repository":"DavidWise01/oasis","path":"aether/evidence/pinned-members.json",
             "source_commit":source,"run_id":17},
      "run":{"repository":"DavidWise01/oasis","head_sha":source,"id":17,
             "status":"completed","conclusion":"success"},
      "ancestry":{"source_sha":source,"pin_commit_sha":pin_commit,
                  "api_confirmed":True,"pin_is_ancestor":True}
    }

class BoundaryTests(unittest.TestCase):
    def check(self,data,reason):
        result=review(data)
        self.assertEqual(result["verdict"],"REJECT_OR_UNVERIFIED")
        self.assertIn(reason,result["reasons"])
        self.assertEqual(result["operational_authority"],"HOLD")
        self.assertFalse(result["physical_act_allowed"])
    def test_consistent_but_not_independently_authenticated(self):
        self.check(fixture(),"INDEPENDENT_PRE_RUN_CUSTODY_UNOBSERVED")
    def test_forged_manifest(self):
        d=fixture();d["manifest"]["files"]["qualification.json"]="d"*64
        self.check(d,"PINNED_MANIFEST_DIGEST_MISMATCH")
    def test_run_source_changed(self):
        d=fixture();d["run"]["head_sha"]="c"*40
        self.check(d,"RUN_MANIFEST_SOURCE_MISMATCH")
    def test_wrong_run_id(self):
        d=fixture();d["run"]["id"]=18
        self.check(d,"PIN_RUN_ID_MISMATCH")
    def test_missing_ancestry(self):
        d=fixture();d.pop("ancestry")
        self.check(d,"ANCESTRY_MISSING")
    def test_false_ancestry(self):
        d=fixture();d["ancestry"]["pin_is_ancestor"]=False
        self.check(d,"PIN_NOT_PROVEN_ANCESTOR")
    def test_unconfirmed_api(self):
        d=fixture();d["ancestry"]["api_confirmed"]=False
        self.check(d,"ANCESTRY_NOT_CONFIRMED")
    def test_pin_equals_run(self):
        d=fixture();d["pin"]["commit_sha"]=d["run"]["head_sha"]
        d["ancestry"]["pin_commit_sha"]=d["run"]["head_sha"]
        self.check(d,"PIN_COMMIT_EQUALS_RUN_HEAD")
    def test_not_completed(self):
        d=fixture();d["run"]["status"]="in_progress"
        self.check(d,"RUN_NOT_SUCCESSFUL_COMPLETED")
    def test_pin_path(self):
        d=fixture();d["pin"]["path"]="artifact/self-pinned.json"
        self.check(d,"PIN_PATH_UNTRUSTED")
    def test_claimed_receipt_still_unauthenticated(self):
        d=fixture();d["independent_pre_run_custody_receipt"]={"signature":"unverified"}
        self.check(d,"CUSTODY_RECEIPT_NOT_CRYPTOGRAPHICALLY_AUTHENTICATED")
    def test_wrong_repo(self):
        d=fixture();d["pin"]["repository"]="attacker/oasis"
        self.check(d,"REPOSITORY_MISMATCH")
    def test_invalid_object(self):
        self.check(None,"EVIDENCE_OBJECT_INVALID")
    def test_malformed_digest(self):
        d=fixture();d["pin"]["manifest_sha256"]="pass"
        self.check(d,"PIN_DIGEST_INVALID")

if __name__=="__main__":
    unittest.main()
