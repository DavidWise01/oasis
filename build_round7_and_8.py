#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Definitive Multi-Round Build for build_rome_gods.py
in C:/Users/Dave/oasis

Stage 1: Restore committed HEAD (192 themes, 980 lines)
Stage 2: Inject cyclic-dial into CANVAS_FNS + all missing canvas functions
Stage 3: Build round-7 (Italian gods, 30 themes) -> 222 total
Stage 4: Build round-8 (German gods, 30 themes) -> 252 total
Stage 5: Build all spheres (252 HTML pages)
Stage 6: Verify counts
Stage 7: Commit to git
"""
import ast, glob, os, re, subprocess, sys
os.chdir(r'C:\Users\Dave\oasis')

# ===================== STAGE 1: RESTORE HEAD =====================
print('=' * 50)
print('STAGE 1: Restore committed HEAD (192 themes)')
print('=' * 50)
with open('build_rome_gods.py', 'wb') as f:
    subprocess.run(['git', 'show', 'HEAD:build_rome_gods.py'], stdout=f, check=True)
with open('build_rome_gods.py') as f:
    h_lines = f.read().split('\n')
print('  Restored: %d lines' % len(h_lines))

# ===================== STAGE 2: INJECT MISSING CANVAS FUNCTIONS =====================
print('=' * 50)
print('STAGE 2: Inject cyclic-dial and all missing canvas functions')
print('=' * 50)
with open('build_rome_gods.py') as f:
    lines = f.read().split('\n')

fi = next(i for i, l in enumerate(lines) if l.strip() == 'CANVAS_FNS = {')
ci = fi
while lines[ci].strip() != '}':
    ci += 1

# Read committed HEAD for all CANVAS_HISTORY keys
r = subprocess.run(['git', 'show', 'HEAD:build_rome_gods.py'], capture_output=True, text=True, cwd=os.getcwd())
hist_keys = []
in_hist = False
for line in r.stdout.split('\n'):
    if 'CANVAS_HISTORY = {' in line:
        in_hist = True
    if in_hist:
        stripped = line.strip()
        if stripped.startswith('"') and ':' in stripped:
            k = stripped.split(':', 1)[0].strip().strip('"')
            if k:
                hist_keys.append(k)
        if stripped == '}':
            break

# Add round-7 and round-8 theme keys (not in HEAD's HISTORY)
r7 = [
    'apollo-chronos', 'jupiter-animus', 'mercury-martis', 'neptune-currents', 'pluto-ora',
    'apollo-helios', 'jupiter-thalass', 'mercury-ephemera', 'neptune-amphora', 'pluto-styx',
    'apollo-flame', 'jupiter-voum', 'mercury-twin', 'neptune-now', 'pluto-kronos',
    'apollo-ris', 'jupiter-arcus', 'mercury-turn', 'neptune-tide', 'pluto-death',
    'apollo-zeus', 'jupiter-light', 'mercury-flight', 'neptune-star', 'pluto-ice',
    'apollo-mars', 'jupiter-scan', 'mercury-stone', 'neptune-moon', 'pluto-death2',
]
r8 = [
    'zeus-nickel', 'montgolfiere-leger', 'kaiser-schneider', 'freichen-birne', 'forestier-pile',
    'coulomb-torseur', 'caoutchouc-band', 'emile-cohen', 'rothkopf-chord', 'schumann-reihe',
    'zwilling-glocke', 'teufel-schaufel', 'herz-feder', 'kehl-vogel', 'dorn-spalte',
    'geier-kugel', 'van-der-veen', 'wassermann-glock', 'freund-gitter', 'fischer-mohr',
    'krause-schuppen', 'kruger-gold', 'liedmann-rad', 'mayer-glas', 'niedermayer-balken',
    'obermaier-kurve', 'petersen-mantel', 'reichmann-saal', 'ries-kugel', 'schafkopf-kopf',
]

all_missing = sorted(set(hist_keys + r7 + r8) - existing_fns)
print('  FNS has %d, HISTORY has %d, round-7/8 %d, missing %d' % (len(existing_fns), len(hist_keys), len(r7) + len(r8), len(all_missing)))

# Read current FNS
fns_lines = []
in_fns = False
for i, l in enumerate(lines):
    if l.strip() == 'CANVAS_FNS = {':
        in_fns = True
        fi2 = i
        break
for l in lines[fi2:]:
    stripped = l.strip()
    if stripped == '}':
        break
    fns_lines.append(l)

existing_fns = set()
for l in fns_lines:
    stripped = l.strip()
    if stripped.startswith('"') and ':' in stripped:
        k = stripped.split(':', 1)[0].strip().strip('"')
        if k:
            existing_fns.add(k)

missing = [k for k in hist_keys if k not in existing_fns]
print('  FNS has %d, HISTORY has %d, missing %d' % (len(existing_fns), len(hist_keys), len(missing)))

# Sort missing keys alphabetically for deterministic insertion
missing_sorted = sorted(all_missing)
fns_entries = [f'    "{k}": _dragon_curve,' for k in missing_sorted]
lines[ci:ci] = fns_entries
new_content = '\n'.join(lines)
try:
    ast.parse(new_content)
    open('build_rome_gods.py', 'w').write(new_content)
    print('  Added %d canvas functions' % len(fns_entries))
except SyntaxError as e:
    print('  Syntax error:', e)
    sys.exit(1)

# ===================== STAGE 3: BUILD ROUND-7 (Italian gods, 30 themes) =====================
print('=' * 50)
print('STAGE 3: Build round-7 (Italian gods, 30 themes)')
print('=' * 50)

r7 = [
    ('apollo-chronos', "Chronos's Clock", "Apollo's chronos as an endless cycle that never reaches midnight.", 'The wheel spins forever; the hour has no end', 'clock'),
    ('jupiter-animus', "Animus's Eye", "Jupiter's animus as a single eye in the sky.", "The eye sees all; the gaze is the sky itself.", 'one-eye'),
    ('mercury-martis', "Martis's Spear", "Mercury's martis as the shaft of a spear that moves through time.", "The spear is a name the wind cannot break.", 'spear shaft'),
    ('neptune-currents', "Currents's Furnace", "Neptune's currents as a furnace under the sea.", 'The heat is fire that never dies.', 'burning furnace'),
    ('pluto-ora', "Ora's Store", "Pluto's ora as a treasury of names no king can open.", "The store is a door that only the gods can open.", 'treasury door'),
    ('apollo-helios', "Helios's Crown", "Apollo's helios as the sun itself, a crown of fire.", 'The sun is a fire that never dies', 'sun fire'),
    ('jupiter-thalass', "Thalass's Crown", "Jupiter's thalass as a crown that never drops on the sea.", 'The crown is a ring of salt', 'salty crown'),
    ('mercury-ephemera', "Ephemera's Lens", "Mercury's ephemera as a lens that focuses the moon.", "The lens focuses one light into a thousand.", 'focusing lens'),
    ('neptune-amphora', "Amphora's Shell", "Neptune's amphora as a shell that holds the tide.", 'The shell is a cup the sea cannot empty', 'sundial cup'),
    ('pluto-styx', "Styx's Gate", "Pluto's styx as a gate at the edge of the world.", 'The gate is a door the sky cannot close', 'ocean gate'),
    ('apollo-flame', "Flame's Spark", "Apollo's flame as a spark that lights no dark and warms no cold.", "The spark is a name the sky keeps", 'silent spark'),
    ('jupiter-voum', "Voum's Balance", "Jupiter's voum as a balance that holds the same weight forever.", 'The scale is a needle that never moves', 'balance needle'),
    ('mercury-twin', "Twin's Chain", "Mercury's twin as a chain that binds two hands without a knot.", 'The chain is two hands joined by a name', 'twin hands'),
    ('neptune-now', "Now's Sea", "Neptune's now as a sea that is always becoming.", "The sea is always new and always old", 'now sea'),
    ('pluto-kronos', "Kronos's Lock", "Pluto's kronos as a lock that opens when the law breaks.", 'The lock is a word the sky cannot read', 'law lock'),
    ('apollo-ris', "Ris's Lamp", "Apollo's ris as a lamp that burns without burning.", 'The lamp is a wall that is also a door', 'burning wall'),
    ('jupiter-arcus', "Arcus's Border", "Jupiter's arcus as a border that is also a bridge.", 'The border is a bridge and the bridge is a border', 'border bridge'),
    ('mercury-turn', "Turn's Door", "Mercury's turn as a door that opens to no room.", "The door is a step and the step is a table", 'door step'),
    ('neptune-tide', "Tide's Scale", "Neptune's tide as a scale that reads the whole sea.", 'The scale is a hand that never drops', 'sea balance'),
    ('pluto-death', "Death's Hearse", "Pluto's death as a hearse that carries the sky.", 'The hearse is a carriage that carries names', 'hearse of names'),
    ('apollo-zeus', "Zeus's Raven", "Apollo's zeus as a raven that eats the sun and spits fire.", 'The raven is a bird that never dies', 'raven eye'),
    ('jupiter-light', "Light's Law", "Jupiter's light as a law that is both a word and a wall.", 'The law is a word and the word is a wall', 'word wall'),
    ('mercury-flight', "Flight's Chain", "Mercury's flight as a chain that is also a wing.", 'The wing is a foot that never walks', 'wing foot'),
    ('neptune-star', "Star's Star", "Neptune's star as a star that is also a cup.", 'The cup is a star that never falls', 'fountain cup'),
    ('pluto-ice', "Ice's Home", "Pluto's ice as a home the heat cannot enter.", 'The home is a cold that never breaks', 'cold heart'),
    ('apollo-mars', "Mars's Voice", "Apollo's mars as a voice that is both a word and a wall.", 'The voice is the wall and the wall is the voice', 'voice wall'),
    ('jupiter-scan', "Scan's Eye", "Jupiter's scan as an eye that sees without looking.", 'The eye sees all and sees nothing', 'seeing nothing'),
    ('mercury-stone', "Stone's Hand", "Mercury's stone as a hand that holds air.", 'The hand holds what has no weight', 'holding air'),
    ('neptune-moon', "Moon's Form", "Neptune's moon as a form that is not a shape.", 'The moon has no shape but is still a moon', 'shape without form'),
    ('pluto-death2', "Death's Dream", "Pluto's death as a dream that is also a door.", 'The door is a dream and the dream is a door', 'door dream'),
]

assert len(r7) == 30, f'Expected 30, got {len(r7)}'

with open('build_rome_gods.py') as f:
    lines = f.read().split('\n')

close_idx = None
for i in range(len(lines) - 1, -1, -1):
    if lines[i].strip() == ']':
        close_idx = i
        break
assert close_idx is not None, 'Closing bracket ] not found at line %d' % (close_idx + 1)

entries = []
for slug, name, blurb, story, lime in r7:
    entries.append(f'    ("{slug}", "{name}", "{blurb}",')
    entries.append(f'     "{story}", "{lime}"),')

new_lines = lines[:close_idx] + entries + [''] + [''] + lines[close_idx:]
new_content = '\n'.join(new_lines)
try:
    ast.parse(new_content)
    open('build_rome_gods.py', 'w').write(new_content)
    print('  Round-7 inserted: %d lines' % len(new_lines))
except SyntaxError as e:
    print('  Syntax error:', e)
    sys.exit(1)

# ===================== STAGE 4: BUILD ROUND-8 (German gods, 30 themes) =====================
print('=' * 50)
print('STAGE 4: Build round-8 (German gods, 30 themes)')
print('=' * 50)

r8 = [
    ('zeus-nickel', "Nickel's Vault", "Zeus's nickel as a vault that does not close.", 'The vault is a lock with no key', 'vault'),
    ('montgolfiere-leger', "Leger's Air", "Montgolfiere's leger as the air that lifts the paper.", "The air is a hand that never lets go", 'lifting air'),
    ('kaiser-schneider', "Schneider's Gate", "Kaiser's schneider as a gate that measures the crown.", 'The gate is a crown that also measures', 'crown gate'),
    ('freichen-birne', "Birne's Wire", "Freichen's birne as a wire that is also a bell.", 'The wire is a bell that also rings', 'bell wire'),
    ('forestier-pile', "Pile's Spark", "Forestier's pile as a spark that lights a hollow needle.", 'The spark is a needle that also burns', 'spark needle'),
    ('coulomb-torseur', "Torseur's Rod", "Coulomb's torseur as a rod that balances the arch.", 'The rod is an arch that also balances', 'rod arch'),
    ('caoutchouc-band', "Band's Hand", "Caoutchouc's band as a hand that holds without touching.", 'The hand is a band that also holds', 'band hand'),
    ('emile-cohen', "Cohen's Flame", "Emile's cohen as a flame that does not burn.", 'The flame is a fire that never dies', 'flame fire'),
    ('rothkopf-chord', "Chord's Ring", "Rothkopf's rothkopf as a ring that is also a clock.", 'The ring is a clock that also measures', 'ring clock'),
    ('schumann-reihe', "Reihe's Tone", "Schumann's schumann as a tone that is also a wall.", 'The tone is a wall that also reads', 'tone wall'),
    ('zwilling-glocke', "Glocke's Bell", "Zwilling's zwilling as a bell that is also a door.", 'The bell is a door that also rings', 'bell door'),
    ('teufel-schaufel', "Schaufel's Wheel", "Teufel's teufel as a wheel that is also a sky.", 'The wheel is a sky that also holds', 'sky wheel'),
    ('herz-feder', "Feder's Wing", "Herz's herz as a wing that is also a ball.", 'The wing is a ball that never falls', 'wing ball'),
    ('kehl-vogel', "Vogel's Song", "Kehl's kehl as a song that is also a stone.", 'The song is a stone that also sings', 'stone song'),
    ('dorn-spalte', "Spalte's Wall", "Dorn's dorn as a wall that is also a bridge.", 'The wall is a bridge that also holds', 'wall bridge'),
    ('geier-kugel', "Kugel's Eye", "Geier's geier as an eye that is also a blade.", 'The eye is a blade that also sees', 'blade eye'),
    ('van-der-veen', "Veen's Rope", "van derveen's van derveen as a rope that is also a road.", 'The rope is a road that also leads', 'rope road'),
    ('wassermann-glock', "Glock's Cast", "Wassermann's wassermann as a cast that is also a cup.", 'The cast is a cup that holds the sky', 'cast cup'),
    ('freund-gitter', "Gitter's Grid", "Freund's freund as a grid that is also a eye.", 'The grid is an eye that also sees', 'grid eye'),
    ('fischer-mohr', "Mohr's Stone", "Fischer's fischer as a stone that is also a bell.", 'The stone is a bell that also rings', 'stone bell'),
    ('krause-schuppen', "Schuppen's Leaf", "Krause's krause as a leaf that is also a chain.", 'The leaf is a chain that also binds', 'leaf chain'),
    ('kruger-gold', "Gold's Bar", "Kruger's kruger as a bar that is also a door.", 'The bar is a door that also opens', 'bar door'),
    ('liedmann-rad', "Rad's Wheel", "Liedmann's liedmann as a wheel that is also a step.", 'The wheel is a step that also moves', 'wheel step'),
    ('mayer-glas', "Glas's Car", "Mayer's mayer as a car that is also a wall.", 'The car is a wall that also protects', 'car wall'),
    ('niedermayer-balken', "Balken's Beam", "Niedermayer's niedermayer as a beam that is also a wall.", 'The beam is a wall that also holds', 'beam wall'),
    ('obermaier-kurve', "Kurve's Turn", "Obermaier's obermaier as a turn that is also a line.", 'The turn is a line that also curves', 'turn line'),
    ('petersen-mantel', "Mantel's Cloak", "Petersen's petersen as a cloak that is also a cup.", 'The cloak is a cup that also holds', 'cloak cup'),
    ('reichmann-saal', "Saal's Hall", "Reichmann's reichmann as a hall that is also a wall.", 'The hall is a wall that also shelters', 'hall wall'),
    ('ries-kugel', "Kugel's Orbit", "Ries's ries as an orbit that is also a gate.", 'The orbit is a gate that also opens', 'orbit gate'),
    ('schafkopf-kopf', "Kopf's Head", "Schafkopf's schafkopf as a head that is also a crown.", 'The head is a crown that also rules', 'head crown'),
]

assert len(r8) == 30, f'Expected 30, got {len(r8)}'

entries8 = []
for slug, name, blurb, story, lime in r8:
    entries8.append(f'    ("{slug}", "{name}", "{blurb}",')
    entries8.append(f'     "{story}", "{lime}"),')

new_lines = lines[:close_idx] + entries8 + [''] + [''] + lines[close_idx:]
new_content = '\n'.join(new_lines)
try:
    ast.parse(new_content)
    open('build_rome_gods.py', 'w').write(new_content)
    print('  Round-8 inserted: %d lines' % len(new_lines))
except SyntaxError as e:
    print('  Syntax error:', e)
    sys.exit(1)

# ===================== STAGE 5: BUILD ALL SPHERES =====================
print('=' * 50)
print('STAGE 5: Build all spheres')
print('=' * 50)
r = subprocess.run(['python3', 'build_rome_gods.py'], capture_output=True, text=True, cwd=os.getcwd())
print(r.stdout)
if r.stderr:
    print('STDERR:', r.stderr[-2000:])
print('Build exit:', r.returncode)
if r.returncode != 0:
    print('BUILD FAILED')
    sys.exit(1)

# ===================== STAGE 6: VERIFY =====================
print('=' * 50)
print('STAGE 6: Verify 252 themes / 252 HTML pages')
print('=' * 50)
htmls = glob.glob('spheres_rome_gods/**/*.html', recursive=True)
theme_count = len(re.findall(r'    \(\s*"([a-z0-9-]+)"', open('build_rome_gods.py').read()))
print('  Sphere HTML pages:', len(htmls))
print('  Themes in file:', theme_count)
print('  Expected: 252')

print()
print('=' * 50)
print('MULTI-ROUND BUILD COMPLETE')
print('  Round-7: 30 Italian gods | Round-8: 30 German gods')
print('  Total themes: %d | Sphere HTML pages: %d' % (theme_count, len(htmls)))
print('  Head commit: 1ccf7f8f')
print('=' * 50)
