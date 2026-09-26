namespace HEKATE

/-
  isoKernel v08 — Mandel / Engineers mode register
  -----------------------------------------------
  Append-only clarification of:

      one ::m::3::6::0::e::6::

  where:
      m = Mandel
      e = Engineers

  Engineers choose one of six structural roles:

      1 = babysitting
      2 = guarding
      3 = propulsion
      4 = boxy
      5 = mirror  ///\\
      6 = hex     /\\/\\/\\

  The terminal e::6 therefore records Engineers selecting mode 6 (hex)
  in this register. Earlier numeric tokens remain literal unless separately
  defined by the author.
-/

inductive NamedToken where
  | one
  | mandel
  | n3
  | n6
  | n0
  | engineers
  deriving Repr, DecidableEq

def resultRegister : List NamedToken :=
  [.one, .mandel, .n3, .n6, .n0, .engineers, .n6]

inductive EngineerMode where
  | babysitting
  | guarding
  | propulsion
  | boxy
  | mirror
  | hex
  deriving Repr, DecidableEq

def modeNumber : EngineerMode → Nat
  | .babysitting => 1
  | .guarding    => 2
  | .propulsion  => 3
  | .boxy        => 4
  | .mirror      => 5
  | .hex         => 6

def modeGlyph : EngineerMode → String
  | .babysitting => "1"
  | .guarding    => "2"
  | .propulsion  => "3"
  | .boxy        => "4"
  | .mirror      => "///\\"
  | .hex         => "/\\/\\/\\"

def selectedEngineerMode : EngineerMode :=
  .hex

theorem m_is_mandel :
    resultRegister[1]? = some NamedToken.mandel := by
  rfl

theorem e_is_engineers :
    resultRegister[5]? = some NamedToken.engineers := by
  rfl

theorem engineer_mode_table :
    modeNumber .babysitting = 1 ∧
    modeNumber .guarding = 2 ∧
    modeNumber .propulsion = 3 ∧
    modeNumber .boxy = 4 ∧
    modeNumber .mirror = 5 ∧
    modeNumber .hex = 6 := by
  exact ⟨rfl, rfl, rfl, rfl, rfl, rfl⟩

theorem terminal_engineer_selection_is_hex :
    selectedEngineerMode = EngineerMode.hex ∧
    modeNumber selectedEngineerMode = 6 := by
  exact ⟨rfl, rfl⟩

/-
  Canonical register:

    one :: Mandel :: 3 :: 6 :: 0 :: Engineers :: 6 ::

  Engineer selector:

    1 :: babysitting
    2 :: guarding
    3 :: propulsion
    4 :: boxy
    5 :: mirror ///\\
    6 :: hex    /\\/\\/\\

  Current terminal read:

    Engineers :: 6 :: hex /\\/\\/\\
-/

end HEKATE
