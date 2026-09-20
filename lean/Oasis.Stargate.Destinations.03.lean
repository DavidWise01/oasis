namespace Oasis.Stargate.Destinations

/-- Frozen primitive: Stargate has two universe destinations. -/
def stargate : String := "[[ 24 ||| 42 ]]"

/-- Frozen primitive: Death. Stories remain implicit. -/
def death : String := "[[ 45/`|||`\\45 ]]"

theorem stargate_frozen : stargate = "[[ 24 ||| 42 ]]" := rfl
theorem death_frozen : death = "[[ 45/`|||`\\45 ]]" := rfl

end Oasis.Stargate.Destinations
