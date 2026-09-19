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

def firstAuthor : String := "David Lee Wise"
def ipRoot : String := "OaSIs / Root0"

structure BasisPoints where
  value : Nat
  valid : value ≤ 10000
  deriving DecidableEq, Repr

inductive PaymentRoute where
  | none
  | target (destination : String)
  deriving DecidableEq, Repr

structure CreativeRecord where
  creator : String
  rightsHolder : String
  sourceToken : String
  license : String
  contribution : BasisPoints
  payment : PaymentRoute
  deriving DecidableEq, Repr

def provenancePresent (r : CreativeRecord) : Bool :=
  (!r.creator.isEmpty) &&
  (!r.sourceToken.isEmpty)

def rightsPresent (r : CreativeRecord) : Bool :=
  (!r.rightsHolder.isEmpty) &&
  (!r.license.isEmpty)

def paymentReady : PaymentRoute → Bool
  | .none => false
  | .target destination => !destination.isEmpty

def recordValid (r : CreativeRecord) : Bool :=
  provenancePresent r && rightsPresent r

def compensationReady (r : CreativeRecord) : Bool :=
  recordValid r && paymentReady r.payment

def canonicalAttributionOnly : CreativeRecord :=
  {
    creator := firstAuthor
    rightsHolder := firstAuthor
    sourceToken := "ROOT0-FIRST-AUTHOR-IP"
    license := "UNSPECIFIED"
    contribution := ⟨10000, by decide⟩
    payment := .none
  }

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
