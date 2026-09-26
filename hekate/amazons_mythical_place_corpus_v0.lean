namespace AmazonsMythCorpusV0

def primitive : String :=
  "w{{ind}}.a{{rgon}}.t{{ime}}.e{{lectrum}}.r{{e-agent}}"

def outerWord : String := "WATER"

inductive MythNode where
  | amazons
  | themiscyra
  | thermodon
  | otrera
  | hippolyta
  | antiope
  | penthesilea
  | heracles
  | theseus
  | achilles
  | amazonomachy
  deriving Repr, DecidableEq

inductive MappingStatus where
  | mythSupported
  | analogy
  | unresolved
  deriving Repr, DecidableEq

def windStatus : MappingStatus := .analogy
def argonStatus : MappingStatus := .unresolved
def timeStatus : MappingStatus := .mythSupported
def electrumStatus : MappingStatus := .unresolved
def reagentStatus : MappingStatus := .analogy

theorem argon_stops : argonStatus = .unresolved := by
  rfl

theorem electrum_stops : electrumStatus = .unresolved := by
  rfl

def rootPlace : String := "THEMISCYRA / THERMODON"

end AmazonsMythCorpusV0
