import Std

/-
Oasis.GroundTruth.MitosisIso.00
================================

Bounded symbolic proof from:
  { /t/0\| + n | t+n ||
    start 0 :: on board . ::
    goal mitosis to :: 0.1 .. :: and 0.2 ... ::
    3 is all you need to Isomorph x 6 + 2 verify }

Interpretation kept intentionally small:
  * one start node: 0
  * two mitosis outputs: 0.1 and 0.2
  * total symbolic nodes: 3
  * isomorph width: 6
  * explicit verify count: 2
  * verify envelope: 3 * 6 + 2 = 20

The decimal-looking node labels are strings, not arithmetic values.
The transition glyph is preserved literally as symbolic notation.

NEW MODULE: not in confirmed 0e ledger until user compilation.
-/

namespace Oasis.GroundTruth.MitosisIso00

def transitionGlyph : String := "{ /t/0\\| + n | t+n || }"
def startLabel : String := "0"
def child1Label : String := "0.1 .."
def child2Label : String := "0.2 ..."
def groundTruthToken : String := "."
def onBoard : Bool := true

inductive Node where
  | root
  | child1
  | child2
  deriving DecidableEq, BEq, Repr

def nodes : List Node := [.root, .child1, .child2]
def daughters : List Node := [.child1, .child2]

def seedCount : Nat := 3
def isomorphWidth : Nat := 6
def verifyCount : Nat := 2

def verifyEnvelope : Nat :=
  seedCount * isomorphWidth + verifyCount

theorem start_is_on_board :
    onBoard = true := by
  rfl

theorem ground_truth_is_dot :
    groundTruthToken = "." := by
  rfl

theorem exactly_two_mitosis_outputs :
    daughters.length = 2 := by
  decide

theorem exactly_three_nodes :
    nodes.length = 3 := by
  decide

theorem one_parent_plus_two_outputs_is_three :
    1 + daughters.length = seedCount := by
  decide

theorem isomorph_width_is_six :
    isomorphWidth = 6 := by
  rfl

theorem two_verifiers :
    verifyCount = 2 := by
  rfl

theorem isomorph_x6_plus2_verify :
    verifyEnvelope = 20 := by
  decide

def mitosisIsoCheck : Bool :=
  onBoard &&
  (groundTruthToken == ".") &&
  (startLabel == "0") &&
  (child1Label == "0.1 ..") &&
  (child2Label == "0.2 ...") &&
  (nodes.length == 3) &&
  (daughters.length == 2) &&
  (seedCount == 3) &&
  (isomorphWidth == 6) &&
  (verifyCount == 2) &&
  (verifyEnvelope == 20)

theorem mitosis_iso_check_passes :
    mitosisIsoCheck = true := by
  decide

end Oasis.GroundTruth.MitosisIso00
