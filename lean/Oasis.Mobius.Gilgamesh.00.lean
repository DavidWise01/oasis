import Std

/-
Oasis.Mobius.Gilgamesh.00

First MOBIUS story-instance manifest.
Historical/narrative claims are typed snapshot data, not proved by Lean.

NEW MODULE: not in confirmed 0e ledger until user compilation.
-/

namespace Oasis.Mobius.Gilgamesh00

def instanceId : String := "MOBIUS-0001"
def title : String := "Gilgamesh"
def asOf : String := "2026-09-19"

inductive ClaimKind where
  | historicallyAttested
  | traditionallyAttributed
  | narrativeInternal
  | contestedOrUncertain
  deriving DecidableEq, BEq, Repr

structure Claim where
  kind : ClaimKind
  text : String
  deriving DecidableEq, Repr

def claims : List Claim :=
  [
    { kind := .historicallyAttested,
      text := "Gilgamesh literature survives in cuneiform clay-tablet traditions." },
    { kind := .historicallyAttested,
      text := "Earlier Sumerian Gilgamesh poems precede later Akkadian epic forms." },
    { kind := .traditionallyAttributed,
      text := "The Standard Babylonian recension is traditionally associated with Sin-leqi-unninni." },
    { kind := .contestedOrUncertain,
      text := "The literary Gilgamesh is not collapsed into a fully documented historical biography." },
    { kind := .narrativeInternal,
      text := "Mortality, friendship, kingship, loss, journey, memory, and return are story material." }
  ]

structure InstanceBoundary where
  snapshotDated : Bool
  portraitMayBeFabricatedAsHistorical : Bool
  fakeCuneiformMayBeLabeledAuthentic : Bool
  modernParaphraseAllowed : Bool
  provenanceRequired : Bool
  deriving DecidableEq, Repr

def boundary : InstanceBoundary :=
  { snapshotDated := true
    portraitMayBeFabricatedAsHistorical := false
    fakeCuneiformMayBeLabeledAuthentic := false
    modernParaphraseAllowed := true
    provenanceRequired := true }

def boundaryPass (b : InstanceBoundary) : Bool :=
  b.snapshotDated &&
  (!b.portraitMayBeFabricatedAsHistorical) &&
  (!b.fakeCuneiformMayBeLabeledAuthentic) &&
  b.modernParaphraseAllowed &&
  b.provenanceRequired

theorem gilgamesh_has_five_snapshot_claims :
    claims.length = 5 := by
  decide

theorem gilgamesh_boundary_passes :
    boundaryPass boundary = true := by
  decide

def gilgameshCheck : Bool :=
  (instanceId == "MOBIUS-0001") &&
  (title == "Gilgamesh") &&
  (asOf == "2026-09-19") &&
  (claims.length == 5) &&
  boundaryPass boundary

theorem gilgamesh_check_passes :
    gilgameshCheck = true := by
  decide

end Oasis.Mobius.Gilgamesh00
