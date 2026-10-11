import unittest
from leeluu_vm68 import run
class VM68(unittest.TestCase):
 def test_all_cells(self):self.assertEqual(len({e["address"] for e in run()["events"]}),256)
 def test_four_cores(self):self.assertEqual({e["core"] for e in run()["events"]},{0,1,2,3})
 def test_unknown(self):self.assertEqual((run()["known"],run()["unknown"]),(0,256))
 def test_first_cycle(self):self.assertEqual([e["address"] for e in run(ticks=1)["events"]],["A1","E1","I1","M1"])
 def test_repeat_character(self):self.assertEqual([e["character"] for e in run({"A1":"hook","E1":"hook","I1":"loop"},1)["events"]],["χ001","χ001","χ002","."])
 def test_glyph_not_code(self):self.assertEqual(run({"A1":"eval(0)"},1)["events"][0]["instruction"],"READ")
 def test_reproducible(self):self.assertEqual(run()["trace_sha256"],run()["trace_sha256"])
 def test_reject_unknown_address(self):
  with self.assertRaises(ValueError):run({"Q1":"x"})
 def test_limit(self):
  with self.assertRaises(ValueError):run(ticks=65)
 def test_partial(self):self.assertEqual(run(ticks=2)["processed"],8)
if __name__=="__main__":unittest.main(verbosity=2)
