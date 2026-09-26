namespace HEKATE

/-
  isoKernel v04 — isomorphACI axis layer
  ---------------------------------------
  Append-only formalization of the author's next state mapping.

  Exact semantic source:

    isomorphaci
    000  = fat belly Mandel 1 stable
    001  = unstable fat belly Mandel
           can ride axis +g -v from 001
    -000 = fat belly of Juliet set
    -001 = fat belly of Juliet set
           at axis -g +v from -001

  IMPORTANT:
  This is an OaSIs / Root0 symbolic state grammar.
  "Mandel", "Juliet", gravity g, velocity v, and signed addresses are
  model tokens here; this file does not claim these relations are
  conventional properties of the Mandelbrot or Julia sets.
-/

inductive Sign where
  | plus
  | minus
  deriving Repr, DecidableEq

inductive Family where
  | mandel
  | juliet
  deriving Repr, DecidableEq

inductive Stability where
  | stable
  | unstable
  | unspecified
  deriving Repr, DecidableEq

inductive Address where
  | p000
  | p001
  | n000
  | n001
  deriving Repr, DecidableEq

structure Axis where
  g : Sign
  v : Sign
  from : Address
  deriving Repr, DecidableEq

structure FatBellyState where
  address     : Address
  family      : Family
  bellyIndex  : Option Nat
  stability   : Stability
  axis        : Option Axis
  deriving Repr, DecidableEq

/-- 000 = fat belly Mandel 1 stable. -/
def state000 : FatBellyState :=
  { address    := .p000
    family     := .mandel
    bellyIndex := some 1
    stability  := .stable
    axis       := none }

/--
  001 = unstable fat belly Mandel;
  from 001 it can ride +g / -v.
-/
def state001 : FatBellyState :=
  { address    := .p001
    family     := .mandel
    bellyIndex := none
    stability  := .unstable
    axis       := some { g := .plus, v := .minus, from := .p001 } }

/-- -000 = fat belly of Juliet set. -/
def stateNeg000 : FatBellyState :=
  { address    := .n000
    family     := .juliet
    bellyIndex := none
    stability  := .unspecified
    axis       := none }

/--
  -001 = fat belly of Juliet set;
  from -001 its axis is -g / +v.
-/
def stateNeg001 : FatBellyState :=
  { address    := .n001
    family     := .juliet
    bellyIndex := none
    stability  := .unspecified
    axis       := some { g := .minus, v := .plus, from := .n001 } }

/-- Preserve 000 exactly as Mandel / stable / belly 1. -/
theorem state000_exact :
    state000.family = Family.mandel ∧
    state000.bellyIndex = some 1 ∧
    state000.stability = Stability.stable := by
  exact ⟨rfl, rfl, rfl⟩

/-- Preserve 001 exactly as unstable Mandel. -/
theorem state001_is_unstable_mandel :
    state001.family = Family.mandel ∧
    state001.stability = Stability.unstable := by
  exact ⟨rfl, rfl⟩

/-- 001 rides the +g / -v axis from 001. -/
theorem state001_axis :
    state001.axis =
      some { g := Sign.plus, v := Sign.minus, from := Address.p001 } := by
  rfl

/-- Preserve -000 exactly as Juliet-set fat belly. -/
theorem stateNeg000_is_juliet :
    stateNeg000.family = Family.juliet := by
  rfl

/-- Preserve -001 exactly as Juliet-set fat belly. -/
theorem stateNeg001_is_juliet :
    stateNeg001.family = Family.juliet := by
  rfl

/-- -001 rides the -g / +v axis from -001. -/
theorem stateNeg001_axis :
    stateNeg001.axis =
      some { g := Sign.minus, v := Sign.plus, from := Address.n001 } := by
  rfl

/-
  Canonical isomorphACI map:

       MANDEL SIDE                         JULIET SIDE

    000 :: fat belly                  -000 :: fat belly
    Mandel 1 stable                    Juliet set
          |                                 |
          v                                 v
    001 :: fat belly                  -001 :: fat belly
    Mandel unstable                    Juliet set
          |                                 |
       +g / -v                           -g / +v
          |                                 |
      FROM 001                           FROM -001

  Axis inversion:

      001   : +g  -v
      -001  : -g  +v

  No further stability property is assigned to -000 or -001 here,
  because the source statement did not specify one.
-/

end HEKATE
