# AETHER-255-RS — Attested pidfd Transcript & Cross-Host Replay Detection

Offline read-only verifier for the AETHER-254 pidfd test-child transcript. Rebuilds the exact transcript SHA-256, checks fixed-child code identity, PID/waitid binding, exit status and boot identity, and binds the transcript to a distinct run/host/challenge nonce.

Three Ed25519 signatures over the complete host/run/challenge/transcript binding and individual witness nonces are verified with caller-supplied key pins. The two caller-supplied consumed-history lists reject repeated challenge and transcript references. Test fixtures create real temporary signing keys but do not establish independent external witness custody.

The supplied host ID, Linux boot ID, external key pins and replay ledgers remain untrusted until authenticated outside this workflow. The program does not perform a live pidfd wait or send network requests. Local signing proves only cryptographic consistency, NOT who controlled the signer.

Run:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/255 -p 'test_*.py' -v
    python3 aether/255/attested_exit.py --bundle pinned-snapshot.json --out hold.json

The verifier always returns REJECT_OR_UNVERIFIED, operational authority HOLD and physical qualification 0%. No lock recovery, process signals, custody promotion or modification of Phase XVIII/XIX freezes.

Next AETHER-256-RS: atomic externally retained replay-ledger head and independent signer-controller ancestry, with a pinned cross-host challenge transcript.
