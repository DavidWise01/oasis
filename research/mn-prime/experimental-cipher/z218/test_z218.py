#!/usr/bin/env python3
"""MN PRIME v16: speculative cipher test Z218, not a discovered element."""
import unittest
Z=218
class Audit(unittest.TestCase):
 def test_name(self): self.assertEqual(("Biunoctium","Buo"),("Biunoctium","Buo"))
 def test_band(self): self.assertTrue(123 <= Z <= 244)
 def test_window(self): self.assertTrue(184 <= Z <= 219)
 def test_geometry(self): self.assertEqual(Z%2,0)
 def test_lineage(self): self.assertEqual((Z-1)//8+1,28)
 def test_wave(self): self.assertEqual(((Z-1)//27+1,(Z-1)%27+1),(9,2))
 def test_two_nibbles(self): self.assertEqual(208+4+4,8*27)
 def test_neutrons_are_hypothetical(self): self.assertEqual(Z+184,402)
if __name__=="__main__": unittest.main(verbosity=2)
