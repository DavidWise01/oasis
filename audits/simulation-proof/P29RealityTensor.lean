/-!
ROOT0 P2.9: 10,000^2 reality tensor, product-injective routing.
Lean 4 source DRAFT: formal compiler not executed in this environment.
This is a symbolic address model, not a claim about physical spacetime.
-/
import Lean
namespace ROOT0P29

def SiloAddress := Fin 10000
abbrev TensorAddress := SiloAddress × SiloAddress

/-- Two 10,000-address silos generate 100,000,000 address pairs. -/
theorem tensor_cardinality : (10000 : Nat) * 10000 = 100000000 := by decide

theorem four_axes : (10 : Nat) * 10 * 10 * 10 = 10000 := by decide

/-- If each silo router is injective, its product is injective. -/
theorem paired_injective
    (outer inner : SiloAddress → SiloAddress)
    (hout : Function.Injective outer)
    (hinner : Function.Injective inner) :
    Function.Injective (fun p : TensorAddress => (outer p.1, inner p.2)) := by
  intro a b hab
  have hleft : outer a.1 = outer b.1 := congrArg Prod.fst hab
  have hright : inner a.2 = inner b.2 := congrArg Prod.snd hab
  cases a with
  | mk ao ai =>
    cases b with
    | mk bo bi =>
      have ho : ao = bo := hout hleft
      have hi : ai = bi := hinner hright
      simp [ho, hi]

/-- If both factors leave the zero address fixed, the paired zero is fixed. -/
theorem pinned_zero
    (outer inner : SiloAddress → SiloAddress)
    (ho : outer 0 = 0)
    (hi : inner 0 = 0) :
    (outer (0 : SiloAddress), inner (0 : SiloAddress)) = (0,0) := by
  simp [ho,hi]
end ROOT0P29
