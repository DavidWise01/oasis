namespace HEKATE

/-
  isoKernel v05 — split-polarity / homeo recurrence
  --------------------------------------------------
  Append-only correction to v04.

  Author correction:

    "they're both because they are split personality"

    -+ {{ -+2 x 1 x 2 , -+ 2 x 1 x 2 }} -+
    repeat 0-++-0 until homeo

  Interpretation inside the Root0 / OaSIs grammar:
  * Mandel-side and Juliet-side fat-belly states are not assigned a single
    exclusive stability personality.
  * Each carries the split pair: stable + unstable.
  * The paired body is mirrored as two copies of the same "-+2 x 1 x 2"
    structural lobe inside an outer -+ / -+ carrier.
  * "x" is preserved as a structural weld/operator, not multiplication.
  * "repeat 0-++-0 until homeo" is encoded as a recurrence policy.
    This file does not claim mathematical termination; homeo is the declared
    stopping state of the symbolic machine.
-/

inductive Pole where
  | stable
  | unstable
  deriving Repr, DecidableEq

structure SplitPersonality where
  first  : Pole
  second : Pole
  deriving Repr, DecidableEq

def bothPoles : SplitPersonality :=
  { first := .stable
    second := .unstable }

inductive Sign where
  | minus
  | plus
  deriving Repr, DecidableEq

inductive Weld where
  | x
  deriving Repr, DecidableEq

/--
  Literal structural lobe:
      -+2 x 1 x 2

  The numeral positions are state labels.
-/
structure Lobe where
  leftSign  : Sign
  rightSign : Sign
  twoA      : Nat
  weldA     : Weld
  one       : Nat
  weldB     : Weld
  twoB      : Nat
  deriving Repr, DecidableEq

def lobe : Lobe :=
  { leftSign  := .minus
    rightSign := .plus
    twoA      := 2
    weldA     := .x
    one       := 1
    weldB     := .x
    twoB      := 2 }

/--
  Exact paired shell:

      -+ {{ -+2 x 1 x 2 , -+2 x 1 x 2 }} -+
-/
structure SplitBody where
  outerLeftMinus  : Sign
  outerLeftPlus   : Sign
  leftLobe        : Lobe
  rightLobe       : Lobe
  outerRightMinus : Sign
  outerRightPlus  : Sign
  deriving Repr, DecidableEq

def splitBody : SplitBody :=
  { outerLeftMinus  := .minus
    outerLeftPlus   := .plus
    leftLobe        := lobe
    rightLobe       := lobe
    outerRightMinus := .minus
    outerRightPlus  := .plus }

inductive Family where
  | mandel
  | juliet
  deriving Repr, DecidableEq

structure IsoMorphState where
  family      : Family
  personality : SplitPersonality
  body        : SplitBody
  deriving Repr, DecidableEq

def mandelSplit : IsoMorphState :=
  { family := .mandel
    personality := bothPoles
    body := splitBody }

def julietSplit : IsoMorphState :=
  { family := .juliet
    personality := bothPoles
    body := splitBody }

/-- Both families carry the same stable/unstable split personality. -/
theorem both_are_split :
    mandelSplit.personality = bothPoles ∧
    julietSplit.personality = bothPoles := by
  exact ⟨rfl, rfl⟩

/-- Both lobes are the same literal -+2 x 1 x 2 body. -/
theorem mirrored_lobes :
    splitBody.leftLobe = lobe ∧
    splitBody.rightLobe = lobe := by
  exact ⟨rfl, rfl⟩

/-- Exact lobe state labels are 2 x 1 x 2. -/
theorem lobe_is_2_x_1_x_2 :
    lobe.twoA = 2 ∧
    lobe.one = 1 ∧
    lobe.twoB = 2 ∧
    lobe.weldA = Weld.x ∧
    lobe.weldB = Weld.x := by
  exact ⟨rfl, rfl, rfl, rfl, rfl⟩

/--
  Recurrence token:
      0 - + + - 0
-/
inductive RecMark where
  | zero
  | minus
  | plus
  deriving Repr, DecidableEq

def homeoCycle : List RecMark :=
  [.zero, .minus, .plus, .plus, .minus, .zero]

inductive StopState where
  | homeo
  deriving Repr, DecidableEq

structure RecurrencePolicy where
  pattern : List RecMark
  stop    : StopState
  deriving Repr, DecidableEq

def repeatUntilHomeo : RecurrencePolicy :=
  { pattern := homeoCycle
    stop := .homeo }

/-- The recurrence pattern is exactly 0-++-0. -/
theorem recurrence_is_exact :
    repeatUntilHomeo.pattern =
      [.zero, .minus, .plus, .plus, .minus, .zero] := by
  rfl

/-- The declared stop state is homeo. -/
theorem recurrence_stops_at_homeo :
    repeatUntilHomeo.stop = StopState.homeo := by
  rfl

/-
  Canonical map:

                  SPLIT PERSONALITY
                 { STABLE | UNSTABLE }
                         |
                -+             -+
                 \             /
                  {{           }}
                  /             \
          -+2 x 1 x 2     -+2 x 1 x 2
                  \             /
                   {{           }}
                 /               \
               -+                 -+

  Applies to BOTH:

      MANDEL fat belly  :: stable | unstable
      JULIET fat belly  :: stable | unstable

  Recurrence:

      0-++-0
        ↓
      0-++-0
        ↓
      0-++-0
        ↓
       ...
        ↓
      HOMEO

  "until homeo" is the declared Root0 stopping condition.
-/

end HEKATE
