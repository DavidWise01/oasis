# PRIM 038 — Disk-backed torn-journal recovery

Executed 2026-10-24. Actual filesystem writes with checksummed JSONL entries, flush and os.fsync. Twelve injected incomplete trailing-record scenarios (three interruption points × four truncation offsets). On restart the valid journal prefix was read, invalid tail truncated, receiver SEEN identifiers rebuilt, outstanding accepted records replayed and ACKed. All cases ended with 60 distinct receiver acceptance records, no logical duplicate or lost IDs.

**Limits:** Controlled truncation only; not an actual OS/process kill or power failure, no network effects, directory durability or mid-file corruption. Receiver deduplication plus durable SEEN-before-ACK protocol is required. Executable test, `results.json` and detailed README available in the ChatGPT `prim_exp038.zip` artifact.
