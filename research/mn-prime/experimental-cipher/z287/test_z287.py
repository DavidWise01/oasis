import unittest,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"batch-z281-z288"
D=json.loads((P/"FROZEN_SLICE.json").read_text())
R=D["rows"][6]
class Audit(unittest.TestCase):
 def test_address(self):self.assertEqual(R["Z"],287)
 def test_name(self):self.assertEqual(R["name"],"Bioctseptium")
 def test_symbol(self):self.assertEqual(R["symbol"],"Bos")
 def test_palette(self):self.assertEqual(R["hex"],"#454BCD")
 def test_band(self):self.assertEqual((R["band"],R["K_symbolic"]),("Nitrogen",0))
 def test_geometry(self):self.assertEqual((R["window"],R["active_view"]),(8,"BOX"))
 def test_cycle(self):self.assertEqual(R["lineage"],"C36:1.2.2")
 def test_wave(self):self.assertEqual((R["wave_pass"],R["wave_slot"]),(11,17))
 def test_mass(self):self.assertEqual(R["A_arithmetic"],471)
 def test_unknown(self):self.assertFalse(R["element_observed"])
if __name__=="__main__":unittest.main()
