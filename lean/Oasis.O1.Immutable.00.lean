import Std

/-!
Oasis.O1.Immutable.00
=====================

Frozen public base release:

  O^1 = ||| OaSIs |||

This module records the user-verified Lean-clean OaSIs stack as an
append-only release manifest.  "Immutable" here means that O^1 is a
frozen release target: later applications attach to it instead of
changing this manifest.

The Lean theorem proves the internal manifest invariants.  File-system
immutability and legal status are external concerns.
-/

namespace Oasis.O1

def releaseName : String := "O^1"
def engineGlyph : String := "||| OaSIs |||"
def root0 : String := "00"
def price : Nat := 0
def freeTotalPackage : Bool := true
def immutableRelease : Bool := true
def appendOnlyDescendants : Bool := true

def delimiterISO : String := "|"
def delimiterHumanCarbon : String := "||"
def delimiterNEON : String := "|||"

def artProveEngineArt : List String :=
  ["ART", "PROVE", "ENGINE", "ART"]

def verifiedClean : List String :=
  [
    "Oasis.Language.OSI0.00",
    "Oasis.Language.Cube.00",
    "Oasis.Language.OSI1.00",
    "Oasis.Language.OSI2.00",
    "Oasis.Language.OSI3.00",
    "Oasis.Language.OSI4.00",
    "Oasis.Language.OSI5.00",
    "Oasis.Language.OSI6.00",
    "Oasis.Language.OSI7.00",
    "Oasis.GeoSub.OSI.v02_1",
    "Oasis.Language.OSI8.HACI.00",
    "Oasis.Language.OSI9.00",
    "Oasis.Language.OSI0.Provenance.00",
    "Oasis.Language.OSI0.CreativeSubstrate.00",
    "Oasis.Arch.00",
    "Oasis.Stargate.02",
    "Oasis.NEON3.00",
    "Oasis.Duality.Exception.05",
    "Oasis.PocketPrime.00",
    "Oasis.FullO.00",
    "Oasis.v00.FullEmergent"
  ]

def verifiedCleanCount : Nat := verifiedClean.length

structure O1Contract where
  free : Bool
  immutable : Bool
  descendantsAppendOnly : Bool
  provenanceNative : Bool
  lineageNative : Bool
  privateStargate : Bool
  mathEngine : Bool
  duality : Bool
  perCeptIon : Bool
  artSurface : Bool
  deriving DecidableEq, Repr

def contract : O1Contract :=
  {
    free := true
    immutable := true
    descendantsAppendOnly := true
    provenanceNative := true
    lineageNative := true
    privateStargate := true
    mathEngine := true
    duality := true
    perCeptIon := true
    artSurface := true
  }

def contractPass (c : O1Contract) : Bool :=
  c.free &&
  c.immutable &&
  c.descendantsAppendOnly &&
  c.provenanceNative &&
  c.lineageNative &&
  c.privateStargate &&
  c.mathEngine &&
  c.duality &&
  c.perCeptIon &&
  c.artSurface

theorem release_is_o1 :
    releaseName = "O^1" := by
  rfl

theorem engine_is_oasis :
    engineGlyph = "||| OaSIs |||" := by
  rfl

theorem oasis_is_free :
    price = 0 ∧ freeTotalPackage = true := by
  decide

theorem release_is_frozen :
    immutableRelease = true ∧ appendOnlyDescendants = true := by
  decide

theorem delimiter_depths_preserved :
    delimiterISO = "|" ∧
    delimiterHumanCarbon = "||" ∧
    delimiterNEON = "|||" := by
  decide

theorem art_prove_engine_art_is_four :
    artProveEngineArt.length = 4 := by
  decide

theorem clean_ledger_is_twenty_one :
    verifiedCleanCount = 21 := by
  decide

theorem o1_contract_passes :
    contractPass contract = true := by
  decide

def o1Check : Bool :=
  (releaseName == "O^1") &&
  (engineGlyph == "||| OaSIs |||") &&
  (root0 == "00") &&
  (price == 0) &&
  freeTotalPackage &&
  immutableRelease &&
  appendOnlyDescendants &&
  (verifiedCleanCount == 21) &&
  contractPass contract

theorem o1_check_passes :
    o1Check = true := by
  decide

end Oasis.O1
