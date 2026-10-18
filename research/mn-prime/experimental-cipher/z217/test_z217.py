#!/usr/bin/env python3
"""MN PRIME v16 / Z217 — speculative symbolic cipher test.
Run directly: python3 test_z217.py; requires only Python standard library.
No discovered element, orbital prediction or measured spectroscopy claimed.
"""
import unittest, math
Z=217
NAME='Biunseptium'; SYMBOL='Bus'; COLOR='#11908E'
LINEAGE='C28:1'
SLOT=1; WINDOW=6
EXPECTED_GEOMETRY='BOX'
ASSUMED_NEUTRONS=184
STAGES=('1', '1.1', '1.2', '1.1.1', '1.1.2', '1.2.1', '1.2.2', '2 mothers')
WINDOW_ENDS=(36,73,109,146,183,219,256,292,329,366)
NAMES=('Biunseptium', 'Biunoctium', 'Biunennium', 'Bibinilium', 'Bibiunium', 'Bibibium', 'Bibitrium', 'Bibiquadium')
SYMBOLS=('Bus', 'Buo', 'Bue', 'Bbn', 'Bbu', 'Bbb', 'Bbt', 'Bbq')
COLORS=('#11908E', '#0E6F6F', '#3ACDF6', '#5AD5F7', '#7ADDF9', '#9AE5FA', '#28BDE7', '#37B4DA')
def calc_window(z):
    return next(i for i,upper in enumerate(WINDOW_ENDS,1) if z<=upper)
def get_stage(z):
    return (z-1)//8+1, STAGES[(z-1)%8]
def calc_fissility(z,n):
    return z*z/(50.13*(z+n))
class TestZ217(unittest.TestCase):
    def test_not_observed_element(self): self.assertGreater(Z,118)
    def test_systematic_name(self): self.assertEqual(NAME,NAMES[SLOT-1])
    def test_systematic_symbol(self): self.assertEqual(SYMBOL,SYMBOLS[SLOT-1])
    def test_inherited_color(self): self.assertEqual(COLOR,COLORS[SLOT-1])
    def test_symbolic_temperature(self): self.assertTrue(123<=Z<=244)
    def test_window(self): self.assertEqual(calc_window(Z),WINDOW)
    def test_view(self): self.assertEqual(EXPECTED_GEOMETRY,'TOROID' if WINDOW%2 else 'BOX')
    def test_219_220_boundary(self): self.assertEqual((calc_window(219),calc_window(220)),(6,7))
    def test_maternal_lineage(self): self.assertEqual(LINEAGE,'C28:'+get_stage(Z)[1])
    def test_wave_pass(self): self.assertEqual((Z-1)//27+1,9)
    def test_wave_slot(self): self.assertEqual((Z-1)%27+1,SLOT)
    def test_hypothetical_isotope_accounting(self): self.assertEqual(Z+ASSUMED_NEUTRONS,401)
    def test_z_alpha(self): self.assertAlmostEqual(Z/137.035999084,1.5835255075345849,places=12)
    def test_liquid_drop_fissility(self): self.assertAlmostEqual(calc_fissility(Z,184),2.3424880845960105,places=12)
    def test_global_two_nibble_rule(self): self.assertEqual(208+4+4,8*27)
    def test_lid_reserved(self): self.assertNotEqual(Z,366)
if __name__=='__main__': unittest.main(verbosity=2)
