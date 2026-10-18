import unittest,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"batch-z281-z288"
D=json.loads((P/"FROZEN_SLICE.json").read_text())
R=D["rows"][7]
class Audit(unittest.TestCase):
 def test_address(self):self.assertEqual(R["Z"],288)
 def test_name(self):self.assertEqual(R["name"],"Bioctoctium")
 def test_symbol(self):self.assertEqual(R["symbol"],"Boo")
 def test_palette(self):self.assertEqual(R["hex"],"#545AC0")
 def test_band(self):self.assertEqual((R["band"],R["K_symbolic"]),("Nitrogen",0))
 def test_geometry(self):self.assertEqual((R["window"],R["active_view"]),(8,"BOX"))
 def test_cycle(self):self.assertEqual(R["lineage"],"C36:2 mothers")
 def test_wave(self):self.assertEqual((R["wave_pass"],R["wave_slot"]),(11,18))
 def test_mass(self):self.assertEqual(R["A_arithmetic"],472)
 def test_unknown(self):self.assertFalse(R["element_observed"])
if __name__=="__main__":unittest.main()
