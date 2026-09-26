namespace Enheduanna42BindV0

def hymnCount : Nat := 42
def decades : Nat := 4
def perDecade : Nat := 10
def closers : Nat := 2

theorem count_distills :
    decades * perDecade + closers = hymnCount := by
  decide

structure HymnNode where
  index : Nat
  deity : String
  place : String
  deriving Repr, DecidableEq

def nodes : List HymnNode := [
  {index := 1, deity := "Enki", place := "Eridug"},
  {index := 2, deity := "Enlil", place := "Nibru"},
  {index := 3, deity := "Ninlil", place := "Nibru"},
  {index := 4, deity := "Nuska", place := "Nibru"},
  {index := 5, deity := "Ninurta", place := "Nibru"},
  {index := 6, deity := "Shu-zi-ana", place := "Ga-gi-mah"},
  {index := 7, deity := "Ninhursaga", place := "Kesh"},
  {index := 8, deity := "Nanna", place := "Urim"},
  {index := 9, deity := "Shulgi", place := "Urim"},
  {index := 10, deity := "Asarluhi", place := "Kuara"},
  {index := 11, deity := "Ningublaga", place := "Ki-abrig"},
  {index := 12, deity := "Nanna", place := "Gaesh"},
  {index := 13, deity := "Utu", place := "Larsam"},
  {index := 14, deity := "Ninazu", place := "Enegir"},
  {index := 15, deity := "Ningishzida", place := "Gishbanda"},
  {index := 16, deity := "Inana", place := "Unug"},
  {index := 17, deity := "Dumuzid", place := "Bad-tibira"},
  {index := 18, deity := "Ninshubur", place := "Akkil"},
  {index := 19, deity := "Ningirim", place := "Murum"},
  {index := 20, deity := "Ningirsu", place := "Lagash"},
  {index := 21, deity := "Bau", place := "Iri-kug"},
  {index := 22, deity := "Nanshe", place := "Sirara"},
  {index := 23, deity := "Ninmarki", place := "Gu-aba"},
  {index := 24, deity := "Dumuzid-abzu", place := "Kinirsha"},
  {index := 25, deity := "Shara", place := "Umma"},
  {index := 26, deity := "Inana", place := "Zabalam"},
  {index := 27, deity := "Ishkur", place := "Karkara"},
  {index := 28, deity := "UNKNOWN", place := "UNKNOWN"},
  {index := 29, deity := "Ninhursaga", place := "Adab"},
  {index := 30, deity := "Ninisina", place := "Isin"},
  {index := 31, deity := "Numushda", place := "Kazallu"},
  {index := 32, deity := "Lugal-Marda", place := "Marda"},
  {index := 33, deity := "Ishtaran", place := "Der"},
  {index := 34, deity := "Ninazu", place := "Eshnunna"},
  {index := 35, deity := "Zababa", place := "Kish"},
  {index := 36, deity := "Nergal", place := "Gudua"},
  {index := 37, deity := "Suen", place := "Urum"},
  {index := 38, deity := "Utu", place := "Zimbir"},
  {index := 39, deity := "Ninhursaga", place := "UNKNOWN"},
  {index := 40, deity := "Inana", place := "Ulmash"},
  {index := 41, deity := "Aba", place := "Agade"},
  {index := 42, deity := "Nisaba", place := "Eresh"}
]

theorem full_bind_has_42 :
    nodes.length = 42 := by
  decide

def closureToken : String := "-+360-+"

theorem closure_exact :
    closureToken = "-+360-+" := by
  rfl

def rootPrime : String :=
  "bind::full::42::4x10+2::-+360-+"

end Enheduanna42BindV0
