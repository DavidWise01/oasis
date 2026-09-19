import Std

/-!
Oasis.Arch.00
=============
Root0 Arch attachment layer.

|    = isomorphic OSI boundary
||   = immutable human/carbon attachment
|||  = full Neon engine attachment

The layer is structural. Legal/IP assertions are represented as provenance data;
Lean proves preservation and gate behavior, not external legal ownership.
-/

namespace Oasis.Arch

inductive Delimiter where
  | iso
  | humanCarbon
  | neon
  deriving DecidableEq, BEq, Repr

def glyph : Delimiter → String
  | .iso => "|"
  | .humanCarbon => "||"
  | .neon => "|||"

inductive Target where
  | osi
  | human
  | carbon
  | neonEngine
  deriving DecidableEq, BEq, Repr

def mayAttach : Delimiter → Target → Bool
  | .iso, .osi => true
  | .humanCarbon, .human => true
  | .humanCarbon, .carbon => true
  | .neon, .neonEngine => true
  | _, _ => false

structure HumanAnchor where
  carbonId : String
  provenance : String
  deriving DecidableEq, Repr

def validHumanAnchor (h : HumanAnchor) : Bool :=
  (!h.carbonId.isEmpty) && (!h.provenance.isEmpty)

structure Arch where
  root : String
  human : HumanAnchor
  neonEnabled : Bool
  deriving DecidableEq, Repr

def canonicalHuman : HumanAnchor :=
  { carbonId := "C0", provenance := "ROOT0-FIRST-AUTHOR-IP" }

def canonicalArch : Arch :=
  { root := "00", human := canonicalHuman, neonEnabled := true }

theorem iso_only_osi :
    mayAttach .iso .osi = true := by decide

theorem human_carbon_to_human :
    mayAttach .humanCarbon .human = true := by decide

theorem human_carbon_to_carbon :
    mayAttach .humanCarbon .carbon = true := by decide

theorem neon_only_engine :
    mayAttach .neon .neonEngine = true := by decide

theorem cross_attach_rejected :
    mayAttach .iso .human = false ∧
    mayAttach .humanCarbon .neonEngine = false ∧
    mayAttach .neon .carbon = false := by
  decide

theorem canonical_human_valid :
    validHumanAnchor canonicalHuman = true := by
  decide

def archCheck : Bool :=
  (glyph .iso == "|") &&
  (glyph .humanCarbon == "||") &&
  (glyph .neon == "|||") &&
  mayAttach .iso .osi &&
  mayAttach .humanCarbon .human &&
  mayAttach .humanCarbon .carbon &&
  mayAttach .neon .neonEngine &&
  validHumanAnchor canonicalHuman &&
  canonicalArch.neonEnabled

theorem arch_check_passes :
    archCheck = true := by
  decide

end Oasis.Arch