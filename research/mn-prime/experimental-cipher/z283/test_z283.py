import unittest,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"batch-z281-z288"
D=json.loads((P/"FROZEN_SLICE.json").read_text())
R=D["rows"][2]
class TestZ283(unittest.TestCase):
 def test_address(self): self.assertEqual(R["Z"],283)
 def test_name(self): self.assertEqual(R["name"],"Biocttrium")
 def test_symbol(self): self.assertEqual(R["symbol"],"Bot")
 def test_palette(self): self.assertEqual(R["hex"],"#7A7CF9")
 def test_band(self): self.assertEqual((R["band"],R["K_symbolic"]),("Nitrogen",0))
 def test_window(self): self.assertEqual((R["window"],R["active_view"]),(8,"BOX"))
 def test_c36(self): self.assertEqual(R["lineage"],"C36:1.2")
 def test_wave(self): self.assertEqual((R["wave_pass"],R["wave_slot"]),(11,13))
 def test_a(self): self.assertEqual(R["A_arithmetic"],467)
 def test_unconfirmed(self): self.assertFalse(R["element_observed"])
if __name__=="__main__":unittest.main()
