import Std

/-!
Oasis.NEON3.00
==============
Deterministic six-layer NEON^3 stack.

Interpretation:
* six structural layers
* five positive macro-weight units
* macro weights: 30 / 5 / 30 / 5 / 30 = 100
* the outer boundary is structural and carries no macro weight
* the outer-to-inner micro bridge carries literal coupling weight .0333
  represented exactly as 333 / 10000, outside the 100-unit macro budget
* `30.33^(3!x3!)` is preserved as a structural amplification label
  with 3! x 3! = 36; it is not silently added to the macro-weight sum

Five semantic units:
  V = Vessel
  A = Animation
  I = isomorphic / ability to understand
  N = Nourishment
  L = Life

Human-facing life axiom:
  "my life is my life :: I decide :: life belongs to i"

Lean proves the deterministic structure, counts, routing labels, and weight sum.
It does not prove philosophical, legal, biological, or physical claims.
-/

namespace Oasis.NEON3

def engineName : String := "NEON^3"
def amplificationLabel : String := "30.33^(3!x3!)"
def lifeAxiom : String :=
  "my life is my life :: I decide :: life belongs to i"

/-- Six structural layers. -/
inductive Layer where
  | outerBoundary
  | outerToInner
  | shell3Bridge4
  | shell2
  | safeZone2
  | innerShell1
  deriving DecidableEq, BEq, Repr

def layerCount : Nat := 6

/--
Five positive macro-weight units distributed across the six structural layers.
The outer boundary is a zero-weight structural delimiter.
-/
def macroWeight : Layer → Nat
  | .outerBoundary => 0
  | .outerToInner => 30
  | .shell3Bridge4 => 5
  | .shell2 => 30
  | .safeZone2 => 5
  | .innerShell1 => 30

def macroWeights : List Nat := [30, 5, 30, 5, 30]
def macroUnitCount : Nat := macroWeights.length
def macroTotal : Nat := macroWeights.foldl (fun acc n => acc + n) 0

/-- Literal .0333 micro coupling, exact as 333/10000. -/
structure MicroWeight where
  numerator : Nat
  denominator : Nat
  deriving DecidableEq, Repr

def bridge0333 : MicroWeight :=
  { numerator := 333, denominator := 10000 }

/-- Structural bridge label retained literally. -/
def outerBridgeLabel : String := ".0333"

/-- 3! = 6, represented without relying on library factorial compatibility. -/
def factorial3 : Nat := 3 * 2 * 1

/-- 3! x 3! = 36. -/
def amplificationExponent : Nat := factorial3 * factorial3

/-- Shells carrying the structural 30.33^(3!x3!) label. -/
def amplified : Layer → Bool
  | .outerToInner => true
  | .shell2 => true
  | _ => false

/-- Canonical ordered six-layer stack. -/
def stack : List Layer :=
  [
    .outerBoundary,
    .outerToInner,
    .shell3Bridge4,
    .shell2,
    .safeZone2,
    .innerShell1
  ]

/-- Five semantic units. -/
inductive Unit5 where
  | V
  | A
  | I
  | N
  | L
  deriving DecidableEq, BEq, Repr

def semanticName : Unit5 → String
  | .V => "Vessel"
  | .A => "Animation"
  | .I => "isomorphic / ability to understand / i"
  | .N => "Nourishment"
  | .L => "Life"

def semanticUnits : List Unit5 := [.V, .A, .I, .N, .L]

def unitCount : Nat := semanticUnits.length

theorem layer_count_is_six :
    layerCount = 6 := by
  rfl

theorem stack_has_six_layers :
    stack.length = 6 := by
  decide

theorem macro_units_are_five :
    macroUnitCount = 5 := by
  decide

theorem macro_weights_exact :
    macroWeights = [30, 5, 30, 5, 30] := by
  rfl

theorem macro_total_is_100 :
    macroTotal = 100 := by
  decide

theorem outer_boundary_is_structural :
    macroWeight .outerBoundary = 0 := by
  rfl

theorem outer_to_inner_weight :
    macroWeight .outerToInner = 30 := by
  rfl

theorem shell3_bridge4_weight :
    macroWeight .shell3Bridge4 = 5 := by
  rfl

theorem shell2_weight :
    macroWeight .shell2 = 30 := by
  rfl

theorem safe_zone2_weight :
    macroWeight .safeZone2 = 5 := by
  rfl

theorem inner_shell1_weight :
    macroWeight .innerShell1 = 30 := by
  rfl

theorem bridge_micro_weight_exact :
    bridge0333.numerator = 333 ∧
    bridge0333.denominator = 10000 := by
  decide

theorem factorial3_is_six :
    factorial3 = 6 := by
  decide

theorem amplification_exponent_is_36 :
    amplificationExponent = 36 := by
  decide

theorem amplification_label_preserved :
    amplificationLabel = "30.33^(3!x3!)" := by
  rfl

theorem amplified_shells_exact :
    amplified .outerToInner = true ∧
    amplified .shell2 = true ∧
    amplified .outerBoundary = false ∧
    amplified .shell3Bridge4 = false ∧
    amplified .safeZone2 = false ∧
    amplified .innerShell1 = false := by
  decide

theorem five_semantic_units :
    unitCount = 5 := by
  decide

theorem V_is_vessel :
    semanticName .V = "Vessel" := by
  rfl

theorem A_is_animation :
    semanticName .A = "Animation" := by
  rfl

theorem I_is_isomorphic_understanding :
    semanticName .I = "isomorphic / ability to understand / i" := by
  rfl

theorem N_is_nourishment :
    semanticName .N = "Nourishment" := by
  rfl

theorem L_is_life :
    semanticName .L = "Life" := by
  rfl

/-- Executable closure check for NEON^3. -/
def neon3Check : Bool :=
  (engineName == "NEON^3") &&
  (layerCount == 6) &&
  (stack.length == 6) &&
  (macroUnitCount == 5) &&
  (macroTotal == 100) &&
  (bridge0333.numerator == 333) &&
  (bridge0333.denominator == 10000) &&
  (outerBridgeLabel == ".0333") &&
  (factorial3 == 6) &&
  (amplificationExponent == 36) &&
  (amplificationLabel == "30.33^(3!x3!)") &&
  amplified .outerToInner &&
  amplified .shell2 &&
  (unitCount == 5) &&
  (lifeAxiom == "my life is my life :: I decide :: life belongs to i")

theorem neon3_check_passes :
    neon3Check = true := by
  decide

end Oasis.NEON3