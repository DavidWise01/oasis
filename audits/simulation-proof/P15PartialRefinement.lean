/-!
ROOT0 P1.5 — a typed partial bridge to the original I13 T2 ring.
Lean 4 draft. Not machine-checked in this execution environment.
The algebra describes a subdomain of the frozen 4-state alphabet;
it does NOT declare the full 55,296-state physics simulated.
-/
namespace ROOT0P15

inductive Slot where
  | inbound | outbound | vacant | occupied
  deriving DecidableEq, Repr

inductive Axis where
  | grid3x3 | abc | negAbc
  deriving DecidableEq, Repr

structure FullState where
  slots : Fin 5 → Slot
  axes : Fin 3 → Axis
  witnessed : Bool

/-- The T2 binary occupancy ring is an intentionally PARTIAL subdomain. -/
def binary (s : FullState) : Prop :=
  ∀ i : Fin 5, s.slots i = Slot.vacant ∨ s.slots i = Slot.occupied

/-- Witness marking is read-only with respect to payload and axes. -/
def observe (s : FullState) : FullState := { s with witnessed := true }

/-- This is the move's payload update. The legal-move predicate must be
checked separately: source occupied, destination vacant, adjacency. -/
def updateSlots (s : FullState) (src dst : Fin 5) : FullState :=
  { s with slots := fun k =>
      if k = src then Slot.vacant
      else if k = dst then Slot.occupied
      else s.slots k }

theorem observe_preserves_slots (s : FullState) :
    (observe s).slots = s.slots := by rfl

theorem observe_preserves_axes (s : FullState) :
    (observe s).axes = s.axes := by rfl

theorem update_preserves_axes (s : FullState) (src dst : Fin 5) :
    (updateSlots s src dst).axes = s.axes := by rfl

theorem update_preserves_witness (s : FullState) (src dst : Fin 5) :
    (updateSlots s src dst).witnessed = s.witnessed := by rfl

/-- Commutation only for witness-blind payload updates. -/
theorem update_observe_commutes (s : FullState) (src dst : Fin 5) :
    updateSlots (observe s) src dst = observe (updateSlots s src dst) := by
  cases s
  rfl

/-- The two excluded symbols cannot be certified as legal binary slots. -/
example : Slot.inbound ≠ Slot.vacant := by decide
example : Slot.outbound ≠ Slot.occupied := by decide

end ROOT0P15
