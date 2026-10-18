#!/usr/bin/env python3
"""Z219 / MN PRIME v16. Speculative pattern cipher, not a discovered element."""
import unittest
Z=219; NAME="Biunennium"; SYMBOL="Bue"
COLOR="#3ACDF6"; LINEAGE="C28:1.2"
WINDOW=6; ACTIVE="BOX"
BORDERS=(36,73,109,146,183,219,256,292,329,366)
STAGES=('1','1.1','1.2','1.1.1','1.1.2','1.2.1','1.2.2','2 mothers')
class Audit(unittest.TestCase):
 def test_unconfirmed(self): self.assertGreater(Z,118)
 def test_name(self): self.assertEqual(NAME,"Biunennium")
 def test_symbol(self): self.assertEqual(SYMBOL,"Bue")
 def test_inherited_color(self): self.assertEqual(COLOR,"#3ACDF6")
 def test_band(self): self.assertTrue(123 <= Z <= 244)
 def test_window(self): self.assertEqual(next(i for i,v in enumerate(BORDERS,1) if Z<=v),WINDOW)
 def test_active_view(self): self.assertEqual(ACTIVE,"BOX" if WINDOW%2==0 else "TOROID")
 def test_window_transition(self): self.assertEqual(next(i for i,v in enumerate(BORDERS,1) if 220<=v),7)
 def test_maternal_cycle(self): self.assertEqual((Z-1)//8+1,28)
 def test_lineage(self): self.assertEqual(LINEAGE,"C28:"+STAGES[(Z-1)%8])
 def test_wave_pass(self): self.assertEqual((Z-1)//27+1,9)
 def test_wave_slot(self): self.assertEqual((Z-1)%27+1,3)
 def test_mass_arithmetic_only(self): self.assertEqual(Z+184,403)
 def test_fissility_diagnostic(self): self.assertGreater(Z*Z/(50.13*(Z+184)),1)
 def test_two_nibbles(self): self.assertEqual(208+4+4,216)
 def test_lid_reserved(self): self.assertNotEqual(Z,366)
if __name__=="__main__": unittest.main(verbosity=2)
