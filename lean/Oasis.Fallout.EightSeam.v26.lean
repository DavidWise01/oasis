/-
OASIS Eight-Seam v26 — standalone structural module
Date: 2026-10-07

Preserves only the executable boundary/probe structure from
"The Atom Over the Box — eight seams".
No physical atom/sandbox equivalence is asserted.
-/

namespace OASIS.EightSeamV26

inductive SeamAxis where
  | edgeMidE | cornerSE | edgeMidS | cornerSW
  | edgeMidW | cornerNW | edgeMidN | cornerNE
deriving DecidableEq, Repr

def allEightSeams : List SeamAxis :=
  [ .edgeMidE, .cornerSE, .edgeMidS, .cornerSW
  , .edgeMidW, .cornerNW, .edgeMidN, .cornerNE ]

theorem eight_seam_count : allEightSeams.length = 8 := by
  decide

def oppositeSeam : SeamAxis → SeamAxis
  | .edgeMidE => .edgeMidW
  | .cornerSE => .cornerNW
  | .edgeMidS => .edgeMidN
  | .cornerSW => .cornerNE
  | .edgeMidW => .edgeMidE
  | .cornerNW => .cornerSE
  | .edgeMidN => .edgeMidS
  | .cornerNE => .cornerSW

theorem opposite_seam_involution (s : SeamAxis) :
    oppositeSeam (oppositeSeam s) = s := by
  cases s <;> rfl

inductive ProbeShell where
  | e | p | g
deriving DecidableEq, Repr

def palindromicProbeSpine : List ProbeShell :=
  [.e, .p, .g, .g, .p, .e]

theorem probe_spine_is_palindrome :
    palindromicProbeSpine.reverse = palindromicProbeSpine := by
  decide

def probeSpineCenterPair : List ProbeShell :=
  palindromicProbeSpine.drop 2 |>.take 2

theorem probe_spine_center_is_g_join :
    probeSpineCenterPair = [.g, .g] := by
  decide

structure ProbeRadii where
  surface  : Nat
  photon   : Nat
  softTurn : Nat
  hardTurn : Nat
  core     : Nat
deriving DecidableEq, Repr

def sourceProbeRadii : ProbeRadii :=
  { surface := 1000
    photon := 660
    softTurn := 380
    hardTurn := 112
    core := 70 }

theorem source_probe_radius_order :
    sourceProbeRadii.core < sourceProbeRadii.hardTurn ∧
    sourceProbeRadii.hardTurn < sourceProbeRadii.softTurn ∧
    sourceProbeRadii.softTurn < sourceProbeRadii.photon ∧
    sourceProbeRadii.photon < sourceProbeRadii.surface := by
  decide

inductive ProbeHardness where
  | soft | hard
deriving DecidableEq, Repr

def probeTurnRadius : ProbeHardness → Nat
  | .soft => sourceProbeRadii.softTurn
  | .hard => sourceProbeRadii.hardTurn

def probeReachesCore (h : ProbeHardness) : Bool :=
  decide (probeTurnRadius h ≤ sourceProbeRadii.core)

theorem neither_probe_reaches_core :
    probeReachesCore .soft = false ∧
    probeReachesCore .hard = false := by
  decide

end OASIS.EightSeamV26
