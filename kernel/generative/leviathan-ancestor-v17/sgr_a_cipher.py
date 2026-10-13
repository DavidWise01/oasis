#!/usr/bin/env python3
"""Standalone Green Chariot ↔ Sgr A* numerical audit, no cipher fit."""
from pathlib import Path
import json, math

HERE = Path(__file__).resolve().parent
glyph = json.loads((HERE / "v16_chariot_registry.json").read_text())
assert glyph["schema"] == "KET/LEVIATHAN/GREEN_CHARIOT/v16"
assert glyph["user_literal"] == r"123 {{45/|\54}} 678"
assert glyph["chariot"]["hinge"] == "/|\\"
assert glyph["chariot"]["left_inner"] == [4, 5]
assert glyph["chariot"]["right_inner"] == [5, 4]
assert [x["label"] for x in glyph["amplitudes"]] == [
    "red", "green", "blue", "orange", "purple", "green", "yellow"
]
assert [x["label"] for x in glyph["carriers"]] == [
    "white", "black", "gray"
]
assert glyph["pinned_zero"]["value"] == 0
assert glyph["chariot"]["left_amplitude"]["id"] == "A2"
assert glyph["chariot"]["right_amplitude"]["id"] == "A6"
assert glyph["address_budgets"]["local"]["total"] == 366
assert glyph["address_budgets"]["parent"]["total"] == 6006

G = 6.67430e-11              # SI Newtonian gravitational constant
C = 299792458.0             # m/s
MSUN = 1.98847e30           # kg
LY = 9.4607304725808e15   # m
M = 4.0e6 * MSUN
D = 27000.0 * LY
microas_per_rad = (180 / math.pi) * 3600 * 1.0e6

theta_g_microas = G * M / (C * C * D) * microas_per_rad
diameter_gr_microas = 2 * math.sqrt(27) * theta_g_microas
eht_ring_microas = 51.8
eht_sigma_microas = 2.3
nominal_residual_sigma = (diameter_gr_microas - eht_ring_microas) / eht_sigma_microas
radio_GHz = C / .0013 / 1e9

# Critical curve is an ideal Schwarzschild angular scale, not an
# exact equality with the measured gas-emission ring.
assert 49.4 < diameter_gr_microas < 49.8
assert abs(nominal_residual_sigma) < 1.1
assert 230.60 < radio_GHz < 230.62

comparison = {
    "glyph": glyph["user_literal"],
    "chariot_structure_preserved": True,
    "target": "Sagittarius A*",
    "mass_solar_nominal": 4.0e6,
    "distance_lightyears_nominal": 27000,
    "EHT_ring_diameter_microas": eht_ring_microas,
    "EHT_ring_sigma_microas": eht_sigma_microas,
    "EHT_radio_wavelength_mm": 1.3,
    "EHT_radio_frequency_GHz": radio_GHz,
    "independent_GR_ideal_critical_diameter_microas": diameter_gr_microas,
    "nominal_residual_sigma": nominal_residual_sigma,
    "cipher_predicts_diameter": False,
    "cipher_predicts_seven_visible_wavelengths": False,
    "cipher_predicts_polarization": False,
    "verdict": "STRUCTURAL_ANALOGY_ONLY_NOT_PREDICTIVE",
    "caveat": "Ring diameter match follows from conventional GR and adopted mass/distance, not from Green Chariot."
}
print(json.dumps(comparison, sort_keys=True, indent=2))
