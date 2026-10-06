import Std

/-!
Oasis.ESpectrum.CellLatticeHierarchy.03
=======================================

Canonical append-only formalization of the current symbolic kernel hierarchy.

MODEL CHAIN

  HomeoCell
    -> Lattice[99.9∞]
    -> Grid[x∞,y∞,z∞]
    -> Projection{vector,voxel,vogel}
    -> GlobalTick
    -> Mitosis

Aligned semantics:
  * One HomeoCell is the local sqrt6-homeo primitive.
  * One Lattice is a realized finite slice of a symbolic 99.9∞ cell capacity.
  * One Grid is the unbounded symbolic x∞ × y∞ × z∞ address space.
  * Vector / voxel / vogel are three projections of the same underlying object.
  * One GlobalTick advances every active realized cell exactly once.
  * Local clock is ternary: t=-1 -> 0 -> +1.
  * Gravity is pinned at g=1 through the local cycle.
  * Mitosis occurs only from a closed homeostatic parent and creates two
    next-generation pre-state daughters.

This is a symbolic/computational model, not an established physical theory.
-/

namespace Oasis.ESpectrum.Hierarchy

inductive Sign where
  | minus
  | plus
  deriving DecidableEq, BEq, Repr

inductive Kind where
  | E
  | P
  deriving DecidableEq, BEq, Repr

structure SignedToken where
  sign : Sign
  kind : Kind
  deriving DecidableEq, BEq, Repr

def prim : List SignedToken :=
  [
    { sign := .minus, kind := .E },
    { sign := .minus, kind := .E },
    { sign := .plus,  kind := .E },
    { sign := .plus,  kind := .E },
    { sign := .plus,  kind := .P },
    { sign := .plus,  kind := .P }
  ]

inductive Force where
  | weak
  | medium
  | strong
  deriving DecidableEq, BEq, Repr

def forces : List Force := [.weak, .medium, .strong]

structure DecoratedToken where
  token : SignedToken
  force : Force
  deriving DecidableEq, BEq, Repr

def decorate (xs : List SignedToken) : List DecoratedToken :=
  xs.flatMap (fun tok => forces.map (fun f => { token := tok, force := f }))

def nestFactor : Nat := 16
def substrateCount : Nat := 3
def pinnedSpine : Int := 0

def leavesPerSubstrate : Nat := prim.length * forces.length * nestFactor
def leavesOnSpine : Nat := substrateCount * leavesPerSubstrate

inductive TimeState where
  | pre
  | zero
  | closed
  deriving DecidableEq, BEq, Repr

def timeValue : TimeState → Int
  | .pre => -1
  | .zero => 0
  | .closed => 1

structure Occupancy where
  milli : Nat
  bound : milli ≤ 1000
  deriving Repr

def occ0 : Occupancy := ⟨0, by decide⟩
def occThreshold : Occupancy := ⟨999, by decide⟩

structure HomeoCell where
  id : Nat
  generation : Nat
  t : TimeState
  gravity : Nat
  occupancy : Occupancy
  active : Bool
  center : Int × Int × Int
  homeoTag : String
  tickCount : Nat
  deriving Repr

def mkCell (id generation : Nat := 0) : HomeoCell :=
  {
    id := id
    generation := generation
    t := .pre
    gravity := 1
    occupancy := occ0
    active := true
    center := (0, 0, 0)
    homeoTag := "sqrt6-homeo"
    tickCount := 0
  }

def pinZero (c : HomeoCell) : HomeoCell :=
  { c with t := .zero }

def propagateToHomeo (c : HomeoCell) : HomeoCell :=
  { c with occupancy := occThreshold }

def closeCell (c : HomeoCell) : HomeoCell :=
  { c with t := .closed }

def tickCell (c : HomeoCell) : HomeoCell :=
  if c.active then { c with tickCount := c.tickCount + 1 } else c

def readyForMitosis (c : HomeoCell) : Bool :=
  c.active &&
  c.gravity == 1 &&
  c.occupancy.milli == 999 &&
  timeValue c.t == 1 &&
  c.center == (0, 0, 0) &&
  c.homeoTag == "sqrt6-homeo"

def mitosis (c : HomeoCell) : Option (HomeoCell × HomeoCell) :=
  if readyForMitosis c then
    some (
      mkCell (2 * c.id) (c.generation + 1),
      mkCell (2 * c.id + 1) (c.generation + 1)
    )
  else
    none

structure Lattice where
  latticeId : Nat
  cells : Array HomeoCell
  capacitySymbol : String
  deriving Repr

def mkLattice (latticeId n generation : Nat := 0) : Lattice :=
  {
    latticeId := latticeId
    cells := Array.ofFn (fun i : Fin n => mkCell i.1 generation)
    capacitySymbol := "99.9∞"
  }

structure Grid where
  xUnbounded : Bool
  yUnbounded : Bool
  zUnbounded : Bool
  symbol : String
  deriving DecidableEq, BEq, Repr

def globalGrid : Grid :=
  {
    xUnbounded := true
    yUnbounded := true
    zUnbounded := true
    symbol := "x∞ × y∞ × z∞"
  }

inductive Projection where
  | vector
  | voxel
  | vogel
  deriving DecidableEq, BEq, Repr

structure ProjectedLattice where
  projection : Projection
  lattice : Lattice
  deriving Repr

def project (p : Projection) (l : Lattice) : ProjectedLattice :=
  { projection := p, lattice := l }

def globalTick (l : Lattice) : Lattice :=
  { l with cells := l.cells.map tickCell }

def tickN : Nat → Lattice → Lattice
  | 0, l => l
  | n + 1, l => tickN n (globalTick l)

def realizeParent (c : HomeoCell) : HomeoCell :=
  closeCell (propagateToHomeo (pinZero c))

def oneLocalCycle (c : HomeoCell) : HomeoCell × Option (HomeoCell × HomeoCell) :=
  let closed := realizeParent c
  (closed, mitosis closed)

theorem prim_has_six_tokens :
    prim.length = 6 := by decide

theorem three_force_states :
    forces.length = 3 := by decide

theorem decorated_prim_has_eighteen_states :
    (decorate prim).length = 18 := by decide

theorem leaves_per_substrate_is_288 :
    leavesPerSubstrate = 288 := by decide

theorem three_substrates_on_spine_is_864 :
    leavesOnSpine = 864 := by decide

theorem new_cell_starts_prestate :
    timeValue (mkCell 0 0).t = -1 := by rfl

theorem new_cell_has_g_one :
    (mkCell 0 0).gravity = 1 := by rfl

theorem new_cell_center_is_zero_zero_zero :
    (mkCell 0 0).center = (0, 0, 0) := by rfl

theorem realized_parent_closes_at_homeo :
    let c := realizeParent (mkCell 0 0)
    timeValue c.t = 1 ∧
    c.gravity = 1 ∧
    c.occupancy.milli = 999 ∧
    c.center = (0,0,0) := by
  decide

theorem realized_parent_is_ready_for_mitosis :
    readyForMitosis (realizeParent (mkCell 0 0)) = true := by
  decide

theorem mitosis_yields_two_daughters :
    match mitosis (realizeParent (mkCell 0 0)) with
    | some (a,b) =>
        a.generation = 1 ∧ b.generation = 1 ∧
        timeValue a.t = -1 ∧ timeValue b.t = -1 ∧
        a.gravity = 1 ∧ b.gravity = 1
    | none => False := by
  decide

theorem lattice_symbol_is_99_9_inf :
    (mkLattice 0 1 0).capacitySymbol = "99.9∞" := by rfl

theorem global_grid_is_unbounded :
    globalGrid.xUnbounded = true ∧
    globalGrid.yUnbounded = true ∧
    globalGrid.zUnbounded = true := by
  decide

theorem projection_preserves_lattice (p : Projection) (l : Lattice) :
    (project p l).lattice = l := by rfl

theorem global_tick_preserves_cell_count (l : Lattice) :
    (globalTick l).cells.size = l.cells.size := by
  simp [globalTick]

theorem one_active_cell_ticks_once :
    let l := mkLattice 0 1 0
    let after := globalTick l
    after.cells[0]!.tickCount = 1 := by
  decide

theorem one_active_cell_ticks_100_times :
    let l := mkLattice 0 1 0
    let after := tickN 100 l
    after.cells[0]!.tickCount = 100 := by
  decide

theorem global_tick_projection_invariant (p : Projection) (l : Lattice) :
    (project p (globalTick l)).lattice =
    globalTick (project p l).lattice := by
  rfl

structure HierarchyDescriptor where
  cell : String
  lattice : String
  grid : String
  views : List String
  cycle : String
  reproduction : String
  deriving DecidableEq, BEq, Repr

def canonicalHierarchy : HierarchyDescriptor :=
  {
    cell := "sqrt6-homeo"
    lattice := "99.9∞ cells"
    grid := "x∞ × y∞ × z∞"
    views := ["vector", "voxel", "vogel"]
    cycle := "every active realized cell ticks exactly once"
    reproduction := "closed homeo parent -> two prestate daughters"
  }

def frozen : Bool := true
def appendOnly : Bool := true

def alignedCheck : Bool :=
  (prim.length == 6) &&
  (forces.length == 3) &&
  ((decorate prim).length == 18) &&
  (nestFactor == 16) &&
  (substrateCount == 3) &&
  (pinnedSpine == 0) &&
  (leavesPerSubstrate == 288) &&
  (leavesOnSpine == 864) &&
  ((mkLattice 0 1 0).capacitySymbol == "99.9∞") &&
  globalGrid.xUnbounded &&
  globalGrid.yUnbounded &&
  globalGrid.zUnbounded &&
  (readyForMitosis (realizeParent (mkCell 0 0))) &&
  frozen &&
  appendOnly

theorem aligned_check_passes :
    alignedCheck = true := by
  decide

end Oasis.ESpectrum.Hierarchy
