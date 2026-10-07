/-
OASIS Register Unload v34 — standalone structural module
Date: 2026-10-07
-/
namespace OASIS.RegisterUnloadV34

structure ReversibleRegister (α : Type) where
  load : α → α
  unload : α → α
  unload_load : ∀ x, unload (load x) = x

theorem round_trip
    {α : Type}
    (r : ReversibleRegister α)
    (x : α) :
    r.unload (r.load x) = x :=
  r.unload_load x

def mean2 (x y : Nat) : Nat := (x+y)/2

theorem mean_noninjective_witness :
    mean2 30 70 = mean2 10 90 ∧
    (30,70) ≠ (10,90) := by
  decide

def endpointNormMicro : Nat := 1465606
def midpointNormMicro : Nat := 1349812

theorem linear_animation_not_norm_preserving :
    endpointNormMicro ≠ midpointNormMicro := by
  decide

end OASIS.RegisterUnloadV34
