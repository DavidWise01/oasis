#!/usr/bin/env python3
"""MN PRIME v21 Z258: 24-case symbolic regression against compact frozen excerpt.
No discovery of an element, physical photon trapping or observed isotope claimed.
Run in full OASIS checkout with Python standard library.
"""
import unittest,json,math
from pathlib import Path
Z=258; DIR=Path(__file__).resolve().parents[1]/"batch-z257-z264"
DATA=json.loads((DIR/"FROZEN_SLICE.json").read_text())
OBS=json.loads((DIR/"DIATOM_V431_OVERLAY.json").read_text())
R=next(r for r in DATA["rows"] if r["Z"]==Z)
class CipherAudit(unittest.TestCase):
 def test_01_unconfirmed(self):self.assertFalse(R["element_observed"])
 def test_02_8_positions(self):self.assertEqual(len(DATA["rows"]),8)
 def test_03_contiguous(self):self.assertEqual([r["Z"] for r in DATA["rows"]],list(range(257,265)))
 def test_04_name(self):self.assertEqual(R["name"],"Bipentoctium")
 def test_05_symbol(self):self.assertEqual(R["symbol"],"Bpo")
 def test_06_hex(self):self.assertEqual(R["hex"],"#5A97F7")
 def test_07_band_nitrogen(self):self.assertEqual(R["band"],"Nitrogen")
 def test_08_symbolic_kelvin(self):self.assertEqual(R["K_symbolic"],0)
 def test_09_window8(self):self.assertEqual(R["window"],8)
 def test_10_active_box(self):self.assertEqual(R["active_view"],"BOX")
 def test_11_enclosure(self):self.assertEqual(R["enclosure"],"BOX contains TOROID")
 def test_12_mother_cycle(self):self.assertEqual(R["maternal_cycle"],33)
 def test_13_stage(self):self.assertEqual(R["maternal_stage"],"1.1")
 def test_14_lineage(self):self.assertEqual(R["lineage"],"C33:1.1")
 def test_15_wave_pass(self):self.assertEqual(R["wave_pass"],10)
 def test_16_wave_slot(self):self.assertEqual(R["wave_slot"],15)
 def test_17_mass_is_arithmetic(self):self.assertEqual(R["A_arithmetic"],Z+184)
 def test_18_lid_reserved(self):self.assertEqual(DATA["lid"],366)
 def test_19_stitches_preserved(self):self.assertEqual(DATA["stitches"],[121,122,243,244,365,366])
 def test_20_boundary(self):self.assertEqual((DATA["window_boundary"]["prior_view"],DATA["window_boundary"]["next_view"]),("TOROID","BOX"))
 def test_21_diatom_fingerprint(self):self.assertEqual(DATA["original_react_v431_sha256"],OBS["original_html_sha256"])
 def test_22_24_not_27(self):self.assertNotEqual(24,27)
 def test_23_no_measured_config(self):self.assertIsNone(R["measured_neutral_electron_configuration"])
 def test_24_no_measured_spectrum(self):self.assertIsNone(R["measured_emission_wavelength_nm"])
if __name__=="__main__":unittest.main(verbosity=2)
