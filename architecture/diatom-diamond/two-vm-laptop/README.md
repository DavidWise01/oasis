# OASIS — Two isolated Ubuntu VMs on one Windows laptop (October 2026)

**Scope:** This is the single-laptop replacement for the previous *two independent physical computers* final field test. It creates two separate QEMU guest systems, each with its own Ubuntu 24.04 OS, 8 GB sparse qcow2 disk, 2 GB RAM, 2 vCPUs and virtual NIC, coordinated by one local Node.js agent. It does **not** prove independent hardware fault tolerance.

The Windows distribution bundle is **OASIS_TWO_VM_LAPTOP_AGENT_2026.zip** (generated conversation artifact). It includes:
- `START_TWO_VMS.cmd`: bootstraps Node.js, QEMU and OpenSSL if missing, downloads/validates Canonical's Ubuntu 24.04 cloud image once, then boots/provisions VM-B and VM-A.
- `vm-lab/agent.mjs`: read-only source integrity check, cloud-init seed server (host loopback only), unique guest disks and SSH-managed role-specific keys, guest readiness, authenticated delivery and receipt verification.
- `RETEST_VMS.cmd`, `STOP_VMS.cmd`, `DOCTOR.cmd` and optional WHPX acceleration script.
- Existing frozen `{{i}}`, `{{d}}`/OBS references, ASTROPHAGE signed OBF2 transport, balanced Rust WebAssembly codec.

The test path is:

```text
Windows laptop / Node agent
  |
  +- VM-A (Ubuntu/Linux + balanced Rust WASM + sender Ed25519 key)
       | authenticated signed OBF2 over TLS 1.3 / mutual certificates
       v
      QEMU NAT -> host 127.0.0.1:32443 -> QEMU NAT
       |
  +- VM-B (Ubuntu/Linux + separate virtual disk + trusted public key)
       | fsync durable receipt journal
       v
      APPLIED -> DUPLICATE -> restart receiver -> DUPLICATE
       + forged Ed25519 signer -> REJECTED
```

The agent only prints **PASS** and writes `vm-lab-state/FINAL_RESULT.json` after confirming the same receipt and only one new journal entry through the restart. Public cloud-init seed HTTP delivers no private TLS or signing keys; the agent transfers each VM's role-specific credentials over SSH, and the private CA key remains on the Windows host. All generated credentials/disks are excluded from the distributed ZIP and GitHub.

**Verification performed while preparing the bundle:** Node syntax checks on twelve modules, valid cloud-init role construction in dry-run, correct frozen dual5 SHA256 `47d4c89ac8155b9470852e0e23d2c059ad087eedc2b7949632a9431b5792fd4b`, and actual Node-hosted balanced Rust WASM byte-for-byte OBF2 round trip (214 B source to 444 B frame). The existing signed mTLS local acceptance suite also passed.

**Not yet observed:** two QEMU guests actually booted and exchanged the message on the user's Windows laptop. This preparation environment has no Windows/QEMU virtualization access, so `FINAL_RESULT.json` from a real Windows execution remains the acceptance evidence. Until then, VM-to-VM gate remains unverified. Even after a VM-to-VM PASS, physical two-device resilience remains outside this test's scope.

Prerequisites: Windows 11, x64 virtualization in firmware, preferably enabled Windows Hypervisor Platform/WHPX, roughly 8GB+ host RAM, 10GB+ free growing disk capacity, Internet for initial Canonical image and packages. QEMU winget ID `SoftwareFreedomConservancy.QEMU`. Details in the distribution `README.md`.

The existing OASIS/KET kernel, `{{i}}` registry, and frozen OBS dual-floor were not modified. This is an **additive deployment harness**, not another kernel iteration.
