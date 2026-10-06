import Std

/-!
Oasis.ESpectrum.GlobalTickCycle.02
=================================

Append-only alignment successor for the recursive lattice/global-tick model.

User model encoded here:

  cell primitive
    = one sqrt6-homeo closure unit

  one lattice
    = 99.9∞ worth of homeo cells (symbolically represented, not enumerated)

  global grid
    = x∞ × y∞ × z∞

  views
    = vector / voxel / vogel projections of the same lattice/cell structure

  one cycle
    = every currently realized/active homeo cell advances exactly one local tick,
      once, under one global cycle boundary

This formalization intentionally separates:
  * symbolic infinite-capacity/state-space notation
  * finite executable benchmark instances

It does not claim established physical cosmology.
-/

namespace Oasis.ESpectrum.GlobalTick

inductive Projection where
  | vector
  | voxel
  | vogel
  deriving DecidableEq, BEq, Repr

structure Coord where
  x : Int
  y : Int
  z : Int
  deriving DecidableEq, BEq, Repr

/-- Symbolic homeostatic primitive. -/
structure HomeoCell where
  id : Nat
  tick : Nat
  active : Bool
  deriving DecidableEq, BEq, Repr

/-- A finite executable lattice instance used for testing the global rule. -/
structure Lattice where
  cells : Array HomeoCell
  deriving Repr

/-- Symbolic descriptors for the unbounded model. -/
def xUnbounded : Bool := true
def yUnbounded : Bool := true
def zUnbounded : Bool := true
def latticeCapacitySymbol : String := "99.9∞"
def cellPrimitiveSymbol : String := "sqrt6-homeo"
def globalGridSymbol : String := "x∞ × y∞ × z∞"

/-- Increment an active cell exactly once; inactive cells are preserved. -/
def tickCell (c : HomeoCell) : HomeoCell :=
  if c.active then { c with tick := c.tick + 1 } else c

/-- One global cycle = one pass over all currently realized cells. -/
def cycle (l : Lattice) : Lattice :=
  { cells := l.cells.map tickCell }

/-- A cell advanced exactly once iff it was active. -/
def advancedExactlyOnce (before after : HomeoCell) : Bool :=
  if before.active then
    after.id == before.id &&
    after.active == before.active &&
    after.tick == before.tick + 1
  else
    after == before

def cycleAligned (before after : Lattice) : Bool :=
  if h : before.cells.size = after.cells.size then
    (List.range before.cells.size).all (fun i =>
      let b := before.cells[i]'(by simpa [h])
      let a := after.cells[i]'(by simpa [h])
      advancedExactlyOnce b a)
  else
    false

def mkLattice (n : Nat) : Lattice :=
  {
    cells := Array.ofFn (fun i : Fin n =>
      { id := i.1, tick := 0, active := true })
  }

def mkAlternatingLattice (n : Nat) : Lattice :=
  {
    cells := Array.ofFn (fun i : Fin n =>
      { id := i.1, tick := 7, active := i.1 % 2 == 0 })
  }

theorem zero_cells_cycle :
    (cycle (mkLattice 0)).cells.size = 0 := by
  decide

theorem one_cell_ticks_once :
    let before := mkLattice 1
    let after := cycle before
    after.cells[0]!.tick = 1 := by
  decide

theorem active_cells_tick_once_16 :
    cycleAligned (mkLattice 16) (cycle (mkLattice 16)) = true := by
  decide

theorem active_cells_tick_once_256 :
    cycleAligned (mkLattice 256) (cycle (mkLattice 256)) = true := by
  decide

theorem alternating_preserves_inactive :
    cycleAligned (mkAlternatingLattice 64) (cycle (mkAlternatingLattice 64)) = true := by
  decide

/-- Repeated cycles compose linearly in tick count for active cells. -/
def cycleN : Nat → Lattice → Lattice
  | 0, l => l
  | n + 1, l => cycleN n (cycle l)

theorem one_cell_100_cycles :
    let after := cycleN 100 (mkLattice 1)
    after.cells[0]!.tick = 100 := by
  decide

/-- Projection invariance: the global tick semantics do not depend on view. -/
def project (_ : Projection) (l : Lattice) : Lattice := l

theorem projection_invariant (p : Projection) (l : Lattice) :
    project p (cycle l) = cycle (project p l) := by
  rfl

def frozen : Bool := true
def appendOnly : Bool := true

def alignedCheck : Bool :=
  xUnbounded &&
  yUnbounded &&
  zUnbounded &&
  (latticeCapacitySymbol == "99.9∞") &&
  (cellPrimitiveSymbol == "sqrt6-homeo") &&
  (globalGridSymbol == "x∞ × y∞ × z∞") &&
  (cycleAligned (mkLattice 256) (cycle (mkLattice 256))) &&
  (cycleAligned (mkAlternatingLattice 64) (cycle (mkAlternatingLattice 64))) &&
  frozen &&
  appendOnly

theorem aligned_check_passes :
    alignedCheck = true := by
  decide

end Oasis.ESpectrum.GlobalTick
