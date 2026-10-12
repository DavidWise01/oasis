#!/usr/bin/env python3
"""KET LEVIATHAN 0root: symbolic ancestry adapter, not an abiogenesis model."""
from dataclasses import asdict, dataclass
import json

ROOT_NAME = "L.E.V.I.A.T.H.A.N."
ROOT_ID = "0root"
ATT = "att"  # Deliberately unexpanded
ROOT_PRESSURE_ATM = 1250  # User hypothetical environment
OBSERVED_SEA_ANCHOR_SIGNED_ATM = -1100  # KET coordinate, not negative absolute pressure
TEMP_UNIT = "K"  # Nonnegative Kelvin axis
IDENTITY = "i"
SURVIVAL_ARCHETYPES = ("LEVIATHAN", "DIATOM", "TARDIGRADE")
SCALES = ("atomic", "molecular", "cellular", "organism", "ecosystem", "planetary", "cosmic")

@dataclass(frozen=True)
class Archetype:
    symbol: str
    role: str
    body_policy: str
    mechanism: str
    evidence_state: str

ARCHETYPES = (
    Archetype("LEVIATHAN", "root-reference", "no fixed body",
              "lineage identity persists", "user-defined mnemonic"),
    Archetype("DIATOM", "survival branch", "microscopic cellular body",
              "silica shell / ecological variation", "real lineage; event-specific survival unverified"),
    Archetype("TARDIGRADE", "survival branch", "multicellular body",
              "cryptobiosis in some species", "real lineage; event-specific survival unverified"),
)

DOMAINS = (
    ("N−", "deep-ocean", -1100, "high hydrostatic-pressure environment"),
    ("O+", "biosphere", -1, "atmospheric/ecological reference: signed coordinate only"),
    ("H+", "space", 0, "cosmic hydrogen branch; actual pressure not necessarily zero"),
)

def lineage_report():
    return {
        "schema": "KET/LEVIATHAN/0root/v04",
        "root_id": ROOT_ID,
        "root_name": ROOT_NAME,
        "root_is_literal_organism": False,
        "root_has_fixed_body": False,
        "att": ATT,
        "hypothetical_root_pressure_atm": ROOT_PRESSURE_ATM,
        "observation_pressure_signed_sea_anchor_atm": OBSERVED_SEA_ANCHOR_SIGNED_ATM,
        "pressure_sign_is_not_absolute_pressure": True,
        "temperature_unit": TEMP_UNIT,
        "temperature_kelvin_nonnegative": True,
        "lineage_identity": IDENTITY,
        "scale_views": list(SCALES),
        "event": {
            "name": "impact / mass-extinction model",
            "date": "unassigned",
            "impactor": "unassigned",
            "only_three_survivors_claimed_in_nature": False
        },
        "survival_archetypes": [asdict(a) for a in ARCHETYPES],
        "three_body_is_literal_celestial_gravity_model": False,
        "environmental_domains": [
            dict(symbol=s, domain=d, signed_atm=p, model_role=m) for s,d,p,m in DOMAINS
        ],
        "local_address_budget": {
            "logical": 250, "workspace": 110, "controls": "C.A.T.G.N.O",
            "control_count": 6, "total": 366
        },
        "parent_address_budget": {
            "positions": 100, "riders": 3, "skins": 20, "controls": 6, "total": 6006
        },
        "root_consumes_address": False,
        "unknown_element_range": [119, 250],
        "states": ("verified", "quarantined", "non_aligned"),
        "caveat": "Symbolic ancestry architecture, not physical or evolutionary verification"
    }

def validate():
    r = lineage_report()
    assert r["root_id"] == "0root"
    assert r["root_has_fixed_body"] is False
    assert r["root_consumes_address"] is False
    assert len(ARCHETYPES) == 3
    assert len({a.symbol for a in ARCHETYPES}) == 3
    assert any(a.symbol == "LEVIATHAN" and a.role == "root-reference" for a in ARCHETYPES)
    assert (r["local_address_budget"]["logical"] + r["local_address_budget"]["workspace"]
            + r["local_address_budget"]["control_count"]) == 366
    assert 100*3*20+6 == r["parent_address_budget"]["total"]
    assert len(DOMAINS) == 3
    assert [p for _,_,p,_ in DOMAINS] == [-1100,-1,0]
    assert r["pressure_sign_is_not_absolute_pressure"]
    assert r["temperature_kelvin_nonnegative"]
    assert r["event"]["date"] == "unassigned"
    assert r["event"]["only_three_survivors_claimed_in_nature"] is False
    assert r["three_body_is_literal_celestial_gravity_model"] is False
    assert r["lineage_identity"] == "i"
    assert [a.symbol for a in ARCHETYPES] == list(SURVIVAL_ARCHETYPES)
    assert r["unknown_element_range"] == [119,250]
    assert ROOT_PRESSURE_ATM != abs(OBSERVED_SEA_ANCHOR_SIGNED_ATM)
    return {"passed":19,"total":19,"kind":"symbolic-invariant-checks-only"}

if __name__ == "__main__":
    result = lineage_report()
    result["structural_validation"] = validate()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
