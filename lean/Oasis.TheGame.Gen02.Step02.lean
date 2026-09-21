namespace Oasis.TheGame.Gen02.Step02
def railWidth : Nat := 26
def totalRails : Nat := railWidth + railWidth
theorem rails_verified : totalRails = 52 := by decide
end Oasis.TheGame.Gen02.Step02
