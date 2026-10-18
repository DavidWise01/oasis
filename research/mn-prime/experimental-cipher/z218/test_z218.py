#!/usr/bin/env python3
"""MN PRIME v16 Z218 16-test corrected audit. Supersedes the first 8-test draft
via explicit GitHub history; speculative cipher pattern-matching only.
No physical element discovered and no nuclear or spectral measurement claimed.
"""
import unittest
Z=218
NAME="Biunoctium"; SYMBOL="Buo"; COLOR="#0E6F6F"; LINEAGE="C28:1.1"
BORDERS=(36,73,109,146,183,219,256,292,329,366)
STAGES=("1","1.1","1.2","1.1.1","1.1.2","1.2.1","1.2.2","2 mothers")
class Audit(unittest.TestCase):
 def test_unconfirmed(self): self.assertGreater(Z,118)
 def test_provisional_name(self): self.assertEqual(NAME,"Biunoctium")
 def test_provisional_symbol(self): self.assertEqual(SYMBOL,"Buo")
 def test_inherited_color(self): self.assertEqual(COLOR,"#0E6F6F")
 def test_symbolic_oxygen_band(self): self.assertTrue(123<=Z<=244)
 def test_sixth_window(self): self.assertEqual(next(i for i,b in enumerate(BORDERS,1) if Z<=b),6)
 def test_highlighted_box(self): self.assertEqual(6%2,0)
 def test_window_boundary(self): self.assertEqual(next(i for i,b in enumerate(BORDERS,1) if 220<=b),7)
 def test_maternal_cycle(self): self.assertEqual((Z-1)//8+1,28)
 def test_maternal_stage(self): self.assertEqual(LINEAGE,"C28:"+STAGES[(Z-1)%8])
 def test_wave_pass(self): self.assertEqual((Z-1)//27+1,9)
 def test_wave_slot(self): self.assertEqual((Z-1)%27+1,2)
 def test_assumed_n_arithmetic(self): self.assertEqual(Z+184,402)
 def test_fissility_diagnostic(self): self.assertGreater(Z*Z/(50.13*(Z+184)),1)
 def test_two_nibble_conservation(self): self.assertEqual(208+4+4,8*27)
 def test_final_lid_separate(self): self.assertNotEqual(Z,366)
if __name__=="__main__": unittest.main(verbosity=2)
