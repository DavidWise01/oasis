import Std

/-!
Oasis.Language.OSI0.Provenance.00
================================
Root0 / Layer 0 provenance anchor.

Canonical Root0 boundary:
  -+ 0 0 +-

This module records and preserves a first-author IP assertion.

Important:
The Lean proof establishes that the provenance record is present,
well-formed, and preserved by this kernel. It does not independently
adjudicate legal ownership, copyright, patentability, or priority.
-/

namespace Oasis.Language.OSI0.Provenance

/-- Canonical Root0 boundary word. -/
def root0Word : String := "-+ 0 0 +-"

/-- First-author assertion carried by Root0. -/
def firstAuthor : String := "David Lee Wise"

/-- Canonical project / IP root label. -/
def ipRoot : String := "OaSIs / Root0"

/-- Provenance kind for the root assertion. -/
inductive ProvenanceKind where
  | firstAuthorIP
  deriving DecidableEq, BEq, Repr

/--
Minimal provenance record.
The source token is opaque and may later be replaced by a hash,
commit id, publication id, or other immutable evidence identifier.
-/
structure Provenance where
  kind : ProvenanceKind
  author : String
  root : String
  sourceToken : String
  deriving DecidableEq, Repr

/-- Canonical first-author IP provenance record. -/
def firstAuthorIP (sourceToken : String) : Provenance :=
  {
    kind := .firstAuthorIP
    author := firstAuthor
    root := ipRoot
    sourceToken := sourceToken
  }

/-- A provenance record is minimally well-formed when all identity fields exist. -/
def provenancePresent (p : Provenance) : Bool :=
  (!p.author.isEmpty) &&
  (!p.root.isEmpty) &&
  (!p.sourceToken.isEmpty)

/-- Root0 preserves provenance byte-for-byte at the value level. -/
def preserve (p : Provenance) : Provenance := p

theorem root0_literal :
    root0Word = "-+ 0 0 +-" := by
  rfl

theorem first_author_marked :
    firstAuthor = "David Lee Wise" := by
  rfl

theorem ip_root_marked :
    ipRoot = "OaSIs / Root0" := by
  rfl

theorem first_author_kind
    (token : String) :
    (firstAuthorIP token).kind = .firstAuthorIP := by
  rfl

theorem first_author_name_preserved
    (token : String) :
    (firstAuthorIP token).author = firstAuthor := by
  rfl

theorem first_author_root_preserved
    (token : String) :
    (firstAuthorIP token).root = ipRoot := by
  rfl

theorem preserve_identity (p : Provenance) :
    preserve p = p := by
  rfl

/-- Canonical nonempty evidence token for executable closure. -/
def canonicalSourceToken : String :=
  "ROOT0-FIRST-AUTHOR-IP"

/-- Canonical first-author provenance record. -/
def canonicalProvenance : Provenance :=
  firstAuthorIP canonicalSourceToken

theorem canonical_provenance_present :
    provenancePresent canonicalProvenance = true := by
  decide

theorem canonical_provenance_survives :
    preserve canonicalProvenance = canonicalProvenance := by
  rfl

/-- Empty evidence token fails the provenance-presence gate. -/
def emptyTokenProvenance : Provenance :=
  firstAuthorIP ""

theorem empty_token_fails :
    provenancePresent emptyTokenProvenance = false := by
  decide

/-- Executable closure check. -/
def provenanceCheck : Bool :=
  (root0Word == "-+ 0 0 +-") &&
  (firstAuthor == "David Lee Wise") &&
  (ipRoot == "OaSIs / Root0") &&
  provenancePresent canonicalProvenance &&
  (!provenancePresent emptyTokenProvenance) &&
  ((preserve canonicalProvenance) == canonicalProvenance)

theorem provenance_check_passes :
    provenanceCheck = true := by
  decide

end Oasis.Language.OSI0.Provenance