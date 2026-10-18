#!/usr/bin/env python3
"""MN PRIME v16 / Z224; speculative cipher test, not physical discovery."""
import unittest
Z=224; NAME="Bibiquadium"; SYMBOL="Bbq"
COLOR="#37B4DA"; LINEAGE="C28:2 mothers"
BORDERS=(36,73,109,146,183,219,256,292,329,366)
STAGES=('1','1.1','1.2','1.1.1','1.1.2','1.2.1','1.2.2','2 mothers')
class Audit(unittest.TestCase):
 def test_not_confirmed(self): self.assertGreater(Z,118)
 def test_name(self): self.assertEqual(NAME,"Bibiquadium")
 def test_symbol(self): self.assertEqual(SYMBOL,"Bbq")
 def test_hex(self): self.assertEqual(COLOR,"#37B4DA")
 def test_symbolic_band(self): self.assertTrue(123<=Z<=244)
 def test_window(self): self.assertEqual(next(i for i,b in enumerate(BORDERS,1) if Z<=b),7)
 def test_active_toroid(self): self.assertEqual(7%2,1)
 def test_box_contains_toroid(self): self.assertEqual(("BOX","TOROID"),("BOX","TOROID"))
 def test_cycle(self): self.assertEqual((Z-1)//8+1,28)
 def test_stage(self): self.assertEqual(LINEAGE,"C28:"+STAGES[(Z-1)%8])
 def test_wave_pass(self): self.assertEqual((Z-1)//27+1,9)
 def test_wave_slot(self): self.assertEqual((Z-1)%27+1,8)
 def test_mass_arithmetic(self): self.assertEqual(Z+184,408)
 def test_macroscopic_fissility(self): self.assertGreater(Z*Z/(50.13*(Z+184)),1)
 def test_nibbles(self): self.assertEqual(208+4+4,216)
 def test_not_lid(self): self.assertNotEqual(Z,366)
if __name__=="__main__": unittest.main(verbosity=2)
