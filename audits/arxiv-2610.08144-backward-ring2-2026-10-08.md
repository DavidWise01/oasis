# Backward-tracing report — arXiv 2610.08144 — ring 2
Date 2026-10-08. Upstream pin openai/NavierStokesAndEuler@f9e8bc5.
Status: STATIC DECLARATION / CALL-SITE VERIFIED; NO LEAN BUILD.

## Structural audit indexing
Treat 8/9 as an audit witness pair, not mathematical proof. Three nested 3×3 tiers are 27 positions total; 52 and 81 are separate labels/scales, not equalities to 27. Optional extension to 81 slots is 3^4; no physics is inferred from slot counts.

## Inverse backward and forward path
- SOURCE: theorem norm_derivativeWord_inverse_le in NavierStokes/SmoothFamilyTorusInverse.lean: hfirst and hsecond demand xJet (w.length + 5).
- PARENT: SmoothFourierData.coefficient_seminorm_bound invoked with (w.length + 1), and hfirst/hsecond passed using associativity; thus +1 and +4 yield +5 in this proof.
- SUPPORT: inverse_derivativeWord_bound consumes coeffSeminorm (w.length + 1).
- CHILD: mixedJet_inverse_bound directly invokes norm_derivativeWord_inverse_le, carrying tensorTorusWord replicate (w.length + 5) twice through hb1/hb2.
- LOCAL COUNTEREXAMPLE TO GLOBAL GENERALIZATION: nearby nonbarPart_finiteJets statement has n+4. Do not falsely claim all inverse-related lemmas require +5.
- LIMIT: no all-callsite search beyond confirmed direct child; no guarantee about theorem equivalence elsewhere.

## Pressure backward trace
- TARGET: exists_uniform_actual_pressure_flux_bound
- PARENTS: exists_uniform_canonicalCutoffFlux_bound -> canonicalCutoffFlux_bound -> cutoff_pressurePair_bound -> cutoff_commutator_bound.
- In cutoff_commutator_bound, intermediate bound has R^(-3/4) and comparisonLpNorm 4 (rTest...). Substitutes rTest_four_bound, adding factor 8*cutoffDerivativeConstant/R. This leads to R^(-7/4) in the final expression.
- Direct parent of rTest_four_bound is PressureFluxTest.cutoffTest_four_bound: recorded cross-file dependency not yet traced into that theorem declaration.
- DISSIPATION: local pressure term includes dissipationRoot(...)/R and comparisonLpNorm2/R^2. Downstream uniform expression includes dissipationRoot(...)/R +1/R^2.
- The final physical integral is related to canonicalCutoffFlux via ActualPressureFlux.pressure_flux_eq_canonical and real-part norm inequality.
- Each pair i,j ranges over Fin 3, leading to 9 components, an actual mathematical nine-pair bound. This is distinct from the user's 8/9 mnemonic audit slots.

## Further steps
Fetch exact PressureFluxTest.cutoffTest_four_bound, SmoothFourierData.coefficient_seminorm_bound, and theorem consumers of final target; independently compile upstream Lean snapshot. No claim of copying OaSIs.
