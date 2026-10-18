#!/usr/bin/env python3
"""MN PRIME v21 Z260: 24-case symbolic pattern matching.
No physical element synthesis, electron measurement, or photon trap proof.
"""
import unittest,json
from pathlib import Path
Z=260; DIR=Path(__file__).resolve().parents[1]/"batch-z257-z264"
D=json.loads((DIR/"FROZEN_SLICE.json").read_text())
O=json.loads((DIR/"DIATOM_V431_OVERLAY.json").read_text())
R=next(r for r in D["rows"] if r["Z"]==Z)
class Audit(unittest.TestCase):
 def test_01_unconfirmed(self):self.assertFalse(R["element_observed"])
 def test_02_eight(self):self.assertEqual(len(D["rows"]),8)
 def test_03_consecutive(self):self.assertEqual([a["Z"] for a in D["rows"]],list(range(257,265)))
 def test_04_name(self):self.assertEqual(R["name"],"Bihexnilium")
 def test_05_symbol(self):self.assertEqual(R["symbol"],"Bhn")
 def test_06_color(self):self.assertEqual(R["hex"],"#9ABFFA")
 def test_07_band(self):self.assertEqual(R["band"],"Nitrogen")
 def test_08_K(self):self.assertEqual(R["K_symbolic"],0)
 def test_09_window(self):self.assertEqual(R["window"],8)
 def test_10_active(self):self.assertEqual(R["active_view"],"BOX")
 def test_11_enclosure(self):self.assertEqual(R["enclosure"],"BOX contains TOROID")
 def test_12_cycle(self):self.assertEqual(R["maternal_cycle"],33)
 def test_13_stage(self):self.assertEqual(R["maternal_stage"],"1.1.1")
 def test_14_lineage(self):self.assertEqual(R["lineage"],"C33:1.1.1")
 def test_15_wavepass(self):self.assertEqual(R["wave_pass"],10)
 def test_16_waveslot(self):self.assertEqual(R["wave_slot"],17)
 def test_17_assumedN(self):self.assertEqual(R["assumed_N"],184)
 def test_18_arithmeticA(self):self.assertEqual(R["A_arithmetic"],444)
 def test_19_lid(self):self.assertEqual(D["lid"],366)
 def test_20_stitches(self):self.assertEqual(D["stitches"],[121,122,243,244,365,366])
 def test_21_boundary(self):self.assertEqual(D["window_boundary"]["prior_view"],"TOROID");self.assertEqual(D["window_boundary"]["next_view"],"BOX")
 def test_22_diatom_hash(self):self.assertEqual(D["original_react_v431_sha256"],O["original_html_sha256"])
 def test_23_electron_unknown(self):self.assertIsNone(R["measured_neutral_electron_configuration"])
 def test_24_wavelength_unknown(self):self.assertIsNone(R["measured_emission_wavelength_nm"])
if __name__=="__main__":unittest.main(verbosity=2)
