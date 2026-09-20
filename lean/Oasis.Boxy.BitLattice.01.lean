import Std

/-
Oasis.Boxy.BitLattice.01
=========================

Fresh descendant of Oasis.Boxy.GeneralPrimitive.00.

Current user definition:

  one BOXy primitive = one bit
  that bit is one primitive inside a lattice of bits

Search / motion may be:
  inward
  outward
  inward AND outward

The lattice extent is bounded inward by literal zero:

  0

and unbounded outward by literal:

  inf

This is symbolic architecture. "inf" is not evaluated as a finite Nat
and no completed infinite traversal is claimed.

The existing BOXy relation remains:

  6 in 4
  trying to be 3
  while 2 = ?
  1 pushes
  0 is total

Fresh candidate. Do not label 0e until user compiles it clean locally.
-/

namespace Oasis.Boxy.BitLattice01

/-! ## One primitive = one bit -/

inductive Bit where
  | zero
  | one
  deriving Repr, DecidableEq

structure Primitive where
  bit : Bit
  deriving Repr, DecidableEq

def oneBitPrim : Primitive :=
  { bit := .one }

theorem primitive_has_one_bit :
    oneBitPrim.bit = .one := by
  rfl

/-! ## Lattice of bits -/

structure LatticeSite where
  index : Nat
  value : Bit
  deriving Repr, DecidableEq

def BitLattice := Nat → Bit

def site (L : BitLattice) (n : Nat) : LatticeSite :=
  { index := n, value := L n }

theorem site_is_one_primitive_of_lattice
    (L : BitLattice) (n : Nat) :
    (site L n).value = L n := by
  rfl

/-! ## Inward / outward / both -/

inductive Direction where
  | inward
  | outward
  deriving Repr, DecidableEq

inductive SearchMode where
  | inward
  | outward
  | both
  deriving Repr, DecidableEq

def modeDirections : SearchMode → List Direction
  | .inward => [.inward]
  | .outward => [.outward]
  | .both => [.inward, .outward]

theorem inward_exact :
    modeDirections .inward = [.inward] := by
  rfl

theorem outward_exact :
    modeDirections .outward = [.outward] := by
  rfl

theorem both_exact :
    modeDirections .both = [.inward, .outward] := by
  rfl

/-! ## Literal lattice endpoints -/

inductive Extent where
  | zero
  | inf
  deriving Repr, DecidableEq

def inwardExtent : Extent := .zero
def outwardExtent : Extent := .inf

def zeroLiteral : String := "0"
def infLiteral : String := "inf"

theorem inward_is_zero :
    inwardExtent = .zero := by
  rfl

theorem outward_is_inf :
    outwardExtent = .inf := by
  rfl

theorem zero_literal_exact :
    zeroLiteral = "0" := by
  rfl

theorem inf_literal_exact :
    infLiteral = "inf" := by
  rfl

/-! ## One local step in the indexed lattice -/

def stepInward : Nat → Nat
  | 0 => 0
  | n + 1 => n

def stepOutward (n : Nat) : Nat :=
  n + 1

theorem inward_stops_at_zero :
    stepInward 0 = 0 := by
  rfl

theorem outward_advances (n : Nat) :
    stepOutward n = n + 1 := by
  rfl

/-! ## BOXy relation retained at one lattice primitive -/

structure BoxyState where
  inside : Nat
  box : Nat
  target : Nat
  query : Nat
  push : Nat
  total : Nat
  deriving Repr, DecidableEq

def boxy : BoxyState :=
  { inside := 6
    box := 4
    target := 3
    query := 2
    push := 1
    total := 0 }

theorem boxy_relation_exact :
    boxy.inside = 6 ∧
    boxy.box = 4 ∧
    boxy.target = 3 ∧
    boxy.query = 2 ∧
    boxy.push = 1 ∧
    boxy.total = 0 := by
  decide

/-! ## Canonical lattice contract -/

theorem one_bit_lattice_contract :
    oneBitPrim.bit = .one ∧
    modeDirections .both = [.inward, .outward] ∧
    inwardExtent = .zero ∧
    outwardExtent = .inf ∧
    zeroLiteral = "0" ∧
    infLiteral = "inf" ∧
    stepInward 0 = 0 := by
  decide

end Oasis.Boxy.BitLattice01
