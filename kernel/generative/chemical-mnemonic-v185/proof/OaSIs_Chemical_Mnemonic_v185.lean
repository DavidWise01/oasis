import Std

/-
OaSIs_Chemical_Mnemonic_v185
==============================

Formalizes the user term "mnemonic" as a chemically persistent/recoverable
trace inside explicitly declared time windows.

This is a discrete symbolic model. It does NOT claim all chemistry follows a
single decay law. Real kinetics depend on compound, environment, assay,
temperature, water, oxygen, microbes, etc.

Father Time   = ordered ring / time-window index.
Mother Nature = reuse / hold / release classification.
Recoverability states:
  STRONG -> MEDIUM -> WEAK -> ZERO
ZERO is absorbing.
-/

namespace OaSIs.ChemicalMnemonicV185

inductive Strength where
  | zero
  | weak
  | medium
  | strong
  deriving DecidableEq, BEq, Repr

def rank : Strength → Nat
  | .zero => 0
  | .weak => 1
  | .medium => 2
  | .strong => 3

def degrade : Strength → Strength
  | .strong => .medium
  | .medium => .weak
  | .weak => .zero
  | .zero => .zero

def walk : Nat → Strength → Strength
  | 0, s => s
  | n + 1, s => walk n (degrade s)

def recoverable : Strength → Bool
  | .zero => false
  | _ => true

inductive Disposition where
  | release
  | hold
  | reuse
  deriving DecidableEq, BEq, Repr

def motherNature : Strength → Disposition
  | .strong => .reuse
  | .medium => .reuse
  | .weak => .hold
  | .zero => .release

structure Ring where
  stage : Nat
  startTick : Nat
  endTick : Nat
  deriving DecidableEq, Repr

def validRing (r : Ring) : Prop :=
  r.startTick ≤ r.endTick

theorem degrade_rank_le (s : Strength) :
    rank (degrade s) ≤ rank s := by
  cases s <;> decide

theorem zero_absorbing :
    degrade .zero = .zero := by
  rfl

theorem walk_zero_absorbing (n : Nat) :
    walk n .zero = .zero := by
  induction n with
  | zero => rfl
  | succ n ih =>
      simpa [walk, degrade] using ih

theorem walk_rank_le (n : Nat) (s : Strength) :
    rank (walk n s) ≤ rank s := by
  induction n generalizing s with
  | zero =>
      simp [walk]
  | succ n ih =>
      exact Nat.le_trans (ih (degrade s)) (degrade_rank_le s)

theorem strong_three_steps_zero :
    walk 3 .strong = .zero := by
  decide

theorem classification_exact :
    motherNature .strong = .reuse ∧
    motherNature .medium = .reuse ∧
    motherNature .weak = .hold ∧
    motherNature .zero = .release := by
  decide

def exampleRings : List Ring :=
  [
    { stage := 0, startTick := 0, endTick := 1 },
    { stage := 1, startTick := 1, endTick := 2 },
    { stage := 2, startTick := 2, endTick := 5 },
    { stage := 3, startTick := 5, endTick := 10 }
  ]

def ringValidB (r : Ring) : Bool :=
  decide (r.startTick ≤ r.endTick)

def allValid : List Ring → Bool
  | [] => true
  | r :: rs => ringValidB r && allValid rs

theorem example_rings_valid :
    allValid exampleRings = true := by
  decide

def lineageTether (n : Nat) (s : Strength) : Strength := walk n s
def decompositionTether (n : Nat) (s : Strength) : Strength := walk n s

theorem tether_alignment (n : Nat) (s : Strength) :
    lineageTether n s = decompositionTether n s := by
  rfl

def modelCheck : Bool :=
  (degrade .strong == .medium) &&
  (degrade .medium == .weak) &&
  (degrade .weak == .zero) &&
  (degrade .zero == .zero) &&
  (motherNature .strong == .reuse) &&
  (motherNature .weak == .hold) &&
  (motherNature .zero == .release) &&
  allValid exampleRings

theorem chemical_mnemonic_v185_pass :
    modelCheck = true := by
  decide

end OaSIs.ChemicalMnemonicV185
