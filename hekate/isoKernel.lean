namespace HEKATE

/-
  isoKernel
  ---------
  Canonical five-slot HEKATE primitive expressed as a deterministic Lean kernel.

  Root0 / OaSIs semantic boundary:
  * the first three slots are held constants/state;
  * the final two slots are ordered operators;
  * no chemistry or nuclear-physics claim is implied by this formal object.
-/

inductive Constant where
  | hydrogen
  | electrum
  | potassium
  deriving Repr, DecidableEq

inductive Operator where
  | transmute
  | exchange
  deriving Repr, DecidableEq

structure Substrate where
  c1 : Constant
  c2 : Constant
  c3 : Constant
  deriving Repr, DecidableEq

structure Program where
  op1 : Operator
  op2 : Operator
  deriving Repr, DecidableEq

structure IsoState where
  substrate : Substrate
  program   : Program
  deriving Repr, DecidableEq

def HEP : Substrate :=
  { c1 := .hydrogen
    c2 := .electrum
    c3 := .potassium }

def TE : Program :=
  { op1 := .transmute
    op2 := .exchange }

def isoKernel : IsoState :=
  { substrate := HEP
    program   := TE }

/-- The kernel preserves the exact 3-constant substrate. -/
theorem isoKernel_substrate :
    isoKernel.substrate = HEP := by
  rfl

/-- The kernel preserves the exact ordered 2-operator program. -/
theorem isoKernel_program :
    isoKernel.program = TE := by
  rfl

/-- Slot 1 is Hydrogen. -/
theorem isoKernel_H :
    isoKernel.substrate.c1 = Constant.hydrogen := by
  rfl

/-- Slot 2 is Electrum. -/
theorem isoKernel_E :
    isoKernel.substrate.c2 = Constant.electrum := by
  rfl

/-- Slot 3 is Potassium. -/
theorem isoKernel_P :
    isoKernel.substrate.c3 = Constant.potassium := by
  rfl

/-- Operator 1 is Transmute. -/
theorem isoKernel_T :
    isoKernel.program.op1 = Operator.transmute := by
  rfl

/-- Operator 2 is Exchange. -/
theorem isoKernel_X :
    isoKernel.program.op2 = Operator.exchange := by
  rfl

/-
  Canonical reading:

      HEP :: TRANSMUTE :: EXCHANGE

      [ Hydrogen ][ Electrum ][ Potassium ]
                       ↓
                    Transmute
                       ↓
                     Exchange

  Distilled invariant:

      hold three → transmute → exchange
-/

end HEKATE
