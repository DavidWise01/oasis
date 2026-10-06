import Std

/-!
Oasis.ESpectrum.VectorVoxelVogel.00.Frozen
===========================================

Frozen formalization of the user's -E+ spectrum geometry.

Model contract:
  * -E+ is the full signed carrier.
  * x is the unbounded signed time carrier.
  * y is the pinned backbone/state axis.
  * quantum is addressed on y as a function indexed by x-time.
  * "-" denotes operation/transition.
  * "_" denotes held state.
  * "{...}" denotes recursive/nested resolution.
  * vector = 1D / 3D view of the same -E+ object.
  * voxel  = 2D / 3D view of the same -E+ object.
  * vogel  = 3D view of the same -E+ object.
  * tape-measure ticks (1/4, 1/2, 3/4 and in-betweens) model nested
    fractional resolution without changing the pinned backbone.

This is a symbolic/computational model. It does not assert a physical
quantum-mechanics theorem.
-/

namespace Oasis.ESpectrum

/-- Signed ends and center of the full carrier: -E, E, +E. -/
inductive EPoint where
  | minusE
  | E
  | plusE
  deriving DecidableEq, BEq, Repr

/-- Cardinal operations in the x/y graph. -/
inductive Cardinal where
  | plusX
  | plusY
  | minusX
  | minusY
  deriving DecidableEq, BEq, Repr

/-- Surface tokens used by the model notation. -/
inductive SurfaceToken where
  | operation   -- "-"
  | state       -- "_"
  | nest        -- "{...}"
  deriving DecidableEq, BEq, Repr

/-- Three dimensional views of one underlying -E+ carrier. -/
inductive Projection where
  | vector
  | voxel
  | vogel
  deriving DecidableEq, BEq, Repr

/-- Dimensions are represented as view dimension / ambient dimension. -/
structure ProjectionSpec where
  view : Projection
  viewDim : Nat
  ambientDim : Nat
  deriving DecidableEq, BEq, Repr

def vectorSpec : ProjectionSpec :=
  { view := .vector, viewDim := 1, ambientDim := 3 }

def voxelSpec : ProjectionSpec :=
  { view := .voxel, viewDim := 2, ambientDim := 3 }

def vogelSpec : ProjectionSpec :=
  { view := .vogel, viewDim := 3, ambientDim := 3 }

/-- The invariant signed -E+ carrier with pinned y-backbone at zero. -/
structure ECarrier where
  negative : EPoint
  center : EPoint
  positive : EPoint
  pinnedY : Int
  deriving DecidableEq, BEq, Repr

def fullSpectrum : ECarrier :=
  {
    negative := .minusE
    center := .E
    positive := .plusE
    pinnedY := 0
  }

/-- A finite decimal/fractal path below a whole y state.
For example [0,1] records the ".01" nest below y9. -/
abbrev NestPath := List Nat

/-- Coordinate/address carrier for x0 yN.nest x0 y0 notation. -/
structure ScalarAddress where
  xLeft : Int
  yWhole : Nat
  yNest : NestPath
  xRight : Int
  yReturn : Int
  deriving DecidableEq, BEq, Repr

def scalar0 : ScalarAddress :=
  { xLeft := 0, yWhole := 0, yNest := [], xRight := 0, yReturn := 0 }

def scalar9 : ScalarAddress :=
  { xLeft := 0, yWhole := 9, yNest := [], xRight := 0, yReturn := 0 }

/-- x0 y9.01 x0 y0. -/
def scalar9_01 : ScalarAddress :=
  { xLeft := 0, yWhole := 9, yNest := [0, 1], xRight := 0, yReturn := 0 }

/-- x runs over Int, so the formal carrier is unbounded in both signed directions.
The y-address is the quantum/fractal gear indexed at that x-time position. -/
def quantumAtTime (x : Int) (y : Nat) (nest : NestPath) : ScalarAddress :=
  { xLeft := x, yWhole := y, yNest := nest, xRight := x, yReturn := 0 }

/-- A rational tick for tape-measure style subdivision. -/
structure Tick where
  num : Nat
  den : Nat
  deriving DecidableEq, BEq, Repr

def quarter : Tick := { num := 1, den := 4 }
def half : Tick := { num := 1, den := 2 }
def threeQuarter : Tick := { num := 3, den := 4 }

def primaryTicks : List Tick :=
  [quarter, half, threeQuarter]

/-- Example recursively finer in-betweens inside the first quarter. -/
def nestedQuarterTicks : List Tick :=
  [
    { num := 1, den := 16 },
    { num := 1, den := 8 },
    { num := 3, den := 16 }
  ]

/-- A recursive tape-measure cell. Each interval may contain another ruler. -/
inductive TapeCell where
  | mark (tick : Tick)
  | interval (left right : Tick) (inside : List TapeCell)
  deriving DecidableEq, BEq, Repr

def firstQuarterNest : TapeCell :=
  .interval
    { num := 0, den := 1 }
    quarter
    (nestedQuarterTicks.map TapeCell.mark)

/-- One view of the same carrier. -/
structure SpectrumView where
  carrier : ECarrier
  spec : ProjectionSpec
  deriving DecidableEq, BEq, Repr

def vectorView : SpectrumView :=
  { carrier := fullSpectrum, spec := vectorSpec }

def voxelView : SpectrumView :=
  { carrier := fullSpectrum, spec := voxelSpec }

def vogelView : SpectrumView :=
  { carrier := fullSpectrum, spec := vogelSpec }

/-- Frozen/append-only flags for this semantic unit. -/
def frozen : Bool := true
def appendOnly : Bool := true

theorem full_spectrum_is_minus_E_plus :
    fullSpectrum.negative = .minusE ∧
    fullSpectrum.center = .E ∧
    fullSpectrum.positive = .plusE := by
  decide

theorem y_backbone_is_pinned_zero :
    fullSpectrum.pinnedY = 0 := by
  rfl

theorem vector_is_1d_in_3d :
    vectorSpec.viewDim = 1 ∧ vectorSpec.ambientDim = 3 := by
  decide

theorem voxel_is_2d_in_3d :
    voxelSpec.viewDim = 2 ∧ voxelSpec.ambientDim = 3 := by
  decide

theorem vogel_is_3d :
    vogelSpec.viewDim = 3 ∧ vogelSpec.ambientDim = 3 := by
  decide

theorem all_views_share_same_E_carrier :
    vectorView.carrier = fullSpectrum ∧
    voxelView.carrier = fullSpectrum ∧
    vogelView.carrier = fullSpectrum := by
  decide

theorem scalar_zero_is_x0_y0_x0_y0 :
    scalar0 =
      { xLeft := 0, yWhole := 0, yNest := [],
        xRight := 0, yReturn := 0 } := by
  rfl

theorem scalar_nine_is_x0_y9_x0_y0 :
    scalar9 =
      { xLeft := 0, yWhole := 9, yNest := [],
        xRight := 0, yReturn := 0 } := by
  rfl

theorem scalar_nine_point_zero_one :
    scalar9_01 =
      { xLeft := 0, yWhole := 9, yNest := [0, 1],
        xRight := 0, yReturn := 0 } := by
  rfl

theorem quantum_is_indexed_by_time
    (x : Int) (y : Nat) (nest : NestPath) :
    (quantumAtTime x y nest).xLeft = x ∧
    (quantumAtTime x y nest).xRight = x ∧
    (quantumAtTime x y nest).yWhole = y ∧
    (quantumAtTime x y nest).yNest = nest := by
  rfl

theorem tape_measure_primary_ticks :
    primaryTicks = [
      { num := 1, den := 4 },
      { num := 1, den := 2 },
      { num := 3, den := 4 }
    ] := by
  rfl

theorem tape_measure_has_recursive_inbetweens :
    nestedQuarterTicks = [
      { num := 1, den := 16 },
      { num := 1, den := 8 },
      { num := 3, den := 16 }
    ] := by
  rfl

def frozenCheck : Bool :=
  (fullSpectrum == {
    negative := EPoint.minusE,
    center := EPoint.E,
    positive := EPoint.plusE,
    pinnedY := 0
  }) &&
  (vectorSpec == { view := Projection.vector, viewDim := 1, ambientDim := 3 }) &&
  (voxelSpec == { view := Projection.voxel, viewDim := 2, ambientDim := 3 }) &&
  (vogelSpec == { view := Projection.vogel, viewDim := 3, ambientDim := 3 }) &&
  (scalar0 == {
    xLeft := 0, yWhole := 0, yNest := [], xRight := 0, yReturn := 0
  }) &&
  (scalar9 == {
    xLeft := 0, yWhole := 9, yNest := [], xRight := 0, yReturn := 0
  }) &&
  (scalar9_01 == {
    xLeft := 0, yWhole := 9, yNest := [0, 1], xRight := 0, yReturn := 0
  }) &&
  frozen &&
  appendOnly

theorem frozen_check_passes :
    frozenCheck = true := by
  decide

end Oasis.ESpectrum
