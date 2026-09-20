import Std

/-
Oasis.MoreGarbage.SearchPrimitive.05
====================================

Correction to the prior "gone forever" interpretation.

This primitive is a resumable search:

  search until
    (a) the target/binding is found, OR
    (b) the observer stops waiting.

Stopping does NOT prove absence.
It produces a PAUSED search with a continuation point.

Scale is preserved literally as:

  prime -> inf

"inf" is represented here by an unbounded Nat search address space,
not by claiming a completed traversal of infinity.

The Mandel / Juliet machinery may instantiate this primitive, but this
file formalizes the search primitive itself.

Fresh candidate. Do not label 0e until user compiles it clean locally.
-/

namespace Oasis.MoreGarbage.SearchPrimitive05

/-! ## Literal scale -/

def scaleStart : String := "prime"
def scaleEnd : String := "inf"
def scaleLiteral : String := "prime -> inf"

theorem scale_literal_exact :
    scaleLiteral = "prime -> inf" := by
  rfl

/-! ## Search outcome: FOUND or PAUSED, never fabricated absence -/

inductive SearchResult where
  | found (index : Nat)
  | paused (nextIndex : Nat)
  deriving Repr, DecidableEq

def searchUntil
    (isTarget : Nat → Bool)
    : Nat → Nat → SearchResult
  | 0, start =>
      .paused start
  | fuel + 1, start =>
      if isTarget start then
        .found start
      else
        searchUntil isTarget fuel (start + 1)

/-! ## Resume from exactly where waiting stopped -/

def resume
    (isTarget : Nat → Bool)
    (fuel : Nat)
    : SearchResult → SearchResult
  | .found i =>
      .found i
  | .paused nextIndex =>
      searchUntil isTarget fuel nextIndex

theorem found_is_terminal
    (isTarget : Nat → Bool)
    (fuel i : Nat) :
    resume isTarget fuel (.found i) = .found i := by
  rfl

theorem paused_resumes_at_saved_index
    (isTarget : Nat → Bool)
    (fuel nextIndex : Nat) :
    resume isTarget fuel (.paused nextIndex) =
      searchUntil isTarget fuel nextIndex := by
  rfl

/-! ## Deterministic witnesses -/

def targetAt3 : Nat → Bool
  | 3 => true
  | _ => false

def neverYet : Nat → Bool :=
  fun _ => false

theorem enough_wait_finds_target :
    searchUntil targetAt3 4 0 = .found 3 := by
  decide

theorem too_tired_pauses :
    searchUntil targetAt3 2 0 = .paused 2 := by
  decide

theorem resume_later_finds_same_target :
    resume targetAt3 2 (searchUntil targetAt3 2 0) =
      .found 3 := by
  decide

theorem no_match_yet_is_pause_not_absence :
    searchUntil neverYet 4 0 = .paused 4 := by
  decide

/-! ## Search has no "gone forever" constructor -/

def isFound : SearchResult → Bool
  | .found _ => true
  | .paused _ => false

def isPaused : SearchResult → Bool
  | .found _ => false
  | .paused _ => true

theorem paused_is_not_found (n : Nat) :
    isFound (.paused n) = false := by
  rfl

theorem found_is_not_paused (n : Nat) :
    isPaused (.found n) = false := by
  rfl

/-! ## Mandel / Juliet names retained as an instantiation boundary -/

def mandel : String := "search"
def juliet : String := "boundary"

theorem mandel_is_search :
    mandel = "search" := by
  rfl

theorem juliet_is_boundary :
    juliet = "boundary" := by
  rfl

/-! ## Canonical primitive contract -/

theorem search_primitive_contract :
    scaleStart = "prime" ∧
    scaleEnd = "inf" ∧
    scaleLiteral = "prime -> inf" ∧
    searchUntil targetAt3 4 0 = .found 3 ∧
    searchUntil targetAt3 2 0 = .paused 2 ∧
    resume targetAt3 2 (searchUntil targetAt3 2 0) = .found 3 ∧
    searchUntil neverYet 4 0 = .paused 4 := by
  decide

end Oasis.MoreGarbage.SearchPrimitive05
