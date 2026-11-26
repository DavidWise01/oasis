"""AETHER-233 test live acquisition decision logic with MOCK API bytes.

These tests do not prove real GitHub API transport or runner execution.
"""
import copy
import json
import unittest
from acquire_execution import acquire,sha,SCHEMA

RUN=233001
COMMIT="a"*40
def fixtures():
 run={"id":RUN,"head_sha":COMMIT,"repository":{"full_name":"DavidWise01/oasis"},
      "path":".github/workflows/aether217-rust-qualification.yml",
      "status":"completed","conclusion":"success"}
 jobs={"total_count":1,"jobs":[{"id":901,"run_id":RUN,
      "name":"Native Rust qualification with captured failure diagnostics",
      "status":"completed","conclusion":"success",
      "steps":[{"name":"Checkout","conclusion":"success"},
               {"name":"Native test","conclusion":"success"}]}]}
 artifacts={"total_count":1,"artifacts":[{"id":902,"name":"aether218-rust-qualification",
       "expired":False,"workflow_run":{"id":RUN}}]}
 return {"run":run,"jobs":jobs,"artifacts":artifacts,
         "job_log":b"SYNTHETIC job log, NOT real CI execution\n",
         "hosted_artifact_zip":b"SYNTHETIC hosted ZIP bytes, NOT actual artifact\n"}

def transport(state,missing=None):
 def fetch(path,raw):
  key=("run" if path.endswith("/"+str(RUN)) else
       "jobs" if "/jobs?" in path else
       "artifacts" if "/artifacts?" in path else
       "job_log" if "/actions/jobs/" in path else
       "hosted_artifact_zip" if "/actions/artifacts/" in path else "unknown")
  if key==missing:raise OSError("Synthetic missing API response")
  value=state[key]
  return value if raw else json.dumps(value,sort_keys=True).encode()
 return fetch

class LiveAcquisitionTests(unittest.TestCase):
 def reject(self,code,edit=None,missing=None):
  data=fixtures()
  if edit:edit(data)
  output=acquire(RUN,COMMIT,transport(data,missing))
  self.assertEqual(output["verdict"],"REJECT_OR_UNVERIFIED",output)
  self.assertIn(code,output["reasons"],output)
  self.assertFalse(output["independently_authenticated_execution"])
  self.assertEqual(output["operational_authority"],"HOLD")
  self.assertEqual(output["physical_qualification_percent"],0)

 def test_all_mock_responses_remain_unqualified(self):
  o=acquire(RUN,COMMIT,transport(fixtures()))
  self.assertEqual(o["verdict"],"LIVE_API_BYTES_OBSERVED_UNQUALIFIED",o)
  self.assertEqual(o["schema"],SCHEMA)
  self.assertEqual(o["observed"]["job_log"]["sha256"],sha(fixtures()["job_log"]))
  self.assertFalse(o["independently_authenticated_execution"])
 def test_missing_run(self):
  self.reject("API_READBACK_UNAVAILABLE:run",missing="run")
 def test_missing_jobs(self):
  self.reject("API_READBACK_UNAVAILABLE:jobs",missing="jobs")
 def test_missing_artifact_index(self):
  self.reject("API_READBACK_UNAVAILABLE:artifacts",missing="artifacts")
 def test_missing_job_log(self):
  self.reject("ACTUAL_JOB_LOG_NOT_OBSERVED",missing="job_log")
 def test_missing_hosted_zip(self):
  self.reject("HOSTED_ARCHIVE_BYTES_NOT_OBSERVED",missing="hosted_artifact_zip")
 def test_changed_commit(self):
  self.reject("RUN_SOURCE_SHA_MISMATCH",lambda x:x["run"].update(head_sha="b"*40))
 def test_changed_run_id(self):
  self.reject("RUN_ID_MISMATCH",lambda x:x["run"].update(id=4))
 def test_foreign_repository(self):
  self.reject("REPOSITORY_MISMATCH",lambda x:x["run"]["repository"].update(full_name="foreign/mirror"))
 def test_other_workflow(self):
  self.reject("WORKFLOW_MISMATCH",lambda x:x["run"].update(path="other.yml"))
 def test_running_workflow(self):
  self.reject("RUN_NOT_TERMINAL",lambda x:x["run"].update(status="in_progress"))
 def test_failed_workflow(self):
  self.reject("RUN_NOT_SUCCESS",lambda x:x["run"].update(conclusion="failure"))
 def test_job_run_mismatch(self):
  self.reject("JOB_RUN_ID_MISMATCH",lambda x:x["jobs"]["jobs"][0].update(run_id=3))
 def test_failed_job(self):
  self.reject("QUALIFICATION_JOB_NOT_SUCCESS",lambda x:x["jobs"]["jobs"][0].update(conclusion="failure"))
 def test_step_failure(self):
  self.reject("JOB_STEP_FAILURE",lambda x:x["jobs"]["jobs"][0]["steps"][0].update(conclusion="failure"))
 def test_missing_steps(self):
  self.reject("JOB_STEPS_UNOBSERVED",lambda x:x["jobs"]["jobs"][0].update(steps=[]))
 def test_multiple_qualification_jobs(self):
  self.reject("QUALIFICATION_JOB_NOT_UNIQUE",lambda x:x["jobs"]["jobs"].append(copy.deepcopy(x["jobs"]["jobs"][0])))
 def test_job_pagination_truncated(self):
  self.reject("JOBS_PAGE_INCOMPLETE",lambda x:x["jobs"].update(total_count=200))
 def test_artifact_pagination_truncated(self):
  self.reject("ARTIFACTS_PAGE_INCOMPLETE",lambda x:x["artifacts"].update(total_count=200))
 def test_expired_artifact(self):
  self.reject("QUALIFICATION_ARTIFACT_EXPIRED",lambda x:x["artifacts"]["artifacts"][0].update(expired=True))
 def test_artifact_run_swapped(self):
  self.reject("QUALIFICATION_ARTIFACT_RUN_MISMATCH",lambda x:x["artifacts"]["artifacts"][0]["workflow_run"].update(id=88))
 def test_missing_artifact(self):
  self.reject("QUALIFICATION_ARTIFACT_NOT_UNIQUE",lambda x:x["artifacts"]["artifacts"].clear())
 def test_bad_artifact_id(self):
  self.reject("ARTIFACT_ID_UNPINNED_OR_EXPIRED",lambda x:x["artifacts"]["artifacts"][0].update(id=None))
 def test_bad_job_id(self):
  self.reject("JOB_ID_UNPINNED",lambda x:x["jobs"]["jobs"][0].update(id=None))
 def test_unpinned_source_revision(self):
  d=acquire(RUN,"invalid",transport(fixtures()))
  self.assertIn("SOURCE_COMMIT_NOT_PINNED",d["reasons"])
 def test_run_not_selected(self):
  d=acquire(0,COMMIT,transport(fixtures()))
  self.assertIn("RUN_ID_NOT_PINNED",d["reasons"])
 def test_reproducible_mock_digests(self):
  self.assertEqual(acquire(RUN,COMMIT,transport(fixtures()))["observed"],
                   acquire(RUN,COMMIT,transport(fixtures()))["observed"])

if __name__=="__main__":
 unittest.main()
