import Std

/-!
Oasis.Language.OSI0.CreativeSubstrate.00
=======================================
Root0 creative-rights and future-payment substrate.

Purpose:
* preserve provenance
* distinguish creator, rights holder, license, contribution, and payment route
* allow attribution and rights records to exist even when no payment route is present
* make future compensation possible without making payment mandatory

This module does NOT decide legal ownership or payment amounts.
It provides deterministic infrastructure for recording and routing them.
-/

namespace Oasis.Language.OSI0.CreativeSubstrate

/-- Canonical Root0 first-author assertion. -/
def firstAuthor : String := "David Lee Wise"

/-- Canonical project root. -/
def ipRoot : String := "OaSIs / Root0"

/-- Contribution weight in basis points: 0..10000. -/
structure BasisPoints where
  value : Nat
  valid : value ≤ 10000
  deriving DecidableEq, Repr

/-- Optional payment destination. Absence is valid and means attribution-only for now. -/
inductive PaymentRoute where
  | none
  | target (destination : String)
  deriving DecidableEq, Repr

/--
Creative rights record.

These are intentionally separate fields:
creator      ≠ rights holder
rights holder ≠ license
license      ≠ contribution weight
contribution ≠ payment destination
-/
structure CreativeRecord where
  creator : String
  rightsHolder : String
  sourceToken : String
  license : String
  contribution : BasisPoints
  payment : PaymentRoute
  deriving DecidableEq, Repr

/-- Identity/provenance fields required for any record. -/
def provenancePresent (r : CreativeRecord) : Bool :=
  (!r.creator.isEmpty) &&
  (!r.sourceToken.isEmpty)

/-- Rights fields required for a record to be actionable. -/
def rightsPresent (r : CreativeRecord) : Bool :=
  (!r.rightsHolder.isEmpty) &&
  (!r.license.isEmpty)

/-- A payment route is ready only if it names a nonempty destination. -/
def paymentReady : PaymentRoute → Bool
  | .none => false
  | .target destination => !destination.isEmpty

/-- Record validity does not depend on payment being configured. -/
def recordValid (r : CreativeRecord) : Bool :=
  provenancePresent r && rightsPresent r

/-- Compensation can be routed only when the record is valid and a route exists. -/
def compensationReady (r : CreativeRecord) : Bool :=
  recordValid r && paymentReady r.payment

/-- Canonical first-author record with no payment route required. -/
def canonicalAttributionOnly : CreativeRecord :=
  {
    creator := firstAuthor
    rightsHolder := firstAuthor
    sourceToken := "ROOT0-FIRST-AUTHOR-IP"
    license := "UNSPECIFIED"
    contribution := ⟨10000, by decide⟩
    payment := .none
  }

/-- Same record with a future payment target attached. -/
def canonicalPaymentReady : CreativeRecord :=
  {
    creator := firstAuthor
    rightsHolder := firstAuthor
    sourceToken := "ROOT0-FIRST-AUTHOR-IP"
    license := "UNSPECIFIED"
    contribution := ⟨10000, by decide⟩
    payment := .target "CREATIVE-PAYMENT-TARGET"
  }

theorem creator_is_first_author :
    canonicalAttributionOnly.creator = firstAuthor := by
  rfl

theorem attribution_only_record_is_valid :
    recordValid canonicalAttributionOnly = true := by
  decide

theorem attribution_only_does_not_require_payment :
    compensationReady canonicalAttributionOnly = false := by
  decide

theorem payment_ready_record_is_valid :
    recordValid canonicalPaymentReady = true := by
  decide

theorem payment_ready_record_can_route :
    compensationReady canonicalPaymentReady = true := by
  decide

/-- Empty payment destination never becomes routable. -/
def emptyPaymentTarget : CreativeRecord :=
  {
    creator := firstAuthor
    rightsHolder := firstAuthor
    sourceToken := "ROOT0-FIRST-AUTHOR-IP"
    license := "UNSPECIFIED"
    contribution := ⟨10000, by decide⟩
    payment := .target ""
  }

theorem empty_payment_target_is_not_ready :
    compensationReady emptyPaymentTarget = false := by
  decide

/-- Provenance failure closes the entire rights/payment substrate. -/
def missingSource : CreativeRecord :=
  {
    creator := firstAuthor
    rightsHolder := firstAuthor
    sourceToken := ""
    license := "UNSPECIFIED"
    contribution := ⟨10000, by decide⟩
    payment := .target "CREATIVE-PAYMENT-TARGET"
  }

theorem missing_source_is_invalid :
    recordValid missingSource = false := by
  decide

theorem missing_source_cannot_route_payment :
    compensationReady missingSource = false := by
  decide

/-- Deterministic closure check. -/
def creativeSubstrateCheck : Bool :=
  (firstAuthor == "David Lee Wise") &&
  (ipRoot == "OaSIs / Root0") &&
  recordValid canonicalAttributionOnly &&
  (!compensationReady canonicalAttributionOnly) &&
  recordValid canonicalPaymentReady &&
  compensationReady canonicalPaymentReady &&
  (!compensationReady emptyPaymentTarget) &&
  (!recordValid missingSource) &&
  (!compensationReady missingSource)

theorem creative_substrate_check_passes :
    creativeSubstrateCheck = true := by
  decide

end Oasis.Language.OSI0.CreativeSubstrate