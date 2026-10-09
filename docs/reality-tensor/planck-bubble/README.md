# ROOT0 P3.6 — Nested Planck Bubble | Orange-in-black

**Input, unmodified:** `{-e{gray{+e{white}}` — this prefix has two unclosed `{`. For display only, two `}` are appended: `{-e{gray{+e{white}}}}`.

An **outside black −211 mV electrum boundary** surrounds a **gray optical shell**, then a **+e port** and **white core**. The target radius is the CODATA Planck length, **1.616255×10⁻³⁵ m**. This is a *user-defined symbolic coordinate model*, not a demonstrated subatomic structure.

Open `standalone.html` (single file, no network), or serve `index.html` with its ES modules. The explorer has a logarithmic bubble-depth coordinate; the dial is expressly *not* physically achieved confinement or transport. The optional orange-wave `λ` and electrum-film `T` are independent parameters. The original 208-gate forward and 208-gate mirrored inverse cipher is reused without alteration.

## Reproduce

```bash
node test_p36.mjs
python test_browser.py
```

For `test_browser.py`, Chromium and Playwright are needed. The tested `standalone.html` is used with `set_content` because localhost and file-navigation may be restricted.

The two-channel complex wave mixing uses two explicit environment/loss channels: outer electrum and gray aperture. The full *three-mode* transformation is unitary and its reverse returns the original state. This **does not imply physical absorbed light can be recovered**; the bath states are an additional modeled and typically unobserved system.

`T_ap = [64/(27π²)](2πr/λ)^4` is the *Bethe–Bouwkamp ideal, zero-thickness perfectly conducting aperture* expression, used only in its nominal `kr≤0.1` domain. Numerically extrapolating to ℓP gives an illustrative `log10(T)` value, but **ordinary Maxwell/continuum optics and the ideal-aperture result are not validated at Planck distances**. A transparent “portal” is a separate arbitrary hypothesis, not derived.

**Scientific verdict:** physical Planck penetration/quantum gravity not established; the −211 mV value alone provides only 0.211 eV per electron charge, not a Planck-wavelength photon. Frozen v92 kernel and prior P3.1 cipher are unchanged. See `REPORT.md` and `p36-results.json`.
