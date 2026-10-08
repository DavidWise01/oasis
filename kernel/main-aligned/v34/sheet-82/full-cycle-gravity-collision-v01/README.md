# SHEET 82 — Full-cycle gravity collision recovery

Append-only successor to SHEET81. Local exact executable benchmark and full results are available in this conversation's `sheet82_full_cycle_gravity.zip`. SHA256 exact executable `7542b00185f4fff18ec0b3a260c1fab7a542ccffb9ba2169ae3d156759030a18`; full results `f0878d0a6aa33398429322ac00fd46587a86e99f028dafdd78ebc27c120ba196`.

Three complete modeled Big Bang/Crunch cycles (2250 frames, 12s/cycle, frame step 0.016s), with all four phases participating in the actual collision simulation. Fixed 0.95 baseline: **2748 collisions**, squared-speed final `0.00013847098009011719`; phase-feedback damping [0.93,0.97]: **2837 collisions**, squared-speed final `0.00012409292611329357`. Both policies preserve 120 lane IDs and have 35/35 local checks. Counts by source phase in coupled run: expanding 1202; expanded 356; collapsing 1078; collapsed 201. Both have 3,655,680 candidate comparisons PER 512 frames; for 2250 frames the total is 16,065,000 per policy.

The source's four UI state names are used; the 4.8s/1.6s/4.8s/.8s deterministic repeating durations are a test fixture and the bounce feedback is experimental, not a source-derived gravity force. The 60/15/3/1/1 register and inversion test are independently verified symbolic metadata; the overall collision state **does not close** due to dissipative damping. 9/6/1 scheduling is not executed. This is screen-space point-proximity detection, not physical collisions.

Local package includes exact tested `benchmark.py`, `results.json`, `README.md` and hash manifest. This GitHub directory stores audit/results summaries and does not claim GitHub's exact source was replayed. Earlier sheets remain unchanged.
