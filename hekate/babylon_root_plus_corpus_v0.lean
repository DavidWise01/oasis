namespace BabylonRootPlusV0

/- Layered corpus index only; historical claims live in companion Markdown. -/

inductive Layer where
  | upstreamMesopotamia
  | oldBabylonian
  | middlePostKassite
  | neoBabylonian
  | lateHellenistic
  deriving Repr, DecidableEq

inductive CorpusPrimitive where
  | record
  | position
  | lookup
  | approximate
  | observe
  | predict
  | bind
  | canon
  | survey
  deriving Repr, DecidableEq

def babylonRoot : List CorpusPrimitive :=
  [.record, .position, .lookup, .observe, .predict, .bind, .canon]

theorem babylon_root_has_seven_primitives :
    babylonRoot.length = 7 := by
  rfl

inductive AttributionStatus where
  | secure
  | traditional
  | uncertain
  deriving Repr, DecidableEq

structure RecordedPerson where
  name : String
  role : String
  status : AttributionStatus
  deriving Repr, DecidableEq

def hammurabi : RecordedPerson :=
  { name := "Hammurabi", role := "jurisprudence/state administration", status := .secure }

def sinLeqiUnninni : RecordedPerson :=
  { name := "Sin-leqi-unninni", role := "Gilgamesh editor/standardizer", status := .traditional }

def esagilKinApli : RecordedPerson :=
  { name := "Esagil-kin-apli", role := "diagnostic handbook standardizer", status := .secure }

def nabuRimannu : RecordedPerson :=
  { name := "Nabu-rimannu", role := "astronomical computation", status := .uncertain }

def kidinnu : RecordedPerson :=
  { name := "Kidinnu", role := "astronomical tradition", status := .uncertain }

def berossus : RecordedPerson :=
  { name := "Berossus", role := "Babylonian archive to Greek transmission", status := .secure }

def corpusLabel : String := "BABYLON_ROOT_PLUS_CORPUS_v0"

theorem corpus_label_exact :
    corpusLabel = "BABYLON_ROOT_PLUS_CORPUS_v0" := by
  rfl

end BabylonRootPlusV0