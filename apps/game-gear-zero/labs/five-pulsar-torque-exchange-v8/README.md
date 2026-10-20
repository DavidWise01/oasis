# Five Pulsars v8: Torque-Exchange Core

[Open live HTML](https://davidwise01.github.io/oasis/apps/game-gear-zero/labs/five-pulsar-torque-exchange-v8/) | [Stand-alone HTML](./index.html) | [Previous v7](../five-pulsar-central-bearing-v7/)

This is the next separate version after the existing v7, preserving the five [-!+] pulsars, the five-gyro baseline, the sixth delayed-return node, CCW carrier, central sun, CW bearing ring, and symbolic black-hole ground. The full 4^4 = 256 RGBP state registry is unchanged.

## Powered reaction torque

Two equal **normalized** inertias (ring and sun), with signed rates in turns/model cycle. CCW positive; intended ring = -1, sun = +1.

Define d = sunRate - ringRate and m = (sunRate + ringRate)/2.

- Torque on ring T = k(d - 2); torque on sun is exactly -T.
- Relative rate d(t) = 2 + (d0 - 2) exp(-2 k t).
- Mean rate m(t) = m0 exp(-g t); g = 0 when ground disconnected.
- Ring rate = m(t) - d(t)/2; sun rate = m(t) + d(t)/2.

The torque is **actively powered**; internal torque can correct d but cannot change the sum of the pair's angular momentum. Only the modeled ground path reduces m, with a corresponding reaction momentum ledger.

## Ledger

- Normalized rotor kinetic energy = m² + d²/4.
- Motor work = (d(t)² - d0²)/4.
- Ground heat = m0² - m(t)².
- Energy closure: kinetic + ground heat = initial kinetic + motor work.
- Ground reaction momentum = 2(m0 - m(t)).
- Angular momentum closure: ring rate + sun rate + ground reaction = initial total angular momentum.

Manual kicks are outside impulses. The ledger is restarted at each kick so the externally supplied energy/impulse is not silently attributed to the motor.

## Live controls

START FROM REST, KICK RING (+0.68), RELOCK TORQUE PAIR, active torque gain K, ground load G, ground connect/disconnect, five pulsar rates, color state 0..255, cable delays, symbolic flare, ASCII, PNG/TXT and four visualization themes. A new oscilloscope plots both velocities, counterspin error, and mean drift, and the sidebar reports torque, motor work, ground heat, ground reaction, and conservation residual.

## Verification

Run node tests/torque.test.cjs from this folder. The local comprehensive regression suite passed **24,612 checks** (zero torque at equilibrium, release from rest, powered spinup, K=0 stall, kicked response, ground on/off, and conservation ledger). Chromium desktop and mobile tests passed including live controls, existing cable/flare behavior, ASCII view and PNG/TXT export.

## Physics boundary

This is a deterministic, *actively driven* mathematical control model, **not** passive self-powered motion or demonstrated gravity. The 1g* metric is a unitless balance score. The 29.75 km/s carrier label is a user-specified linear speed; without an actual radius it does not determine angular speed or centrifugal acceleration. No physical black-hole/electron/pulsar mechanism is asserted.
