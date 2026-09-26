namespace NewWorldOrderV0

/-
  NEW_WORLD_ORDER v0
  ------------------
  Frozen comparison protocol.

  This Lean file formalizes only the STATUS / STOP discipline.
  It does not mechanically prove the scientific claims in the companion
  Markdown file; those claims remain grounded in external experimental
  and observational sources.
-/

inductive Status where
  | supported
  | analogy
  | modelOnly
  | unresolved
  | conflict
  deriving Repr, DecidableEq

def mayPromote : Status -> Bool
  | .supported => true
  | .analogy => false
  | .modelOnly => false
  | .unresolved => false
  | .conflict => false

def mustStop : Status -> Bool
  | .unresolved => true
  | .conflict => true
  | _ => false

theorem unresolved_stops :
    mustStop .unresolved = true := by
  rfl

theorem conflict_stops :
    mustStop .conflict = true := by
  rfl

theorem model_only_not_promoted :
    mayPromote .modelOnly = false := by
  rfl

theorem only_supported_promotes :
    mayPromote .supported = true := by
  rfl

def frozenVersion : String := "new_world_order_v0"

def freezeRule : String :=
  "append-only; no silent reconciliation; stop on unresolved"

theorem frozen_version_exact :
    frozenVersion = "new_world_order_v0" := by
  rfl

end NewWorldOrderV0