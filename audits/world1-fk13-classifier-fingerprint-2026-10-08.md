# World I: Folded Kernel classifier source analysis — 2026-10-08

## Primary source
DavidWise01/folded-kernel, historical commit cddd6e07255d2ff261175a50ae07e525171cbe7d, original card.html Git blob 77101da9c72908a027dbad8d778bfb74723ff69e. Seal FK-1.3-seal.dlw.json blob b7a59b96a4e4ae1d026ceae91359e4f343885b5a.

## Actual classifier logic extracted
`classify(V,tolD,tolA)`: defaults tolerance to .12 and 1e-6; fewer than 3 values => CATCH TOO SHORT; if all differences equal within tolerance => ADDITIVE; any nonpositive otherwise => CATCH NONPOSITIVE. Log2 adjacent ratios yield exponents. Remove trailing near-zero exponent differences as a floor marker. If remaining exponents near their mean => MULTIPLICATIVE. If they have strictly rising/falling exponent pattern at >.02 => CATCH NONSTATIONARY. Otherwise delete one exponent at a time: if remaining exponents match within tolerance => SEAMED with deleted index, exceptional exponent, and floor. Otherwise CATCH NO VALID GRAMMAR.

## Built-in reference sequences
ROOT0 rail [1,.8,.6,.4,.2,0] => ADDITIVE
ROOT0 value column [64,32,16,4,2,2] => SEAMED, d=1, seam index 2 (16/4=x4), floor=true
Pure chain [32,16,8,4,2,1] => MULTIPLICATIVE d=1
Octree [512,64,8,1] => MULTIPLICATIVE d=3
Bench cost [1.07e9,2.10e6,4.10e3] => expected MULTIPLICATIVE ~d=9
Whisper eps [.4987,.3283,.1833,.0967,.05] => expected CATCH NONSTATIONARY
Garbage [9,3,7,2,9,1] => expected CATCH NO VALID GRAMMAR
The above are **source-defined expected results**. We have inspected definitions, not separately executed the browser test harness this iteration.

## Source-specific fingerprint
{additive difference, multiplicative log-ratio, delete-one-seam, trailing floor, named refusal, 16->4 skip, classified under tolerance}. Much stronger than generic torus, mirror, or duality analogies. The class is not an algebraic group of permutations; dropping exponent as an exceptional seam is a sequence classifier, not a reversible mapping.

## Version chronology caution
FK-1.3 original seal references FK-1.0 ed939169, FK-1.1 c88b5ca1, FK-1.2 4ba44687 as prior card/hash prefixes. Source inspection confirms the REFERENCES; no separate timestamped Git objects for these prefixes were retrieved in this pass. Search over Git commit messages for FK-1.0 and foldkernel returned no predecessor. Do not claim those intermediate binaries/commits independently located.

## ?001 / ?002
Search candidate source code for an equivalent ordered classifier (log-ratio differences + single seam exception + refusal reasons + terminal floor), rather than equating general mathematical features. No transfer path or matched implementation established.
