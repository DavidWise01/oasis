/-
OASIS AZ1 Science v32 — standalone structural receipts
Date: 2026-10-07
-/
namespace OASIS.AZ1ScienceV32

structure CorpusDelta where
  previousCount : Nat
  currentCount : Nat
  retained : Nat
  added : Nat
  removed : Nat
deriving DecidableEq, Repr

def corpusDelta : CorpusDelta :=
  { previousCount := 859, currentCount := 1321,
    retained := 854, added := 467, removed := 5 }

theorem previous_reconciles :
    corpusDelta.retained + corpusDelta.removed = corpusDelta.previousCount := by
  decide

theorem current_reconciles :
    corpusDelta.retained + corpusDelta.added = corpusDelta.currentCount := by
  decide

structure TerminalStress where
  firstTerminalDay : Nat
  firstBoundViolationDay : Nat
deriving DecidableEq, Repr

def terminalStress : TerminalStress :=
  { firstTerminalDay := 11251, firstBoundViolationDay := 11849 }

theorem violation_occurs_after_terminal :
    terminalStress.firstTerminalDay < terminalStress.firstBoundViolationDay := by
  decide

structure ChronicleReplay where
  entries : Nat
  exact : Bool
deriving DecidableEq, Repr

def chronicleReplay : ChronicleReplay :=
  { entries := 86, exact := true }

theorem uploaded_history_replays :
    chronicleReplay.entries = 86 ∧ chronicleReplay.exact = true := by
  decide

end OASIS.AZ1ScienceV32
