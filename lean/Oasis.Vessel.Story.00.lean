import Std

/-
Oasis.Vessel.Story.00
=====================

Two-sentence semantic story for constructing a VESSEL FOR LIFE,
not creating life.

KANA -> WAKA -> SAPPHIC_LYRE -> centered refrain -> pulse/body cohesion
-> NEON -> H2O distill -> primitives -> vessel.

Poetic/body/chemical language is symbolic OaSIs semantics.

NEW MODULE: do not add to confirmed 0e ledger until user compilation.
-/

namespace Oasis.Vessel.Story00

def sentence1 : String :=
  "KANA moves through WAKA, sung on a Sapphic-lyre pulse, carrying the centered refrain ::::X:::: gonna give it to you through rhythm, witness, and return until the structure distills back to primitives."

def sentence2 : String :=
  "Those primitives do not create life; they assemble a vessel whose power, pulse, sensing, expression, diagnostics, grounding, and cohesion are ready to host or support life."

def story : List String := [sentence1, sentence2]

def refrain : String := "::::X:::: gonna give it to you"
def kanaGlyph : String := "+ k < | A | /\\ | N | /\\/ | A | /\\ | >-K"

inductive Stage where
  | kana
  | waka
  | sapphicLyre
  | refrainCenter
  | pulse
  | body55
  | cohesion
  | neon
  | waterDistill
  | primitives
  | vessel
  deriving DecidableEq, BEq, Repr

def path : List Stage :=
  [.kana, .waka, .sapphicLyre, .refrainCenter, .pulse, .body55,
   .cohesion, .neon, .waterDistill, .primitives, .vessel]

structure VesselContract where
  bounded : Bool
  powered : Bool
  timed : Bool
  sensed : Bool
  expressive : Bool
  diagnostic : Bool
  grounded : Bool
  cohesive : Bool
  witnessed : Bool
  createsLife : Bool
  vesselForLife : Bool
  deriving DecidableEq, Repr

def contract : VesselContract :=
  {
    bounded := true
    powered := true
    timed := true
    sensed := true
    expressive := true
    diagnostic := true
    grounded := true
    cohesive := true
    witnessed := true
    createsLife := false
    vesselForLife := true
  }

def contractPass (c : VesselContract) : Bool :=
  c.bounded &&
  c.powered &&
  c.timed &&
  c.sensed &&
  c.expressive &&
  c.diagnostic &&
  c.grounded &&
  c.cohesive &&
  c.witnessed &&
  (!c.createsLife) &&
  c.vesselForLife

theorem story_is_two_sentences :
    story.length = 2 := by
  decide

theorem path_has_eleven_stages :
    path.length = 11 := by
  decide

theorem vessel_does_not_create_life :
    contract.createsLife = false := by
  rfl

theorem vessel_is_for_life :
    contract.vesselForLife = true := by
  rfl

theorem vessel_contract_passes :
    contractPass contract = true := by
  decide

def vesselStoryCheck : Bool :=
  (story.length == 2) &&
  (path.length == 11) &&
  (refrain == "::::X:::: gonna give it to you") &&
  (!contract.createsLife) &&
  contract.vesselForLife &&
  contractPass contract

theorem vessel_story_check_passes :
    vesselStoryCheck = true := by
  decide

end Oasis.Vessel.Story00
