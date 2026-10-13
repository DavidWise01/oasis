# E.T. / Energy Titan — Sapien Six-Channel 3D WASM v0.6
**2026-10-13 — additive to frozen KET v2.0.**

## Built release
A fully offline HTML dashboard with genuine compiled wasm32 computational core; 6 independent Sapien Phone nodes at signed X/Y/Z directions, one coordinate origin (not a seventh channel); 6 channel gates and adjustable logical message rates; independent toroidal 3D cells; ring / off / broadcast routing; seed, depth, pulse, threshold, tick generator, 3D canvas-perspective viewport, JSON / CSV / PNG export.

The **complete runnable HTML, compiled `.wasm`, 3D native SVG blueprint, original C, browser screenshots, all tests, manifest, and Nginx Ansible playbook** were delivered as the conversation archive `KET_Energy_Titan_Six_Channel_3D_WASM_v06.zip`. **The archive and compiled HTML are NOT represented as hosted on GitHub by this document**. The GitHub directory provides the release contract and Ansible deployment files only.

## Six signed channels
| ID | Vector | 3D coordinate |
|---|---|---|
| CH01 | −X | (-1,0,0) |
| CH02 | +X | (+1,0,0) |
| CH03 | −Y | (0,-1,0) |
| CH04 | +Y | (0,+1,0) |
| CH05 | −Z | (0,0,-1) |
| CH06 | +Z | (0,0,+1) |

Origin `0` is a coordinate routing reference, not a seventh phone. Time is a linear simulation tick. Six KET instances preserve their independent `360+3+3=366` frozen logical registers. The 3D WASM simulation creates `6 × 360 × radial_layers` ephemeral cells (default 6480, 1–6 layers). Permanent holes stay open, no additional enclosing KET geometry. Seeded cells have ready, excited and refractory states.

Routing: `OFF` yields zero cross-node deliveries; `RING` sends to the next signed node if both channels online; `HUB` forwards to all other online nodes from an origin-routing *logic* reference. Per-node gates control packets, not living cellular state. Controller at baseline closes to 360° at tick 360 independently on all six nodes.

## Tests from companion archive
- Node.js real WASM checks: **70/70 PASS**.
- System-Chromium browser tests: **24/24 PASS**, no JS exceptions. JSON / CSV / PNG exports exercised.
- Compiled wasm32 binary SHA256: `68f367bd352467c552d40b2e0ecdf0e5685b2eb624a8bd63c152bd2d25cd7eec`.
- Standalone compiled HTML SHA256: `559a6287c6024a031233273af49146a657d490a088f0fd055d3254dbfe296118`.
- Ansible playbook SHA256 in companion ZIP: `52da4271a07c40a3ae43d28297241de2ba102a9378ce46885795d297db84ce36`.
- ZIP SHA256: `8e15a319353f52f0815f970c7645b3ef61637c1c185d42ab72b13b1bfca2de4e`.
- CRC, member file SHA256s and native SVG XML parse passed.
- **Ansible was not executed against a real Debian/Ubuntu host**; YAML was statically parsed/reviewed. Deployment script is delivered as source only until executed by the user.

## Hosting with Ansible
Extract the companion archive preserving `ansible/` and `index.html` paths. Run within `ansible/`:

```bash
ansible-playbook -i inventory.example.ini deploy.yml --ask-become-pass
```

Installs Nginx on Debian/Ubuntu, copies the fully self-contained HTML, configures localhost port 8086 by default, validates Nginx and checks the served app. This does **not** configure real Wi-Fi, transmit electricity, or expose a public service by default.

## Scientific honesty
“E.T. / Energy Titan” is a project name, not an established physical mechanism. All transfers are **software messages**. No hardware RF wireless-power claims or literal Planck-scale physics. This is a functional symbolic model.

Pinned kernel v2.0: `de8f8b80aba3a73dd371811f6b4be39df92e45ce`; not modified. Rule 01 six symbolic boundaries plus one open hole, Rule 02 independent optional exchange, Rule 03 six signed spatial directions. Exact Green Chariot remains `123 {{45/|\54}} 678`.
