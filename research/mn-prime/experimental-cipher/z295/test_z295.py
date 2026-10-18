#!/usr/bin/env python3
"""MN PRIME v25 Z295: speculative cipher regression against frozen source slice.
No atomic discovery, measured spectrum, or verified Diatom quantum mechanism.
"""
import json,unittest
from pathlib import Path
Z=295
P=Path(__file__).resolve().parents[1]/"batch-z289-z296"
D=json.loads((P/"FROZEN_SLICE.json").read_text())
O=json.loads((P/"DIATOM_V431_OVERLAY.json").read_text())
R=next(x for x in D["rows"] if x["Z"]==Z)
W=lambda z:((z-1)//27+1,(z-1)%27+1)
class CipherAudit(unittest.TestCase):
 def test_01_unobserved(self):self.assertFalse(R["observed_element"])
 def test_02_count(self):self.assertEqual(len(D["rows"]),8)
 def test_03_contiguous(self):self.assertEqual([x["Z"] for x in D["rows"]],list(range(289,297)))
 def test_04_name(self):self.assertEqual(R["name"],"Biennpentium")
 def test_05_symbol(self):self.assertEqual(R["symbol"],"Bep")
 def test_06_color(self):self.assertEqual(R["hex"],"#AB7AF9")
 def test_07_band(self):self.assertEqual(R["band"],"Nitrogen")
 def test_08_symbolic_K(self):self.assertEqual(R["K_symbolic"],0)
 def test_09_window(self):self.assertEqual(R["window"],9)
 def test_10_active_view(self):self.assertEqual(R["view"],"TOROID")
 def test_11_parity(self):self.assertEqual(R["view"],"BOX" if R["window"]%2==0 else "TOROID")
 def test_12_enclosure(self):self.assertEqual(R["enclosure"],"BOX contains TOROID")
 def test_13_mother(self):self.assertEqual(R["cycle"],37)
 def test_14_stage(self):self.assertEqual(R["stage"],"1.2.2")
 def test_15_pass11(self):self.assertEqual((R["wave_pass"],W(Z)[0]),(11,11))
 def test_16_slot(self):self.assertEqual((R["wave_slot"],W(Z)[1]),(25,25))
 def test_17_before_boundary(self):self.assertEqual((D["rows"][3]["window"],D["rows"][3]["view"]),(8,"BOX"))
 def test_18_after_boundary(self):self.assertEqual((D["rows"][4]["window"],D["rows"][4]["view"]),(9,"TOROID"))
 def test_19_no_wave_reset(self):self.assertEqual((W(292),W(293)),((11,22),(11,23)))
 def test_20_no_band_reset(self):self.assertEqual((D["rows"][3]["band"],D["rows"][4]["band"]),("Nitrogen","Nitrogen"))
 def test_21_mother_continuity(self):self.assertEqual((D["rows"][3]["cycle"],D["rows"][4]["cycle"]),(37,37))
 def test_22_A_arithmetic(self):self.assertEqual(R["A_arithmetic"],Z+184)
 def test_23_measurements_unknown(self):self.assertIsNone(R["measured_wavelength_nm"]);self.assertIsNone(R["measured_electron_configuration"])
 def test_24_stitches(self):self.assertEqual(D["stitches"],[121,122,243,244,365,366])
 def test_25_lid(self):self.assertEqual(D["lid"],366)
 def test_26_diatom_hash(self):self.assertEqual(D["original_diatom_v431_html_sha256"],O["original_v431_sha256"]);self.assertFalse(O["experimental_validation"])
if __name__=="__main__":unittest.main(verbosity=2)
