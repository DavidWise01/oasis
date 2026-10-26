#!/usr/bin/env python3
"""
Fix build_rome_gods.py THEMES list.

Current state (committed HEAD bae0eecb):
- THEMES list starts at line 568
- 40 base themes (569-608) plus 51 more (611-753) = 91 theme tuples
- CANVAS_HISTORY closes at line 426
- CANVAS_FNS starts at line 428
- def main at line 876
- Between THEMES close (873) and def main (876) there are:
  - Line 874: blank
  - Line 875: blank
  - Lines 813-872: 60 appended round-6/7 themes (sapphon 30 + pershan 30)
  Wait, that's wrong. Let me recheck.

Actual structure:
- THEMES = [ starts at line 568
- Lines 569-754: 91 theme tuples (40 base + 51 more? No...)

Let me recount from the file:
- Line 568: THEMES = [
- Lines 569-754: base themes (lines 570-753)
  - 570-608: ROUND ONE (20)
  - 611-649: ROUND TWO (20)
  - 652-690: ROUND THREE (20)
  - 693-753: ROUND FOUR (20)
  - That's 80 theme tuples in lines 570-753
- Line 754: ] (THEMES closes)
- Line 755: blank
- Line 756: blank
- Line 757: def main():
- Line 758: render_themes()
- Line 759: write_index()
- Line 760: print(...)
- Line 761: blank
- Line 762: blank
- Line 763: if __name__ == "__main__":
- Line 764: main()
- Lines 813-872: 60 appended round-6/7 themes (after CANVAS_FNS, before main)
- Line 873: ]

Wait, that doesn't match. Let me just look at the actual file.

Actually from the git show output:
- Line 568: THEMES = [
- Line 754: ]
- Line 755: blank
- Line 756: blank
- Line 757: def main():
- Line 761: if __name__ == "__main__":
- Line 764: main()

And the appended themes are at lines 813-872 (after CANVAS_FNS).

The issue: the build script can't run because the 60 appended themes at lines 813-872
are bare tuple expressions that get evaluated and discarded (no trailing commas).

The fix: Add trailing commas to the 60 appended themes so they don't error out.
