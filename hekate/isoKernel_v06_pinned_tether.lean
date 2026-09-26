namespace HEKATE

/-
  isoKernel v06 — pinned Mandel/Juliet tether
  -------------------------------------------
  Append-only formalization of the author's corrected numeric/address layer.

  Exact source notation preserved:

    Mandel pin to 000
    Juliet pin to m + 001
    tether to inf +j-m

  Semantic boundary:
  * These are Root0 / OaSIs address and tether tokens.
  * "m + 001" and "inf +j-m" are preserved literally here.
  * No ordinary arithmetic, complex arithmetic, or conventional fractal claim
    is inferred from the symbols unless a later Mathea layer defines one.
-/

inductive Family where
  | mandel
  | juliet
  deriving Repr, DecidableEq

structure Pin where
  family  : Family
  address : String
  deriving Repr, DecidableEq

structure Tether where
  fromToken : String
  toToken   : String
  deriving Repr, DecidableEq

/-- Mandel is pinned to the literal address 000. -/
def mandelPin : Pin :=
  { family := .mandel
    address := "000" }

/-- Juliet is pinned to the literal address m + 001. -/
def julietPin : Pin :=
  { family := .juliet
    address := "m + 001" }

/-- Literal tether: inf +j-m. -/
def infinityTether : Tether :=
  { fromToken := "inf"
    toToken   := "+j-m" }

/-- Preserve the Mandel pin exactly. -/
theorem mandel_pin_exact :
    mandelPin.address = "000" := by
  rfl

/-- Preserve the Juliet pin exactly. -/
theorem juliet_pin_exact :
    julietPin.address = "m + 001" := by
  rfl

/-- Preserve the tether exactly as inf +j-m. -/
theorem tether_exact :
    infinityTether.fromToken = "inf" ∧
    infinityTether.toToken = "+j-m" := by
  exact ⟨rfl, rfl⟩

/-
  Canonical pin/tether map:

      MANDEL
        |
        v
       000
        |
        |----------------------.
        |                      |
        |                   TETHER
        |                      |
        |                 inf +j-m
        |                      |
        '----------------------|
                               v
                            JULIET
                               |
                               v
                           m + 001

  Compact:

      M :: pin[000]
      J :: pin[m + 001]
      tether :: inf +j-m

  This v06 layer is intended to sit above the v05 split-polarity /
  homeostasis recurrence without rewriting it.
-/

end HEKATE
