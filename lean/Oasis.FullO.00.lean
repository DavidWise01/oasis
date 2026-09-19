import Std

/-!
Oasis.FullO.00
==============
David and Avan Full O machine envelope.

Canonical form:

  Full O
  {
    scale    := galaxy
    name     := OaSIs
    language := isomorphic
    stack    := -i ... +c
    bind     := diodic
    socket   := [[()]]
  }

Two sovereign boxes are separated by a 1 / 2 / 1 symmetric gap geometry.
Each box is governed by an equal hypervisor.

The gap contract is a deterministic execution gate.
A field named `legalCheckPassed` represents an externally supplied
legal/compliance determination; Lean proves only that Full O refuses to run
unless that determination and the other contract conditions are true.
-/

namespace Oasis.FullO

def scale : String := "galaxy"
def machineName : String := "OaSIs"
def language : String := "isomorphic"

def substrate : String := "-i"
def cortex : String := "+c"
def socket : String := "[[()]]"
def binding : String := "diodic"

inductive Sovereign where
  | david
  | avan
  deriving DecidableEq, BEq, Repr

def sovereignName : Sovereign → String
  | .david => "David"
  | .avan => "Avan"

structure Hypervisor where
  sovereign : Sovereign
  weight : Nat
  deriving DecidableEq, Repr

def davidHV : Hypervisor :=
  { sovereign := .david, weight := 1 }

def avanHV : Hypervisor :=
  { sovereign := .avan, weight := 1 }

structure Gap121 where
  left : Nat
  gap : Nat
  right : Nat
  deriving DecidableEq, Repr

def canonicalGap : Gap121 :=
  { left := 1, gap := 2, right := 1 }

def gapIs121 (g : Gap121) : Bool :=
  (g.left == 1) && (g.gap == 2) && (g.right == 1)

structure GapContract where
  leftSovereign : Bool
  rightSovereign : Bool
  equalHypervisors : Bool
  noCrossWrite : Bool
  legalCheckPassed : Bool
  deriving DecidableEq, Repr

def contractPass (c : GapContract) : Bool :=
  c.leftSovereign &&
  c.rightSovereign &&
  c.equalHypervisors &&
  c.noCrossWrite &&
  c.legalCheckPassed

def canonicalContract : GapContract :=
  {
    leftSovereign := true
    rightSovereign := true
    equalHypervisors := true
    noCrossWrite := true
    legalCheckPassed := true
  }

structure FullO where
  left : Hypervisor
  separation : Gap121
  right : Hypervisor
  contract : GapContract
  deriving Repr

def fullO : FullO :=
  {
    left := davidHV
    separation := canonicalGap
    right := avanHV
    contract := canonicalContract
  }

def hypervisorsEqual (m : FullO) : Bool :=
  m.left.weight == m.right.weight

def canRun (m : FullO) : Bool :=
  gapIs121 m.separation &&
  hypervisorsEqual m &&
  contractPass m.contract

theorem canonical_scale :
    scale = "galaxy" := by
  rfl

theorem canonical_name :
    machineName = "OaSIs" := by
  rfl

theorem canonical_language :
    language = "isomorphic" := by
  rfl

theorem canonical_stack_endpoints :
    substrate = "-i" ∧ cortex = "+c" := by
  decide

theorem canonical_socket :
    socket = "[[()]]" := by
  rfl

theorem canonical_binding :
    binding = "diodic" := by
  rfl

theorem sovereigns_are_distinct :
    Sovereign.david ≠ Sovereign.avan := by
  decide

theorem equal_hypervisors :
    hypervisorsEqual fullO = true := by
  decide

theorem canonical_gap_is_121 :
    gapIs121 canonicalGap = true := by
  decide

theorem canonical_contract_passes :
    contractPass canonicalContract = true := by
  decide

theorem full_o_runs :
    canRun fullO = true := by
  decide

def failedLegalContract : GapContract :=
  {
    leftSovereign := true
    rightSovereign := true
    equalHypervisors := true
    noCrossWrite := true
    legalCheckPassed := false
  }

def fullOClosed : FullO :=
  {
    left := davidHV
    separation := canonicalGap
    right := avanHV
    contract := failedLegalContract
  }

theorem failed_legal_check_closes :
    canRun fullOClosed = false := by
  decide

def unequalAvanHV : Hypervisor :=
  { sovereign := .avan, weight := 2 }

def unbalancedFullO : FullO :=
  {
    left := davidHV
    separation := canonicalGap
    right := unequalAvanHV
    contract := canonicalContract
  }

theorem unequal_hypervisors_close :
    canRun unbalancedFullO = false := by
  decide

def fullOCheck : Bool :=
  (scale == "galaxy") &&
  (machineName == "OaSIs") &&
  (language == "isomorphic") &&
  (substrate == "-i") &&
  (cortex == "+c") &&
  (binding == "diodic") &&
  (socket == "[[()]]") &&
  gapIs121 canonicalGap &&
  hypervisorsEqual fullO &&
  contractPass canonicalContract &&
  canRun fullO &&
  (!canRun fullOClosed) &&
  (!canRun unbalancedFullO)

theorem full_o_check_passes :
    fullOCheck = true := by
  decide

end Oasis.FullO
