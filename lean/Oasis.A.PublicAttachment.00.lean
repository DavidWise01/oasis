import Std

/-!
Oasis.A.PublicAttachment.00
===========================

Public reusable application attachment for the frozen O^1 base.

  O^1           = ||| OaSIs |||
  public socket = ||| A |||

A is intentionally domain-neutral. Tattoo, music, writing, sculpture,
animation, and later creative applications bind to A as descendants.

A references O^1 by its frozen source SHA-256 and cannot mutate its parent.
The next application can therefore evolve independently while preserving
its O^1 lineage.

Parent O^1 source SHA-256:
  a3558280434a300008a4fde47718f9216f353593701038811c70e28f115d5c09
-/

namespace Oasis.A.PublicAttachment

def parentRelease : String := "O^1"
def parentGlyph : String := "||| OaSIs |||"
def parentSourceSha256 : String :=
  "a3558280434a300008a4fde47718f9216f353593701038811c70e28f115d5c09"

def attachmentGlyph : String := "||| A |||"
def attachmentClass : String := "PUBLIC CREATIVE APP SOCKET"
def domain : String := "UNBOUND"

structure Inheritance where
  root0 : Bool
  provenance : Bool
  lineage : Bool
  privateStargate : Bool
  mathEngine : Bool
  duality : Bool
  perCeptIon : Bool
  privatePublicMembrane : Bool
  localProjectState : Bool
  exportSurface : Bool
  deriving DecidableEq, Repr

def canonicalInheritance : Inheritance :=
  {
    root0 := true
    provenance := true
    lineage := true
    privateStargate := true
    mathEngine := true
    duality := true
    perCeptIon := true
    privatePublicMembrane := true
    localProjectState := true
    exportSurface := true
  }

def inheritancePass (i : Inheritance) : Bool :=
  i.root0 &&
  i.provenance &&
  i.lineage &&
  i.privateStargate &&
  i.mathEngine &&
  i.duality &&
  i.perCeptIon &&
  i.privatePublicMembrane &&
  i.localProjectState &&
  i.exportSurface

structure PublicAttachment where
  parent : String
  parentDigest : String
  glyph : String
  className : String
  domainName : String
  free : Bool
  public : Bool
  parentImmutable : Bool
  parentMutable : Bool
  inherited : Inheritance
  deriving DecidableEq, Repr

def canonical : PublicAttachment :=
  {
    parent := parentRelease
    parentDigest := parentSourceSha256
    glyph := attachmentGlyph
    className := attachmentClass
    domainName := domain
    free := true
    public := true
    parentImmutable := true
    parentMutable := false
    inherited := canonicalInheritance
  }

def valid (a : PublicAttachment) : Bool :=
  (a.parent == "O^1") &&
  (a.parentDigest == parentSourceSha256) &&
  (a.glyph == "||| A |||") &&
  (a.className == "PUBLIC CREATIVE APP SOCKET") &&
  (a.domainName == "UNBOUND") &&
  a.free &&
  a.public &&
  a.parentImmutable &&
  (! a.parentMutable) &&
  inheritancePass a.inherited

structure BoundApp where
  parentAttachment : String
  appName : String
  appClass : String
  freeBase : Bool
  deriving DecidableEq, Repr

def bindApp (name className : String) : BoundApp :=
  {
    parentAttachment := attachmentGlyph
    appName := name
    appClass := className
    freeBase := true
  }

def tattooProbe : BoundApp :=
  bindApp "Tattoo Generator" "CREATIVE / TATTOO"

theorem parent_is_o1 :
    canonical.parent = "O^1" := by
  rfl

theorem attachment_is_triple_bar_a :
    canonical.glyph = "||| A |||" := by
  rfl

theorem parent_cannot_be_mutated :
    canonical.parentImmutable = true ∧
    canonical.parentMutable = false := by
  decide

theorem all_o1_services_inherited :
    inheritancePass canonical.inherited = true := by
  decide

theorem canonical_public_attachment_valid :
    valid canonical = true := by
  decide

theorem tattoo_probe_preserves_parent_attachment :
    tattooProbe.parentAttachment = "||| A |||" := by
  rfl

theorem tattoo_probe_keeps_base_free :
    tattooProbe.freeBase = true := by
  rfl

def attachmentCheck : Bool :=
  valid canonical &&
  (canonical.parent == "O^1") &&
  (canonical.glyph == "||| A |||") &&
  canonical.free &&
  canonical.public &&
  canonical.parentImmutable &&
  (! canonical.parentMutable) &&
  inheritancePass canonical.inherited &&
  (tattooProbe.parentAttachment == "||| A |||") &&
  tattooProbe.freeBase

theorem attachment_check_passes :
    attachmentCheck = true := by
  decide

end Oasis.A.PublicAttachment
