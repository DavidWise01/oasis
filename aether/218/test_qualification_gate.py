"""AETHER-218 synthetic gate tests; do not substitute for Cargo execution."""
import unittest
from qualification_gate import CHECKS, EXPECTED_SOURCE, classify

class FailClosedGateTests(unittest.TestCase):
    def good_commands(self):
        return {name: {"executed": True, "returncode": 0} for name, _ in CHECKS}

    def good_report(self):
        return {
            "source_freeze": EXPECTED_SOURCE,
            "documentary_decision_consistent": True,
            "physical_qualification_percent": 0,
            "operational_authority": "HOLD",
            "physical_act_allowed": False,
            "may_recover": False,
            "may_repair": False,
            "may_reclaim_lock": False,
            "may_choose_history": False,
        }

    def test_absent_native_results_are_not_pass(self):
        d=classify({},None)
        self.assertFalse(d["native_qualification_passed"])

    def test_one_missing_result_is_not_pass(self):
        commands=self.good_commands()
        commands.pop("cargo_test")
        self.assertFalse(classify(commands,self.good_report())["native_qualification_passed"])

    def test_one_command_fails_gate(self):
        commands=self.good_commands()
        commands["cargo_check"]["returncode"]=101
        self.assertIn("NATIVE_COMMAND_FAILED:cargo_check",classify(commands,self.good_report())["reasons"])

    def test_stated_not_executed_does_not_pass(self):
        commands=self.good_commands()
        commands["cargo_test"]["executed"]=False
        self.assertFalse(classify(commands,self.good_report())["native_qualification_passed"])

    def test_missing_json_fails(self):
        self.assertFalse(classify(self.good_commands(),None)["native_qualification_passed"])

    def test_wrong_source_freeze_fails(self):
        report=self.good_report()
        report["source_freeze"]="AETHER-215"
        self.assertFalse(classify(self.good_commands(),report)["native_qualification_passed"])

    def test_documentary_reject_fails(self):
        report=self.good_report()
        report["documentary_decision_consistent"]=False
        self.assertFalse(classify(self.good_commands(),report)["native_qualification_passed"])

    def test_physical_act_claim_fails(self):
        report=self.good_report()
        report["physical_act_allowed"]=True
        self.assertFalse(classify(self.good_commands(),report)["native_qualification_passed"])

    def test_physical_qualification_claim_fails(self):
        report=self.good_report()
        report["physical_qualification_percent"]=1
        self.assertFalse(classify(self.good_commands(),report)["native_qualification_passed"])

    def test_recovery_promotion_fails(self):
        report=self.good_report()
        report["may_recover"]=True
        self.assertFalse(classify(self.good_commands(),report)["native_qualification_passed"])

    def test_all_observed_synthetic_results_classify_pass(self):
        # Pure function fixture, not a claim that Cargo actually ran.
        d=classify(self.good_commands(),self.good_report())
        self.assertTrue(d["native_qualification_passed"])
        self.assertEqual(d["operational_authority"],"HOLD")
        self.assertEqual(d["physical_qualification_percent"],0)

if __name__=="__main__":
    unittest.main()
