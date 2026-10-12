# Xenonite-X0 / Candidate 001 — ALON Transparent Cubic Spinel

**Recorded:** 2026-10-12  
**Candidate:** aluminum oxynitride, typically written **ALON / AlON**, a *real, polycrystalline transparent ceramic*, NOT the fictional Xenonite of Andy Weir's _Project Hail Mary_.  
**Assessment:** **provisionally suitable material family for studying a curved transparent pressure boundary**. No actual atmosphere-separating Xenonite, complete sealed pressure assembly, or physical sample created.  
**Parent model:** [Xenonite-X0 computational pressure boundary](./XENONITE-X0.md).

## Why ALON is the closest found candidate

1. **Actual crystal structure:** aluminum, oxygen and nitrogen arranged in a cubic spinel (defect-spinel) lattice. This is a **three-element crystal**, not an isolated "Xenonite molecule." Surmet's *approximate* commercial composition is **Al₂₃O₂₇N₅**. The composition is nonstoichiometric and can vary. Some crystal sites contain vacancies.
2. **Optical boundary:** a polished, near-fully-dense ceramic transparent through the visible band and into the near/mid-IR. Surmet indicates optical wavelength range about **0.22–6 µm** depending on wavelength, thickness, surface preparation and grade, not perfect 100% transmission.
3. **Rigid boundary:** NASA Glenn directly measured **Young's modulus 319 ± 1 GPa**, **Poisson's ratio 0.263 ± 0.001**, and **fracture toughness Kᵢᵥᵦ(A) 2.19 ± 0.04 MPa√m** in dry nitrogen on a tested 2015 vintage ALON specimen. These values are **particular measured specimens**, not a universal guaranteed piece rating.
4. **Real propagation and damage:** NASA measured **subcritical / slow crack growth**, documenting a **slow-crack-growth power-law exponent about n = 36** for specimens tested in water and a characteristic specimen strength of about **250.2 MPa**, qualified by flaw populations and finish. This is an independently studied **crack-propagation mechanism under stress**. It is **not** the user's abstract exponential attenuation constant κ or a general natural-death rate.
5. **Assembly / sealing boundary:** Surmet publicly reports work to join ALON windows to metals (including niobium/Kovar) and hermetically seal ALON-to-ALON or ALON-to-metal. Seals, joints, thermal interfaces and compatibility constitute **distinct engineering parts** and are not guaranteed by the ceramic alone.
6. **Limits and alternatives:** **Sapphire (single-crystal Al₂O₃)** and **magnesium aluminate spinel (MgAl₂O₄)** are legitimate other transparent ceramics. Existing commercial sapphire viewports may be a *more mature certified engineered assembly* for particular pressure/temperature requirements, subject to manufacturer ratings.

## Mapping to the user's model (do not overinterpret)

```text
              Xenonite-X0 :: real candidate ALON
    P0 = 1.6165 × 10^-35          [symbolic reference]
           × √5 = 3.6146038856 × 10^-35
                   |
            boundary correction               [MODEL-LOCAL ONLY]
                   |
        +---------------------------+
        | AlON cubic spinel lattice  |        [ACTUAL CRYSTAL]
        | Al — O — N with vacancies  |
        | transparent ceramic body   |
        +---------------------------+
                   |
        real curved shell + real seal          [ENGINEERING ASSEMBLY]
                   |
      Δpressure ⇒ membrane / joint stresses
                   |
       cracks / microdefects can propagate     [NASA MEASURED PROCESS]
                   |
      strength / lifetime are sample dependent
                   |
       Homeo = 10^-26     1 × 1.25 ~           [SEPARATE SYMBOLIC TAGS]
```

Scientific tiers:
- `P/Q/N1`: fundamental references and particles/atomic nuclei. No evidence ALON derives strength from √5 Planck dimensions or homeostatic 10^-26.
- `A`: **Al, O, N actual atoms**. Chemical bonding, electronic structure and periodic crystal lattice are physically explanatory.
- `M`: **solid-state crystal network** in contrast to a molecule. Crystal defects, local bonding and grains govern strength/optics.
- `N2/C/B`: nucleic, cell, organism analogies only. ALON is **not alive**, and has no self-repairing homeostatic mechanism.

## Numeric benchmark context, and why it is NOT a pass/fail material test

The baseline Xenonite-X0 example uses **29 atm inside, 1 atm outside**, an ideal **sphere** with radius **0.2 m** and wall thickness **0.01 m**. The **calculated nominal spherical membrane tension is 28.371 MPa**. This assumes a pressure *difference* of **28 atm**, 1 atm = 101325 Pa, and **positive inside over outside**.

That number must **NOT** be compared directly to the NASA material characteristic strength and labeled a safe ALON pressure window. Real ALON is brittle and flaw-sensitive; its strength is statistically distributed and depends on surface finish, crack geometry, scaling from test specimens, load duration, temperature, environment and edge stress. Flat windows have flexural/edge stresses that the sphere equation misses. NASA's **ISS "kick pane" research** concerns an internal protective pane, not an already certified 29-atm hermetic structural bulkhead. No pressure qualification or extrapolated lifetime is reported for this proposed assembly.

The original Xenonite-X0 calculator keeps **125 MPa** as a hypothetical user-adjustable *allowable*. This is **not** set equal to NASA's 250.2 MPa *characteristic specimen strength*. Characteristic strength and allowable working stress are not interchangeable.

## Highest-priority missing measurements

| Candidate subsystem | What is supported? | Needed for engineering qualification |
|---|---|---|
| AlON ceramic | Production material, cubic lattice, optical and specimen mechanical data | Grade, batch statistics, geometry, validated fracture / lifetime |
| Seal / joining | Manufacturer reported hermetic joining development | Qualified joint, leak rate, differential thermal expansion, interface fatigue |
| Hot ammonia environment | No Xenonite-X0-specific compatibility result established | Temperature-specific chemical stability, permeation, transport, pressure cycle |
| Optical propagation | ALON known to transmit visible/NIR at appropriate thicknesses | Transmission vs wavelength/thickness, loss measured in intended environment |
| Natural mechanical decay | NASA slow crack growth measured under defined laboratory conditions | Flaw spectrum, atmosphere, temperature, loading cycles and fracture life |
| Homeostatic/self-repairing material | No evidence that ALON autonomously detects and repairs cracks | Actual actuator/repair mechanism; do not assume √5 or 1.25 accomplishes this |

## Provenance — original sources

- **NASA Glenn Research Center**, Jonathan A. Salem, _Crack Growth Testing of an Aluminum Oxynitride (AlON) for International Space Station Kick Panes_, NASA/TM—2017-219165, January 2017: <https://ntrs.nasa.gov/api/citations/20170001289/downloads/20170001289.pdf>.
- **Surmet ALON optical ceramics**, original supplier typical properties and cubic structure: <https://cdn.thomasnet.com/ccp/01097403/135889.pdf>.
- **Surmet**, _Versatile ALON Optical Ceramic in Energy Applications_ (2022): manufacturer discussion of ALON-to-metal and hermetic-bonding R&D: <https://www.surmet.com/post/versatile-alon-optical-ceramic-in-energy-applications>.
- **NASA**, _Transparent Armor Ceramics as Spacecraft Windows_, published research abstract: <https://digitalcommons.unl.edu/nasapub/121/>.
- **Commercial high-pressure sapphire window assemblies** — existence of packaged viewports with advertised ratings depends on assembly not loose pane: <https://www.sapphire.lt/products/high_pressure.shtml>.

**Truth-state disposition**: the existence and reported measurements of ALON are **verified** by external sources. ALON as a successful Xenonite stand-in at 29-atm differential in the exact OASIS geometry is only a **candidate**, not verified. The user's √5 boundary/homoe symbols remain model-local and are neither assigned to atom sizes nor used to fabricate ALON.

**No physical synthesis, pressure qualification, active runtime simulation, or frozen KELVIN tests performed.**
