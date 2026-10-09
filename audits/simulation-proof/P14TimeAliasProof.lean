/-!
ROOT0 P1.4: minimal mathematics of repeat-cycle witness alias.
Lean 4 DRAFT; no compiler was available during this run.
This does not assert anything about physical simulation.
-/
namespace ROOT0P14

def edgeAtTick (tick : Nat) : Nat × Nat :=
  (tick % 5, (tick + 1) % 5)

theorem repeated_edge : edgeAtTick 0 = edgeAtTick 5 := by
  rfl

theorem v1_receipt_alias (α : Type) (digest : (Nat × Nat) → α) :
    digest (edgeAtTick 0) = digest (edgeAtTick 5) := by
  rw [repeated_edge]

theorem actual_tick_distinct : (0 : Nat) ≠ 5 := by
  decide

def versionedInput (tick : Nat) : Nat × (Nat × Nat) :=
  (tick, edgeAtTick tick)

theorem versioned_input_distinct : versionedInput 0 ≠ versionedInput 5 := by
  decide

end ROOT0P14
