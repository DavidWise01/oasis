# AETHER-125 — Failed recovery gate (preserved)

The original **320 synthetic paired episodes**, 40 seeds × eight replacement scenarios × 32 ticks, passed 4,480 deterministic tests and produced zero unsafe actions under the guarded policy versus 1,120 unsafe actions with inherited instrument authority.

**Acceptance FAIL:** the initial test defined recovery as the first packet with a valid new calibration and timing certificate. In 13/40 noisy-replacement episodes, that packet's risk error bound still mandated HOLD. The initial recovery check reported **307/320** instead of the required 320/320.

The failure is *not* evidence that unsafe action was taken; it reveals a conflation of sensor readiness with independent risk authorization. This case earns no turn progress. [Accepted correction](../125b/) retains the detector and redefines recovery to the first *risk-admissible* fresh packet, checked independently.

The sources are synthetic and assume authenticated device identity, certificate issuer, protected acquisition counter and probe truth.
