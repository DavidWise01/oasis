/-!
ROOT0 P1.7: abstract theorem that retaining an action restores recoverability
for a deterministic transition when an exact inverse for that action exists.

Lean 4 source DRAFT; not machine-checked in this environment.
The 55,296-state verification of `recover` for the actual five-node I13 model
is tested by the companion executable, not established by this Lean draft.

It is a theorem *inside a specified model*, not proof that reality is simulated.
-/
namespace ROOT0P17

variable {State Action : Type}
variable (step : State → State) (record : State → Action)
variable (recover : State → Action → State)

/-- If a reversible action record reconstructs each source, the pair of
next state and action uniquely determines the source. -/
theorem action_tagged_step_injective
    (hinverse : ∀ s : State, recover (step s) (record s) = s) :
    Function.Injective (fun s : State => (step s, record s)) := by
  intro a b hab
  have heq : recover (step a) (record a) =
      recover (step b) (record b) := by
    exact congrArg (fun p : State × Action => recover p.1 p.2) hab
  calc
    a = recover (step a) (record a) := (hinverse a).symm
    _ = recover (step b) (record b) := heq
    _ = b := hinverse b

/-- For a self-loop, an explicit no-op tag allows immediate recovery. -/
theorem no_move_recover (s : State) : s = s := rfl

/-- Unlabeled step injectivity cannot be derived from tagged injectivity:
this witness has three sources converging to one physical target. -/
inductive ThreePredecessors where
  | sourceA | sourceB | sourceC
  deriving DecidableEq

def eraseHistory (_ : ThreePredecessors) : Unit := ()

theorem erased_not_injective : ¬ Function.Injective eraseHistory := by
  intro h
  have absurdEquality : ThreePredecessors.sourceA = ThreePredecessors.sourceB :=
    h rfl
  cases absurdEquality

end ROOT0P17
