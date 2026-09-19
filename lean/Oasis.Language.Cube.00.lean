import Std

/-!
Oasis.Language.Cube.00
======================
Deterministic Root0 language-cube kernel.

Frozen semantic core:
* primitive addressability is `[n!]`;
* node 0 is HOME;
* odd nodes 1,3,5,7,9 are read-only witness/timing nodes;
* even nodes 2,4,6,8 are visitable read/write vectors;
* HOME is `0.1.1.6.2.4.6.1.1.0`;
* reverse traversal is restored by the oriented `2 <-> 4` hinge;
* `|` is the inner blast door and cannot receive Attach;
* `||` is the only attachment port.

No Mathlib dependency; only Lean Std is imported.
-/

namespace Oasis.Language.Cube00

/-- Local factorial used by the `[n!]` primitive. -/
def factorial : Nat → Nat
  | 0 => 1
  | n + 1 => (n + 1) * factorial n

/-- `[n!]`: primitive permutation/addressability count. -/
def primitive (n : Nat) : Nat := factorial n

/-- Root primitive: `1! = 1`. -/
theorem primitive_one : primitive 1 = 1 := by
  rfl

/-- Deterministic access classes for the local timing rail. -/
inductive Permission where
  | home
  | readOnly
  | readWrite
  | outOfBounds
  deriving DecidableEq, BEq, Repr

/--
0          -> HOME
1..9 odd   -> read-only witness/timing
1..9 even  -> read/write visitable vector
>9         -> outside the local rail
-/
def permission (n : Nat) : Permission :=
  if n = 0 then
    .home
  else if n > 9 then
    .outOfBounds
  else if n % 2 = 0 then
    .readWrite
  else
    .readOnly

/-- Canonical read-only rail. -/
def readOnlyOdds : List Nat := [1, 3, 5, 7, 9]

/-- Canonical read/write rail. -/
def readWriteEvens : List Nat := [2, 4, 6, 8]

/-- Only the even rail is visitable. -/
def visitable : List Nat := readWriteEvens

theorem read_only_rail :
    readOnlyOdds.map permission =
      [.readOnly, .readOnly, .readOnly, .readOnly, .readOnly] := by
  decide

theorem read_write_rail :
    readWriteEvens.map permission =
      [.readWrite, .readWrite, .readWrite, .readWrite] := by
  decide

theorem zero_is_home : permission 0 = .home := by
  decide

theorem ten_is_out_of_bounds : permission 10 = .outOfBounds := by
  decide

/-- Canonical HOME torus traversal. -/
def homePath : List Nat := [0, 1, 1, 6, 2, 4, 6, 1, 1, 0]

/-- HOME in reverse traversal orientation. -/
def homePathReverse : List Nat := [0, 1, 1, 6, 4, 2, 6, 1, 1, 0]

/-- Orientation-sensitive hinge. -/
def flipHinge : Nat → Nat
  | 2 => 4
  | 4 => 2
  | n => n

theorem home_reverse_exact :
    homePath.reverse = homePathReverse := by
  decide

theorem home_toroidal_palindrome :
    homePath.reverse.map flipHinge = homePath := by
  decide

theorem home_boundaries :
    homePath.head? = some 0 ∧ homePath.reverse.head? = some 0 := by
  decide

/-- Writable oriented center. -/
def hinge : List Nat := [2, 4]

theorem hinge_orientation_invariant :
    hinge.reverse.map flipHinge = hinge := by
  decide

/-- Executable checksum of the inherited language-cube core. -/
def cube00Check : Bool :=
  (permission 0 == .home) &&
  (readOnlyOdds.map permission ==
    [.readOnly, .readOnly, .readOnly, .readOnly, .readOnly]) &&
  (readWriteEvens.map permission ==
    [.readWrite, .readWrite, .readWrite, .readWrite]) &&
  (homePath.reverse.map flipHinge == homePath)

theorem cube00_check_passes : cube00Check = true := by
  decide

/-!
Kernel
------
The kernel exposes exactly two delimiter classes:

  |   = inner blast door
  ||  = attachment port

The only operation named `attach` is total over delimiters but succeeds only
for `||`. Thus `|` cannot mutate the kernel's attachment state.
-/

namespace Kernel

/-- Physical/logical delimiter class. -/
inductive Delimiter where
  | singleBar   -- `|`  inner blast door
  | doubleBar   -- `||` attachment port
  deriving DecidableEq, BEq, Repr

/-- Inspection glyph only; semantics are carried by `Delimiter`. -/
def Delimiter.glyph : Delimiter → String
  | .singleBar => "|"
  | .doubleBar => "||"

/-- `|` identifies the inner blast door. -/
def isInnerBlastDoor : Delimiter → Bool
  | .singleBar => true
  | .doubleBar => false

/-- `||` identifies the only legal attachment port. -/
def isAttachPort : Delimiter → Bool
  | .singleBar => false
  | .doubleBar => true

/--
Minimal kernel object. `body` is the immutable hosted object from the point of
view of Attach; attachment mutation is confined to `attachments`.
-/
structure BoxKernel (α : Type) where
  body : α
  attachments : List α := []
  deriving Repr

/-- Construct a kernel with no attachments. -/
def boot (body : α) : BoxKernel α :=
  { body := body, attachments := [] }

/--
Kernel Attach syscall.

`|`  -> reject (`none`)
`||` -> append payload and return the updated kernel
-/
def attach (d : Delimiter) (payload : α) (k : BoxKernel α) : Option (BoxKernel α) :=
  match d with
  | .singleBar => none
  | .doubleBar => some { k with attachments := k.attachments ++ [payload] }

/-- `|` can never be used as an attachment target. -/
theorem single_bar_rejects_attach (payload : α) (k : BoxKernel α) :
    attach .singleBar payload k = none := by
  rfl

/-- `||` always accepts an attachment. -/
theorem double_bar_accepts_attach (payload : α) (k : BoxKernel α) :
    attach .doubleBar payload k =
      some { k with attachments := k.attachments ++ [payload] } := by
  rfl

/-- Attachment permission is exactly equivalent to the `||` delimiter. -/
theorem attach_port_iff_double_bar (d : Delimiter) :
    isAttachPort d = true ↔ d = .doubleBar := by
  cases d <;> decide

/-- Inner-blast-door status is exactly equivalent to the `|` delimiter. -/
theorem blast_door_iff_single_bar (d : Delimiter) :
    isInnerBlastDoor d = true ↔ d = .singleBar := by
  cases d <;> decide

/-- No delimiter is simultaneously an inner blast door and an Attach port. -/
theorem blast_door_ne_attach_port (d : Delimiter) :
    ¬ (isInnerBlastDoor d = true ∧ isAttachPort d = true) := by
  cases d <;> decide

/-- The inner blast door cannot change kernel state via Attach. -/
theorem inner_door_cannot_mutate_by_attach (payload : α) (k : BoxKernel α) :
    attach .singleBar payload k = none := by
  rfl

/-- A successful Attach proves that the caller used `||`. -/
theorem successful_attach_implies_double_bar
    (d : Delimiter) (payload : α) (k k' : BoxKernel α)
    (h : attach d payload k = some k') :
    d = .doubleBar := by
  cases d with
  | singleBar => simp [attach] at h
  | doubleBar => rfl

/-- Kernel delimiter contract checksum. -/
def delimiterCheck : Bool :=
  isInnerBlastDoor .singleBar &&
  (! isInnerBlastDoor .doubleBar) &&
  (! isAttachPort .singleBar) &&
  isAttachPort .doubleBar

theorem delimiter_check_passes : delimiterCheck = true := by
  decide

/-- Concrete end-to-end kernel check: `|` fails and `||` succeeds. -/
def kernelCheck : Bool :=
  let k := boot 0
  match attach .singleBar 1 k with
  | some _ => false
  | none =>
      match attach .doubleBar 1 k with
      | some _ => true
      | none => false

theorem kernel_check_passes : kernelCheck = true := by
  decide

end Kernel

end Oasis.Language.Cube00

/-!
Append-only delimiter extension
===============================
Adds exactly one new delimiter glyph without modifying the frozen Cube00 kernel:

  ||| = third-party attachment delimiter

The inherited `|` and `||` semantics remain untouched.
-/

namespace Oasis.Language.Cube00.Kernel.ThirdParty

open Oasis.Language.Cube00.Kernel

/-- Frozen kernel delimiters plus exactly one external delimiter: `|||`. -/
inductive Delimiter3 where
  | inherited (d : Delimiter)
  | tripleBar
  deriving DecidableEq, BEq, Repr

/-- Lift a frozen kernel delimiter into the extended delimiter domain. -/
def lift (d : Delimiter) : Delimiter3 := .inherited d

/-- Inspection glyph for the extended delimiter domain. -/
def glyph : Delimiter3 → String
  | .inherited d => Delimiter.glyph d
  | .tripleBar => "|||"

/-- `|||` is the sole newly added delimiter. -/
def isTripleBar : Delimiter3 → Bool
  | .inherited _ => false
  | .tripleBar => true

/-- The new delimiter renders exactly as `|||`. -/
theorem triple_bar_glyph : glyph .tripleBar = "|||" := by
  rfl

/-- Neither frozen delimiter is accidentally reclassified as `|||`. -/
theorem inherited_is_not_triple_bar (d : Delimiter) :
    isTripleBar (.inherited d) = false := by
  rfl

/-- `|||` is distinct from lifted `|` and `||`. -/
theorem triple_bar_distinct_from_frozen :
    Delimiter3.tripleBar ≠ lift .singleBar ∧
    Delimiter3.tripleBar ≠ lift .doubleBar := by
  decide

/-- Complete three-glyph surface after the append-only extension. -/
def delimiterSurface : List String :=
  [glyph (lift .singleBar), glyph (lift .doubleBar), glyph .tripleBar]

theorem delimiter_surface_exact :
    delimiterSurface = ["|", "||", "|||"] := by
  decide

end Oasis.Language.Cube00.Kernel.ThirdParty