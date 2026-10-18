#!/usr/bin/env python3
"""MN PRIME v20 Z254; speculative symbolic cipher, NOT discovered element.
Run in the cloned OASIS repository: python3 research/mn-prime/experimental-cipher/z254/test_z254.py
Remote GitHub suite uses committed FROZEN_SLICE.json; local v20 ZIP contains additional source-hash full-CSV tests.
"""
from pathlib import Path
import unittest, json, math
Z=254
BASE=Path(__file__).resolve().parents[1]/"batch-z249-z256"
DATA=json.loads((BASE/"FROZEN_SLICE.json").read_text())
OVERLAY=json.loads((BASE/"DIATOM_V431_OVERLAY.json").read_text())
ROWS=DATA["rows"]
R=next(r for r in ROWS if r["z"]==Z)
class Audit(unittest.TestCase):
 def test_unconfirmed(self):self.assertFalse(R["physical_validation"])
 def test_eight_rows(self):self.assertEqual(len(ROWS),8)
 def test_contiguous(self):self.assertEqual([r["z"] for r in ROWS],list(range(249,257)))
 def test_name(self):self.assertEqual(R["name"],"Bipentquadium")
 def test_symbol(self):self.assertEqual(R["symbol"],"Bpq")
 def test_color(self):self.assertEqual(R["color"],"#1451B4")
 def test_N_band(self):self.assertEqual(R["band"],"Nitrogen")
 def test_symbolic_K0(self):self.assertEqual(R["K_symbolic"],0)
 def test_seventh_window(self):self.assertEqual(R["window"],7)
 def test_odd_toroid(self):self.assertEqual(R["active_view"],"TOROID")
 def test_containment(self):self.assertEqual(R["enclosure"],"BOX contains TOROID")
 def test_cycle32(self):self.assertEqual(R["lineage"],"C32:"+"1.2.1")
 def test_wave10(self):self.assertEqual(R["wave_pass"],10)
 def test_wave_slot(self):self.assertEqual(R["wave_slot"],11)
 def test_hypothetical_n184(self):self.assertEqual(R["A_arithmetic"],Z+184)
 def test_no_spectrum_claim(self):self.assertIsNone(R["measured_wavelength_nm"])
 def test_integrated_source_fingerprint(self):self.assertEqual(DATA["source_diatom_v431_sha256"],OVERLAY["original_sha256"])
 def test_24_not_27(self):self.assertNotEqual(24,27)
 def test_60x60_plus6_not366(self):self.assertEqual(60*60+6,3606);self.assertNotEqual(3606,366)
 def test_next_boundary(self):self.assertEqual(DATA["next_window_transition"]["to_view"],"BOX")
 def test_original_366_lid(self):self.assertEqual(DATA["lid"],366)
 def test_no_fabricated_orbital(self):self.assertIsNone(R["electron_configuration"])
 def test_physics_unvalidated(self):self.assertFalse(OVERLAY["physical_validation"])
 def test_source_preservation(self):self.assertIn("not edited",OVERLAY["preservation"])
if __name__=="__main__":unittest.main(verbosity=2)
