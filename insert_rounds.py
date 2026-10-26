#!/usr/bin/env python3
"""Insert round-5 (Roman gods) and round-6 (French gods) into build_rome_gods.py."""
import ast
import sys

filepath = 'build_rome_gods.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Split into lines
content = content.replace('\r\n', '\n').replace('\r', '\n')
lines = content.split('\n')

# Find def main()
main_idx = None
for i, line in enumerate(lines):
    if line.strip() == 'def main():':
        main_idx = i
        break

# Find closing ']' of THEMES
close_idx = None
for i in range(main_idx - 1, 0, -1):
    if lines[i].strip() == ']':
        close_idx = i
        break

print(f"THEMES close at line {close_idx}")
print(f"def main() at line {main_idx}")

def build_round_themes(header, themes):
    """Build list of lines with 4-space indent for a round block."""
    out = [header]
    for slug, name, blurb, story, lime in themes:
        out.append(f'    ("{slug}", "{name}", "{blurb}",')
        out.append(f'     "{story}", "{lime}")')
        out.append("")
    out.append("")
    return out

roman_themes = [
    ('apollo-margaret', "Margaret of Vendôme", "Apollo's margaret as a white bloom in the solar sign.", "The bloom is a star that never falls.", 'margaret sign'),
    ('jupiter-avignon', "Avignon's Arc", "Jupiter's avignon as a bridge over the gulf.", "The water is a sieve and the foot is a path.", 'bridge bridge'),
    ('hermes-louis', "The Louis Rod", "Hermes' louis as a rod of three sites.", "The three sights are the same sky under three lights.", 'three-site rod'),
    ('zeus-henri', "Henri's Horizon", "Zeus' henri as the horizon at all four corners.", "The four corners are the same eye the sky keeps.", 'four-corner eye'),
    ('themis-elizabeth', "Elizabeth's Scale", "Themis' elizabeth as a balance of amber and gold.", "The beam is a needle that reads the salt.", 'amber-gold beam'),
    ('apollo-louis', "The Louis Dawn", "Apollo's louis as a dawn that is a single letter.", "The letter is a gate the sea cannot close.", 'single-letter bed'),
    ('jupiter-napoleon', "Napoleon's Eye", "Jupiter's napoleon as an eye that sees without a face.", "The gaze is a question the sky keeps.", 'gaze without face'),
    ('hermes-charles', "Charles' Cement", "Hermes' charles as cement that holds the wall without a joint.", "The joint is a name the wind does not move.", 'joint-less wall'),
    ('zeus-ephemera', "The Ephemera Vow", "Zeus' ephemera as a vow sealed in sand.", "The sand is a star that never falls.", 'sand seal'),
    ('themis-paris', "Paris' Hand", "Themis' paris as a hand that holds the scale.", "The scale is a weight that never tips.", 'hand on scale'),
    ('apollo-bordeaux', "Bordeaux's Lamp", "Apollo's bordeaux as a lamp in the study.", "The light is a name the door cannot close.", 'lamp in study'),
    ('jupiter-strasbourg', "Strasbourg's Ring", "Jupiter's strasbourg as a ring that does not break.", "The ring is a seat at the table.", 'ring that holds'),
    ('hermes-lyon', "Lyon's Thread", "Hermes' lyon as a thread that spins the wheel.", "The wheel is a law the hand cannot break.", 'spinning thread'),
    ('zeus-tours', "Tours' Tour", "Zeus' tours as a turning in the tomb.", "The tomb is a cup the flame cannot break.", 'turn in tomb'),
    ('themis-metz', "Metz' Light", "Themis' metz as a light that is a door.", "The door opens when the wind calls.", 'light as door'),
    ('apollo-dijon', "Dijon's Vine", "Apollo's dijons as a vine that climbs a wall.", "The wall is a spine the sun keeps.", 'vine on spine'),
    ('jupiter-rene', "René's Seal", "Jupiter's rene as a seal that keeps the flood.", "The seal is a star that never falls.", 'flood seal'),
    ('hermes-versailles', "Versailles' Gate", "Hermes' versailles as a gate that never closes.", "The gate is the wall that opens.", 'gate without walls'),
    ('zeus-orleans', "Orléans' Bridge", "Zeus' orleans as a bridge over the river.", "The river is a mirror the moon reads.", 'bridge over mirror'),
    ('themis-amiens', "Amiens' Arch", "Themis' amiens as an arch that holds the city.", "The arch is a wall the wind does not move.", 'arch that holds'),
    ('apollo-langres', "Langres' Spoke", "Apollo's langres as a spoke in the field.", "The field is a line the wind spins.", 'spoke in field'),
    ('jupiter-grasse', "Grasse's Amber", "Jupiter's grassee as amber that holds the scent.", "The scent is a song the sky keeps.", 'amber that holds'),
    ('hermes-reims', "Reims' Flame", "Hermes' reims as the flame that does not fall.", "The flame is a lamp on the altar.", 'flame on altar'),
    ('zeus-nantes', "Nantes' Gate", "Zeus' nantes as a gate set in the embankment.", "The embankment is a name the tide cannot wash.", 'bank gate'),
    ('themis-marseille', "Marseille's Seal", "Themis' marseille as a seal that sets the water.", "The water is a sundial the hand turns.", 'sundial sea'),
    ('apollo-toulouse', "Toulouse' Vine", "Apollo's toulouse as a vine over the wall.", "The wall is a road the sun never closes.", 'vine wall'),
    ('jupiter-poitiers', "Poitiers' Crown", "Jupiter's poitiers as a crown of three points.", "The three points are the same eye the sky keeps.", 'three-point crown'),
    ('hermes-nice', "Nice' Thread", "Hermes' nice as a thread through the mount.", "The mount is a name the wind does not move.", 'thread mount'),
    ('zeus-nice2', "Nice' Aster", "Zeus' nice as an aster that keeps the sea.", "The sea is a cup the hands cannot spill.", 'cup sea'),
    ('themis-orly', "Orly's Ring", "Themis' orly as a ring that sets the tide.", "The tide is a hand the sea does not drop.", 'ring tide'),
]

french_themes = [
    ('apollo-villeneuve', "Villeneuve's Hearth", "Apollo's villeneuve as a hearth in the town.", "The flame is a name the water cannot put out.", 'hearth in stone'),
    ('jupiter-villedroit', "Ville-Droit's Yard", "Jupiter's ville-droit as a yard held by the right hand.", "The hand is a plant the roots keep.", 'yard in right'),
    ('hermes-villeneuve2', "Villeneuve's Knot", "Hermes' villeneuve as a knot beneath the dock.", "The knot is a seal the sea cannot undo.", 'knot under dock'),
    ('zeus-brest', "Brest's Water", "Zeus' brest as water that reads the moon.", "The moon is a coin the wave cannot spend.", 'water that reads'),
    ('themis-blois', "Blois' Curve", "Themis' blois as a curve that holds the street.", "The street is a chain the sea cannot break.", 'curve that holds'),
    ('apollo-formigny', "Formigny's Line", "Apollo's formigny as a line that keeps the sea.", "The sea is a lamp the hands cannot move.", 'line that keeps'),
    ('jupiter-hereford', "Hereford's Door", "Jupiter's hereford as a door set in the wall.", "The wall is a name the sky cannot close.", 'door in wall'),
    ('hermes-drancy', "Drancy's Square", "Hermes' drancy as a square in the dust.", "The dust is a promise the wind does not break.", 'square in dust'),
    ('zeus-dommartin', "Dommartin's Peak", "Zeus' dommartin as a peak in the field.", "The field is a proof the hand cannot falsify.", 'peak in field'),
    ('themis-bordeaux2', "Bordeaux's Second", "Themis' bordeaux as a second settlement.", "The second is the first that never sleeps.", 'second settlement'),
    ('apollo-reims', "Reims' Flame", "Apollo's reims as the flame that does not fall.", "The flame is a lamp on the altar.", 'flame on altar'),
    ('jupiter-theseus', "Theseus' Bridge", "Jupiter's theseus as a bridge over the wall.", "The wall is a door the hand cannot count.", 'bridge over wall'),
    ('hermes-rouen', "Rouen's Bank", "Hermes' rouen as a bank of mud that holds the tide.", "The tide is a hand the sea does not drop.", 'bank tide'),
    ('zeus-lagny', "Lagny's Line", "Zeus' lagny as a line that never bends.", "The line is a name the fire reads.", 'line fire'),
    ('themis-montreuil', "Montreuil's Wall", "Themis' montreuil as a wall that shelters the valley.", "The valley is a cup the rain does not fill.", 'wall shelters'),
    ('apollo-versailles2', "Versailles' Second", "Apollo's versailles as a second king.", "The second is the first that never sleeps.", 'second king'),
    ('jupiter-lens', "Lens' Light", "Jupiter's lens as a point of fire.", "The fire is a word the hand cannot break.", 'point of fire'),
    ('hermes-saint-denis', "Saint-Denis' Door", "Hermes' saint-denis as a door at the tomb.", "The tomb is a cup the flame cannot break.", 'door at tomb'),
    ('zeus-bobigny', "Bobigny's Line", "Zeus' bobigny as a line that holds the bridge.", "The bridge is a name the tide cannot wash.", 'line bridge'),
    ('themis-argenteuil', "Argenteuil's Seal", "Themis' argenteuil as a seal on the water.", "The water is a sundial the hand turns.", 'seal water'),
    ('apollo-pelec', "Pelec's Gut", "Apollo's pelec as a gut that keeps the fire.", "The fire is a flame the hands cannot move.", 'gut fire'),
    ('jupiter-bobigny2', "Bobigny's Ring", "Jupiter's bobigny as a ring on the field.", "The field is a line the wind spins.", 'ring field'),
    ('hermes-noisy', "Noisy's Knot", "Hermes' noisy as a knot on the road.", "The road is a step the sky does not close.", 'knot road'),
    ('zeus-cedex', "Cedex' Eye", "Zeus' cedex as an eye in the sand.", "The sand is a star that never falls.", 'eye in sand'),
    ('themis-garches', "Garches' Hand", "Themis' garchas as a hand on the rail.", "The rail is a name the wind does not move.", 'hand rail'),
    ('apollo-villiers', "Villiers' Lamp", "Apollo's villers as a lamp on the wall.", "The wall is a spine the sun keeps.", 'lamp wall'),
    ('jupiter-bicetre', "Bicêtre's Crown", "Jupiter's bicêtre as a crown on the hill.", "The hill is a name the fire reads.", 'crown on hill'),
    ('hermes-le-mans', "Le Mans' Thread", "Hermes' le-mans as a thread that spins the wheel.", "The wheel is a law the hand cannot break.", 'spinning thread'),
    ('zeus-saint-mande', "Saint-Mande's Star", "Zeus' saint-mande as a star in the field.", "The field is a proof the hand cannot falsify.", 'star in field'),
    ('themis-henneaux', "Henneaux' Curve", "Themis' henneaux as a curve that holds the yard.", "The yard is a seal the sea cannot undo.", 'curve holds'),
]

blk5 = build_round_themes("# ── ROUND FIVE (30 Roman gods: towns, temples, consuls, pagans) ─────────────", roman_themes)
blk6 = build_round_themes("# ── ROUND SIX (30 French gods: Paris towns/endowments) ───────────────────", french_themes)

# Insert BEFORE the ']' closing bracket
new_lines = lines[:close_idx] + blk5 + blk6 + lines[close_idx:]
new_content = '\n'.join(new_lines) + '\n'

# Verify parses
try:
    ast.parse(new_content)
    print("New content parses OK")
except SyntaxError as e:
    print(f"Syntax error: {e}")
    sys.exit(1)

print(f"Inserted {len(roman_themes)} + {len(french_themes)} = {len(roman_themes)+len(french_themes)} round-5/6 themes")
print(f"New line count: {len(new_lines)}")

with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
    f.write(new_content)
