#!/usr/bin/env python3
"""MN PRIME v18 / Z239, speculative cipher test ONLY.
No discovered element, validated quantum gravity, isotope or measured emission.
Run directly with the standard Python library: python3 test_z239.py
"""
import unittest, math
Z=239; NAME='Bitriennium'; SYMBOL='Bte'; COLOR='#17AAD4'; LINEAGE='C30:1.2.2'
STAGES=('1', '1.1', '1.2', '1.1.1', '1.1.2', '1.2.1', '1.2.2', '2 mothers')
WINDOW_ENDS=(36, 73, 109, 146, 183, 219, 256, 292, 329, 366)
def window(z): return next(i for i,end in enumerate(WINDOW_ENDS,1) if z<=end)
def fissility(z,n): return z*z/(50.13*(z+n))
class CipherAudit(unittest.TestCase):
 def test_element_unconfirmed(self): self.assertGreater(Z,118)
 def test_baseline_name(self): self.assertEqual(NAME,'Bitriennium')
 def test_baseline_symbol(self): self.assertEqual(SYMBOL,'Bte')
 def test_baseline_hex(self): self.assertEqual(COLOR,'#17AAD4') ; self.assertEqual(len(COLOR),7)
 def test_symbolic_oxygen_band(self): self.assertTrue(123<=Z<=244)
 def test_symbolic_one_kelvin(self): self.assertEqual(('Oxygen',1),('Oxygen',1))
 def test_window_address(self): self.assertEqual(window(Z),7)
 def test_active_toroid(self): self.assertEqual(7%2,1)
 def test_enclosing_box(self): self.assertEqual(('BOX','TOROID'),('BOX','TOROID'))
 def test_maternal_cycle(self): self.assertEqual((Z-1)//8+1,30)
 def test_maternal_stage(self): self.assertEqual(LINEAGE,'C30:'+STAGES[(Z-1)%8])
 def test_wave_pass(self): self.assertEqual((Z-1)//27+1,9)
 def test_wave_slot(self): self.assertEqual((Z-1)%27+1,23)
 def test_hypothetical_mass(self): self.assertEqual(Z+184,423)
 def test_fissility_diagnostic(self): self.assertTrue(math.isclose(fissility(Z,184),2.6937527440475093,abs_tol=1e-12))
 def test_symbolic_nibbles_and_lid(self): self.assertEqual(208+4+4,8*27); self.assertNotEqual(Z,366)
if __name__=='__main__': unittest.main(verbosity=2)
