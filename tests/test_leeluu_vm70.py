import unittest
from leeluu_vm70 import run, TRACKS, SUBLANES, PHASES
class VM70(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=run()
 def test_three_tracks(self):self.assertEqual(TRACKS,('i','u','u.s.'))
 def test_five_sublanes(self):self.assertEqual(len(SUBLANES),5)
 def test_four_cores(self):self.assertEqual({e[1] for e in self.r['events']},{0,1,2,3})
 def test_120_lanes(self):self.assertEqual(len({e[2] for e in self.r['events']}),120)
 def test_1800_slots(self):self.assertEqual(self.r['explorer_slots'],1800)
 def test_all_glyphs(self):self.assertEqual(len({e[0] for e in self.r['events']}),256)
 def test_3840_observations(self):self.assertEqual(self.r['observations'],3840)
 def test_3840_backtracks(self):self.assertEqual(self.r['backtrack_records'],3840)
 def test_track_distribution(self):
  from collections import Counter
  self.assertEqual(Counter(e[3] for e in self.r['backtracks']),{'i':1280,'u':1280,'u.s.':1280})
 def test_lifecycle(self):self.assertEqual(PHASES,('creation','life','death','recycle','repeat'))
 def test_unknowns(self):self.assertEqual((self.r['known_glyphs'],self.r['unique_character_classes']),(0,0))
 def test_determinism(self):self.assertEqual(run()['sha256'],self.r['sha256'])
 def test_known(self):self.assertEqual(run({'A1':'hook','E1':'hook'})['unique_character_classes'],1)
 def test_invalid(self):
  with self.assertRaises(ValueError):run({'Q1':'oops'})
 def test_no_fourth_backtrack(self):self.assertEqual({b[3] for b in self.r['backtracks']},set(TRACKS))
if __name__=='__main__':unittest.main(verbosity=2)
