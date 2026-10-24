# Experiment 037 — journal / acknowledgment boundary

Nine deterministic crash scenarios (3 IDs × stages after intent, after delivery and after ACK), each over 60 records. Simulated append-only sender events ACCEPT, EGRESS_INTENT, ACK and receiver-side persistent deduplication. With deduplication: 60 distinct deliveries, zero duplicates in each case. Without deduplication: crash after delivery before ACK duplicates one event upon retry. Full executable test and results in ChatGPT ZIP prim_exp037.zip.

Important: in-memory journal and persistent receiver simulated; no disk durability, torn writes, network faults, or real process failures validated. Next: actual on-disk checksummed append journal and receiver crash test.
