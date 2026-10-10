# 0ROOT Gate 04 — Babylonian Astronomical Diaries
Date: 2026-10-10
Status: documentary evidence inventory; no claimed validation of A.E.O.N. physics.

## Historical chronology
- Earlier sources: Old Babylonian Venus Tablet observations; MUL.APIN organized stellar and calendar material.
- The earliest *surviving* Astronomical Diary is dated 652 BCE. The sequence is fragmentary, with only another pre-5th-century-BCE survivor around 568 BCE. This does NOT establish the start of astronomy or prove uninterrupted surviving records.
- Critical edition: Abraham J. Sachs and Hermann Hunger (1988), Astronomical Diaries and Related Texts from Babylonia, vol I, Diaries from 652 B.C. to 262 B.C.
- These tablets record observations and contextual information, rather than merely synodic period approximations.

## Data schema for actual observations
Each original entry should become:
`(tablet_id, original_line, year, month, day, dating_system, calendar_conversion_uncertainty, object, phenomenon, relative_reference_star, direction, observer_conditions, observed_or_not_watched, source_uri)`.
Recorded categories: Moon/sky reports, visible planet positions, weather, prices, Euphrates river levels, and notable events.
Do not infer a planet was invisible from a written `I did not watch` due to cloud or non-observation.

## Leap-year/calendar discipline
- Babylonian chronology used a lunisolar calendar with intercalary months (calendar intercalation is NOT the Gregorian February 29 leap-day formula).
- Maya Haab is a 365-day fixed cycle, not a Gregorian civil year.
- Modern Gregorian conversion requires explicit BCE astronomical-year handling, Julian/Gregorian distinction, and uncertainty. Never map BCE diary dates onto proleptic Gregorian dates silently.

## Scientific comparison
Test date-tagged planetary visibility events against astronomical calculations with an explicit Earth location and local horizon. The rounded 584-day Venus counter is a hypothesis baseline, not the observation itself.
Potential checks: predicted vs observed first appearance, last appearance, lunar conjunction, lunar visibility and observational gaps.
A.E.O.N. `[.0.]` and append-only audit are computational analogies, not terms attested in the diaries.

## Research sources
- https://pmc.ncbi.nlm.nih.gov/articles/PMC5127895/ (refereed article on diaries, their structure, observing gaps and earliest preserved year)
- https://cdli.earth/publications/1733952 (bibliographic record of original Sachs–Hunger vol I edition)
- https://catalogue.bnf.fr/ark:/12148/cb35024229q
- https://www.britishmuseum.org/collection/object/W_1881-0706-403 (323 BCE diary mentioning Alexander's death, evidence of historical diary context; much later than 652 BCE)

## Next gate
Obtain transcription/translation of Diary No. -651 (652 BCE) from authoritative publication, select five complete line-specific events, record original dating and missing-data indicators, and compare to astronomical ephemerides. Do not invent line quotations.
