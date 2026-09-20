import Std

/-
Oasis.KANA.Isomorph.00
======================

Append-only KANA isomorphic carrier.

Canonical glyph:
  + k < | A | /\ | N | /\/ | A | /\ | >-K

"Entangled" here means a software invariant-preservation relation between
layer bindings. It does not denote physical quantum entanglement.

This module is NEW and is not added to the user-confirmed 0e ledger until
the user compiles it successfully.
-/

namespace Oasis.KANA.Isomorph00

def glyph : String := "+ k < | A | /\\ | N | /\\/ | A | /\\ | >-K"

inductive Anchor where
  | leftA
  | neutralN
  | rightA
  deriving DecidableEq, BEq, Repr

def mirrorAnchor : Anchor → Anchor
  | .leftA => .rightA
  | .neutralN => .neutralN
  | .rightA => .leftA

theorem mirror_anchor_involution (a : Anchor) :
    mirrorAnchor (mirrorAnchor a) = a := by
  cases a <;> rfl

structure LayerBinding where
  layer : String
  leftAnchor : String
  invariant : String
  rightAnchor : String
  returnWitness : String
  isoPreserved : Bool
  deriving DecidableEq, Repr

def bind
    (layer leftAnchor invariant rightAnchor returnWitness : String) :
    LayerBinding :=
  {
    layer := layer
    leftAnchor := leftAnchor
    invariant := invariant
    rightAnchor := rightAnchor
    returnWitness := returnWitness
    isoPreserved := true
  }

def layers : List LayerBinding :=
  [
    bind "ROOT0/O1" "requested state" "root/provenance identity" "emitted state" "lineage check",
    bind "ISO |" "source representation" "semantic invariant" "target representation" "round-trip check",
    bind "HUMAN/CARBON ||" "authored intent" "provenance" "attached artifact" "attribution witness",
    bind "NEON |||" "engine input" "contract/invariant" "engine output" "deterministic check",
    bind "ELECTRONICS" "input signal/state" "threshold/logical state" "output signal/state" "measurement",
    bind "NETWORKING" "sender meaning" "message/payload identity" "receiver meaning" "ACK/hash/trace",
    bind "STORAGE" "logical object" "block/integrity identity" "recovered object" "readback/hash",
    bind "JAVA" "source/runtime intent" "typed/behavioral invariant" "observed behavior" "return/test/exception",
    bind "FENG_SHUI" "occupant/use intent" "spatial fit invariant" "experienced arrangement" "observation/rearrangement",
    bind "ART_BEAUTY" "creative intent" "composition/read invariant" "viewer-facing artifact" "perception/critique",
    bind "ATTACHMENT" "user brief" "attachment contract" "domain result" "provenance/export"
  ]

def allPreserve : List LayerBinding → Bool
  | [] => true
  | x :: xs => x.isoPreserved && allPreserve xs

def entangled (a b : LayerBinding) : Bool :=
  a.isoPreserved &&
  b.isoPreserved &&
  (!a.invariant.isEmpty) &&
  (!b.invariant.isEmpty)

theorem kana_has_eleven_layer_bindings :
    layers.length = 11 := by
  decide

theorem kana_all_layers_preserve :
    allPreserve layers = true := by
  decide

theorem root_iso_entangled :
    entangled
      (bind "ROOT0/O1" "requested state" "root/provenance identity" "emitted state" "lineage check")
      (bind "ISO |" "source representation" "semantic invariant" "target representation" "round-trip check") = true := by
  decide

def kanaCheck : Bool :=
  (glyph == "+ k < | A | /\\ | N | /\\/ | A | /\\ | >-K") &&
  (layers.length == 11) &&
  allPreserve layers

theorem kana_check_passes :
    kanaCheck = true := by
  decide

end Oasis.KANA.Isomorph00
