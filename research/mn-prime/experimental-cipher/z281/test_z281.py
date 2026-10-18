#!/usr/bin/env python3
"""MN PRIME v24 C36 Z281 symbolic-pattern audit; physical status unverified."""
import unittest,json
from pathlib import Path
Z=281
P=Path(__file__).resolve().parents[1]/"batch-z281-z288"
R0=json.loads((P/"FROZEN_SLICE.json").read_text())
O=json.loads((P/"DIATOM_V431_OVERLAY.json").read_text())
R=R0["rows"][0]
class Audit(unittest.TestCase):
 def test_01(self):self.assertEqual(R["Z"],Z)
 def test_02(self):self.assertEqual(R["name"],"Bioctunium")
 def test_03(self):self.assertEqual(R["symbol"],"Bou")
 def test_04(self):self.assertEqual(R["hex"],"#3A3EF6")
 def test_05(self):self.assertEqual(R["band"],"Nitrogen")
 def test_06(self):self.assertEqual(R["K_symbolic"],0)
 def test_07(self):self.assertEqual(R["window"],8)
 def test_08(self):self.assertEqual(R["active_view"],"BOX")
 def test_09(self):self.assertEqual(R["enclosure"],"BOX contains TOROID")
 def test_10(self):self.assertEqual(R["maternal_cycle"],36)
 def test_11(self):self.assertEqual(R["lineage"],"C36:1")
 def test_12(self):self.assertEqual(R["wave_pass"],11)
 def test_13(self):self.assertEqual(R["wave_slot"],11)
 def test_14(self):self.assertEqual(R["A_arithmetic"],465)
 def test_15(self):self.assertFalse(R["element_observed"])
 def test_16(self):self.assertIsNone(R["measured_electron_configuration"])
 def test_17(self):self.assertIsNone(R["measured_wavelength_nm"])
 def test_18(self):self.assertEqual(len(R0["rows"]),8)
 def test_19(self):self.assertEqual([x["Z"] for x in R0["rows"]],list(range(281,289)))
 def test_20(self):self.assertEqual({x["wave_pass"] for x in R0["rows"]},{11})
 def test_21(self):self.assertEqual([x["wave_slot"] for x in R0["rows"]],list(range(11,19)))
 def test_22(self):self.assertEqual(R0["global_stitches"],[121,122,243,244,365,366])
 def test_23(self):self.assertEqual(R0["lid"],366)
 def test_24(self):self.assertEqual(R0["source_diatom_html_sha256"],O["original_html_sha256"])
 def test_25(self):self.assertFalse(O["physical_validation"])
if __name__=="__main__":unittest.main(verbosity=2)
