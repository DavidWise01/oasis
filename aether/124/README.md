# AETHER-124 — Failed uncertainty propagation preserved

The initial experiment used the **minimum plausible sensor error count** for conservative authorization. This was an incorrect inequality direction: it underestimates risk. On 450 paired synthetic episodes the interval policy authorized **3 unsafe actions**, so its acceptance gate **FAILED**. No phase progress is earned here. Source, failing results and manifest are preserved unchanged by the correction.

See [AETHER-124B](../124b/) for the corrected maximum plausible count.
