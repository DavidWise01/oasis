# AETHER-251-RS — Fresh Challenge Supervisor–Worker Binding

A read-only adjudicator binds a supervisor observation and worker observation to exactly one run, source commit, challenge identifier and challenge nonce. The two namespaces and process IDs must differ. The exact pair is hashed and signed by three Ed25519 witness statements; signatures are verified using caller-supplied public-key pins. Challenge and witness nonces are checked against caller-supplied consumed-nonce history.

**Limitations:** same namespace inode is a clear failure, but different namespace inodes alone do not establish correct isolation. The hash of a fabricated observation is still a hash of fabricated data. Three cryptographic keys are not three independently authenticated controllers. The nonce ledger is not externally sealed; therefore even fully passing local cryptography remains unqualified. No actual namespace execution or external witness is claimed. All results HOLD, physical qualification 0%, no ACT.

Tests use generated Ed25519 test keys, without committed secrets. Run:

    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/251 -p 'test_*.py' -v
    python3 aether/251/namespace_binding.py --bundle sample-evidence.json --out hold.json

Earlier Phase XVIII and XIX freezes remain unchanged. Next natural bound AETHER-252-RS: independent process-liveness binding, namespace inode ownership and append-only challenge consumption with externally pinned signatures.
