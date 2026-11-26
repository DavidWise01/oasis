"""AETHER-231 synthetic five-gate ensemble tests; NOT independent proof."""
import json
import unittest
from integrated_review import assess,SCHEMA
SHA="a"*40
H="b"*64

def fixture():
 def gate(schema,verdict,**extra):
  return dict(schema=schema,verdict=verdict,operational_authority="HOLD",
              physical_act_allowed=False,physical_qualification_percent=0,**extra)
 return {
  "schema":SCHEMA,"bound":"AETHER-231","phase":"XIX",
  "source_commit":SHA,"run_id":231001,
  "previous_phase_freeze":"../224/decision.json","previous_bound":"../230/protocol.json",
  "operational_authority":"HOLD","physical_act_allowed":False,
  "original_physical_evidence":"UNVERIFIED",
  "assessments":{
   "ci_provenance":gate("AETHER-226/github-run-provenance-v1",
     "DOCUMENTARY_GITHUB_API_METADATA_CONSISTENT",expected_source_sha=SHA,run_id=231001),
   "archive":gate("AETHER-227/archive-inventory-v1",
     "DOCUMENTARY_ARCHIVE_BYTES_CONSISTENT_ONLY",source_commit=SHA),
   "browser_parity":gate("AETHER-228/hosted-browser-parity-v1",
     "DOCUMENTARY_HOSTED_BROWSER_BYTES_MATCH_ONLY",source_commit=SHA,run_id=231001,
     hosted_sha256=H,browser_sha256=H),
   "ancestry":gate("AETHER-229/ancestry-assessment-v1",
     "DOCUMENTARY_DISTINCT_CONTROL_CLAIMS_ONLY",witness_records_received=3,declared_witness_roots=3),
   "challenge":gate("AETHER-230/challenge-assessment-v1",
     "DOCUMENTARY_CHALLENGE_LEDGER_CONSISTENT_ONLY",
     receipt_observed_sha256="c"*64,ledger_observed_sha256="d"*64)
  }
 }

class IntegrationTests(unittest.TestCase):
 def reject(self,code,edit):
  x=fixture();edit(x);r=assess(x)
  self.assertEqual(r["verdict"],"REJECT_OR_UNVERIFIED",r)
  self.assertIn(code,r["reasons"],r)
  self.assertEqual(r["operational_authority"],"HOLD")
  self.assertFalse(r["physical_act_allowed"])
  self.assertFalse(r["independent_ci_execution_authenticated"])
  self.assertEqual(r["physical_qualification_percent"],0)
 def test_coherent_synthetic_bundle_documentary_only(self):
  r=assess(fixture())
  self.assertEqual(r["verdict"],"DOCUMENTARY_ENSEMBLE_CONSISTENT_UNAUTHENTICATED",r)
  self.assertEqual(r["independent_external_custodians_authenticated"],0)
  self.assertFalse(r["external_challenge_consumption_authenticated"])
 def test_missing_all_assessments(self):
  self.reject("REQUIRED_ASSESSMENT_ABSENT:archive",lambda x:x.update(assessments={}))
 def test_missing_ci(self):
  self.reject("REQUIRED_ASSESSMENT_ABSENT:ci_provenance",lambda x:x["assessments"].pop("ci_provenance"))
 def test_missing_archive(self):
  self.reject("REQUIRED_ASSESSMENT_ABSENT:archive",lambda x:x["assessments"].pop("archive"))
 def test_missing_parity(self):
  self.reject("REQUIRED_ASSESSMENT_ABSENT:browser_parity",lambda x:x["assessments"].pop("browser_parity"))
 def test_missing_ancestry(self):
  self.reject("REQUIRED_ASSESSMENT_ABSENT:ancestry",lambda x:x["assessments"].pop("ancestry"))
 def test_missing_challenge(self):
  self.reject("REQUIRED_ASSESSMENT_ABSENT:challenge",lambda x:x["assessments"].pop("challenge"))
 def test_wrong_gate_schema(self):
  self.reject("ASSESSMENT_SCHEMA_CONFLICT:archive",lambda x:x["assessments"]["archive"].update(schema="INVALID"))
 def test_rejected_run(self):
  self.reject("ASSESSMENT_UNQUALIFIED:ci_provenance",lambda x:x["assessments"]["ci_provenance"].update(verdict="REJECT"))
 def test_rejected_archive(self):
  self.reject("ASSESSMENT_UNQUALIFIED:archive",lambda x:x["assessments"]["archive"].update(verdict="REJECT"))
 def test_rejected_challenge(self):
  self.reject("ASSESSMENT_UNQUALIFIED:challenge",lambda x:x["assessments"]["challenge"].update(verdict="REJECT"))
 def test_unpinned_commit(self):
  self.reject("SOURCE_REVISION_UNPINNED",lambda x:x.update(source_commit="NOT_PINNED"))
 def test_unpinned_run(self):
  self.reject("RUN_ID_UNPINNED",lambda x:x.update(run_id=0))
 def test_ci_revision_mismatch(self):
  self.reject("SOURCE_REVISION_CONFLICT:ci_provenance",lambda x:x["assessments"]["ci_provenance"].update(expected_source_sha="f"*40))
 def test_archive_revision_mismatch(self):
  self.reject("SOURCE_REVISION_CONFLICT:archive",lambda x:x["assessments"]["archive"].update(source_commit="f"*40))
 def test_browser_revision_mismatch(self):
  self.reject("SOURCE_REVISION_CONFLICT:browser_parity",lambda x:x["assessments"]["browser_parity"].update(source_commit="f"*40))
 def test_ci_run_mismatch(self):
  self.reject("CI_RUN_ID_CONFLICT",lambda x:x["assessments"]["ci_provenance"].update(run_id=4))
 def test_browser_run_mismatch(self):
  self.reject("BROWSER_PARITY_RUN_ID_CONFLICT",lambda x:x["assessments"]["browser_parity"].update(run_id=4))
 def test_parity_digest_mismatch(self):
  self.reject("HOSTED_BROWSER_DIGEST_PARITY_UNPROVEN",lambda x:x["assessments"]["browser_parity"].update(browser_sha256="e"*64))
 def test_parity_digest_missing(self):
  self.reject("HOSTED_BROWSER_DIGEST_PARITY_UNPROVEN",lambda x:x["assessments"]["browser_parity"].update(hosted_sha256=None))
 def test_two_witnesses_only(self):
  self.reject("THREE_DECLARED_ANCESTRIES_MISSING",lambda x:x["assessments"]["ancestry"].update(witness_records_received=2))
 def test_repeat_witness_root(self):
  self.reject("THREE_DECLARED_ANCESTRIES_MISSING",lambda x:x["assessments"]["ancestry"].update(declared_witness_roots=2))
 def test_receipt_bytes_missing(self):
  self.reject("ORIGINAL_RECEIPT_BYTES_UNOBSERVED",lambda x:x["assessments"]["challenge"].update(receipt_observed_sha256=None))
 def test_ledger_bytes_missing(self):
  self.reject("REPLAY_LEDGER_BYTES_UNOBSERVED",lambda x:x["assessments"]["challenge"].update(ledger_observed_sha256=None))
 def test_gate_claims_act(self):
  self.reject("ASSESSMENT_AUTHORITY_PROMOTION:ancestry",lambda x:x["assessments"]["ancestry"].update(physical_act_allowed=True))
 def test_request_claims_act(self):
  self.reject("REQUESTED_AUTHORITY_PROMOTION",lambda x:x.update(operational_authority="ACT"))
 def test_fake_physical_source(self):
  self.reject("ORIGINAL_HARDWARE_AUTHENTICATION_UNSUPPORTED",lambda x:x.update(original_physical_evidence="VERIFIED"))
 def test_missing_previous_freeze(self):
  self.reject("SEALED_PHASE_XVIII_ANCESTRY_MISSING",lambda x:x.update(previous_phase_freeze=""))
 def test_missing_previous_bound(self):
  self.reject("PRIOR_BOUND_LINK_INVALID",lambda x:x.update(previous_bound=""))
 def test_wrong_integrated_schema(self):
  self.reject("INTEGRATED_REVIEW_SCHEMA_OR_PHASE_INVALID",lambda x:x.update(schema="FORGED"))
 def test_repeat_deterministic(self):
  self.assertEqual(assess(fixture()),assess(fixture()))

if __name__=="__main__":
 unittest.main()
