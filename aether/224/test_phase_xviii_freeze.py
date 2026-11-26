"""AETHER-224 Phase XVIII freeze adversarial tests. Synthetic, not native Rust."""
import copy
import json
from pathlib import Path
import unittest
from phase_xviii_freeze import (
    assess, ZERO_FIELDS, FALSE_FIELDS, FALSE_CONSTRAINTS,
    TRUE_CONSTRAINTS, EXPECTED_BOUNDS,
)

FREEZE=Path(__file__).with_name("decision.json")

def fixture():
    return json.loads(FREEZE.read_text(encoding="utf-8"))

class PhaseFreezeTests(unittest.TestCase):
    def reject(self, expected, change):
        doc=fixture()
        change(doc)
        result=assess(doc)
        self.assertEqual(result["verdict"],"REJECT", result)
        self.assertIn(expected,result["reasons"])
        self.assertEqual(result["operational_authority"],"HOLD")
        self.assertFalse(result["physical_act_allowed"])
        self.assertFalse(result["may_recover"])
        self.assertEqual(result["physical_qualification_percent"],0)

    def test_original_freeze_documentary_only(self):
        result=assess(fixture())
        self.assertEqual(result["verdict"],"DOCUMENTARY_PHASE_XVIII_FREEZE_CONSISTENT",result)
        self.assertEqual(result["documentary_software_progress_percent"],100)
        self.assertEqual(result["physical_qualification_percent"],0)

    def test_json_roundtrip(self):
        doc=fixture()
        self.assertEqual(assess(json.loads(json.dumps(doc)))["verdict"],
                         "DOCUMENTARY_PHASE_XVIII_FREEZE_CONSISTENT")

    def test_wrong_bound(self):
        self.reject("PHASE_FREEZE_IDENTITY_INVALID",lambda x:x.update(bound="AETHER-223"))
    def test_wrong_phase(self):
        self.reject("PHASE_FREEZE_IDENTITY_INVALID",lambda x:x.update(phase="XVII"))
    def test_wrong_turn(self):
        self.reject("PHASE_FREEZE_IDENTITY_INVALID",lambda x:x.update(turn=7))
    def test_wrong_planned_turns(self):
        self.reject("PHASE_FREEZE_IDENTITY_INVALID",lambda x:x.update(planned_turns=7))
    def test_open_state(self):
        self.reject("DOCUMENTARY_PHASE_CLOSURE_INVALID",lambda x:x.update(phase_state="OPEN"))
    def test_lost_software_percent(self):
        self.reject("DOCUMENTARY_PHASE_CLOSURE_INVALID",lambda x:x.update(documentary_software_progress_percent=87.5))
    def test_dropped_bound(self):
        self.reject("BOUND_ORDER_OR_COMPLETENESS_MISMATCH",lambda x:x["completed_bounds"].pop())
    def test_reordered_bound(self):
        self.reject("BOUND_ORDER_OR_COMPLETENESS_MISMATCH",lambda x:x["completed_bounds"].reverse())
    def test_duplicate_bound(self):
        self.reject("BOUND_ORDER_OR_COMPLETENESS_MISMATCH",lambda x:x["completed_bounds"].__setitem__(1,"AETHER-217"))
    def test_missing_documentary_scope(self):
        self.reject("DOCUMENTARY_SCOPE_MISSING_OR_REORDERED",lambda x:x["documentary_scope"].pop())
    def test_reordered_scope(self):
        self.reject("DOCUMENTARY_SCOPE_MISSING_OR_REORDERED",lambda x:x["documentary_scope"].reverse())
    def test_source_commit_unverified(self):
        self.reject("DOCUMENTARY_SOURCE_COMMIT_UNVERIFIED",lambda x:x.update(documentary_implementation_committed=False))
    def test_missing_unresolved(self):
        self.reject("UNRESOLVED_REQUIREMENTS_NOT_PRESERVED",lambda x:x["unresolved_fail_closed"].pop())
    def test_duplicate_unresolved(self):
        self.reject("UNRESOLVED_REQUIREMENTS_NOT_PRESERVED",lambda x:x["unresolved_fail_closed"].__setitem__(0,x["unresolved_fail_closed"][1]))
    def test_wrong_previous_phase(self):
        self.reject("FROZEN_ANCESTRY_OR_WATERMARK_INVALID",lambda x:x.update(previous_phase_freeze="../215/protocol.json"))
    def test_wrong_previous_bound(self):
        self.reject("FROZEN_ANCESTRY_OR_WATERMARK_INVALID",lambda x:x.update(previous_bound="../222/protocol.json"))
    def test_missing_watermark(self):
        self.reject("FROZEN_ANCESTRY_OR_WATERMARK_INVALID",lambda x:x.update(watermark=""))
    def test_decision_promoted(self):
        self.reject("FREEZE_DECISION_MISMATCH",lambda x:x.update(decision="QUALIFIED"))
    def test_invalid_schema(self):
        self.reject("PHASE_FREEZE_IDENTITY_INVALID",lambda x:x.update(schema="OTHER"))
    def test_missing_constraints(self):
        self.reject("TRUST_BOUNDARY_INVALID:original_physical_evidence_required_for_act",lambda x:x.update(constraints={}))
    def test_self_asserted_independence_is_not_physical(self):
        self.reject("TRUST_BOUNDARY_INVALID:owned_mirrors_are_independent_sources",
                    lambda x:x["constraints"].update(owned_mirrors_are_independent_sources=True))
    def test_missing_original_hardware_requirement(self):
        self.reject("TRUST_BOUNDARY_INVALID:original_physical_evidence_required_for_act",
                    lambda x:x["constraints"].update(original_physical_evidence_required_for_act=False))
    def test_quorum_evidence_not_runtimes(self):
        self.reject("TRUST_BOUNDARY_INVALID:self_attested_native_reports_prove_execution",
                    lambda x:x["constraints"].update(self_attested_native_reports_prove_execution=True))

# Generate distinct tests for every exact zero / no-authority / provenance
# condition; their names and checks remain stable and human-readable.
for field in ZERO_FIELDS:
    def make_zero_test(name):
        def run(self):
            self.reject("UNSUPPORTED_EXTERNAL_OR_PHYSICAL_EVIDENCE:" + name,
                        lambda x:x.update({name:1}))
        return run
    setattr(PhaseFreezeTests,"test_promote_"+field,make_zero_test(field))

for field in FALSE_FIELDS:
    def make_false_test(name):
        def run(self):
            self.reject("UNSUPPORTED_EXECUTION_OR_AUTHORITY_PROMOTION:" + name,
                        lambda x:x.update({name:True}))
        return run
    setattr(PhaseFreezeTests,"test_assert_"+field,make_false_test(field))

for field in FALSE_CONSTRAINTS:
    def make_boundary_test(name):
        def run(self):
            self.reject("TRUST_BOUNDARY_INVALID:" + name,
                        lambda x:x["constraints"].update({name:True}))
        return run
    setattr(PhaseFreezeTests,"test_weaken_"+field,make_boundary_test(field))

for field in TRUE_CONSTRAINTS:
    def make_true_test(name):
        def run(self):
            self.reject("TRUST_BOUNDARY_INVALID:" + name,
                        lambda x:x["constraints"].update({name:False}))
        return run
    setattr(PhaseFreezeTests,"test_remove_"+field,make_true_test(field))

if __name__=="__main__":
    unittest.main()
