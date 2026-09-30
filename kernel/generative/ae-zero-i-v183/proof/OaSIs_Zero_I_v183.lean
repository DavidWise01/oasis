import Std

namespace OaSIs.V183

/-
Canonical symbolic root:

  {{0::{i::}}}

The equalities below are model-local information-state transforms,
not ordinary integer arithmetic.
-/

inductive Ternary where
  | neg
  | zero
  | pos
deriving Repr, DecidableEq

inductive Image where
  | zero
  | negOne
  | zeroAndOne
deriving Repr, DecidableEq

def i : Ternary → Image
  | .neg  => .zero
  | .zero => .negOne
  | .pos  => .zeroAndOne

def iInv : Image → Ternary
  | .zero       => .neg
  | .negOne     => .zero
  | .zeroAndOne => .pos

structure RootTransform where
  referent : Nat
  transform : Ternary → Image

def root : RootTransform :=
  { referent := 0
    transform := i }

theorem root_referent : root.referent = 0 := rfl
theorem root_transform : root.transform = i := rfl

theorem neg_maps_zero : i .neg = .zero := rfl
theorem zero_maps_neg : i .zero = .negOne := rfl
theorem pos_maps_zeroAndOne : i .pos = .zeroAndOne := rfl

theorem iInv_i (x : Ternary) : iInv (i x) = x := by
  cases x <;> rfl

theorem i_iInv (y : Image) : i (iInv y) = y := by
  cases y <;> rfl

theorem i_leftInverse : Function.LeftInverse iInv i := by
  intro x
  exact iInv_i x

theorem i_rightInverse : Function.RightInverse iInv i := by
  intro y
  exact i_iInv y

theorem i_injective : Function.Injective i :=
  i_leftInverse.injective

theorem i_surjective : Function.Surjective i := by
  intro y
  exact ⟨iInv y, i_iInv y⟩

theorem i_bijective : Function.Bijective i :=
  ⟨i_injective, i_surjective⟩

theorem canon :
    root.referent = 0 ∧
    root.transform .neg = .zero ∧
    root.transform .zero = .negOne ∧
    root.transform .pos = .zeroAndOne := by
  decide

end OaSIs.V183
