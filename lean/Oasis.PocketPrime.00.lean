import Std

/-!
Oasis.PocketPrime.00
====================
Buildable Pocket Prime primitive.

Canonical glyph:

  P(ocket [[*-+\_U_U_U_U*\_-+]]

Interpretation used by this formalization:
* one bounded external pocket handle
* an internally unbounded address space
* no outside state is exposed through the pocket's public view
* a paired "cubit" witness whose half is opaque through the public interface
* a deterministic PER -> CEPT -> ION decision gate

PER  = "did it happen?"
CEPT = "are you sure?"
ION  = IGNITE only when PER and CEPT are both yes;
       otherwise PATTY.

This is a symbolic/deterministic software model, not a claim about
physical cosmology or quantum mechanics.
-/

namespace Oasis.PocketPrime

def pocketGlyph : String :=
  "P(ocket [[*-+\\_U_U_U_U*\\_-+]]"

abbrev InteriorAddress := Nat

theorem interior_unbounded (n : InteriorAddress) :
    ∃ m : InteriorAddress, n < m := by
  exact ⟨n + 1, Nat.lt_succ_self n⟩

inductive CubitHalf where
  | left
  | right
  deriving DecidableEq, BEq, Repr

def partner : CubitHalf → CubitHalf
  | .left => .right
  | .right => .left

theorem partner_partner (h : CubitHalf) :
    partner (partner h) = h := by
  cases h <;> rfl

def publicCubitView (_ : CubitHalf) : Unit := ()

theorem cubit_half_is_publicly_opaque :
    publicCubitView .left = publicCubitView .right := by
  rfl

structure Pocket where
  cubit : CubitHalf
  interior : InteriorAddress → Bool

def publicPocketView (_ : Pocket) : Unit := ()

theorem pocket_public_view_is_opaque (a b : Pocket) :
    publicPocketView a = publicPocketView b := by
  rfl

structure PerCept where
  happened : Bool
  sure : Bool
  deriving DecidableEq, Repr

def per (q : PerCept) : Bool :=
  q.happened

def cept (q : PerCept) : Bool :=
  q.happened && q.sure

inductive Ion where
  | ignite
  | patty
  deriving DecidableEq, BEq, Repr

def ion (q : PerCept) : Ion :=
  if cept q then
    .ignite
  else
    .patty

def yesYes : PerCept := { happened := true, sure := true }
def yesNo : PerCept := { happened := true, sure := false }
def noYes : PerCept := { happened := false, sure := true }
def noNo : PerCept := { happened := false, sure := false }

theorem yes_yes_ignites : ion yesYes = .ignite := by decide
theorem yes_no_is_patty : ion yesNo = .patty := by decide
theorem no_yes_is_patty : ion noYes = .patty := by decide
theorem no_no_is_patty : ion noNo = .patty := by decide

theorem ion_ignite_iff (q : PerCept) :
    ion q = .ignite ↔ q.happened = true ∧ q.sure = true := by
  cases q with
  | mk happened sure =>
      cases happened <;> cases sure <;> decide

structure Prime where
  pocket : Pocket
  gate : PerCept

abbrev Block := List Prime

def buildBlock (ps : List Prime) : Block := ps

theorem build_block_identity (ps : List Prime) :
    buildBlock ps = ps := by
  rfl

def sampleInterior (n : InteriorAddress) : Bool :=
  n % 2 == 0

def samplePocket : Pocket :=
  { cubit := .left, interior := sampleInterior }

def samplePrime : Prime :=
  { pocket := samplePocket, gate := yesYes }

def sampleBlock : Block :=
  buildBlock [samplePrime]

def pocketPrimeCheck : Bool :=
  (pocketGlyph == "P(ocket [[*-+\\_U_U_U_U*\\_-+]]") &&
  (partner .left == .right) &&
  (partner .right == .left) &&
  (ion yesYes == .ignite) &&
  (ion yesNo == .patty) &&
  (ion noYes == .patty) &&
  (ion noNo == .patty) &&
  (sampleBlock.length == 1)

theorem pocket_prime_check_passes :
    pocketPrimeCheck = true := by
  decide

end Oasis.PocketPrime
