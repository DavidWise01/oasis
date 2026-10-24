# PRIM 039 — subprocess termination and recovery

2026-10-24. Actual child-process exits (os._exit) and restart with sender/receiver SHA256-checked JSONL journals. Four crash windows: after sender INTENT, after receiver's persisted SEEN, after delivery but before sender ACK, after sender ACK. Reduced test: 3 records per case, all four cases pass, exactly three unique accepted records and ACKs, no duplicates.

Two broader subprocess sweeps timed out and are not reported as passing. Receiver `SEEN` is logical acceptance, not necessarily a completed external side effect. fsync used but no OS power-cut/torn-write/network test. Runnable code and results in conversation ZIP prim_exp039.zip.
