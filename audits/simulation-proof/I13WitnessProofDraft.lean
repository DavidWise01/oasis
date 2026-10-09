/-! I13 witness-only transition model. Formalization DRAFT; NOT Lean-compiled here. -/
inductive Physical where
  | inbound | outbound | vacant | occupied
  deriving DecidableEq, Repr

inductive Orientation where
  | grid3x3 | abc | negAbc
  deriving DecidableEq, Repr

structure Payload where
  slots : Fin 5 → Physical
  axes : Fin 3 → Orientation

structure World where
  payload : Payload
  witnessed : Bool
  ledger : List Bool

def observe (s : World) : World :=
  { s with witnessed := true, ledger := s.ledger ++ [s.witnessed] }

theorem observe_preserves_payload (s : World) :
    (observe s).payload = s.payload := by
  rfl

theorem observe_sets_witness (s : World) :
    (observe s).witnessed = true := by
  rfl

theorem observe_append_only (s : World) :
    ∃ suffix : List Bool, (observe s).ledger = s.ledger ++ suffix := by
  exact ⟨[s.witnessed], rfl⟩

-- Missing: equivalence to frozen code, physical transitions,
-- physics observable equations, discriminatory measurements.
