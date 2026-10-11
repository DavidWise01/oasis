import unittest
from leeluu_i67 import grid,ipass
class TestI(unittest.TestCase):
 def test_grid(self):self.assertEqual(len(grid()),256)
 def test_unknown(self):
  x=ipass(grid());self.assertEqual((x["resolved"],x["unresolved"],x["candidate_pairs"],x["resolved_pairs"]),(0,256,480,0))
 def test_one(self):
  g=grid();g["C8"]="hook";x=ipass(g);self.assertEqual((x["resolved"],x["distinct_characters"]),(1,1))
 def test_repeat(self):
  g=grid();g["C8"]=g["C9"]="hook";x=ipass(g);self.assertEqual((x["distinct_characters"],x["resolved_pairs"]),(1,1))
 def test_distinct(self):
  g=grid();g["C8"]="hook";g["C9"]="loop";x=ipass(g);self.assertEqual((x["distinct_characters"],x["resolved_pairs"]),(2,1))
 def test_invalid(self):
  g=grid();g["Q1"]="x"
  with self.assertRaises(AssertionError):ipass(g)
if __name__=="__main__":unittest.main(verbosity=2)
