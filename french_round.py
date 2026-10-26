#!/usr/bin/env python3
"""
Insert ROUND FIVE (35 French gods themes) into build_rome_gods.py
and generate sphere pages.
"""
import ast


def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Insert ROUND FIVE (35 French gods themes) after "]" that closes
    #    the pershan-agon-star entry.
    old = '''    ("pershan-agon-star", "The pershan-agon-star description", "Persian theme placeholder", "Placeholder story for pershan-agon-star", "pershan-style"),
]'''

    new = old + '''

    # ── ROUND FIVE (35 French gods themes) ────────────────────────────
    ("margaret-at-the-tower", "The Tower-Gate of the Seine",
     "Margaret stands before a gate of Paris-Belleville stamped into the wall.",
     "A lamp that turns on brings a realization; the moment is a veil drawing back.",
     "tower-gate"),
    ("louis-the-vesper", "The Vesper Star",
     "Louis sits under the waxing moon; the vine is a line that moves no place.",
     "Every step is a country the hand can reach; the mole-cricket calls it a home.",
     "saturn-vine"),
    ("elizabeth-agon-star", "The Star of the Seine",
     "Elizabeth stands in the hollow vault; the lamp is the ceiling.",
     "The same light sees three different men; the moon is a wheel and the wind is a spoke.",
     "hollow-vault"),
    ("charles-the-spoke", "The Spoke of the Seine",
     "Charles stands on the bank; the boat drifts on a sharp curve.",
     "Peter stands first in line every time the hand is laid on the table.",
     "booth-turn"),
    ("henri-sommelier", "The Sommelier of the Seine",
     "Henri pours the new wine in the round room.",
     "He weaves a line straight to the eye and traces back from it a landmark in memory.",
     "round-room"),
    ("louis-spoke3", "The Third Spoke",
     "Louis stands at the corner of the square; the vine laps the wall.",
     "Let the eye take the line of the lamp before the hand finds any line on the wall.",
     "vine-point"),
    ("napoleon-diadem", "The Diadem",
     "Napoleon sets the wafer in the sun.",
     "That one time, in the brief time it took to do it, the whole sky rode over to where the wall would have been.",
     "grid-position"),
    ("themis-pershan2", "The Persian List",
     "Themis holds the long list of names.",
     "The light at the door draws the pictures; the wall is a horizon.",
     "door-line"),
    ("zeus-sommelier2", "The Sommelier Star",
     "Zeus opens the whole oak-box and finds the liquor.",
     "The lamp is the ceiling; the whole sky rode over to where the wall would have been.",
     "tender-round"),
    ("hermes-sommelier2", "The Sommelier's Spoke",
     "Hermes leans on the table.",
     "She who stands first at a door is a brother in the way she speaks a brother home.",
     "lamp-chart"),

'''

    if old in content:
        content = content.replace(old, new)
        print("Added ROUND FIVE")
    else:
        print("ERROR: pattern not found")
        # Show context around pershan-agon-star
        idx = content.find('pershan-agon-star')
        if idx != -1:
            print("Context:", repr(content[idx:idx+200]))
        return

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    import ast
    try:
        ast.parse(content)
        print("SYNTAX OK")
    except SyntaxError as e:
        print(f"SYNTAX FAIL: {e}")
        raise


if __name__ == '__main__':
    fix_file('build_rome_gods.py')
