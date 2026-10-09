/-!
ROOT0 P3.5 — finite cipher identity and tagged model nonidentifiability.
Lean 4 DRAFT ONLY; not machine-compiled, and not a theorem about photons.
-/
import Lean
namespace ROOT0P35

theorem cipher_size : 16 * 13 = 208 := by decide
theorem cipher_balance : (104 : Nat) + 104 = 208 := by decide
theorem full_inverse_steps : 208 + 208 = 416 := by decide
theorem experimental_reference_count : 44 * 2 = 88 := by decide

/-- Independent optical coupling is not fixed by the discrete cipher. -/
structure OpticalAttachment (Baseline : Type) where
  baseline : Baseline
  cipherCoupling : Int

def isNonzeroCoupling {T : Type} (m : OpticalAttachment T) : Bool :=
  m.cipherCoupling != 0

theorem null_vs_alternative {T : Type} (x : T) :
    isNonzeroCoupling (OpticalAttachment.mk x 0) = false ∧
    isNonzeroCoupling (OpticalAttachment.mk x 2) = true := by
  decide

end ROOT0P35
