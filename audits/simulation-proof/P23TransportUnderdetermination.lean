/-!
ROOT0 P2.3 conditional photon transport theorem. Lean 4 DRAFT.
The 2^3 directions are an EXTERNAL physical interpretation, not in v92.
-/
import Lean
namespace ROOT0P23
structure TransportState where
  generation : Nat
  phase : Nat
  bits : Fin 8
  x : Int
  y : Int
  z : Int
  deriving Repr, DecidableEq

def clockStep (g q : Nat) : Nat × Nat :=
  if q = 11 then (g+1,0) else (g,q+1)
def project (s : TransportState) : Nat × Nat := (s.generation,s.phase)
def dx (b : Fin 8) : Int := if b.val % 2 = 0 then 1 else -1
def dy (b : Fin 8) : Int := if (b.val / 2) % 2 = 0 then 1 else -1
def dz (b : Fin 8) : Int := if (b.val / 4) % 2 = 0 then 1 else -1
def step (policy : Fin 8 → Fin 8) (s : TransportState) : TransportState :=
  let c := clockStep s.generation s.phase
  { generation := c.1, phase := c.2,
    bits := policy s.bits, x := s.x + dx s.bits,
    y := s.y + dy s.bits, z := s.z + dz s.bits }

theorem projection_compatible (policy : Fin 8 → Fin 8) (s : TransportState) :
    project (step policy s) = clockStep s.generation s.phase := by
  rfl
def straight (b : Fin 8) : Fin 8 := b
def rotate (b : Fin 8) : Fin 8 :=
  ⟨(b.val + 1) % 8, Nat.mod_lt _ (by decide)⟩
theorem both_policies_have_identical_logical_successor (s : TransportState) :
    project (step straight s) = project (step rotate s) := by
  rw [projection_compatible, projection_compatible]

def origin : TransportState :=
  { generation := 0, phase := 0, bits := ⟨0, by decide⟩,
    x := 0, y := 0, z := 0 }
theorem distinct_internal_next_state :
    (step straight origin).bits ≠ (step rotate origin).bits := by
  decide

def sumEight (f : Fin 8 → Int) : Int :=
  f 0 + f 1 + f 2 + f 3 + f 4 + f 5 + f 6 + f 7
theorem eight_corner_steps_cancel :
    sumEight dx = 0 ∧ sumEight dy = 0 ∧ sumEight dz = 0 := by
  decide
theorem eight_corner_set_not_all_orientations :
    ¬∃ b : Fin 8, dx b = 0 := by
  decide
end ROOT0P23
