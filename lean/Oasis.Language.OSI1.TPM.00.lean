import Std

/-!
Oasis.Language.OSI1.TPM.00
==========================
Append-only TPM-plane attachment for OaSIs Layer 1.

Plane:
  0x00 .. 0xZZ, using the base-36 alphabet 0-9,A-Z.
  0x00 is the empty reserved plane root.
  0x01 is the first live selector.
  0xZZ is the maximum two-digit plane selector.

HOME:
  xdeadb55fx is a reserved HOME tag bound to the empty root.
  It is a symbolic reservation tag, not a hexadecimal literal.

This descendant attaches to the frozen O^1 release without altering it.
-/

namespace Oasis.Language.OSI1.TPM

/-- One base-36 selector digit: 0-9, A-Z. -/
abbrev Digit36 := Fin 36

/-- Two base-36 digits form one TPM-plane address. -/
structure Address where
  high : Digit36
  low : Digit36
  deriving DecidableEq, BEq, Repr

def radix : Nat := 36
def planeWidth : Nat := radix
def planeStates : Nat := planeWidth * planeWidth

/-- Empty, reserved root: 0x00. -/
def emptyRoot : Address :=
  { high := ⟨0, by decide⟩, low := ⟨0, by decide⟩ }

/-- First occupied TPM-plane selector: 0x01. -/
def firstLive : Address :=
  { high := ⟨0, by decide⟩, low := ⟨1, by decide⟩ }

/-- Maximum two-digit base-36 selector: 0xZZ. -/
def maxPlane : Address :=
  { high := ⟨35, by decide⟩, low := ⟨35, by decide⟩ }

def emptyRootLabel : String := "0x00"
def firstLiveLabel : String := "0x01"
def maxPlaneLabel : String := "0xZZ"

/-- Reserved HOME tag anchored at the empty TPM root. -/
def reservedHomeTag : String := "xdeadb55fx"
def reservedHome : Address := emptyRoot

def isReserved (a : Address) : Bool :=
  a == reservedHome

theorem plane_is_base36_square :
    planeStates = 1296 := by
  decide

theorem live_plane_states :
    planeStates - 1 = 1295 := by
  decide

theorem first_live_is_0x01 :
    firstLiveLabel = "0x01" := by
  rfl

theorem max_plane_is_0xZZ :
    maxPlaneLabel = "0xZZ" := by
  rfl

theorem home_tag_is_xdeadb55fx :
    reservedHomeTag = "xdeadb55fx" := by
  rfl

theorem reserved_home_is_empty :
    reservedHome = emptyRoot := by
  rfl

theorem empty_root_is_reserved :
    isReserved emptyRoot = true := by
  decide

theorem first_live_is_not_reserved :
    isReserved firstLive = false := by
  decide

/-- Executable TPM-plane attachment check. -/
def tpmPlaneCheck : Bool :=
  (radix == 36) &&
  (planeStates == 1296) &&
  (planeStates - 1 == 1295) &&
  (emptyRootLabel == "0x00") &&
  (firstLiveLabel == "0x01") &&
  (maxPlaneLabel == "0xZZ") &&
  (reservedHomeTag == "xdeadb55fx") &&
  isReserved emptyRoot &&
  (!isReserved firstLive)

theorem tpm_plane_check_passes :
    tpmPlaneCheck = true := by
  decide

end Oasis.Language.OSI1.TPM
