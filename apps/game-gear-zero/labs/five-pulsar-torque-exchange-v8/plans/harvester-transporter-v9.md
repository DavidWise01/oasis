# Harvester — carrier, clamp, vessel

Status: user-defined symbolic assembly. Design only; not a physical device.

## Canonical roles

- Carrier = adjacent sixfold stages BRACE6 + THRUST6.
- Clamp = a separate coupling element that the carrier brings to the vessel. Do not conflate the clamp with the brace.
- Vessel = the receiving structure around the core {{x^2y^2z^2}}.
- Harvester = carrier + clamp + vessel, the user's name for the combined assembly.

## Transporter order

    GYRO1
      |
    DIRECTION3
      |
    +---------------- CARRIER ----------------+
    | BRACE6 ---- THRUST6                     |
    |                    carries CLAMP        |
    +----------------------+------------------+
                           |
                       [ CLAMP ]
                           |
                       [ VESSEL ]
                    {{x^2y^2z^2}}
                           |
                        BRACE6
                           |
                     DIRECTION3
                           |
                         GYRO1

Ordered source expression:
    gyro1direction3brace6thrust6{{x^2y^2z^2}}6brace3direction1gyro

HARVESTER := CARRIER + CLAMP + VESSEL.

## Relationship to earlier numeric envelope

Earlier literal: 1x3x6xx6x6x3x1.
Numerical stages: 1 / 3 / 6 / 6 / 6 / 3 / 1.
The source stage labels now identify input gyro1, direction3, brace6, thrust6, then the transporter core, outbound brace6, direction3, gyro1. The adjacent BRACE6/THRUST6 stages form the carrier.

Preserve the doubled 'xx' from the original notation as an unresolved specific junction operator. The naming of a transported clamp does not establish the precise machine implementation of that operator.

## Read-only v9 integration proposal

The existing Hall grammar on every instrumented vector is {{-+000+-}}; 19 rails and 57 virtual Hall positions are specified but not yet installed. Suggested new observation interfaces, beyond that existing 19-rail manifest:

1. Direction3 to carrier BRACE6: alignment and ingress witness.
2. BRACE6 to THRUST6: carrier motion command and response witness.
3. Carrier to CLAMP: transported-clamp identity and engagement readiness.
4. CLAMP to VESSEL: arrival, attachment, and acknowledgement receipt.
5. VESSEL core to outbound BRACE6, DIRECTION3, GYRO1: completion and stabilization receipt.

No physical Hall fields, transport forces, clamp mechanics, or real x²y²z² volume semantics have been established. No claim of functional matter transport or harvesting. Keep existing v8 torque/ground engine, ledgers, and Hall-manifest unchanged.

Structured file: harvester-transporter-v9.json
Earlier literal: vessel-1x3x6xx6x6x3x1.md
Hall layout: hall-rails-v9.md
