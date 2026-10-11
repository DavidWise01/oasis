import unittest
from leeluu_vm69 import run
class VM69(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=run()
 def test_topology(self):self.assertEqual((self.r["cores"],self.r["lanes"],self.r["sublanes"],self.r["explorers"]),(4,120,600,1800))
 def test_coverage(self):self.assertEqual((self.r["covered_cells"],self.r["assignments"]),(256,256))
 def test_observations(self):self.assertEqual(self.r["observations"],3840)
 def test_lane_load(self):self.assertEqual((self.r["lane_min_load"],self.r["lane_max_load"]),(2,3))
 def test_unknown(self):self.assertEqual((self.r["known_cells"],self.r["repeat_findings"]),(0,0))
 def test_determinism(self):self.assertEqual(run()["trace_sha256"],self.r["trace_sha256"])
 def test_reject_address(self):
  with self.assertRaises(ValueError):run({"Q1":"x"})
 def test_reject_blank(self):
  with self.assertRaises(ValueError):run({"A1":""})
 def test_first_core(self):self.assertEqual({c for _,c,_ in self.r["assignments_trace"][:64]},{0})
 def test_repeat_detected(self):self.assertGreater(run({"A1":"X","A2":"X"})["repeat_findings"],0)
 def test_no_false_repeat(self):self.assertEqual(run({"A1":"X","A2":"Y"})["repeat_findings"],0)
 def test_unequal_vs_extra_evidence(self):self.assertEqual(run({"M8":"α"})["known_cells"],1)
if __name__=="__main__":unittest.main(verbosity=2)
