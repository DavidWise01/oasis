# P3.30 — Leap-year count correction, 2026-10-09
User correction: 183 concerns the 366-slot leap-year counter: 183 + 183 = 366, four cycles = 1464 logical slots. Sign split after slot 183; slot 184 begins positive half. This supersedes the previous assumption that 183 is intrinsically an outer-torus angle or that 360/720 must be the **calendar count**. The geometric 360° torus phase can remain separate if desired.

Four consecutive Gregorian years usually have 1461 actual days (one leap year), leaving 3 unavailable slots. For 2097–2100 there is no leap day because 2100 is not divisible by 400: 1460 actual days and 4 unavailable slots. Calendar projection keeps these slot gaps explicit instead of compressing addresses.

Executed exact local Node test: 1464 indexed roundtrips, sign split at 183/184, Gregorian 2024–27 and century exception 2097–2100: PASS. This is a symbolic calendar mapping, not evidence of exotic geometry. The mapping from sign flip to a physically realized Möbius seam is not determined by calendar arithmetic alone.
