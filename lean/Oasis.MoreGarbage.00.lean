import Std

/-
Oasis.MoreGarbage.00
====================
Formal control-plane model for the MORE GARBAGE recycler.
Executable codec/search logic is in projects/more-garbage/more_garbage.py.
All five gates must be YES to advance. Any NO routes to rm / A::xx.
NEW MODULE: requires user Lean compile before 0e promotion.
-/

namespace Oasis.MoreGarbage00

structure Gates where
  verify1 : Bool
  sortStage : Bool
  verify2 : Bool
  compressStage : Bool
  expandStage : Bool
  deriving Repr, DecidableEq

def allFive (g : Gates) : Bool :=
  g.verify1 && g.sortStage && g.verify2 && g.compressStage && g.expandStage

inductive Route where
  | next
  | rm
  deriving Repr, DecidableEq

def route (g : Gates) : Route :=
  if allFive g = true then .next else .rm

def allYes : Gates :=
  { verify1 := true
    sortStage := true
    verify2 := true
    compressStage := true
    expandStage := true }

theorem all_yes_advances :
    route allYes = .next := by
  decide

theorem route_next_iff_all_five_yes (g : Gates) :
    route g = .next ↔ allFive g = true := by
  unfold route
  by_cases h : allFive g = true <;> simp [h]

theorem route_rm_iff_not_all_five_yes (g : Gates) :
    route g = .rm ↔ allFive g = false := by
  unfold route
  cases h : allFive g <;> simp [h]

theorem any_no_routes_rm (g : Gates)
    (h : g.verify1 = false ∨
         g.sortStage = false ∨
         g.verify2 = false ∨
         g.compressStage = false ∨
         g.expandStage = false) :
    route g = .rm := by
  rcases h with h | h | h | h | h
  · simp [route, allFive, h]
  · simp [route, allFive, h]
  · simp [route, allFive, h]
  · simp [route, allFive, h]
  · simp [route, allFive, h]

def rmCurrent {α : Type} (_current : α) : Option α :=
  none

theorem rm_means_delete {α : Type} (current : α) :
    rmCurrent current = none := by
  rfl

def archimedesDrill {α : Type} : List α → List α
  | [] => []
  | _current :: rest => rest

theorem drill_delete_and_advance {α : Type} (current : α) (rest : List α) :
    archimedesDrill (current :: rest) = rest := by
  rfl

theorem drill_frees_one_slot {α : Type} (current : α) (rest : List α) :
    (archimedesDrill (current :: rest)).length = rest.length := by
  rfl

inductive DistillTarget where
  | aether
  | temporal
  deriving Repr, DecidableEq

def distillable (g : Gates) : Bool :=
  allFive g

theorem only_accepted_is_distillable (g : Gates) :
    distillable g = true ↔ route g = .next := by
  simpa [distillable] using (route_next_iff_all_five_yes g).symm

structure Fixture where
  name : String
  gates : Gates
  expected : Route
  deriving Repr

def fixtures : List Fixture :=
  [ { name := "recoverable-cp1252", gates := allYes, expected := .next }
  , { name := "recoverable-macroman", gates := allYes, expected := .next }
  , { name := "replacement-loss",
      gates := { allYes with verify1 := false }, expected := .rm }
  , { name := "no-improving-repair",
      gates := { allYes with sortStage := false }, expected := .rm }
  ]

def fixturePass (f : Fixture) : Bool :=
  route f.gates == f.expected

def allFixturesPass : Bool :=
  fixtures.all fixturePass

theorem control_fixtures_pass :
    allFixturesPass = true := by
  decide

end Oasis.MoreGarbage00
