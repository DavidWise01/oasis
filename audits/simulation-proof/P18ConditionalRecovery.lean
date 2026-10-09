/-!
ROOT0 P1.8 — abstract action-tagged recovery and a Boolean pigeonhole.
Contains no physical-world premise, and does not establish that nature is simulated.
Lean 4 target toolchain: leanprover/lean4:v4.33.1.
Machine compilation is pending; do not label these declarations verified yet.
-/
import Lean

namespace ROOT0P18

variable {State Tag : Type}

/-- If the decoder recovers every input from its successor and retained tag,
then the next-state/tag representation is injective. -/
theorem tagged_step_injective
    (step : State → State) (tag : State → Tag)
    (recover : State → Tag → State)
    (h : ∀ s : State, recover (step s) (tag s) = s) :
    Function.Injective (fun s : State => (step s, tag s)) := by
  intro a b hab
  have hdec : recover (step a) (tag a) = recover (step b) (tag b) := by
    exact congrArg (fun p : State × Tag => recover p.1 p.2) hab
  calc
    a = recover (step a) (tag a) := (h a).symm
    _ = recover (step b) (tag b) := hdec
    _ = b := h b

/-- Three possible sources cannot be distinguished by one Boolean bit. -/
theorem three_need_more_than_one_bit (f : Fin 3 → Bool) :
    f 0 = f 1 ∨ f 0 = f 2 ∨ f 1 = f 2 := by
  cases h0 : f 0 <;> cases h1 : f 1 <;> cases h2 : f 2 <;>
    simp [h0, h1, h2]

/-- Two booleans yield at least three distinct code words. -/
def code3 (k : Fin 3) : Bool × Bool :=
  if k.val = 0 then (false, false)
  else if k.val = 1 then (false, true)
  else (true, false)

theorem two_bit_code_three_distinct :
    code3 0 ≠ code3 1 ∧
    code3 0 ≠ code3 2 ∧
    code3 1 ≠ code3 2 := by
  decide

end ROOT0P18