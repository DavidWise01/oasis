#!/usr/bin/env python3
"""MN PRIME Z212 research audit, v15. Speculative cipher pattern matching ONLY.
No measured emission wavelength, ground-state configuration, isotope, or gravity law.
Run: python3 test_z212.py
"""
import math
import unittest

Z=212
NAME="Biunbium"
SYMBOL="Bub"
COLOR="#37D6D2"
LINEAGE="C27:1.1.1"
NIBBLE=1
NIBBLE_ROLE="transfer overlay"
N=184  # deliberately hypothetical neutron comparison

class MNPrimeAudit(unittest.TestCase):
    def test_provisional_not_discovered(self):
        self.assertTrue(Z > 118)
        self.assertEqual((NAME, SYMBOL), ("Biunbium", "Bub"))
    def test_symbolic_color(self):
        self.assertEqual(COLOR, "#37D6D2")
        self.assertTrue(COLOR.startswith("#") and len(COLOR) == 7)
    def test_symbolic_band_and_window(self):
        self.assertTrue(123 <= Z <= 244)
        self.assertTrue(184 <= Z <= 219)
        self.assertEqual(("Oxygen", 1, "BOX", "TOROID"), ("Oxygen", 1, "BOX", "TOROID"))
    def test_cycle_mother_lineage(self):
        stages = ("1", "1.1", "1.2", "1.1.1", "1.1.2", "1.2.1", "1.2.2", "2 mothers")
        self.assertEqual(LINEAGE, "C27:" + stages[(Z - 209) % 8])
    def test_wave_27_primitive(self):
        self.assertEqual(((Z - 1) // 27 + 1, (Z - 1) % 27 + 1),
                         (8, 23))
    def test_two_nibbles_are_address_overlay(self):
        self.assertEqual((NIBBLE, NIBBLE_ROLE), (1, "transfer overlay"))
        self.assertEqual(208 + 4 + 4, 216)
        self.assertEqual(8 * 27, 216)
    def test_hypothetical_nuclear_arithmetic(self):
        self.assertEqual(Z + N, 396)
        self.assertTrue(math.isfinite(Z / 137.035999084))
        self.assertGreater(Z*Z/(50.13*(Z+N)), 2)
        self.assertNotEqual((Z, N), (82, 126))  # lead-208 is a different object

if __name__ == "__main__":
    unittest.main(verbosity=2)
