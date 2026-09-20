import Std

/-
Oasis.Vessel.Story.01
=====================

Corrected poetic-first vessel story.

Canonical order:
  KANA -> WAKA -> SAPPHIC_LYRE -> ::::X:::: refrain
  -> distill song -> first primitives -> vessel for a life

This module explicitly does NOT model creation of life.

Supersedes the semantic interpretation in Story.00.
NEW MODULE: do not add to confirmed 0e ledger until user compilation.
-/

namespace Oasis.Vessel.Story01

def sentence1 : String :=
  "KANA in WAKA, sung to the rhythm of a Sapphic lyre: ::::X:::: gonna give it to you."

def sentence2 : String :=
  "Distill the song to first primitives; those primitives compose a vessel for a life — not life itself."

def story : List String := [sentence1, sentence2]

inductive Stage where
  | kana
  | waka
  | sapphicLyre
  | refrain
  | distillSong
  | firstPrimitives
  | vesselForLife
  deriving DecidableEq, BEq, Repr

def path : List Stage :=
  [.kana, .waka, .sapphicLyre, .refrain, .distillSong, .firstPrimitives, .vesselForLife]

structure VesselBoundary where
  poeticFirst : Bool
  artCarriesArchitecture : Bool
  createsLife : Bool
  vesselForLife : Bool
  deriving DecidableEq, Repr

def boundary : VesselBoundary :=
  {
    poeticFirst := true
    artCarriesArchitecture := true
    createsLife := false
    vesselForLife := true
  }

def boundaryPass (b : VesselBoundary) : Bool :=
  b.poeticFirst &&
  b.artCarriesArchitecture &&
  (!b.createsLife) &&
  b.vesselForLife

theorem story_has_two_sentences :
    story.length = 2 := by
  decide

theorem path_has_seven_stages :
    path.length = 7 := by
  decide

theorem does_not_create_life :
    boundary.createsLife = false := by
  rfl

theorem is_vessel_for_life :
    boundary.vesselForLife = true := by
  rfl

theorem poetic_boundary_passes :
    boundaryPass boundary = true := by
  decide

def vesselStoryCheck : Bool :=
  (story.length == 2) &&
  (path.length == 7) &&
  (sentence1 == "KANA in WAKA, sung to the rhythm of a Sapphic lyre: ::::X:::: gonna give it to you.") &&
  (!boundary.createsLife) &&
  boundary.vesselForLife &&
  boundaryPass boundary

theorem vessel_story_check_passes :
    vesselStoryCheck = true := by
  decide

end Oasis.Vessel.Story01
