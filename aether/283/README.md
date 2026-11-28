# AETHER-283-RS — Prefix Witness Custody Claims and Retained-Journal Crash Interruption

A read-only verifier compares three Ed25519-signed historical-prefix witnesses against the actual AETHER-282 journal head at a pinned sequence. Each witness signs its exact head SHA-256, sequence, nonce, controller and run. The separate canonical SHA-256 of the claimed trust record is required out-of-band. Ancestor overlap between witness controller claims and the journal controller is rejected, as is shared ancestry between witnesses, repeated nonces, bad keys, conflicting prefix claims, missing prefixes and overwritten local heads.

The verifier invokes the AETHER-282 retained-challenge recovery auditor to reverify original stored signed receipts. The tests also cover an actual subprocess termination before an uncommitted SQLite challenge insert and recovery of a previously committed prefix. These are process-interruption experiments, **not** hardware power-loss qualification.

The trust pin, witness PEMs and controller ancestry are still user/caller supplied. Three valid signatures DO NOT prove three independent externally operated custodians, a trusted timestamp, or actual external acquisition. All outputs are HOLD and physical qualification 0%. Historical freezes remain unchanged.

Run:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/283 -p 'test_*.py' -v
    python3 aether/283/prefix_witness.py --db /tmp/aether282.db --witness-bundle claimed-witnesses.json --trusted-record-sha256 <64hex> --out hold.json

Next AETHER-284-RS: externally acquired witness record bytes with locked trust-root readback and a separately sealed nonce history; avoid promoting self-issued ancestry to independent authority.
