# KET Rose V6 — Durable recovery boundary

Append-only successor to V5. Uses SQLite with DELETE journaling and synchronous=FULL. Each of 14 2.5% transfers uses a single ACID transaction containing debit, credit and unique receipt, so recovery after a simulated process interruption can safely replay without duplicating credits.

Test matrix: 14 links × 4 crash sites = **56/56 passing scenarios**. Reopening the database reconstructs precisely the uninterrupted balance and receipts, and a second replay does not mutate state. 366 starting balances are 100 units each; total remains 36,600. Fixed-point arithmetic uses 10^12 micro-units per unit and rounds transfer down to integer micro-units.

Pinned source: `0vwxyz`; 8 paths × 3 spectral bands = 24 identities; 60 phase positions; optional tesseract shadow stays unresolved. All physical interpretations remain hypotheses. SQLite durability settings do not prove safety against real power failures or disk faults.

Run `python durable_v6.py`.
