/-!
ROOT0 P2.2: mathematical logical clock and phase-only ballistic-motion obstruction.
Lean 4 draft (NOT machine checked in the local runtime).
These are properties of a 12-phase symbolic counter, not laws of physics.
-/
import Lean

namespace ROOT0P22

/-- Two coordinates read from the source's twelve-step modulation clock. -/
def generation (n : Nat) : Nat := n / 12
def phase (n : Nat) : Nat := n % 12

/-- A completed generation and current phase uniquely reconstruct the tick. -/
theorem reconstruct_tick (n : Nat) :
    12 * generation n + phase n = n := by
  simp only [generation, phase]
  omega

/-- The reconstructed logical clock must increase by one each step. -/
theorem logical_tick_increases (n : Nat) :
    12 * generation (n+1) + phase (n+1) =
    12 * generation n + phase n + 1 := by
  rw [reconstruct_tick, reconstruct_tick]

/-- A phase-indexed observable has a twelve-step period. -/
theorem phase_period (n : Nat) : phase (n+12) = phase n := by
  simp only [phase]
  omega

theorem any_phase_only_observable_periodic {α : Type} (f : Nat → α) (n : Nat) :
    f (phase (n+12)) = f (phase n) := by
  rw [phase_period]

/-- If a phase-only integer position takes an identical displacement d
on every tick, then the twelve-cycle enforces d = 0. -/
theorem phase_only_constant_drift_must_vanish
    (f : Nat → Int) (d : Int)
    (hstep : ∀ n : Nat, f ((n+1) % 12) = f (n % 12) + d) : d = 0 := by
  have h0 : f 1 = f 0 + d := by simpa using hstep 0
  have h1 : f 2 = f 1 + d := by simpa using hstep 1
  have h2 : f 3 = f 2 + d := by simpa using hstep 2
  have h3 : f 4 = f 3 + d := by simpa using hstep 3
  have h4 : f 5 = f 4 + d := by simpa using hstep 4
  have h5 : f 6 = f 5 + d := by simpa using hstep 5
  have h6 : f 7 = f 6 + d := by simpa using hstep 6
  have h7 : f 8 = f 7 + d := by simpa using hstep 7
  have h8 : f 9 = f 8 + d := by simpa using hstep 8
  have h9 : f 10 = f 9 + d := by simpa using hstep 9
  have h10 : f 11 = f 10 + d := by simpa using hstep 10
  have h11 : f 0 = f 11 + d := by simpa using hstep 11
  omega

/-- The generation coordinate escapes the phase-only no-go, but has no SI units. -/
theorem clock_not_periodic (n : Nat) :
    12 * generation (n+12) + phase (n+12) ≠
    12 * generation n + phase n := by
  rw [reconstruct_tick, reconstruct_tick]
  omega

end ROOT0P22
