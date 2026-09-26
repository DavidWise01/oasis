namespace AmazonionRootPlusV0

/-
  AMAZONION ROOT+ CORPUS v0
  Historical/ecological claims are documented in the companion Markdown.
  This file preserves only the symbolic corpus/index structure.
-/

def primitive : String :=
  "w{{ind}}.a{{rgon}}.t{{ime}}.e{{lectrum}}.r{{e-agent}}"

def outerWord : String := "WATER"

theorem primitive_exact :
    primitive = "w{{ind}}.a{{rgon}}.t{{ime}}.e{{lectrum}}.r{{e-agent}}" := by
  rfl

theorem outer_word_exact : outerWord = "WATER" := by
  rfl

inductive CorpusLayer where
  | hydrology
  | cultivation
  | darkEarth
  | earthwork
  | settlement
  | exchange
  | materialCulture
  | continuingPeoples
  deriving Repr, DecidableEq

def layers : List CorpusLayer :=
  [.hydrology, .cultivation, .darkEarth, .earthwork,
   .settlement, .exchange, .materialCulture, .continuingPeoples]

theorem layer_count : layers.length = 8 := by
  rfl

inductive MappingStatus where
  | supported
  | analogy
  | unresolved
  deriving Repr, DecidableEq

def windAmazon : MappingStatus := .analogy
def argonAmazon : MappingStatus := .unresolved
def timeAmazon : MappingStatus := .supported
def electrumAmazon : MappingStatus := .unresolved
def reagentAmazon : MappingStatus := .analogy

theorem argon_stops : argonAmazon = .unresolved := by
  rfl

theorem electrum_stops : electrumAmazon = .unresolved := by
  rfl

def corpusLabel : String := "AMAZONION_ROOT_PLUS_CORPUS_v0"

theorem corpus_label_exact :
    corpusLabel = "AMAZONION_ROOT_PLUS_CORPUS_v0" := by
  rfl

end AmazonionRootPlusV0