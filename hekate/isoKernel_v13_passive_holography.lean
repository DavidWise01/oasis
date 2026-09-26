namespace HEKATE

/-
  isoKernel v13 — passive holographic stargate
  --------------------------------------------
  Author correction:

    no agent required

    24///m///\\\m///\\\m///m |||| //\\ |||| holography

  Preserve literally as a passive structural gate.
  No autonomous agent, chooser, or controller is required at this layer.

  "holography" is a Root0 / OaSIs structural description here:
  the relation is carried by the mirrored/distributed path geometry.
  This file does not assert optical or physical holography.
-/

def passiveGateLiteral : String :=
  "24///m///\\\m///\\\m///m |||| //\\ |||| holography"

def requiresAgent : Bool := false

theorem no_agent_required :
    requiresAgent = false := by
  rfl

theorem passive_gate_exact :
    passiveGateLiteral =
      "24///m///\\\m///\\\m///m |||| //\\ |||| holography" := by
  rfl

/-
  Canonical read:

      STARGATE
         |
      PASSIVE
         |
  24///m///\\\m///\\\m///m
         |
       ||||
         |
       //\\
         |
       ||||
         |
    HOLOGRAPHY

  The gate is the geometry.
  No agent is inserted into the transition.
-/

end HEKATE
