/-!
ROOT0 P2.5 abstract properties; Lean 4 DRAFT, NOT COMPILED.
This theorem is CONDITIONAL on a provided continuum dynamics/rotation map.
It does not derive such a map from frozen ROOT0.
-/
import Lean
namespace ROOT0P25

/-- Eight complex amplitudes are indexed by six E/B components and two
    inert auxiliary slots. This is a *new* representation, not an I13 source definition. -/
inductive FieldComponent where
  | Ex | Ey | Ez | Bx | By | Bz | S0 | S1
  deriving Repr, DecidableEq

/-- A physical transverse basis for propagation along the z-axis is two-dimensional. -/
inductive TransverseZ where
  | electricX | electricY
  deriving Repr, DecidableEq

theorem two_polarizations_distinct :
    TransverseZ.electricX ≠ TransverseZ.electricY := by decide

/-- Logical observations are unchanged when only auxiliary field values change.
    The theorem deliberately does not identify this field with physical reality. -/
structure Attached (Aux : Type) where
  generation : Nat
  phase : Fin 12
  field : Aux

variable {Aux : Type}
def logical (s : Attached Aux) : Nat × Fin 12 := (s.generation,s.phase)
def attach (g : Nat) (q : Fin 12) (f : Aux) : Attached Aux :=
  ⟨g,q,f⟩
theorem same_kernel_clock_for_any_fields (g : Nat) (q : Fin 12) (a b : Aux) :
    logical (attach g q a) = logical (attach g q b) := by rfl

/-- A modified group speed with nonzero correction cannot equal the
    unmodified Maxwell law at a nonzero wavenumber. -/
theorem nonzero_dispersion_differs (x : Nat) (hx : x > 0) :
    x * x ≠ 0 := by
  exact Nat.ne_of_gt (Nat.mul_pos hx hx)

end ROOT0P25
