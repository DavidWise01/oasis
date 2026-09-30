import Std

namespace OaSIs.V180

inductive HomeoBranch where
  | pull
  | balance
  | push
deriving Repr, DecidableEq

inductive InternalPhase where
  | zero
  | pos
  | neg
deriving Repr, DecidableEq

inductive Occupancy where
  | root
  | carrierOpen
  | oe
deriving Repr, DecidableEq

structure Layer where
  index : Nat
  plank : Nat
  angleDeg : Nat
  phase : InternalPhase
  homeo : HomeoBranch
  occupancy : Occupancy
deriving Repr, DecidableEq

def L0 : Layer :=
  { index := 0, plank := 0, angleDeg := 0,
    phase := .zero, homeo := .balance, occupancy := .root }

def L1 : Layer :=
  { index := 1, plank := 1, angleDeg := 30,
    phase := .pos, homeo := .push, occupancy := .carrierOpen }

def L2 : Layer :=
  { index := 2, plank := 2, angleDeg := 60,
    phase := .neg, homeo := .push, occupancy := .oe }

theorem phase_quantum_closes : 36 * 10 = 360 := by decide
theorem plank_is_three_quanta : 3 * 10 = 30 := by decide
theorem two_planks_sector : 2 * 30 = 60 := by decide
theorem twelve_planks_turn : 12 * 30 = 360 := by decide
theorem mini_prim_sector : 3 * 20 = 60 := by decide
theorem mini_prim_turn : 18 * 20 = 360 := by decide
theorem element_plank_gcd : Nat.gcd 10 12 = 2 := by decide
theorem element_plank_lcm : Nat.lcm 10 12 = 60 := by decide

theorem frozen_boundary :
    L0.occupancy = .root ∧
    L1.phase = .pos ∧
    L1.homeo = .push ∧
    L2.phase = .neg ∧
    L2.homeo = .push ∧
    L2.occupancy = .oe := by
  decide

/- Arithmetic gives LCM(10,12)=60, but this module deliberately defines no
   theorem equating an element tick with a plank or angular tick. -/

end OaSIs.V180
