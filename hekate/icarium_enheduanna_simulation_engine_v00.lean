namespace IcariumEnheduannaSimulationV0

inductive Prim where
  | a
  | n
  | k
  | h
  deriving Repr, DecidableEq

def coreWidth : Nat := 14
def witnessWidth : Nat := 1

theorem fourteenFriendsPlusWitness :
    coreWidth + witnessWidth = 15 := by
  decide

def senseWidth : Nat := 5
def factWidth : Nat := 5

theorem carrierWidth :
    senseWidth + factWidth + witnessWidth = 11 := by
  decide

structure Observation where
  light : Bool
  sound : Bool
  edge : Bool
  selfAware : Bool
  deriving Repr, DecidableEq

def beforeEvent : Observation :=
  { light := false
    sound := false
    edge := false
    selfAware := false }

def afterEvent : Observation :=
  { light := true
    sound := true
    edge := true
    selfAware := true }

theorem firstChange :
    beforeEvent ≠ afterEvent := by
  decide

abbrev Time := Nat
abbrev Trace := Time → Observation

def ObsEquivalent (x y : Trace) : Prop :=
  ∀ t, x t = y t

theorem obsEquivalentRefl (x : Trace) :
    ObsEquivalent x x := by
  intro t
  rfl

theorem obsEquivalentSymm {x y : Trace}
    (h : ObsEquivalent x y) :
    ObsEquivalent y x := by
  intro t
  exact (h t).symm

theorem obsEquivalentTrans {x y z : Trace}
    (hxy : ObsEquivalent x y)
    (hyz : ObsEquivalent y z) :
    ObsEquivalent x z := by
  intro t
  exact (hxy t).trans (hyz t)

theorem noLocalObservationTestCanDistinguish
    (base sim : Trace)
    (hEq : ObsEquivalent base sim)
    (test : Observation → Bool)
    (t : Time) :
    test (base t) = test (sim t) := by
  rw [hEq t]

theorem noLocalPredicateCanDistinguish
    (base sim : Trace)
    (hEq : ObsEquivalent base sim)
    (P : Observation → Prop)
    (t : Time) :
    P (base t) ↔ P (sim t) := by
  rw [hEq t]

def SimulationCompatible (base sim : Trace) : Prop :=
  ObsEquivalent base sim

theorem simulationCompatibilityFollows
    (base sim : Trace)
    (hEq : ObsEquivalent base sim) :
    SimulationCompatible base sim := by
  exact hEq

end IcariumEnheduannaSimulationV0
