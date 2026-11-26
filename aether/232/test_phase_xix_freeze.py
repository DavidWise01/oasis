"""AETHER-232 frozen Phase XIX decision tests. Synthetic and read-only."""
import json
from pathlib import Path
import unittest
from phase_xix_freeze import assess,FALSE_FIELDS,ZERO_FIELDS,FALSE_CONSTRAINTS,TRUE_CONSTRAINTS

PATH=Path(__file__).with_name("decision.json")
def fixture():
 return json.loads(PATH.read_text(encoding="utf-8"))

class PhaseXIXFreezeTests(unittest.TestCase):
 def reject(self,reason,edit):
  d=fixture();edit(d);result=assess(d)
  self.assertEqual(result["verdict"],"REJECT",result)
  self.assertIn(reason,result["reasons"],result)
  self.assertEqual(result["physical_qualification_percent"],0)
  self.assertFalse(result["physical_act_allowed"])
  self.assertEqual(result["operational_authority"],"HOLD")
  self.assertFalse(result["independent_ci_execution_authenticated"])

 def test_frozen_decision_documentary_consistent(self):
  r=assess(fixture())
  self.assertEqual(r["verdict"],"DOCUMENTARY_PHASE_XIX_FREEZE_CONSISTENT",r)
  self.assertEqual(r["documentary_software_progress_percent"],100)
  self.assertEqual(r["authenticated_external_witness_roots"],0)

 def test_round_trip_json(self):
  self.assertEqual(assess(json.loads(json.dumps(fixture()))),
                   assess(fixture()))
 def test_missing_document(self):
  self.assertEqual(assess(None)["verdict"],"REJECT")
 def test_wrong_phase(self):
  self.reject("FREEZE_IDENTITY_INVALID",lambda x:x.update(phase="XVIII"))
 def test_wrong_bound(self):
  self.reject("FREEZE_IDENTITY_INVALID",lambda x:x.update(bound="AETHER-231"))
 def test_wrong_turn(self):
  self.reject("FREEZE_IDENTITY_INVALID",lambda x:x.update(turn=7))
 def test_wrong_plan(self):
  self.reject("FREEZE_IDENTITY_INVALID",lambda x:x.update(planned_turns=9))
 def test_missing_schema(self):
  self.reject("FREEZE_IDENTITY_INVALID",lambda x:x.pop("schema"))
 def test_software_percent_reduced(self):
  self.reject("DOCUMENTARY_CLOSURE_INVALID",lambda x:x.update(documentary_software_progress_percent=87.5))
 def test_software_percent_forged_above_100(self):
  self.reject("DOCUMENTARY_CLOSURE_INVALID",lambda x:x.update(documentary_software_progress_percent=125))
 def test_reopened_phase(self):
  self.reject("DOCUMENTARY_CLOSURE_INVALID",lambda x:x.update(phase_state="OPEN"))
 def test_missing_milestone(self):
  self.reject("BOUND_ANCESTRY_OR_ORDER_INVALID",lambda x:x["completed_bounds"].pop())
 def test_reordered_milestone(self):
  self.reject("BOUND_ANCESTRY_OR_ORDER_INVALID",lambda x:x["completed_bounds"].reverse())
 def test_duplicate_milestone(self):
  self.reject("BOUND_ANCESTRY_OR_ORDER_INVALID",lambda x:x["completed_bounds"].__setitem__(1,"AETHER-225"))
 def test_scope_truncated(self):
  self.reject("DOCUMENTARY_SCOPE_INCOMPLETE",lambda x:x["documentary_scope"].pop())
 def test_scope_reordered(self):
  self.reject("DOCUMENTARY_SCOPE_INCOMPLETE",lambda x:x["documentary_scope"].reverse())
 def test_source_unpublished(self):
  self.reject("SOURCE_PUBLICATION_UNVERIFIED",lambda x:x.update(documentary_implementation_committed=False))
 def test_missing_unresolved_requirement(self):
  self.reject("TEN_UNRESOLVED_REQUIREMENTS_NOT_PRESERVED",lambda x:x["unresolved_fail_closed"].pop())
 def test_duplicated_unresolved_requirement(self):
  self.reject("TEN_UNRESOLVED_REQUIREMENTS_NOT_PRESERVED",lambda x:x["unresolved_fail_closed"].__setitem__(0,x["unresolved_fail_closed"][1]))
 def test_modified_xviii_ancestry(self):
  self.reject("HISTORICAL_PHASE_XVIII_LINK_INVALID",lambda x:x.update(previous_phase_freeze="../223/protocol.json"))
 def test_previous_bound_rewritten(self):
  self.reject("PREVIOUS_BOUND_LINK_INVALID",lambda x:x.update(previous_bound="../230/protocol.json"))
 def test_decision_qualified(self):
  self.reject("DECISION_OR_WATERMARK_INVALID",lambda x:x.update(decision="PHYSICALLY_QUALIFIED"))
 def test_watermark_removed(self):
  self.reject("DECISION_OR_WATERMARK_INVALID",lambda x:x.update(watermark=""))
 def test_operational_act(self):
  self.reject("OPERATIONAL_AUTHORITY_PROMOTED",lambda x:x.update(operational_authority="ACT"))
 def test_deterministic_result(self):
  self.assertEqual(assess(fixture()),assess(fixture()))

# Each asserted execution, external evidence and weakened boundary has its own
# stable regression identity; no unsupported authority can pass this evaluator.
for field in FALSE_FIELDS:
 def make(f):
  def test(self):
   self.reject("UNSUPPORTED_QUALIFICATION_OR_ACT:"+f,
               lambda d:d.update({f:True}))
  return test
 setattr(PhaseXIXFreezeTests,"test_promote_"+field,make(field))
for field in ZERO_FIELDS:
 def make(f):
  def test(self):
   self.reject("UNSUPPORTED_EXTERNAL_OR_PHYSICAL_EVIDENCE:"+f,
               lambda d:d.update({f:1}))
  return test
 setattr(PhaseXIXFreezeTests,"test_fabricate_"+field,make(field))
for field in FALSE_CONSTRAINTS:
 def make(f):
  def test(self):
   self.reject("TRUST_BOUNDARY_WEAKENED:"+f,
               lambda d:d["constraints"].update({f:True}))
  return test
 setattr(PhaseXIXFreezeTests,"test_weaken_"+field,make(field))
for field in TRUE_CONSTRAINTS:
 def make(f):
  def test(self):
   self.reject("REQUIRED_TRUST_BOUNDARY_MISSING:"+f,
               lambda d:d["constraints"].update({f:False}))
  return test
 setattr(PhaseXIXFreezeTests,"test_remove_"+field,make(field))

if __name__=="__main__":
 unittest.main()
