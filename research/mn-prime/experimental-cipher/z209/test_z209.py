#!/usr/bin/env python3
"""MN PRIME Z209: standalone symbolic registry / nuclear diagnostic audit.

Run: python3 test_z209.py
PASS concerns deterministic arithmetic and preserved symbolic address values ONLY.
It does not validate the existence of element 209, its electron configuration,
emission spectrum, or a quantum-gravity mechanism.
"""
import math
import unittest

Z = 209
N_ASSUMED = 184
ALPHA_INVERSE = 137.035999084
FISSILITY_DENOM = 50.13  # approximate liquid-drop diagnostic
CIPHER = {
    "name": "Binilennium", "symbol": "Bne",
    "science_status": "UNCONFIRMED PLACEHOLDER",
    "band": "Oxygen", "symbolic_kelvin": 1,
    "color_hex": "#7AF9F2",
    "window": 6, "view": "BOX", "embedded": "TOROID",
    "lineage": "C27:1", "stitch": False, "lid": False,
    "electron_configuration": None, "measured_wavelength_nm": None,
}
def band(z):
    if 1 <= z <= 122: return "Hydrogen"
    if 123 <= z <= 244: return "Oxygen"
    if 245 <= z <= 366: return "Nitrogen"
    raise ValueError("address outside registry")

def window(z):
    # Exact v13 even-ish ten-window address partition.
    ends = (36, 73, 109, 146, 183, 219, 256, 292, 329, 366)
    return next(i for i, end in enumerate(ends, start=1) if z <= end)

def generation_stage(z):
    # Eight-stage symbolic motif: 1 / 1.1 / 1.2 / ... / 2 mothers.
    return ((z-1)//8 + 1, (z-1)%8 + 1)

def fissility(z, n):
    return z*z / (FISSILITY_DENOM*(z+n))

class TestZ209(unittest.TestCase):
    def test_candidate_not_confirmed(self):
        self.assertEqual(CIPHER["science_status"], "UNCONFIRMED PLACEHOLDER")
    def test_name_preserved(self):
        self.assertEqual((CIPHER["name"],CIPHER["symbol"]),("Binilennium","Bne"))
    def test_band(self):
        self.assertEqual(band(Z), CIPHER["band"])
    def test_kelvin_is_symbolic(self):
        self.assertEqual(CIPHER["symbolic_kelvin"], 1)
    def test_color_preserved(self):
        self.assertEqual(CIPHER["color_hex"], "#7AF9F2")
    def test_window(self):
        self.assertEqual(window(Z), CIPHER["window"])
    def test_box_contains_toroid(self):
        self.assertEqual((CIPHER["view"], CIPHER["embedded"]), ("BOX","TOROID"))
    def test_maternal_motif(self):
        self.assertEqual(generation_stage(Z), (27,1))
        self.assertEqual(CIPHER["lineage"], "C27:1")
    def test_wave_phase(self):
        self.assertEqual(((Z-1)//27+1,(Z-1)%27+1),(8,20))
    def test_two_nibble_overhead(self):
        self.assertEqual(208+4+4,216)
        self.assertEqual(216,8*27)
    def test_hypothetical_neutron_arithmetic(self):
        self.assertEqual(Z+N_ASSUMED,393)
    def test_coulomb_diagnostic(self):
        self.assertTrue(math.isclose(Z/ALPHA_INVERSE,1.5251466869803145,abs_tol=1e-12))
    def test_fissility_diagnostic(self):
        self.assertTrue(math.isclose(fissility(Z,N_ASSUMED),2.2171869678276686,abs_tol=1e-12))
    def test_no_fabricated_measurements(self):
        self.assertIsNone(CIPHER["electron_configuration"])
        self.assertIsNone(CIPHER["measured_wavelength_nm"])
    def test_lead_208_not_confused(self):
        self.assertEqual(82+126,208)
        self.assertNotEqual((82,126),(Z,N_ASSUMED))
    def test_no_lid_or_stitch(self):
        self.assertFalse(CIPHER["stitch"] or CIPHER["lid"])
        self.assertEqual((band(366),window(366)),("Nitrogen",10))

if __name__ == "__main__":
    unittest.main(verbosity=2)
