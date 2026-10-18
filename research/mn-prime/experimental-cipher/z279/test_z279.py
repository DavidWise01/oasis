#!/usr/bin/env python3
"""MN PRIME v23 • symbolic Z279 regression, 25 tests.
Requires sibling batch-z273-z280/FROZEN_SLICE.json and DIATOM_V431_OVERLAY.json.
No element discovery, spectroscopy, isotope existence, or quantum-gravity validation.
"""
import unittest,json,math
from pathlib import Path
Z=279
D=Path(__file__).resolve().parents[1]/"batch-z273-z280"
S=json.loads((D/"FROZEN_SLICE.json").read_text())
O=json.loads((D/"DIATOM_V431_OVERLAY.json").read_text())
R=next(x for x in S["rows"] if x["Z"]==Z)
W=lambda z:((z-1)//27+1,(z-1)%27+1)
class TestSymbolicCipher(unittest.TestCase):
 def test_01_unconfirmed(self):self.assertFalse(R["element_observed"])
 def test_02_record_count(self):self.assertEqual(len(S["rows"]),8)
 def test_03_contiguous(self):self.assertEqual([r["Z"] for r in S["rows"]],list(range(273,281)))
 def test_04_name(self):self.assertEqual(R["name"],"Biseptennium")
 def test_05_symbol(self):self.assertEqual(R["symbol"],"Bse")
 def test_06_hex(self):self.assertEqual(R["hex"],"#111494")
 def test_07_nitrogen(self):self.assertEqual(R["band"],"Nitrogen")
 def test_08_zero_K_symbol(self):self.assertEqual(R["K_symbolic"],0)
 def test_09_window(self):self.assertEqual(R["window"],8)
 def test_10_active_box(self):self.assertEqual(R["active_view"],"BOX")
 def test_11_enclosure(self):self.assertEqual(R["enclosure"],"BOX contains TOROID")
 def test_12_c35(self):self.assertEqual((Z-1)//8+1,35)
 def test_13_stage(self):self.assertEqual(R["maternal_stage"],"1.2.2")
 def test_14_lineage(self):self.assertEqual(R["lineage"],"C35:1.2.2")
 def test_15_pass11(self):self.assertEqual(W(Z)[0],11);self.assertEqual(R["wave_pass"],11)
 def test_16_wave_slot(self):self.assertEqual((W(Z)[1],R["wave_slot"]),(9,9))
 def test_17_no_internal_wave_reset(self):self.assertEqual({r["wave_pass"] for r in S["rows"]},{11})
 def test_18_wave_slots_3_to_10(self):self.assertEqual([r["wave_slot"] for r in S["rows"]],list(range(3,11)))
 def test_19_no_band_change(self):self.assertEqual({r["band"] for r in S["rows"]},{"Nitrogen"})
 def test_20_no_window_change(self):self.assertEqual({r["window"] for r in S["rows"]},{8})
 def test_21_arithmetic_mass(self):self.assertEqual(R["A_arithmetic"],Z+184)
 def test_22_parent_csv_hash(self):self.assertEqual(S["original_366_csv_sha256"],O["original_cipher_csv_sha256"])
 def test_23_parent_diatom_hash(self):self.assertEqual(S["diatom_v431_html_sha256"],O["original_react_html_sha256"])
 def test_24_six_stitches_lid(self):self.assertEqual(S["global_stitches"],[121,122,243,244,365,366]);self.assertEqual(S["final_box_lid"],366)
 def test_25_unknown_science(self):self.assertIsNone(R["measured_wavelength_nm"]);self.assertIsNone(R["measured_electron_configuration"]);self.assertFalse(O["physical_validation"])
if __name__=="__main__":unittest.main(verbosity=2)
