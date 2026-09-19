import Std

/-!
Oasis.Language.OSI0.00
======================
Root0 / Layer 0.

Canonical Root0 boundary word:

  -+ 0 0 +-

Layer 0 owns the immutable intellectual-property / provenance root.
It does not interpret higher-layer language.

The two zeroes are the Root0 center.
The outer polarity is mirrored:
  -+ ... +-
-/

namespace Oasis.Language.OSI0

/-- Canonical Root0 literal. -/
def root0Word : String := "-+ 0 0 +-"

/-- Left polarity delimiter. -/
def leftPolarity : String := "-+"

/-- Root0 center. -/
def rootCenter : List Nat := [0, 0]

/-- Right mirrored polarity delimiter. -/
def rightPolarity : String := "+-"

/--
Minimal Layer-0 provenance anchor.
The token is opaque here: Layer 0 only pins it to Root0.
-/
structure IPAnchor where
  token : String
  deriving DecidableEq, Repr

/-- Bind an opaque provenance token to Root0. -/
def bindIP (token : String) : IPAnchor :=
  { token := token }

/-- Layer 0 never rewrites the provenance token. -/
def preserveIP (a : IPAnchor) : IPAnchor := a

theorem root0_literal :
    root0Word = "-+ 0 0 +-" := by
  rfl

theorem root_center_is_double_zero :
    rootCenter = [0, 0] := by
  rfl

theorem preserve_ip_identity (a : IPAnchor) :
    preserveIP a = a := by
  rfl

theorem bind_preserves_token (s : String) :
    (bindIP s).token = s := by
  rfl

/-- Executable closure check for Layer 0. -/
def osi0Check : Bool :=
  (root0Word == "-+ 0 0 +-") &&
  (leftPolarity == "-+") &&
  (rightPolarity == "+-") &&
  (rootCenter == [0, 0]) &&
  ((preserveIP (bindIP "ROOT0")).token == "ROOT0")

theorem osi0_check_passes :
    osi0Check = true := by
  decide

end Oasis.Language.OSI0