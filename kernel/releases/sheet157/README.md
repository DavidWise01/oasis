# SHEET 157 — Quorum-Certified Witness Catch-Up

Status: **41/41 new adversarial checks PASS** (`node gate157.js`, exit 0).

This release extends SHEET 156 with an explicit, majority-certified recovery path for a lagging external-floor witness. Each recovering witness issues and persists a random single-use challenge; two *other* independently pinned mTLS peers sign a matching high-water head bound to that challenge; a quorum member signs the full append-only history. The recovering witness independently replays history from genesis and verifies a strict prefix of its own durable history before atomically installing the certified extension.

The protocol will never silently overwrite a conflicting prepared proposal. Such a witness is **quarantined** and requires reviewed resolution outside the automatic catch-up path. Repair refuses to proceed with fewer than two matching, fresh, separately signed peer heads.

## New executables

- `witness157.js` — extended TLS witness service: `/challenge`, `/export`, `/catchup` alongside inherited `/read`, `/prepare`, `/commit`.
- `catchup-verify157.js` — signed-head certification, bounded history verification, strict-prefix and pending-conflict admission checks.
- `catchup157.js` — recovery coordinator that initiates the witness challenge and acquires a fresh 2-of-3 peer proof.
- `gate157.js` — 41 exercised fault checks, including actual witness restart and crash after atomic install but before RPC acknowledgement.
- `run-all.sh` — inherited SHEET156 runner plus the new gate. Inherited runner may take several minutes.
- `KERNEL-ASCII.txt` — 48-stage complete operational and recovery process pipe.
- `index.html` — interactive dark emerald fault viewer; no network access required.

## Quick tests

```bash
node gate157.js
bash run-all.sh
```

## Verification

**New gate:** 41/41 checks, clean exit 0. **Inherited:** a combined rerun was attempted but exceeded this environment's execution limit while running older SHEET148 resource/bridge tests. Its partial log is bundled and must not be treated as a full inherited PASS. SHEET156's most recent *prior-release* complete run passed 1,519/1,519.

## Security and operational boundary

The repairing proxy is an authenticated, trusted coordinator. A replayed or forged signed head cannot pass the target's one-time challenge. The source export is authenticated and hash checked, but full-history exports are limited to **256 entries** and the service uses the inherited 16 KB TLS message cap. Implement paginated, bounded consistency proofs before attempting large histories. The local-disk guarantee is Node.js `fsync` of temporary state plus its parent directory after atomic rename; this is not an independent verification of disk-controller behavior. Services run as separate processes on **one** physical host. Never interpret these tests as a global Byzantine or cross-host linearizability proof.

No existing SHEET156 source was edited: the baseline is copied underneath `baseline156/` and verified byte for byte.