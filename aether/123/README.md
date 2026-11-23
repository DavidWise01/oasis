# AETHER-123 — Failed acceptance preserved

Four interior probes at error counts 32, 96, 160, 224 permitted constrained affine gain/offset estimation. The initial variant applied a **mandatory +3 corrected-error margin**, even to an exact identity-calibrated sensor. It passed 7,560 deterministic checks, had zero unsafe ACT, and restored actions for several corrected faults, but **FAILED clean and hazard availability gates**: clean safe ACT fell 839→810; hazard-shift safe ACT fell 480→467. The no-regression gate was predeclared and this run earns **no phase credit**.

AETHER-123B fixes the exact-identity case without weakening nonidentity corrections. See [123B](../123b/). Synthetic only; no general safety assurance.
