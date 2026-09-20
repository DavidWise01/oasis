import Std

/-
Oasis.NEON.SemanticCompound.00
==============================

Append-only semantic evolution descendant of Oasis.NEON3.00.

Canonical cycle:
  PRIMS -> N_COLD -> E_CARRIER -> O_HOT -> N_GRAY -> H2O_DISTILL -> PRIMS'

The element/color/solvent language is symbolic OaSIs semantics.
This module makes no physical chemistry or spectroscopy claims.

NEW MODULE: do not add to the confirmed 0e ledger until user compilation.
-/

namespace Oasis.NEON.SemanticCompound00

def parent : String := "Oasis.NEON3.00"
def kanaGlyph : String := "+ k < | A | /\\ | N | /\\/ | A | /\\ | >-K"

inductive Phase where
  | nitrogenCold
  | energyCarrier
  | oxygenHot
  | neutralGray
  | waterDistill
  deriving DecidableEq, BEq, Repr

def phaseName : Phase → String
  | .nitrogenCold => "N :: nitrogen :: cold :: blueshift"
  | .energyCarrier => "E :: energy :: carrier"
  | .oxygenHot => "O :: oxygen :: hot :: redshift :: break-apart"
  | .neutralGray => "N :: neutral :: energy-gray"
  | .waterDistill => "H2O :: solvent metaphor :: distill-to-primitives"

def cycle : List Phase :=
  [.nitrogenCold, .energyCarrier, .oxygenHot, .neutralGray, .waterDistill]

inductive Domain where
  | rootO1
  | iso
  | humanCarbon
  | neonEngine
  | electronics
  | networking
  | storage
  | javaRuntime
  | fengShui
  | artBeauty
  | attachment
  deriving DecidableEq, BEq, Repr

def domains : List Domain :=
  [.rootO1, .iso, .humanCarbon, .neonEngine, .electronics, .networking,
   .storage, .javaRuntime, .fengShui, .artBeauty, .attachment]

structure EvolutionBinding where
  domain : Domain
  invariant : String
  provenanceRequired : Bool
  kanaWitnessRequired : Bool
  unresolvedMayRemain : Bool
  deriving DecidableEq, Repr

def bind (d : Domain) : EvolutionBinding :=
  {
    domain := d
    invariant := "semantic intent + domain contract"
    provenanceRequired := true
    kanaWitnessRequired := true
    unresolvedMayRemain := true
  }

def bindings : List EvolutionBinding := domains.map bind

def validBinding (b : EvolutionBinding) : Bool :=
  (!b.invariant.isEmpty) &&
  b.provenanceRequired &&
  b.kanaWitnessRequired &&
  b.unresolvedMayRemain

def allValid : List EvolutionBinding → Bool
  | [] => true
  | x :: xs => validBinding x && allValid xs

theorem cycle_has_five_phases :
    cycle.length = 5 := by
  decide

theorem domains_have_eleven_bindings :
    domains.length = 11 := by
  decide

theorem bindings_match_domains :
    bindings.length = domains.length := by
  decide

theorem every_binding_requires_witness :
    allValid bindings = true := by
  decide

def semanticCompoundCheck : Bool :=
  (parent == "Oasis.NEON3.00") &&
  (cycle.length == 5) &&
  (domains.length == 11) &&
  (bindings.length == 11) &&
  allValid bindings

theorem semantic_compound_check_passes :
    semanticCompoundCheck = true := by
  decide

end Oasis.NEON.SemanticCompound00
