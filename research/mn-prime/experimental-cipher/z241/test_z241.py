#!/usr/bin/env python3
"""MN PRIME v19 / Z241 — independent speculative cipher regression audit.
This tests inherited source-registry patterns, NOT physical element discovery.
Run from DavidWise01/oasis checkout: python3 research/mn-prime/experimental-cipher/z241/test_z241.py
"""
from pathlib import Path
import json,math,unittest
Z=241
EXPECTED_NAME="Biquadunium"
EXPECTED_SYMBOL="Bqu"
EXPECTED_HEX="#117594"
EXPECTED_BAND="Oxygen"
EXPECTED_K=1
EXPECTED_LINEAGE="C31:1"
EXPECTED_STITCH=False
FROZEN=Path(__file__).resolve().parents[1]/"batch-z241-z248"/"FROZEN_SLICE.json"
DATA=json.loads(FROZEN.read_text(encoding="utf-8"))
ROWS=DATA["rows"]
ROW=next(item for item in ROWS if item["Z"]==Z)
def wave(z):return (1+(z-1)//27,1+(z-1)%27)
def fissility(z,n):return z*z/(50.13*(z+n))
class CipherAudit(unittest.TestCase):
 def test_eight_rows(self):self.assertEqual(len(ROWS),8)
 def test_contiguous(self):self.assertEqual([x["Z"] for x in ROWS],list(range(241,249)))
 def test_name(self):self.assertEqual(ROW["name"],EXPECTED_NAME)
 def test_symbol(self):self.assertEqual(ROW["symbol"],EXPECTED_SYMBOL)
 def test_hex(self):self.assertEqual(ROW["hex"],EXPECTED_HEX)
 def test_band(self):self.assertEqual(ROW["band"],EXPECTED_BAND)
 def test_kelvin_symbolic(self):self.assertEqual(ROW["K"],EXPECTED_K)
 def test_lineage(self):self.assertEqual(ROW["lineage"],EXPECTED_LINEAGE)
 def test_stitch(self):self.assertEqual(ROW["stitch"],EXPECTED_STITCH)
 def test_window7(self):self.assertEqual(DATA["window"],7)
 def test_active_toroid(self):self.assertEqual(DATA["window_geometry"],"TOROID")
 def test_box_contains_toroid(self):self.assertEqual(DATA["enclosure"],"BOX contains TOROID")
 def test_maternal_cycle(self):self.assertEqual((Z-1)//8+1,31)
 def test_wave_pass(self):self.assertEqual(wave(Z)[0],9)
 def test_wave_slot(self):self.assertEqual(wave(Z)[1],25)
 def test_wave_reset(self):self.assertEqual((wave(243),wave(244)),((9,27),(10,1)))
 def test_middle_stitch_pair(self):self.assertEqual([x["Z"] for x in ROWS if x["stitch"]],[243,244])
 def test_band_reset(self):self.assertEqual((ROWS[3]["band"],ROWS[4]["band"],ROWS[3]["K"],ROWS[4]["K"]),("Oxygen","Nitrogen",1,0))
 def test_six_stitches_and_lid(self):self.assertEqual(DATA["stitch_positions"],[121,122,243,244,365,366]);self.assertEqual(DATA["lid_position"],366)
 def test_hypothetical_nuclear_only(self):self.assertEqual(Z+184,425);self.assertTrue(math.isfinite(fissility(Z,184)));self.assertFalse(DATA["physical_verification"])
if __name__=="__main__":unittest.main(verbosity=2)
