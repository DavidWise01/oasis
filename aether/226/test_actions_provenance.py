"""AETHER-226 GitHub API provenance tests using SYNTHETIC HTTP responses.

Matching mocked API payloads are not a live authenticated GitHub observation.
"""
import json
import unittest
from actions_provenance import observe, HOLD, sha

RUN_ID=226001
COMMIT="a"*40

def fixture():
    run={"id":RUN_ID,"head_sha":COMMIT,
        "repository":{"full_name":"DavidWise01/oasis"},
        "path":".github/workflows/aether217-rust-qualification.yml",
        "event":"push","status":"completed","conclusion":"success"}
    jobs={"total_count":1,"jobs":[{
        "id":1001,"run_id":RUN_ID,
        "name":"Native Rust qualification with captured failure diagnostics",
        "status":"completed","conclusion":"success",
        "steps":[{"name":"Checkout","conclusion":"success"},
                 {"name":"Cargo tests","conclusion":"success"}]
    }]}
    artifacts={"total_count":1,"artifacts":[{
        "name":"aether218-rust-qualification",
        "expired":False,"size_in_bytes":123,
        "workflow_run":{"id":RUN_ID}}]}
    return {"run":run,"jobs":jobs,"artifacts":artifacts}

def caller(d,missing=None):
    def fetch(path):
        name="run" if path.endswith("/"+str(RUN_ID)) else "jobs" if "/jobs?" in path else "artifacts"
        if name==missing:raise OSError("Synthetic unavailable API response")
        value=d[name];raw=json.dumps(value,sort_keys=True).encode()
        return value,raw
    return fetch

class ProvenanceTests(unittest.TestCase):
    def reject(self,expected,mutate=None,missing=None):
        d=fixture()
        if mutate:mutate(d)
        r=observe(RUN_ID,COMMIT,caller(d,missing))
        self.assertEqual(r["verdict"],"REJECT_OR_UNVERIFIED",r)
        self.assertIn(expected,r["reasons"],r)
        self.assertFalse(r["runner_binary_or_logs_independently_authenticated"])
        self.assertEqual(r["operational_authority"],"HOLD")
        self.assertFalse(r["physical_act_allowed"])

    def test_matching_mocked_api_is_documentary_only(self):
        r=observe(RUN_ID,COMMIT,caller(fixture()))
        self.assertEqual(r["verdict"],"DOCUMENTARY_GITHUB_API_METADATA_CONSISTENT",r)
        self.assertFalse(r["source_authenticated_independently"])
        self.assertEqual(len(r["api_response_digests"]),3)

    def test_missing_run(self):
        self.reject("API_READBACK_UNAVAILABLE:run",missing="run")
    def test_missing_jobs(self):
        self.reject("API_READBACK_UNAVAILABLE:jobs",missing="jobs")
    def test_missing_artifacts(self):
        self.reject("API_READBACK_UNAVAILABLE:artifacts",missing="artifacts")
    def test_swapped_run_id(self):
        self.reject("RUN_ID_MISMATCH",lambda x:x["run"].update(id=555))
    def test_swapped_commit(self):
        self.reject("RUN_COMMIT_MISMATCH",lambda x:x["run"].update(head_sha="b"*40))
    def test_mirror_repository(self):
        self.reject("REPOSITORY_MISMATCH",lambda x:x["run"]["repository"].update(full_name="other/mirror"))
    def test_workflow_swapped(self):
        self.reject("WORKFLOW_IDENTITY_MISMATCH",lambda x:x["run"].update(path=".github/workflows/other.yml"))
    def test_manual_trigger_allowed(self):
        d=fixture();d["run"]["event"]="workflow_dispatch"
        self.assertEqual(observe(RUN_ID,COMMIT,caller(d))["verdict"],"DOCUMENTARY_GITHUB_API_METADATA_CONSISTENT")
    def test_unexpected_trigger(self):
        self.reject("TRIGGER_UNEXPECTED",lambda x:x["run"].update(event="pull_request"))
    def test_pending_run(self):
        self.reject("RUN_NOT_SUCCESSFULLY_COMPLETED",lambda x:x["run"].update(status="in_progress"))
    def test_failed_run(self):
        self.reject("RUN_NOT_SUCCESSFULLY_COMPLETED",lambda x:x["run"].update(conclusion="failure"))
    def test_missing_qualification_job(self):
        self.reject("QUALIFICATION_JOB_NOT_UNIQUE",lambda x:x["jobs"]["jobs"].clear())
    def test_duplicate_job(self):
        self.reject("QUALIFICATION_JOB_NOT_UNIQUE",lambda x:x["jobs"]["jobs"].append(dict(x["jobs"]["jobs"][0])))
    def test_job_bound_to_other_run(self):
        self.reject("JOB_RUN_MISMATCH",lambda x:x["jobs"]["jobs"][0].update(run_id=333))
    def test_failed_job(self):
        self.reject("QUALIFICATION_JOB_NOT_SUCCESSFUL",lambda x:x["jobs"]["jobs"][0].update(conclusion="failure"))
    def test_missing_steps(self):
        self.reject("JOB_STEPS_NOT_OBSERVED",lambda x:x["jobs"]["jobs"][0].update(steps=[]))
    def test_failed_step(self):
        self.reject("JOB_STEP_NOT_SUCCESSFUL",lambda x:x["jobs"]["jobs"][0]["steps"][1].update(conclusion="failure"))
    def test_expired_artifact(self):
        self.reject("RUN_BOUND_QUALIFICATION_ARTIFACT_NOT_OBSERVED",lambda x:x["artifacts"]["artifacts"][0].update(expired=True))
    def test_artifact_run_mismatch(self):
        self.reject("RUN_BOUND_QUALIFICATION_ARTIFACT_NOT_OBSERVED",lambda x:x["artifacts"]["artifacts"][0]["workflow_run"].update(id=3))
    def test_missing_artifact(self):
        self.reject("RUN_BOUND_QUALIFICATION_ARTIFACT_NOT_OBSERVED",lambda x:x["artifacts"]["artifacts"].clear())
    def test_incomplete_jobs_page(self):
        self.reject("JOBS_PAGINATED_INCOMPLETE",lambda x:x["jobs"].update(total_count=101))
    def test_incomplete_artifacts_page(self):
        self.reject("ARTIFACTS_PAGINATED_INCOMPLETE",lambda x:x["artifacts"].update(total_count=101))
    def test_source_sha_not_pinned(self):
        r=observe(RUN_ID,"bad",caller(fixture()))
        self.assertIn("EXPECTED_COMMIT_UNPINNED",r["reasons"])
        self.assertEqual(r["operational_authority"],"HOLD")
    def test_run_id_invalid(self):
        r=observe(0,COMMIT,caller(fixture()))
        self.assertIn("RUN_ID_INVALID",r["reasons"])
    def test_response_byte_hashes_repeat(self):
        one=observe(RUN_ID,COMMIT,caller(fixture()))
        two=observe(RUN_ID,COMMIT,caller(fixture()))
        self.assertEqual(one["api_response_digests"],two["api_response_digests"])

if __name__=="__main__":
    unittest.main()
