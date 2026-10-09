# SHEET 142 — Serialized Resource Commit + Signed External Fence Pin

**Status:** `0e / PASS` — **901/901 regression checks** (863 inherited SHEET 141 checks plus 38 new SHEET 142 checks).

## What changed

SHEET 141 read the authoritative checkpoint twice around a resource write. There remained a race if membership moved immediately after the second read. SHEET 142 uses the existing SHEET 140 `M.authorize()` to hold the **same shared membership filesystem lock** through the entire resource write. All supported membership operations (`propose`, `accept`, `finish`) acquire that same lock and cannot race through it.

SHEET 142 also verifies a separately signed Ed25519 external high-watermark pin; restoring an old membership revision is rejected when an independently retained, more recent pin is supplied. The simulated pin is stored on the same test machine and is **not externally anchored**.

## New source

- `serial142.js`: membership-serialized resource write, signed pin verifier, crash-hold recovery inspection.
- `resource142.js`: mTLS protected resource process invoking `serial142.commit`.
- `gate142.js`: 38 new network and fault-injection tests.
- `run-all.sh`: executes the preserved SHEET 141 chain in an isolated copy plus SHEET 142 tests.
- `baseline141/`: entire previous release source, unchanged.
- `KERNEL-ASCII.txt`: full high-level architecture.
- `index.html`: interactive, **precomputed** fault-scenario SVG dashboard.

## Run

```bash
cd sheet142
bash run-all.sh
```

Requirements: Node.js 20+, OpenSSL CLI, Bash. No production credentials included.

## Safety assertions exercised

1. Two real local mTLS resource processes share a serialized membership lock.
2. A held resource commit prevents a concurrent membership proposal.
3. After the write completes, joint consensus can be proposed and finalized with OLD 3/3 and NEW 3/3 approvals.
4. Old leases are rejected after membership cutover; new leases commit.
5. An externally pinned Ed25519 signature rejects old-state rollback and altered head values.
6. Resource records remain hash-linked and durable across process restart.
7. Corrupt resource state, orphan lock, invalid pin, forged lease and unauthorized client all fail closed.
8. Simultaneous writers contend rather than being silently executed twice.

## Important boundaries

**Local, cooperative serialization only.** This closes the checkpoint-read/write race for resource and membership mutations using the same filesystem and the same supported lock. It does not prove global distributed linearizability across hosts, storage providers, or byzantine processes. Direct file edits that bypass the membership API can violate the lock assumption. A process crash can leave an orphaned lock requiring operator review, rather than automatic recovery. Only local test keys and CA credentials are generated at runtime; external-pin custody is demonstrative rather than truly off-host. No integration with original SHEET 103 has been proven.

GitHub may contain only the new source and receipt rather than the complete baseline; the full ZIP preserves the inherited artifacts.