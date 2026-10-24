#!/usr/bin/env python3
"""
Append 30 sapphic round-6 THEMES to build_rome_gods.py.
Starts from the committed clean round-5 base (HEAD).
"""
import ast

PATH = r"C:\Users\Dave\oasis\build_rome_gods.py"

S6 = [
    ("sapphon-agon", "The Agon", "SaPpH{{i}}on's agon that is the same wall as the door.",
     "The agon is the same wall as the door; the door is a step and the step is a table.", "gods-at-one door", "agon-wall"),
    ("apollo-agon", "The Agon-Flame", "Apollo's agon that burns without heat.",
     "The agon-flame burns without heat; the flame is a law and the law is a name.", "needle lay", "agon-flame"),
    ("jupiter-sappho", "The Sapphic-Star", "Jupiter's sappho that shows the same sky.",
     "The sapphic-star shows the same sky; the sky is not a sound.", "light without sound", "sappho-star"),
    ("hermes-sappho", "The Sappho-Wind", "Hermes' sappho that is a step",
     "The sappho-wind is a step; the door is a step and the step is a table.", "gods-at-one door", "sappho-wind"),
    ("zeus-sappho", "The Sappho-Flag", "Zeus' sappho that waves without wind.",
     "The sappho-flag waves without wind; the fire is a name the sky cannot close.", "twelve door", "sappho-flag"),
    ("themis-sappho", "The Sappho-Law", "Themis' sappho that reads the one line.",
     "The sappho-law reads the one line; the needle tests the truth before the hands turn.", "needle lay", "sappho-law"),
    ("apollo-sappho", "The Sappho-Sun", "Apollo's sappho that is the same sun.",
     "The sappho-sun is the same sun; the sun is a wheel and the sun is a wall.", "storm-light mesh", "sappho-sun"),
    ("poseidon-sappho", "The Sappho-Sea", "Poseidon's sappho that means the same sea.",
     "The sappho-sea means the same sea; the sea is a wheel and the wind is a spoke.", "spiral scrawl", "sappho-sea"),
    ("mnemosyne-sappho", "The Sappho-Memory", "Mnemosyne's sappho that means the same man.",
     "The sappho-memory means the same man; the man is a wheel and the man is a wall.", "8x8-anchor", "sappho-memory"),
    ("natura-sappho", "The Sappho-Flower", "Natura's sappho that means the same one.",
     "The sappho-flower means the same one; the needle tests the truth before the hands turn.", "needle lay", "sappho-flower"),
    ("atlas-sappho", "The Sappho-Stone", "Atlas' sappho that means the same sun.",
     "The sappho-stone means the same sun; the stone is a wheel and the stone is the wall.", "storm-light mesh", "sappho-stone"),
    ("hermes-spoke2", "The Two-Spoke", "Hermes' two-spoke that means the one man.",
     "The two-spoke means the one man; the man is a wheel and the man is a wall.", "8x8-anchor", "two-spoke"),
    ("zeus-spoke2", "The Two-Sun", "Zeus' two-sun that means the one man.",
     "The two-sun means the one man; the man is a wheel and the man is a wall.", "8x8-anchor", "two-sun"),
    ("jupiter-sommelier", "The Sommelier", "Jupiter's sommelier that picks the same stone.",
     "The sommelier picks the same stone; the needle tests the truth before the hands turn.", "needle lay", "sommelier"),
    ("hermes-ladder", "The Ladder", "Hermes' ladder that reads the same name.",
     "The ladder reads the same name; the needle tests the truth before the hands turn.", "needle lay", "ladder"),
    ("apollo-diadem", "The Diadem", "Apollo's diadem that means the one man.",
     "The diadem means the one man; the man is a wheel and the man is a wall.", "8x8-anchor", "diadem"),
    ("themis-sommelier", "The Sommelier-Law", "Themis' sommelier that picks the same man.",
     "The sommelier-law picks the same man; the man is a wheel and the man is a wall.", "8x8-anchor", "sommelier-law"),
    ("natura-sommelier", "The Sommelier-Flower", "Natura's sommelier that picks the same smell.",
     "The sommelier-flower picks the same smell; the smell is a wall and the smell is a name.", "needle lay", "sommelier-flower"),
    ("zeus-sommelier", "The Sommelier-Star", "Zeus' sommelier that picks the same sky.",
     "The sommelier-star picks the same sky; the sky is not a sound.", "light without sound", "sommelier-star"),
    ("hermes-sommelier", "The Sommelier-Step", "Hermes' sommelier that picks the same star.",
     "The sommelier-step picks the same star; the star is a wall and the star is a door.", "zenith-line", "sommelier-step"),
    ("sapphon-sommelier", "The Sommelier-Sea", "SaPpH{{i}}on's sommelier that picks the same sea.",
     "The sommelier-sea picks the same sea; the sea is a wheel and the wind is a spoke.", "spiral scrawl", "sommelier-sea"),
    ("sapphon-star", "The Sappho-Star", "SaPpH{{i}}on's sappho that means the same star.",
     "The sappho-star means the same star; the star is a wall and the star is a door.", "zenith-line", "sappho-star"),
    ("sapphon-mouth", "The Sappho-Mouth", "SaPpH{{i}}on's sappho that means the same man.",
     "The sappho-mouth means the same man; the man is a wheel and the man is a wall.", "8x8-anchor", "sappho-mouth"),
    ("sapphon-mountain", "The Sappho-Mountain", "SaPpH{{i}}on's sappho that means the same world.",
     "The sappho-mountain means the same world; the world is a wheel and the wind is a spoke.", "spiral scrawl", "sappho-mountain"),
    ("sapphon-tower", "The Sappho-Tower", "SaPpH{{i}}on's tower that means the same one.",
     "The sappho-tower means the same one; the needle tests the truth before the hands turn.", "needle lay", "sappho-tower"),
    ("sapphon-ladder", "The Sappho-Ladder", "SaPpH{{i}}on's ladder that means the same one.",
     "The sappho-ladder means the same one; the needle tests the truth before the hands turn.", "needle lay", "sappho-ladder"),
    ("sapphon-agon-fire", "The Agon-Fire", "SaPpH{{i}}on's agon that burns without heat.",
     "The agon-fire burns without heat; the flame is a law and the law is a name.", "needle lay", "agon-fire"),
    ("sapphon-agon-wind", "The Agon-Wind", "SaPpH{{i}}on's agon that is the same wind.",
     "The agon-wind is the same wind; the wind is a wheel and the wind is a spoke.", "spiral scrawl", "agon-wind"),
    ("sapphon-agon-sun", "The Agon-Sun", "SaPpH{{i}}on's agon that means the same sun.",
     "The agon-sun means the same sun; the sun is a wheel and the sun is a wall.", "storm-light mesh", "agon-sun"),
    ("sapphon-agon-sea", "The Agon-Sea", "SaPpH{{i}}on's agon that means the same sea.",
     "The agon-sea means the same sea; the sea is a wheel and the wind is a spoke.", "spiral scrawl", "agon-sea"),
    ("sapphon-agon-star", "The Agon-Star", "SaPpH{{i}}on's agon that means the same star.",
     "The agon-star means the same star; the star is a wall and the star is a door.", "zenith-line", "agon-star"),
]

with open(PATH, encoding="utf-8") as f:
    src = f.read()

lines = src.split("\n")

# Find "THEMES = [" then find the ']' right after it (the THEMES close bracket)
start_idx = None
end_idx = None
for i, ln in enumerate(lines):
    if ln.strip() == "THEMES = [":
        start_idx = i
        break
assert start_idx is not None, "Could not find THEMES = []"

# Search forward from start_idx for the first ']' that ends the THEMES list
# (skip comments and tuples)
for i in range(start_idx + 1, len(lines)):
    s = lines[i].strip()
    if s == "]":  # This is the THEMES close bracket
        end_idx = i
        break
assert end_idx is not None, "Could not find THEMES close bracket"

# Insert the S6 themes right before the closing ']' at end_idx
theme_block = "\n".join([
    '    ("' + t[0] + '", "' + t[1] + '", "' + t[2] + '",\n'
    '     "' + t[3] + '", "' + t[4] + '"),'
    for t in S6
])
lines = lines[:end_idx] + theme_block.split("\n") + ["]"] + lines[end_idx + 1:]
src2 = "\n".join(lines)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(src2)

ast.parse(src2)
print("appended", len(S6), "sapphic round-6 themes; syntax OK")
