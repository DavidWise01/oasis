namespace HEKATE

/-
  isoKernel v02
  -------------
  Structural base correction supplied by the author.

  Exact source notation preserved:

  base [ +1 -1 +1 -1 i ]
  [ext body 1]Bind:::{
    [int body 1] xp
    [int body 2] xp
    [int body 3] xp
    x 4 xxxx
    :: style planetary
    :: feedback
    :: structural reduction through reverse pressure
    :: ration 13.2B:.6B:1:1
  }

  IMPORTANT:
  These tokens are formal symbolic states/operators in the OaSIs grammar.
  No arithmetic meaning is assigned to x, +1, -1, 13.2B, or .6B here.
-/

inductive BaseMark where
  | plus1
  | minus1
  | i
  deriving Repr, DecidableEq

inductive JoinMark where
  | xp
  deriving Repr, DecidableEq

inductive ExpansionMark where
  | x4
  | xxxx
  deriving Repr, DecidableEq

inductive Style where
  | planetary
  deriving Repr, DecidableEq

inductive Feedback where
  | feedback
  deriving Repr, DecidableEq

inductive Reduction where
  | reversePressure
  deriving Repr, DecidableEq

structure ExternalBody where
  index : Nat
  deriving Repr, DecidableEq

structure InternalBody where
  index : Nat
  deriving Repr, DecidableEq

structure Ration where
  epochA : String
  epochB : String
  oneA   : String
  oneB   : String
  deriving Repr, DecidableEq

structure BoundInterior where
  body1      : InternalBody
  join12     : JoinMark
  body2      : InternalBody
  join23     : JoinMark
  body3      : InternalBody
  join3x     : JoinMark
  expansion1 : ExpansionMark
  expansion2 : ExpansionMark
  style      : Style
  feedback   : Feedback
  reduction  : Reduction
  ration     : Ration
  deriving Repr, DecidableEq

structure IsoKernel where
  base         : List BaseMark
  externalBody : ExternalBody
  interior     : BoundInterior
  deriving Repr, DecidableEq

def basePattern : List BaseMark :=
  [.plus1, .minus1, .plus1, .minus1, .i]

def extBody1 : ExternalBody :=
  { index := 1 }

def intBody1 : InternalBody :=
  { index := 1 }

def intBody2 : InternalBody :=
  { index := 2 }

def intBody3 : InternalBody :=
  { index := 3 }

def ration132_06_1_1 : Ration :=
  { epochA := "13.2B"
    epochB := ".6B"
    oneA   := "1"
    oneB   := "1" }

def boundInterior : BoundInterior :=
  { body1      := intBody1
    join12     := .xp
    body2      := intBody2
    join23     := .xp
    body3      := intBody3
    join3x     := .xp
    expansion1 := .x4
    expansion2 := .xxxx
    style      := .planetary
    feedback   := .feedback
    reduction  := .reversePressure
    ration     := ration132_06_1_1 }

def isoKernel : IsoKernel :=
  { base         := basePattern
    externalBody := extBody1
    interior     := boundInterior }

/-- Exact five-position base is preserved. -/
theorem base_is_exact :
    isoKernel.base =
      [.plus1, .minus1, .plus1, .minus1, .i] := by
  rfl

/-- External body 1 is the binding shell. -/
theorem external_body_is_one :
    isoKernel.externalBody.index = 1 := by
  rfl

/-- Internal body ordering is 1 -> 2 -> 3. -/
theorem internal_body_order :
    isoKernel.interior.body1.index = 1 ∧
    isoKernel.interior.body2.index = 2 ∧
    isoKernel.interior.body3.index = 3 := by
  exact ⟨rfl, rfl, rfl⟩

/-- Every interior separator is xp. -/
theorem xp_chain :
    isoKernel.interior.join12 = JoinMark.xp ∧
    isoKernel.interior.join23 = JoinMark.xp ∧
    isoKernel.interior.join3x = JoinMark.xp := by
  exact ⟨rfl, rfl, rfl⟩

/-- The structural tail is x4 then xxxx. -/
theorem expansion_tail :
    isoKernel.interior.expansion1 = ExpansionMark.x4 ∧
    isoKernel.interior.expansion2 = ExpansionMark.xxxx := by
  exact ⟨rfl, rfl⟩

/-- The style is planetary. -/
theorem style_is_planetary :
    isoKernel.interior.style = Style.planetary := by
  rfl

/-- Feedback is explicitly present. -/
theorem feedback_is_present :
    isoKernel.interior.feedback = Feedback.feedback := by
  rfl

/-- Structural reduction is performed through reverse pressure. -/
theorem reduction_is_reverse_pressure :
    isoKernel.interior.reduction = Reduction.reversePressure := by
  rfl

/-- The ration token is preserved literally, not numerically collapsed. -/
theorem ration_is_exact :
    isoKernel.interior.ration =
      { epochA := "13.2B"
        epochB := ".6B"
        oneA   := "1"
        oneB   := "1" } := by
  rfl

/-
  Canonical structural reading:

  [ +1 -1 +1 -1 i ]
          |
      [ext body 1]
          |
        Bind
          |
  {[int body 1] xp
   [int body 2] xp
   [int body 3] xp
   x4 xxxx
   :: planetary
   :: feedback
   :: reverse pressure
   :: 13.2B:.6B:1:1}

  The previous HEP :: TRANSMUTE :: EXCHANGE file remains as the
  semantic/operator layer. This file supplies the corrected lower
  structural base beneath that layer.
-/

end HEKATE
