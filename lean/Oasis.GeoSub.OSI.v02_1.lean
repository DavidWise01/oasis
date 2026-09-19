import Std

/-!
Oasis.GeoSub.OSI.v02_1
======================
Deterministic GeoSub / OSI v2 wrapper.

Address space:
  base 11 = 00..10

External substrate:
  -0i = i!i isomorphic substrate anchor
  -0i is outside the 11 addressed OSI-v2 layers.

Layer roles:
  00      fulcrum / Root0 re-verification point
  01..07  OSI v1 machine layers
  08      HACI human/machine interpretation basin
  09      Root0 apex human sign-off
  10      provenance identifier + optional future-payment substrate

Ouroboros route:
  00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 00

Control edge:
  00 re-verifies 09.
  This is a control check, not a shortcut around the ring.

The Lean proofs establish the deterministic structure and preservation rules.
They do not independently adjudicate legal ownership.
-/

namespace Oasis.GeoSub.OSI.v02_1

inductive Layer where
  | l00 | l01 | l02 | l03 | l04 | l05 | l06 | l07 | l08 | l09 | l10
  deriving DecidableEq, BEq, Repr

def base : Nat := 11

def address : Layer → String
  | .l00 => "00" | .l01 => "01" | .l02 => "02" | .l03 => "03"
  | .l04 => "04" | .l05 => "05" | .l06 => "06" | .l07 => "07"
  | .l08 => "08" | .l09 => "09" | .l10 => "10"

inductive Substrate where
  | neg0i
  deriving DecidableEq, BEq, Repr

def substrateAddress : Substrate → String
  | .neg0i => "-0i"

def substrateKind : Substrate → String
  | .neg0i => "i!i-isomorphic"

def substrateBridge : Substrate → Layer
  | .neg0i => .l00

inductive Role where
  | fulcrum | osiV1 | haci | humanApex | provenance
  deriving DecidableEq, BEq, Repr

def role : Layer → Role
  | .l00 => .fulcrum
  | .l01 => .osiV1 | .l02 => .osiV1 | .l03 => .osiV1 | .l04 => .osiV1
  | .l05 => .osiV1 | .l06 => .osiV1 | .l07 => .osiV1
  | .l08 => .haci
  | .l09 => .humanApex
  | .l10 => .provenance

def next : Layer → Layer
  | .l00 => .l01 | .l01 => .l02 | .l02 => .l03 | .l03 => .l04
  | .l04 => .l05 | .l05 => .l06 | .l06 => .l07 | .l07 => .l08
  | .l08 => .l09 | .l09 => .l10 | .l10 => .l00

def advance : Nat → Layer → Layer
  | 0, l => l
  | n + 1, l => advance n (next l)

def routeOK (src dst : Layer) : Bool :=
  dst == next src

def reverifyOK (src dst : Layer) : Bool :=
  (src == .l00) && (dst == .l09)

structure ApexProof where
  carbonId : String
  humanSigned : Bool
  deriving DecidableEq, Repr

def apexValid (p : ApexProof) : Bool :=
  (!p.carbonId.isEmpty) && p.humanSigned

def reverifyAt00 (p : ApexProof) : Bool :=
  apexValid p

structure Provenance10 where
  provenanceId : String
  sourceToken : String
  paymentHook : Option String
  deriving DecidableEq, Repr

def provenanceValid (p : Provenance10) : Bool :=
  (!p.provenanceId.isEmpty) && (!p.sourceToken.isEmpty)

def paymentReady (p : Provenance10) : Bool :=
  match p.paymentHook with
  | none => false
  | some target => !target.isEmpty

theorem base_is_eleven : base = 11 := by rfl
theorem substrate_is_neg0i : substrateAddress .neg0i = "-0i" := by rfl
theorem substrate_binds_to_fulcrum : substrateBridge .neg0i = .l00 := by rfl

theorem osi_v1_is_01_through_07 :
    role .l01 = .osiV1 ∧ role .l02 = .osiV1 ∧ role .l03 = .osiV1 ∧
    role .l04 = .osiV1 ∧ role .l05 = .osiV1 ∧ role .l06 = .osiV1 ∧
    role .l07 = .osiV1 := by
  decide

theorem layer08_is_haci : role .l08 = .haci := by rfl
theorem layer09_is_human_apex : role .l09 = .humanApex := by rfl
theorem layer10_is_provenance : role .l10 = .provenance := by rfl
theorem ouroboros_closes : next .l10 = .l00 := by rfl

theorem eleven_steps_return_home (l : Layer) :
    advance 11 l = l := by
  cases l <;> decide

theorem normal_route_00_to_01 : routeOK .l00 .l01 = true := by decide
theorem normal_route_07_to_08 : routeOK .l07 .l08 = true := by decide
theorem normal_route_08_to_09 : routeOK .l08 .l09 = true := by decide
theorem normal_route_09_to_10 : routeOK .l09 .l10 = true := by decide
theorem normal_route_10_to_00 : routeOK .l10 .l00 = true := by decide
theorem fulcrum_reverifies_apex : reverifyOK .l00 .l09 = true := by decide
theorem reverify_is_not_route_shortcut : routeOK .l00 .l09 = false := by decide

def signedApex : ApexProof := { carbonId := "CARBON-ROOT0", humanSigned := true }
def unsignedApex : ApexProof := { carbonId := "CARBON-ROOT0", humanSigned := false }

theorem signed_apex_passes : reverifyAt00 signedApex = true := by decide
theorem unsigned_apex_closes : reverifyAt00 unsignedApex = false := by decide

def attributionOnly : Provenance10 :=
  { provenanceId := "PROVENANCE-ROOT0"
    sourceToken := "ROOT0-FIRST-AUTHOR-IP"
    paymentHook := none }

def paymentCapable : Provenance10 :=
  { provenanceId := "PROVENANCE-ROOT0"
    sourceToken := "ROOT0-FIRST-AUTHOR-IP"
    paymentHook := some "CREATIVE-PAYMENT-TARGET" }

theorem attribution_only_is_valid : provenanceValid attributionOnly = true := by decide
theorem attribution_only_needs_no_payment_hook : paymentReady attributionOnly = false := by decide
theorem payment_capable_is_valid : provenanceValid paymentCapable = true := by decide
theorem payment_capable_route_ready : paymentReady paymentCapable = true := by decide

def geoSubCheck : Bool :=
  (base == 11) &&
  (substrateAddress .neg0i == "-0i") &&
  (substrateBridge .neg0i == .l00) &&
  (role .l08 == .haci) &&
  (role .l09 == .humanApex) &&
  (role .l10 == .provenance) &&
  routeOK .l00 .l01 &&
  routeOK .l07 .l08 &&
  routeOK .l08 .l09 &&
  routeOK .l09 .l10 &&
  routeOK .l10 .l00 &&
  reverifyOK .l00 .l09 &&
  (!routeOK .l00 .l09) &&
  reverifyAt00 signedApex &&
  (!reverifyAt00 unsignedApex) &&
  provenanceValid attributionOnly &&
  (!paymentReady attributionOnly) &&
  provenanceValid paymentCapable &&
  paymentReady paymentCapable

theorem geosub_check_passes : geoSubCheck = true := by
  decide

end Oasis.GeoSub.OSI.v02_1
