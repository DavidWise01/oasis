import Std

/-
OaSIs_Orbital_Tether_v186
==========================

Formal core for the five-phase orbital tether.

PHYSICS ALIGNMENT
-----------------
For Newtonian two-body motion the standard invariants include:
  specific orbital energy      eps = |v|^2 / 2 - mu / r
  specific angular momentum    h   = r x v

Energy sign classifies ideal conics:
  eps < 0  bound
  eps = 0  parabolic
  eps > 0  unbound

MODEL LAYER
-----------
Father Time is represented as five exact phase addresses:
  0 -> 1/5 -> 2/5 -> 3/5 -> 4/5 -> 0
with one revolution committed on wrap.

This proof establishes the discrete phase/closure architecture and a symbolic
energy-classification layer. It does not formalize the differential equations
of orbital mechanics and does not claim physical orbits advance in five jumps.
-/

namespace OaSIs.OrbitalTetherV186

/-! ## Exact five-phase ring -/

inductive Phase5 where
  | p0
  | p1
  | p2
  | p3
  | p4
  deriving DecidableEq, BEq, Repr

def phaseIndex : Phase5 → Nat
  | .p0 => 0
  | .p1 => 1
  | .p2 => 2
  | .p3 => 3
  | .p4 => 4

def nextPhase : Phase5 → Phase5
  | .p0 => .p1
  | .p1 => .p2
  | .p2 => .p3
  | .p3 => .p4
  | .p4 => .p0

def advancePhase : Nat → Phase5 → Phase5
  | 0, p => p
  | n + 1, p => advancePhase n (nextPhase p)

theorem phase_index_lt_five (p : Phase5) :
    phaseIndex p < 5 := by
  cases p <;> decide

theorem next_phase_is_plus_one_mod_five (p : Phase5) :
    phaseIndex (nextPhase p) = (phaseIndex p + 1) % 5 := by
  cases p <;> decide

theorem five_phase_closure (p : Phase5) :
    advancePhase 5 p = p := by
  cases p <;> decide

theorem ten_phase_two_closures (p : Phase5) :
    advancePhase 10 p = p := by
  cases p <;> decide

/-! ## Clock with revolution witness -/

structure Clock where
  phase : Phase5
  revolutions : Nat
  deriving DecidableEq, Repr

def stepClock : Clock → Clock
  | ⟨.p0, r⟩ => ⟨.p1, r⟩
  | ⟨.p1, r⟩ => ⟨.p2, r⟩
  | ⟨.p2, r⟩ => ⟨.p3, r⟩
  | ⟨.p3, r⟩ => ⟨.p4, r⟩
  | ⟨.p4, r⟩ => ⟨.p0, r + 1⟩

def runClock : Nat → Clock → Clock
  | 0, c => c
  | n + 1, c => runClock n (stepClock c)

theorem zero_clock_five_steps :
    runClock 5 ⟨.p0, 0⟩ = ⟨.p0, 1⟩ := by
  decide

theorem phase_specific_five_step_commit :
    (runClock 5 ⟨.p0, 7⟩ = ⟨.p0, 8⟩) ∧
    (runClock 5 ⟨.p1, 7⟩ = ⟨.p1, 8⟩) ∧
    (runClock 5 ⟨.p2, 7⟩ = ⟨.p2, 8⟩) ∧
    (runClock 5 ⟨.p3, 7⟩ = ⟨.p3, 8⟩) ∧
    (runClock 5 ⟨.p4, 7⟩ = ⟨.p4, 8⟩) := by
  decide

/-! ## Symbolic conic classification -/

inductive OrbitClass where
  | bound
  | parabolic
  | unbound
  deriving DecidableEq, BEq, Repr

def classifyEnergy (eps : Int) : OrbitClass :=
  if eps < 0 then .bound
  else if eps = 0 then .parabolic
  else .unbound

theorem negative_energy_is_bound (eps : Int) (h : eps < 0) :
    classifyEnergy eps = .bound := by
  simp [classifyEnergy, h]

theorem zero_energy_is_parabolic :
    classifyEnergy 0 = .parabolic := by
  decide

theorem positive_energy_is_unbound (eps : Int) (h : 0 < eps) :
    classifyEnergy eps = .unbound := by
  have hn : ¬ eps < 0 := by omega
  have hz : eps ≠ 0 := by omega
  simp [classifyEnergy, hn, hz]

/-! ## Orbital tether witness -/

structure OrbitalTether where
  phase : Phase5
  orbitClass : OrbitClass
  angularMomentumWitness : Bool
  energyWitness : Bool
  provenanceWitness : Bool
  deriving DecidableEq, Repr

def validTether (t : OrbitalTether) : Bool :=
  t.angularMomentumWitness &&
  t.energyWitness &&
  t.provenanceWitness

def circularWitness : OrbitalTether :=
  {
    phase := .p0
    orbitClass := .bound
    angularMomentumWitness := true
    energyWitness := true
    provenanceWitness := true
  }

theorem circular_witness_valid :
    validTether circularWitness = true := by
  decide

def modelCheck : Bool :=
  (advancePhase 5 .p0 == .p0) &&
  (advancePhase 5 .p1 == .p1) &&
  (advancePhase 5 .p2 == .p2) &&
  (advancePhase 5 .p3 == .p3) &&
  (advancePhase 5 .p4 == .p4) &&
  (runClock 5 ⟨.p0, 0⟩ == ⟨.p0, 1⟩) &&
  (classifyEnergy (-1) == .bound) &&
  (classifyEnergy 0 == .parabolic) &&
  (classifyEnergy 1 == .unbound) &&
  validTether circularWitness

theorem orbital_tether_v186_pass :
    modelCheck = true := by
  decide

end OaSIs.OrbitalTetherV186
