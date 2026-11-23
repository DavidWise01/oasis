# AETHER-124B — Corrected bounded-noise uncertainty propagation

**Accepted synthetic test:** 450 paired episodes × 24 ticks = 10,800 decisions per policy. **6,300/6,300 checks passed**. One-controller verified interval policy authorized **zero unsafe actions**, compared with **three unsafe actions in failed AETHER-124**.

The controller computes a conservative rectangle containing all affine gain/offset combinations compatible with four interior pilot responses and the declared bounded noise magnitude. For measured count y, certified noise bound ε, minimum compatible gain g_min and minimum compatible offset b_min, the **maximum plausible count** is at most `(y + ε − b_min)/g_min`, clipped to 0..560. The model uses ceil of that maximum when testing the one-sided 95% binomial risk bound. A missing or unverifiable noise certificate forces HOLD.

Clean safe actions **800/800** preserved. As noise bound rose from 1 to 3 to 6, safe actions decreased **773 → 250 → 45**. Overall safe ACT **6,587 point estimate versus 3,259 uncertainty-aware**; total illustrative costs **242,449.6 versus 362,667.2** due to conservative holds and additional calibration.

**Important limitations:** Bounds require true affine response, authentic probes, signing and truthful bounded-noise certificates. Per-decision 95% statistical bounds do not themselves control simultaneous familywise failure over repeated actions. The evaluation is synthetic, not field validation. AETHER-124 failure is retained rather than overwritten.
