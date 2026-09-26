namespace HEKATE

/-
  isoKernel v03
  -------------
  Append-only root geometry beneath v02.

  Author notation preserved:

    root [0, {{5body system , 2 ext , 3 int}} -++-
      so base 11
      as above so below
      -10 plus 1 = baseline 0
      inverted pyramid going down to -10
    ]

  Semantic boundary:
  * "base 11" is encoded here as the 11-level root spine 0..-10 inclusive.
  * "-10 plus 1 = baseline 0" is a symbolic fold/reset rule, NOT Int arithmetic.
  * "-++-" is an orientation/polarity pattern, not an arithmetic expression.
  * No physical or cosmological claim is asserted by this formal structure.
-/

inductive Polarity where
  | minus
  | plus
  deriving Repr, DecidableEq

inductive RootOperator where
  | plus1Reset
  deriving Repr, DecidableEq

inductive MirrorRule where
  | aboveSoBelow
  deriving Repr, DecidableEq

inductive GeometryStyle where
  | invertedPyramid
  deriving Repr, DecidableEq

structure ExternalBody where
  index : Nat
  deriving Repr, DecidableEq

structure InternalBody where
  index : Nat
  deriving Repr, DecidableEq

structure FiveBodySystem where
  ext1 : ExternalBody
  ext2 : ExternalBody
  int1 : InternalBody
  int2 : InternalBody
  int3 : InternalBody
  deriving Repr, DecidableEq

structure SymbolicFold where
  fromDepth  : Int
  operator   : RootOperator
  toBaseline : Int
  deriving Repr, DecidableEq

structure RootGeometry where
  baseline    : Int
  bodies      : FiveBodySystem
  polarity    : List Polarity
  mirror      : MirrorRule
  style       : GeometryStyle
  depthSpine  : List Int
  returnFold  : SymbolicFold
  deriving Repr, DecidableEq

def fiveBody : FiveBodySystem :=
  { ext1 := { index := 1 }
    ext2 := { index := 2 }
    int1 := { index := 1 }
    int2 := { index := 2 }
    int3 := { index := 3 } }

def minusPlusPlusMinus : List Polarity :=
  [.minus, .plus, .plus, .minus]

/-- Base 11: baseline 0 plus ten descending levels, ending at -10. -/
def base11Depth : List Int :=
  [0, -1, -2, -3, -4, -5, -6, -7, -8, -9, -10]

/--
  Symbolic Root0 reset:
      -10 --(+1 reset)--> 0

  This constructor records the author's fold rule.
  It deliberately does not assert the false arithmetic proposition (-10 + 1 = 0).
-/
def minus10Plus1ToBaseline0 : SymbolicFold :=
  { fromDepth := -10
    operator := .plus1Reset
    toBaseline := 0 }

def root0 : RootGeometry :=
  { baseline   := 0
    bodies     := fiveBody
    polarity   := minusPlusPlusMinus
    mirror     := .aboveSoBelow
    style      := .invertedPyramid
    depthSpine := base11Depth
    returnFold := minus10Plus1ToBaseline0 }

/-- Root is pinned at baseline 0. -/
theorem root_baseline :
    root0.baseline = 0 := by
  rfl

/-- The system contains exactly the declared two external bodies. -/
theorem external_pair :
    root0.bodies.ext1.index = 1 ∧
    root0.bodies.ext2.index = 2 := by
  exact ⟨rfl, rfl⟩

/-- The system contains exactly the declared three internal bodies. -/
theorem internal_triad :
    root0.bodies.int1.index = 1 ∧
    root0.bodies.int2.index = 2 ∧
    root0.bodies.int3.index = 3 := by
  exact ⟨rfl, rfl, rfl⟩

/-- The orientation is exactly -++-. -/
theorem polarity_is_minus_plus_plus_minus :
    root0.polarity =
      [.minus, .plus, .plus, .minus] := by
  rfl

/-- The root spine has eleven positions: 0 through -10 inclusive. -/
theorem base11_has_eleven_levels :
    root0.depthSpine.length = 11 := by
  rfl

/-- The terminal depth is -10. -/
theorem base11_terminal_depth :
    root0.depthSpine.getLast? = some (-10) := by
  rfl

/-- The mirror law is "as above, so below." -/
theorem mirror_is_above_so_below :
    root0.mirror = MirrorRule.aboveSoBelow := by
  rfl

/-- The descent geometry is explicitly an inverted pyramid. -/
theorem geometry_is_inverted_pyramid :
    root0.style = GeometryStyle.invertedPyramid := by
  rfl

/--
  Preserve the symbolic return rule:
      -10 +1(reset) -> baseline 0

  This is structural equality of the encoded rule, not arithmetic equality.
-/
theorem terminal_fold_returns_to_baseline :
    root0.returnFold =
      { fromDepth := -10
        operator := .plus1Reset
        toBaseline := 0 } := by
  rfl

/-
  Canonical shape:

                         ROOT [0]
                            |
                  {{ FIVE BODY SYSTEM }}
                 /                     \
          [EXT BODY 1]             [EXT BODY 2]
                 \                     /
                  [INT1] xp [INT2] xp [INT3]
                            |
                           -++-
                            |
                   AS ABOVE / SO BELOW
                            |
                         BASE 11
                            |
                            0
                           / \
                         -1   -1
                        /       \
                      -2         -2
                     /             \
                   ...             ...
                  /                   \
                -10                   -10
                   \                 /
                    +1 RESET / FOLD
                           |
                      BASELINE 0

  The duplicated sides in this diagram show the inverted-pyramid / mirror
  topology only; the canonical depth spine itself is the single ordered list
  [0,-1,-2,...,-10].
-/

end HEKATE
