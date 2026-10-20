# Harvester v11 — Powered Carrier Stroke & Clamp Force Budget

[Open the standalone browser lab](./index.html) | [Read the pure motion engine](./engine/harvester-motion.js) | [Previous v10](../harvester-hall-clamp-v10/)

## What changed

V10 modeled Hall witnesses and clamp engagement but never moved its clamp to the vessel. V11 introduces a **powered finite-stroke carrier** transporting its clamp from a normalized x=0 station to the {{x²y²z²}} vessel at x=1. The original v10 executable and the v8 sun/gyro engine remain separate and unchanged.

The Harvester hierarchy is GYRO1 → DIRECTION3 → BRACE6 + THRUST6 (carrier) → CLAMP → {{x²y²z²}} (vessel) → BRACE6 → DIRECTION3 → GYRO1. Existing sensor grammar **{{-+000+-}}** remains read-only: 19 rails, 13 computed virtual signal paths, 6 visual-only perimeter connections, 57 virtual Hall-sensor positions.

## Motion law (dimensionless simulation)

Mass m=1 by default, dt=1/64 model cycle, x in [0,1]. A bounded actively powered PD servo applies:

    u = clip(load + 10(target-x) - 5.5*v, -thrustMax, +thrustMax)
    F = u - load - damping*v_mid
    v_next = (m*v + dt*(u-load-damping*v/2)) / (m+dt*damping/2)
    x_next = clip(x + dt*(v+v_next)/2, 0, 1)

A hard endpoint stop sets v=0 and records the difference as boundary work. The independently tracked mechanical-energy identity is:

    kinetic + potential = epochEnergy + motorWork - viscousLoss - boundaryWork
    kinetic = m*v²/2       potential = load*x

This is a powered mechanism. No free energy, real propulsion or gravitational acceleration is implied by the model.

## Nine interlocks

Existing v10 checks (six): Hall sensor path, carrier alignment, ring/sun counterspin, delayed cable, symbolic ground, orientation.

New v11 checks (three):
1. **Position:** x ≥ 0.978.
2. **Velocity:** |v| ≤ 0.08 per model cycle.
3. **Hold-force margin:** holdCapacity − [load+disturbance+0.15|v|] ≥ 0.18.

Start from rest. Click NEXT CLAMP STEP to enter APPROACH, then DRIVE +128 / DOCK. The carrier normally arrives at x≈0.982, v≈0.051, with positive hold-force margin. Then proceed ALIGN → ATTACH → VERIFY → VERIFY → SECURED; the two verification samples must have distinct ticks.

Under insufficient thrust (≤ load), the carrier cannot depart x=0. Under force overload after SECURED, the clamp enters SAFE_HOLD without falsely recording it detached. RESET is denied. To disengage, issue RELEASE, perform actual modeled retraction to x≤0.02 at |v|≤0.08, and only then use NEXT to mark COMPLETE.

The simulator includes sliders for thrust, payload bias, holding capacity and damping; graphically animates the clamp on its track; shows force margin, velocity, motor work, viscous/boundary heat and ledger closure; and exports witness receipts as JSON and original visuals as PNG/TXT.

## Verification

In a local Node environment, the comprehensive v11 numerical test suite passed **26,384 deterministic assertions**, including motor stall, default dock, energy closure, slider rebasing, Hall fault, overload, latched SAFE_HOLD and full release. The inherited v10 reference tests passed **117,630 deterministic assertions**. Chromium desktop/mobile tests passed for all of those UI sequences plus ASCII/JSON/TXT/PNG downloads.

The downloadable ZIP includes the complete standalone HTML, reference motion engine, full tests and browser screenshots. The GitHub repository includes the standalone, self-contained model and a direct motion-engine source copy.

## Scope / limitations

This is a deterministic **symbolic engineering simulator**. There is no simulated magnetic field in tesla, physical Hall device, actual holding force in newtons, usable thrust actuator, black-hole electrical ground, transporter, harvester apparatus or produced 1g acceleration. 29.75 km/s is a user-defined visualization label, not a measured carrier speed. Keep the explicit 1g* balance **proxy** separate from physical gravity.
