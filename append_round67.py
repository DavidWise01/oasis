import os

REPO = os.getcwd()

with open(os.path.join(REPO, "build_rome_gods.py"), "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find the THEMES close bracket (line 813)
insert_idx = None
for i, line in enumerate(lines):
    if line.strip() == "]" and i > 300:
        insert_idx = i
        break

print(f"Found THEMES close bracket at line {insert_idx+1}")

# S6 themes - 30 sapphic
s6 = [
    ("sapphon-agon", "The Agon of the Sappho", "The sapphic agon that turns the mouth to the dark", "The sapphic agon turns the mouth to the dark; the word is a stone and the stone is a door."),
    ("apollo-agon", "The Apollo Agon", "The sapphic agon that reads the voice before it speaks", "The sapphic agon reads the voice before it speaks; the voice is a note and the note is a law."),
    ("jupiter-sappho", "The Jupiter Sappho", "The sapphic jupiter that steadies the storm", "The sapphic jupiter steadies the storm; the storm is a wave and the wave is a wall."),
    ("hermes-sappho", "The Hermes Sappho", "The sapphic hermes that scatters the fine dust", "The sapphic hermes scatters the fine dust; the dust is a seed and the seed is a star."),
    ("zeus-sappho", "The Zeus Sappho", "The sapphic zeus that shapes the sky", "The sapphic zeus shapes the sky; the sky is a dome and the dome is a heart."),
    ("themis-sappho", "The Themis Sappho", "The sapphic themis that anchors the law", "The sapphic themis anchors the law; the law is a ring and the ring is a covenant."),
    ("apollo-sappho", "The Apollo Sappho", "The sapphic sappho that is the fire behind the veil", "The sapphic sappho is the fire behind the veil; the veil is a smoke and the smoke is a name."),
    ("poseidon-sappho", "The Poseidon Sappho", "The sapphic sappho that keeps the shape of the wave", "The sapphic sappho keeps the shape of the wave; the wave is a sea and the sea is a sphere."),
    ("mnemosyne-sappho", "The Mnemosyne Sappho", "The sapphic sappho that keeps every name by clicking", "The sapphic sappho keeps every name by clicking; the name is a coin and the coin is a king."),
    ("natura-sappho", "The Natura Sappho", "The sapphic sappho that is the sea-glow that spins the sea", "The sapphic sappho is the sea-glow that spins the sea; the sea is a wheel and the wheel is a spoke."),
    ("atlas-sappho", "The Atlas Sappho", "The sapphic sappho that holds the world without bending", "The sapphic sappho holds the world without bending; the world is a web and the web is a seed."),
    ("hermes-spoke2", "The Hermes Spoke 2", "The sapphic hermes that turns the world without a hub", "The sapphic hermes turns the world without a hub; the spoke is a line and the line is a wall."),
    ("zeus-spoke2", "The Zeus Spoke 2", "The sapphic zeus that is the same lattice of rods", "The sapphic zeus is the same lattice of rods; the lattice is a net and the net is a web."),
    ("jupiter-sommelier", "The Jupiter Sommelier", "The sapphic jupiter that splits the river without breaking it", "The sapphic jupiter splits the river without breaking it; the river is a line and the line is a wall."),
    ("hermes-ladder", "The Hermes Ladder", "The sapphic hermes that turns the ladder without a step", "The sapphic hermes turns the ladder without a step; the ladder is a gate and the gate is a door."),
    ("apollo-diadem", "The Apollo Diadem", "The sapphic apollo that is the first sphere", "The sapphic apollo is the first sphere; the sphere is a seed and the seed is a star."),
    ("themis-sommelier", "The Themis Sommelier", "The sapphic themis that anchors the law", "The sapphic themis anchors the law; the law is a ring and the ring is a covenant."),
    ("natura-sommelier", "The Natura Sommelier", "The sapphic natura that is the sea-glow that spins the sea", "The sapphic natura is the sea-glow that spins the sea; the sea is a wheel and the wheel is a spoke."),
    ("zeus-sommelier", "The Zeus Sommelier", "The sapphic zeus that is the same fire that turns the wall", "The sapphic zeus is the same fire that turns the wall; the wall is a seal and the seal is a stone."),
    ("hermes-sommelier", "The Hermes Sommelier", "The sapphic hermes that is the wind that thwarts the truth", "The sapphic hermes is the wind that thwarts the truth; the truth is a line and the line is a wall."),
    ("sapphon-sommelier", "The Sappho Sommelier", "The sapphic sappho that is the fire behind the veil", "The sapphic sappho is the fire behind the veil; the veil is a smoke and the smoke is a name."),
    ("sapphon-star", "The Sappho Star", "The sapphic sappho that is the same square of stars", "The sapphic sappho is the same square of stars; the square is a seal and the seal is a stone."),
    ("sapphon-mouth", "The Sappho Mouth", "The sapphic sappho that moves without a breath", "The sapphic sappho moves without a breath; the mouth is a gate and the gate is a door."),
    ("sapphon-mountain", "The Sappho Mountain", "The sapphic sappho that is the pinnacle string", "The sapphic sappho is the pinnacle string; the string is a line and the line is a wall."),
    ("sapphon-tower", "The Sappho Tower", "The sapphic sappho that charts the highest line", "The sapphic sappho charts the highest line; the line is a ray and the ray is a law."),
    ("sapphon-ladder", "The Sappho Ladder", "The sapphic sappho that will not break the string", "The sapphic sappho will not break the string; the string is a thread and the thread is a name."),
    ("sapphon-agon-fire", "The Sappho Agon Fire", "The sapphic sappho that is the fracture-set", "The sapphic sappho is the fracture-set; the fracture is a wall and the wall is a door."),
    ("sapphon-agon-wind", "The Sappho Agon Wind", "The sapphic sappho that is the orbit-weave", "The sapphic sappho is the orbit-weave; the orbit is a ring and the ring is a covenant."),
    ("sapphon-agon-sun", "The Sappho Agon Sun", "The sapphic sappho that is the tangent gate", "The sapphic sappho is the tangent gate; the gate is a door and the door is a step."),
    ("sapphon-agon-sea", "The Sappho Agon Sea", "The sapphic sappho that is the veil of smoke", "The sapphic sappho is the veil of smoke; the smoke is a name and the name is a star."),
]

# S7 themes - 30 persian
s7 = [
    ("pershan-agon", "The Agon of the Pershan", "The Persian agon that turns the mouth to the dark", "The pershan agon turns the mouth to the dark; the word is a stone and the stone is a door."),
    ("apollo-pershan", "The Apollo Pershan", "The Persian agon that reads the voice before it speaks", "The pershan agon reads the voice before it speaks; the voice is a note and the note is a law."),
    ("jupiter-pershan", "The Jupiter Pershan", "The Persian jupiter that steadies the storm", "The pershan jupiter steadies the storm; the storm is a wave and the wave is a wall."),
    ("hermes-pershan", "The Hermes Pershan", "The Persian hermes that scatters the fine dust", "The pershan hermes scatters the fine dust; the dust is a seed and the seed is a star."),
    ("zeus-pershan", "The Zeus Pershan", "The Persian zeus that shapes the sky", "The pershan zeus shapes the sky; the sky is a dome and the dome is a heart."),
    ("themis-pershan", "The Themis Pershan", "The Persian themis that anchors the law", "The pershan themis anchors the law; the law is a ring and the ring is a covenant."),
    ("poseidon-pershan", "The Poseidon Pershan", "The Persian sappho that keeps the shape of the wave", "The pershan sappho keeps the shape of the wave; the wave is a sea and the sea is a sphere."),
    ("mnemosyne-pershan", "The Mnemosyne Pershan", "The Persian sappho that keeps every name by clicking", "The pershan sappho keeps every name by clicking; the name is a coin and the coin is a king."),
    ("natura-pershan", "The Natura Pershan", "The Persian sappho that is the sea-glow that spins the sea", "The pershan sappho is the sea-glow that spins the sea; the sea is a wheel and the wheel is a spoke."),
    ("atlas-pershan", "The Atlas Pershan", "The Persian sappho that holds the world without bending", "The pershan sappho holds the world without bending; the world is a web and the web is a seed."),
    ("hermes-spoke3", "The Hermes Spoke 3", "The Persian hermes that turns the world without a hub", "The pershan hermes turns the world without a hub; the spoke is a line and the line is a wall."),
    ("zeus-spoke3", "The Zeus Spoke 3", "The Persian zeus that is the same lattice of rods", "The pershan zeus is the same lattice of rods; the lattice is a net and the net is a web."),
    ("jupiter-sommelier2", "The Jupiter Sommelier 2", "The Persian jupiter that splits the river without breaking it", "The pershan jupiter splits the river without breaking it; the river is a line and the line is a wall."),
    ("hermes-ladder2", "The Hermes Ladder 2", "The Persian hermes that turns the ladder without a step", "The pershan hermes turns the ladder without a step; the ladder is a gate and the gate is a door."),
    ("apollo-diadem2", "The Apollo Diadem 2", "The Persian apollo that is the first sphere", "The pershan apollo is the first sphere; the sphere is a seed and the seed is a star."),
    ("themis-sommelier2", "The Themis Sommelier 2", "The Persian themis that anchors the law", "The pershan themis anchors the law; the law is a ring and the ring is a covenant."),
    ("natura-sommelier2", "The Natura Sommelier 2", "The Persian natura that is the sea-glow that spins the sea", "The pershan natura is the sea-glow that spins the sea; the sea is a wheel and the wheel is a spoke."),
    ("zeus-sommelier2", "The Zeus Sommelier 2", "The Persian zeus that is the same fire that turns the wall", "The pershan zeus is the same fire that turns the wall; the wall is a seal and the seal is a stone."),
    ("hermes-sommelier2", "The Hermes Sommelier 2", "The Persian hermes that is the wind that thwarts the truth", "The pershan hermes is the wind that thwarts the truth; the truth is a line and the line is a wall."),
    ("pershan-sommelier", "The Pershan Sommelier", "The Persian sappho that is the fire behind the veil", "The pershan sappho is the fire behind the veil; the veil is a smoke and the smoke is a name."),
    ("pershan-star", "The Pershan Star", "The Persian sappho that is the same square of stars", "The pershan sappho is the same square of stars; the square is a seal and the seal is a stone."),
    ("pershan-mouth", "The Pershan Mouth", "The Persian sappho that moves without a breath", "The pershan sappho moves without a breath; the mouth is a gate and the gate is a door."),
    ("pershan-mountain", "The Pershan Mountain", "The Persian sappho that is the pinnacle string", "The pershan sappho is the pinnacle string; the string is a line and the line is a wall."),
    ("pershan-tower", "The Pershan Tower", "The Persian sappho that charts the highest line", "The pershan sappho charts the highest line; the line is a ray and the ray is a law."),
    ("pershan-ladder", "The Pershan Ladder", "The Persian sappho that will not break the string", "The pershan sappho will not break the string; the string is a thread and the thread is a name."),
    ("pershan-agon-fire", "The Pershan Agon Fire", "The Persian sappho that is the fracture-set", "The pershan sappho is the fracture-set; the fracture is a wall and the wall is a door."),
    ("pershan-agon-wind", "The Pershan Agon Wind", "The Persian sappho that is the orbit-weave", "The pershan sappho is the orbit-weave; the orbit is a ring and the ring is a covenant."),
    ("pershan-agon-sun", "The Pershan Agon Sun", "The Persian sappho that is the tangent gate", "The pershan sappho is the tangent gate; the gate is a door and the door is a step."),
    ("pershan-agon-sea", "The Pershan Agon Sea", "The Persian sappho that is the veil of smoke", "The pershan sappho is the veil of smoke; the smoke is a name and the name is a star."),
    ("pershan-agon-star", "The Pershan Agon Star", "The Persian sappho that is the veil of smoke", "The pershan sappho is the veil of smoke; the smoke is a name and the name is a star."),
]

# Build block with unique s6 + s7 themes (no duplicates between lists)
block = []
for t in s6:
    block.append(f'    ("{t[0]}", "{t[1]}", "{t[2]}", "{t[3]}", "sapphon-style")\n')
for t in s7:
    block.append(f'    ("{t[0]}", "{t[1]}", "{t[2]}", "{t[3]}", "pershan-style")\n')

# Insert BEFORE the closing bracket (so themes are INSIDE the THEMES list)
new_lines = lines[:insert_idx] + block + lines[insert_idx:]

with open(os.path.join(REPO, "build_rome_gods.py"), "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"Inserted {len(s6) + len(s7)} themes, total {len(new_lines)} lines")

# Verify with regex
import re
with open(os.path.join(REPO, "build_rome_gods.py"), "r", encoding="utf-8") as f:
    content = f.read()
all_themes = re.findall(r'\(\s*"(sapphon-[a-z0-9-]+|pershan-[a-z0-9-]+)"', content)
unique = set(all_themes)
print(f"Total found: {len(all_themes)}, Unique: {len(unique)}")
print(f"Duplicates: {[t for t in unique if all_themes.count(t) > 1]}")
