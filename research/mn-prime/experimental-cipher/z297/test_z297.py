#!/usr/bin/env python3
"""MN PRIME v26 • Z297: speculative 26-case cipher regression, not element discovery.
Reproduction requires sibling batch-z297-z304 compact inputs in OASIS checkout.
"""
import unittest,json
from pathlib import Path
Z=297
P=Path(__file__).resolve().parents[1]/"batch-z297-z304"
D=json.loads((P/"FROZEN_SLICE.json").read_text())
O=json.loads((P/"DIATOM_V431_OVERLAY.json").read_text())
R=next(x for x in D["rows"] if x["Z"]==Z)
wave=lambda z:((z-1)//27+1,(z-1)%27+1)
class CipherAudit(unittest.TestCase):
 def test_01_unobserved(self):self.assertFalse(R["element_observed"])
 def test_02_count(self):self.assertEqual(len(D["rows"]),8)
 def test_03_range(self):self.assertEqual([x["Z"] for x in D["rows"]],list(range(297,305)))
 def test_04_name(self):self.assertEqual(R["name"],"Biennseptium")
 def test_05_symbol(self):self.assertEqual(R["symbol"],"Bes")
 def test_06_palette(self):self.assertEqual(R["hex"],"#712AE7")
 def test_07_band(self):self.assertEqual(R["band"],"Nitrogen")
 def test_08_symbolic_k(self):self.assertEqual(R["K_symbolic"],0)
 def test_09_window(self):self.assertEqual(R["window"],9)
 def test_10_view(self):self.assertEqual(R["active_view"],"TOROID")
 def test_11_enclosure(self):self.assertEqual(R["enclosure"],"BOX contains TOROID")
 def test_12_cycle(self):self.assertEqual(R["maternal_cycle"],38)
 def test_13_stage(self):self.assertEqual(R["maternal_stage"],"1")
 def test_14_lineage(self):self.assertEqual(R["lineage"],"C38:1")
 def test_15_wave_pass(self):self.assertEqual((R["wave_pass"],wave(Z)[0]),(11,11))
 def test_16_wave_slot(self):self.assertEqual((R["wave_slot"],wave(Z)[1]),(27,27))
 def test_17_last_slot(self):self.assertEqual(wave(297),(11,27))
 def test_18_first_slot(self):self.assertEqual(wave(298),(12,1))
 def test_19_no_window_change(self):self.assertEqual((D["rows"][0]["window"],D["rows"][1]["window"]),(9,9))
 def test_20_no_band_change(self):self.assertEqual((D["rows"][0]["band"],D["rows"][1]["band"]),("Nitrogen","Nitrogen"))
 def test_21_no_mother_change(self):self.assertEqual((D["rows"][0]["maternal_cycle"],D["rows"][1]["maternal_cycle"]),(38,38))
 def test_22_hypothetical_mass(self):self.assertEqual(R["A_arithmetic"],Z+184)
 def test_23_six_stitches(self):self.assertEqual(D["six_stitches"],[121,122,243,244,365,366])
 def test_24_lid(self):self.assertEqual(D["lid"],366)
 def test_25_diatom_hash(self):self.assertEqual(D["original_diatom_html_sha256"],O["original_html_sha256"])
 def test_26_no_measured_physics(self):self.assertIsNone(R["measured_electron_configuration"]);self.assertIsNone(R["measured_emission_wavelength_nm"]);self.assertFalse(O["physical_validation"])
if __name__=="__main__":unittest.main(verbosity=2)
