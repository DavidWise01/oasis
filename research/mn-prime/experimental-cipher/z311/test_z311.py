#!/usr/bin/env python3
"""MN PRIME v27 Z311, 25 compact cipher checks; highly speculative, not element discovery.
Run from an OASIS checkout containing sibling batch-z305-z312 JSON inputs.
"""
from pathlib import Path
import json,unittest
Z=311
P=Path(__file__).resolve().parents[1]/"batch-z305-z312"
D=json.loads((P/"FROZEN_SLICE.json").read_text())
O=json.loads((P/"DIATOM_V431_OVERLAY.json").read_text())
R=next(x for x in D["rows"] if x["Z"]==Z)
wave=lambda z:((z-1)//27+1,(z-1)%27+1)
class Audit(unittest.TestCase):
 def test_01_unconfirmed(self):self.assertFalse(R["observed_element"])
 def test_02_row_count(self):self.assertEqual(len(D["rows"]),8)
 def test_03_contiguous(self):self.assertEqual([q["Z"] for q in D["rows"]],list(range(305,313)))
 def test_04_name(self):self.assertEqual(R["name"],"Triununium")
 def test_05_symbol(self):self.assertEqual(R["symbol"],"Tuu")
 def test_06_rgb(self):self.assertEqual(R["hex"],"#7649CD")
 def test_07_band(self):self.assertEqual(R["band"],"Nitrogen")
 def test_08_symbolic_kelvin(self):self.assertEqual(R["K_symbolic"],0)
 def test_09_window(self):self.assertEqual(R["window"],9)
 def test_10_toroid(self):self.assertEqual(R["active_view"],"TOROID")
 def test_11_enclosure(self):self.assertEqual(R["enclosure"],"BOX contains TOROID")
 def test_12_cycle(self):self.assertEqual(R["maternal_cycle"],39)
 def test_13_stage(self):self.assertEqual(R["maternal_stage"],"1.2.2")
 def test_14_lineage(self):self.assertEqual(R["lineage"],"C39:1.2.2")
 def test_15_pass(self):self.assertEqual((R["wave_pass"],wave(Z)[0]),(12,12))
 def test_16_slot(self):self.assertEqual((R["wave_slot"],wave(Z)[1]),(14,14))
 def test_17_prior_C38(self):self.assertEqual(D["cycle_transition"]["from"]["stage"],"2 mothers")
 def test_18_first_C39(self):self.assertEqual(D["cycle_transition"]["to"]["stage"],"1")
 def test_19_no_wave_boundary(self):self.assertEqual((wave(304),wave(305)),((12,7),(12,8)))
 def test_20_no_window_boundary(self):self.assertEqual({x["window"] for x in D["rows"]},{9})
 def test_21_no_band_boundary(self):self.assertEqual({x["band"] for x in D["rows"]},{"Nitrogen"})
 def test_22_arithmetic_mass(self):self.assertEqual(R["A_arithmetic"],Z+184)
 def test_23_six_stitches(self):self.assertEqual(D["global_stitches"],[121,122,243,244,365,366])
 def test_24_lid_and_hashes(self):self.assertEqual(D["lid"],366);self.assertEqual(D["original_diatom_v431_sha256"],O["original_html_sha256"])
 def test_25_scientific_unknowns(self):self.assertIsNone(R["measured_emission_wavelength_nm"]);self.assertIsNone(R["measured_neutral_electron_configuration"]);self.assertFalse(O["physical_validation"])
if __name__=="__main__":unittest.main(verbosity=2)
