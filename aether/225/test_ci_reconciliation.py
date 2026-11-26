"""AETHER-225 synthetic CI record reconciliation tests.

These fixtures are NOT GitHub API responses or executed Rust CI evidence.
"""
import json
import unittest
from ci_reconciliation import reconcile,REQUIRED_STEPS,HOLD

SHA="a"*40
def fixture():
    target={"target_sha":SHA}
    run={"id":225001,"repository":"DavidWise01/oasis","head_sha":SHA,
         "status":"completed","conclusion":"success","event":"push",
         "html_url":"https://github.com/DavidWise01/oasis/actions/runs/225001"}
    jobs=[{"name":"Native Rust qualification with captured failure diagnostics",
           "run_id":225001,"status":"completed","conclusion":"success",
           "steps":[{"name":name,"conclusion":"success"} for name in REQUIRED_STEPS]}]
    artifacts=[{"name":"aether218-rust-qualification","workflow_run_id":225001,
                "expired":False,"size_in_bytes":1800}]
    logs=b"SYNTHETIC JOB LOG. NOT AN ACTUAL CI RUN.\n"
    manifest={"source_commit":SHA,"native_qualification_verified_by_this_manifest":True,
              "operational_authority":"HOLD","physical_qualification_percent":0,
              "inputs":{"src":{"state":"OBSERVED"}},"evidence":{"log":{"state":"OBSERVED"}}}
    return [target,run,jobs,artifacts,logs,json.dumps(manifest).encode()]

class ReconciliationTests(unittest.TestCase):
    def reject(self,reason,edit):
        f=fixture()
        edit(f)
        d=reconcile(*f)
        self.assertEqual(d["verdict"],"REJECT",d)
        self.assertIn(reason,d["reasons"],d)
        self.assertFalse(d["physical_act_allowed"])
        self.assertFalse(d["independently_authenticated_ci_execution"])
        self.assertEqual(d["physical_qualification_percent"],0)

    def test_synthetic_bundle_is_documentary_not_independent(self):
        d=reconcile(*fixture())
        self.assertEqual(d["verdict"],"DOCUMENTARY_CI_RECORD_CONSISTENT_UNAUTHENTICATED",d)
        self.assertFalse(d["independently_authenticated_ci_execution"])
        self.assertEqual(d["operational_authority"],"HOLD")
    def test_missing_run(self):
        self.reject("GITHUB_RUN_NOT_OBSERVED",lambda f:f.__setitem__(1,None))
    def test_wrong_source(self):
        self.reject("RUN_SOURCE_COMMIT_MISMATCH",lambda f:f[1].update(head_sha="b"*40))
    def test_wrong_repository(self):
        self.reject("RUN_REPOSITORY_MISMATCH",lambda f:f[1].update(repository="untrusted/repo"))
    def test_uncompleted_run(self):
        self.reject("RUN_NOT_COMPLETED_SUCCESSFULLY",lambda f:f[1].update(status="in_progress"))
    def test_failed_run(self):
        self.reject("RUN_NOT_COMPLETED_SUCCESSFULLY",lambda f:f[1].update(conclusion="failure"))
    def test_unexpected_trigger(self):
        self.reject("RUN_TRIGGER_UNEXPECTED",lambda f:f[1].update(event="pull_request"))
    def test_missing_run_id(self):
        self.reject("RUN_ID_INVALID",lambda f:f[1].update(id=None))
    def test_missing_jobs(self):
        self.reject("RUN_JOBS_NOT_OBSERVED",lambda f:f.__setitem__(2,None))
    def test_job_run_id_mismatch(self):
        self.reject("JOB_RUN_ID_MISMATCH",lambda f:f[2][0].update(run_id=2))
    def test_job_failed(self):
        self.reject("JOB_NOT_COMPLETED_SUCCESSFULLY",lambda f:f[2][0].update(conclusion="failure"))
    def test_missing_step(self):
        self.reject("REQUIRED_STEP_MISSING:"+REQUIRED_STEPS[1],lambda f:f[2][0]["steps"].pop(1))
    def test_failed_step(self):
        self.reject("REQUIRED_STEP_NOT_SUCCESSFUL:"+REQUIRED_STEPS[3],
                    lambda f:f[2][0]["steps"][3].update(conclusion="failure"))
    def test_missing_artifacts(self):
        self.reject("RUN_ARTIFACTS_NOT_OBSERVED",lambda f:f.__setitem__(3,None))
    def test_wrong_artifact_id(self):
        self.reject("ARTIFACT_RUN_ID_MISMATCH",lambda f:f[3][0].update(workflow_run_id=9))
    def test_expired_artifact(self):
        self.reject("ARTIFACT_EXPIRED_OR_EMPTY",lambda f:f[3][0].update(expired=True))
    def test_missing_log(self):
        self.reject("RUN_LOG_BYTES_MISSING",lambda f:f.__setitem__(4,None))
    def test_empty_log(self):
        self.reject("RUN_LOG_EMPTY",lambda f:f.__setitem__(4,b""))
    def test_missing_manifest(self):
        self.reject("RUN_MANIFEST_BYTES_MISSING",lambda f:f.__setitem__(5,None))
    def test_corrupt_manifest(self):
        self.reject("RUN_MANIFEST_JSON_INVALID",lambda f:f.__setitem__(5,b"bad json"))
    def test_manifest_commit_mismatch(self):
        def edit(f):
            m=json.loads(f[5]);m["source_commit"]="b"*40;f[5]=json.dumps(m).encode()
        self.reject("MANIFEST_SOURCE_COMMIT_MISMATCH",edit)
    def test_native_gate_unverified(self):
        def edit(f):
            m=json.loads(f[5]);m["native_qualification_verified_by_this_manifest"]=False
            f[5]=json.dumps(m).encode()
        self.reject("NATIVE_GATE_NOT_QUALIFIED",edit)
    def test_manifest_claims_act(self):
        def edit(f):
            m=json.loads(f[5]);m["operational_authority"]="ACT";f[5]=json.dumps(m).encode()
        self.reject("MANIFEST_AUTHORITY_PROMOTION",edit)
    def test_no_manifest_evidence(self):
        def edit(f):
            m=json.loads(f[5]);m["evidence"]={};f[5]=json.dumps(m).encode()
        self.reject("MANIFEST_INVENTORY_MISSING:evidence",edit)
    def test_unpinned_target(self):
        self.reject("TARGET_COMMIT_UNPINNED",lambda f:f[0].update(target_sha="not a SHA"))
    def test_run_url_substitution(self):
        self.reject("RUN_URL_UNTRUSTED",lambda f:f[1].update(html_url="https://example.org/fake"))
    def test_two_jobs_duplicate(self):
        def edit(f):
            import copy
            f[2].append(copy.deepcopy(f[2][0]))
        self.reject("QUALIFICATION_JOB_NOT_UNIQUE",edit)

if __name__=="__main__":
    unittest.main()
