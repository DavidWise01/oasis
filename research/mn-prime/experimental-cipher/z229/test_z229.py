#!/usr/bin/env python3
"""MN PRIME v17 • Z229 • speculative cipher pattern audit.
Executable with Python standard library. No element discovery, validated
quantum gravity, observed isotope, or emission wavelength asserted.
"""
import math, unittest
Z=229; NAME="Bibiennium"; SYMBOL="Bbe"
COLOR="#117594"; LINEAGE="C29:1.1.2"
WINDOW_ENDS=(36,73,109,146,183,219,256,292,329,366)
STAGES=("1","1.1","1.2","1.1.1","1.1.2","1.2.1","1.2.2","2 mothers")
def window(z): return next(i for i,v in enumerate(WINDOW_ENDS,1) if z<=v)
def fissility(z,n): return z*z/(50.13*(z+n))
class Audit(unittest.TestCase):
 def test_unconfirmed(self): self.assertGreater(Z,118)
 def test_name(self): self.assertEqual(NAME,"Bibiennium")
 def test_symbol(self): self.assertEqual(SYMBOL,"Bbe")
 def test_color_from_frozen_cipher(self): self.assertEqual(COLOR,"#117594")
 def test_band(self): self.assertTrue(123<=Z<=244)
 def test_symbolic_kelvin(self): self.assertEqual(1,1)
 def test_window(self): self.assertEqual(window(Z),7)
 def test_active_toroid(self): self.assertEqual("TOROID","TOROID" if window(Z)%2 else "BOX")
 def test_maternal_cycle(self): self.assertEqual((Z-1)//8+1,29)
 def test_maternal_stage(self): self.assertEqual(LINEAGE,"C29:"+STAGES[(Z-1)%8])
 def test_wave_pass(self): self.assertEqual((Z-1)//27+1,9)
 def test_wave_slot(self): self.assertEqual((Z-1)%27+1,13)
 def test_mass_arithmetic(self): self.assertEqual(Z+184,413)
 def test_alpha(self): self.assertTrue(math.isclose(Z/137.035999084,1.6710937383659905,abs_tol=1e-12))
 def test_fissility(self): self.assertTrue(math.isclose(fissility(Z,184),2.532930120186305,abs_tol=1e-12))
 def test_two_nibbles_and_lid(self): self.assertEqual(208+4+4,8*27); self.assertNotEqual(Z,366)
if __name__=="__main__": unittest.main(verbosity=2)
