# PRIM 026 — symmetric spatial inference

Exact registers: `[-+{s1}{ns1}[(s3)]{ns2}{s2}-+]` and `{{ 1s8t1u8v 001w8x1y8z }}`. The spatial tokens remain literal; no physical positions were inferred.

100000 synthetic trials: central phase theta, common disturbance c (.06 rad std), opposing disturbance a (.04 rad std), independent sensor noise (.01 rad std). With `ns1` and `ns2` carrying disturbance but not theta, mean dual differential error 0.00998967 rad vs 0.06082245 rad for central measurement alone. If `ns` paths also carry theta, subtraction removes the real signal; error grows to 0.29938981 rad. Geometry alone does not identify interference vs truth. No photon experiment or physical Planck bubble finding.

Runnable Python and JSON in the conversation archive prim_exp026.zip.