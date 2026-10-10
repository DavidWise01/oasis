# ROOT0 P4.18 — dual-store signed checkpoint anchor (2026-10-10)

**Executed locally** Node.js v22.16.0, 15/15 assertions PASS, latest run 9.283ms. P4.18 `Anchor` has its own Ed25519 keypair and SQLite database; P4.15 `SeparateWitness` maintains an independently signed local checkpoint. The test preserves proper SQLite snapshots with `VACUUM INTO`.

| Check | Outcome |
|---|---|
| Valid histories | accepted |
| Missing anchor | fail closed |
| Local ahead / interrupted publication | quarantined |
| Stale anchor epoch or same-epoch fork | rejected |
| Altered signature | rejected |
| Local-only rollback with newer anchor retained | **detected** |
| Local AND anchor coherently rolled back to the older epoch | **undetected** |

Test is **two databases in one Node.js process on one host**, not a remotely independent witness. Separate signing keys and storage files alone cannot guarantee antirollback against a single adversary controlling the host. Also no authenticated automatic recovery or arbitrary crash-point execution. Physical timing, Planck phenomena and photonics not measured.

Executable `p418_anchor.mjs` committed; test source, prerequisite and results packaged in downloadable ZIP. ZIP SHA-256: `b7c227c8fe7b93086055e0d4c72405a9a936fb828275eb040368cf75ed5f20b9`.

P4.19 target: network/RPC separate process authority, signed recovery authorization, and independent physical storage/host evaluation.