namespace Oasis.TheGame.Gen03.Step08
structure AcceptedRecord where
  ordinal : Nat
  witnesses : Nat
  deriving Repr, DecidableEq
def appendRecord (ledger : List AcceptedRecord) (record : AcceptedRecord) : List AcceptedRecord :=
  ledger ++ [record]
def firstAccepted : AcceptedRecord := { ordinal := 1, witnesses := 3 }
theorem accepted_record_appends : (appendRecord [] firstAccepted).length = 1 := by decide
end Oasis.TheGame.Gen03.Step08
