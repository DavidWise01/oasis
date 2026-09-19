import Std

/-!
Oasis.Stargate.02
=================
Deterministic Stargate primitive.

Canonical form:

  (d toroid_source){ 0 . 0 . 1 . 1 . 24 . 42 . 1 . 1 . 0 . 0 }(ecruos_diorot d)
  etagrats *

Interpretation used here:
* `d toroid_source` is the left source marker
* the numeric core is a 10-slot toroidal source word
* `24 . 42` is the oriented hinge pair
* the right marker is the mirrored source marker
* the full core is toroidally palindromic up to hinge swap 24 <-> 42

This is a symbolic/deterministic software model.
-/

namespace Oasis.Stargate02

def leftSource : String := "(d toroid_source)"
def rightSource : String := "(ecruos_diorot d)"
def gateName : String := "etagrats *"

/-- Canonical 10-slot toroidal source word. -/
def sourceCore : List Nat := [0, 0, 1, 1, 24, 42, 1, 1, 0, 0]

/-- The oriented hinge swaps 24 and 42 under toroidal reversal. -/
def flipHinge : Nat → Nat
  | 24 => 42
  | 42 => 24
  | n => n

theorem left_source_literal :
    leftSource = "(d toroid_source)" := by
  rfl

theorem right_source_literal :
    rightSource = "(ecruos_diorot d)" := by
  rfl

theorem gate_name_literal :
    gateName = "etagrats *" := by
  rfl

theorem source_core_length :
    sourceCore.length = 10 := by
  decide

theorem source_core_exact :
    sourceCore = [0, 0, 1, 1, 24, 42, 1, 1, 0, 0] := by
  rfl

theorem source_hinge_pair :
    ∃ (pre : List Nat) (suf : List Nat),
      sourceCore = pre ++ [24, 42] ++ suf := by
  exact ⟨[0, 0, 1, 1], [1, 1, 0, 0], by decide⟩

/--
The source is not an ordinary palindrome.
It becomes self-equal when reversed and hinge-flipped.
-/
theorem toroidal_source_palindrome :
    sourceCore.reverse.map flipHinge = sourceCore := by
  decide

/-- A deterministic Stargate record. -/
structure Gate where
  left : String
  core : List Nat
  right : String
  name : String
  deriving DecidableEq, Repr

def canonical : Gate :=
  {
    left := leftSource
    core := sourceCore
    right := rightSource
    name := gateName
  }

/-- Validity check for the canonical Stargate primitive. -/
def valid (g : Gate) : Bool :=
  (g.left == leftSource) &&
  (g.right == rightSource) &&
  (g.name == gateName) &&
  (g.core.length == 10) &&
  (g.core.reverse.map flipHinge == g.core)

/-- Deterministic open condition: only the canonical valid gate opens. -/
def canOpen (g : Gate) : Bool :=
  valid g

theorem canonical_valid :
    valid canonical = true := by
  decide

theorem canonical_opens :
    canOpen canonical = true := by
  decide

/-- A hinge-broken gate closes. -/
def brokenCore : List Nat := [0, 0, 1, 1, 24, 24, 1, 1, 0, 0]

def broken : Gate :=
  {
    left := leftSource
    core := brokenCore
    right := rightSource
    name := gateName
  }

theorem broken_does_not_open :
    canOpen broken = false := by
  decide

/-- Executable closure check. -/
def stargateCheck : Bool :=
  (leftSource == "(d toroid_source)") &&
  (rightSource == "(ecruos_diorot d)") &&
  (gateName == "etagrats *") &&
  (sourceCore.length == 10) &&
  (sourceCore == [0, 0, 1, 1, 24, 42, 1, 1, 0, 0]) &&
  (sourceCore.reverse.map flipHinge == sourceCore) &&
  valid canonical &&
  canOpen canonical &&
  (! canOpen broken)

theorem stargate_check_passes :
    stargateCheck = true := by
  decide

end Oasis.Stargate02