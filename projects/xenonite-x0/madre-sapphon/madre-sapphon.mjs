/**
 * Madre Sapphon / Aa.Nn.Nn — manual live parent vessel for the frozen KELVIN v11.3 kernel.
 *
 * Parent-facing symbolic shell with Au79 core and 10 (+5/-5) magnetic-view registers.
 * It imports, never rewrites, the real KELVIN instantiateKelvin() state machine.
 *
 * This is not a molecular model, magnetic field solver, autonomous agent,
 * certified pressure vessel, physical experiment or claim that Aa/Nn are elements.
 */
import { KELVIN, instantiateKelvin } from "../../sapphon-li/kelvin.mjs";

const positive = Object.freeze([1, 2, 3, 4, 5]);
const negative = Object.freeze([-1, -2, -3, -4, -5]);
const fieldBands = Object.freeze(["weak", "medium", "strong"]);
const sectors = Object.freeze([0, 1, 2, 3, 4, 5, 6, 7]);

export const MADRE_SAPPHON = Object.freeze({
  id: "Aa.Nn.Nn",
  title: "Madre Sapphon",
  family: "SAPPHON",
  role: "parent / enclosing vessel / maternal shell",
  parentOf: "the local Au79/KELVIN vessel view only (symbolic)",
  generation: 0,
  offspringAutonomy: false,
  outerPrimitive: "-+",
  pinnedReference: "0",
  tensorCount: 1,
  worldCount: 1,
  tracks: Object.freeze(["i", "u", "us"]),
  goldCore: Object.freeze({
    symbol: "Au",
    atomicNumber: 79,
    naturallyStableIsotope: "Au-197",
    silverPartner: "Ag-47",
    electrum: "Au-Ag alloy",
    goldIsStructuralPressureSeal: false
  }),
  envelope: Object.freeze({
    notation: "Aa.Nn.Nn",
    actualElements: false,
    allPhysicalProperties: "unspecified",
    physicalCandidate: "aluminum oxynitride (ALON), separate measured material",
    materialQualified: false
  }),
  geometry: Object.freeze({
    positiveSurfaces: positive,
    negativeSurfaces: negative,
    spatialSectors: sectors,
    labeledStrengthBands: fieldBands,
    surfaceCount: 10,
    sectorCount: 8,
    scenarioBands: 3,
    viewSlots: 240,
    physicalMagneticIsosurfaceSolution: false
  }),
  boundary: Object.freeze({
    userScale: "1.6165e-35",
    correction: "sqrt(5)",
    correctedValue: Math.sqrt(5) * 1.6165e-35,
    unit: null,
    homeo: 1e-26,
    homeoNotation: "10^-36 × 10^10",
    separateHomeostaticMarker: "1 × 1.25 ~",
    physicalPressureCoupling: false
  }),
  KelvinVersion: KELVIN.version,
  maxManualTransitions: 128,
  runtime: "operator-driven, in-memory, append-only, no timers",
  physicalExperiment: false
});

function finiteNumber(value, label, minimum, strict) {
  const number = Number(value);
  if (value === "" || value === null || value === undefined ||
      !Number.isFinite(number) || (strict ? number <= minimum : number < minimum)) {
    throw new RangeError(label + " must be " +
      (strict ? "greater than " : "at least ") + minimum);
  }
  return number;
}

export function evaluateVessel(inputs = {}) {
  const insideAtm = finiteNumber(inputs.insideAtm ?? 29, "inside pressure (atm absolute)", 0, false);
  const outsideAtm = finiteNumber(inputs.outsideAtm ?? 1, "outside pressure (atm absolute)", 0, false);
  const radiusMeters = finiteNumber(inputs.radiusMeters ?? 0.2, "radius (m)", 0, true);
  const thicknessMillimeters = finiteNumber(inputs.thicknessMillimeters ?? 10, "thickness (mm)", 0, true);
  const assumedAllowableMPa = finiteNumber(inputs.assumedAllowableMPa ?? 125, "assumed allowance (MPa)", 0, true);
  const pathMeters = finiteNumber(inputs.pathMeters ?? 0.5, "path (m)", 0, false);
  const attenuationPerMeter = finiteNumber(inputs.attenuationPerMeter ?? 0.8, "attenuation coefficient (/m)", 0, false);

  // Positive means greater pressure inside the hypothetical sphere than outside.
  const deltaPascal = (insideAtm - outsideAtm) * 101325;
  const wallMeters = thicknessMillimeters / 1000;
  const sphericalTensileStressMPa =
    deltaPascal > 0 ? deltaPascal * radiusMeters / (2 * wallMeters) / 1e6 : null;
  const cylindricalComparisonMPa =
    deltaPascal > 0 ? deltaPascal * radiusMeters / wallMeters / 1e6 : null;
  const stressUtilizationPercent =
    sphericalTensileStressMPa === null ? null :
      100 * sphericalTensileStressMPa / assumedAllowableMPa;
  const projectedForceKilonewtons = Math.abs(deltaPascal) *
    Math.PI * radiusMeters ** 2 / 1000;
  const passiveRetainedFraction = Math.exp(-attenuationPerMeter * pathMeters);
  const warnings = [];
  if (deltaPascal <= 0) warnings.push("Zero/external pressure: buckling and collapse are not modeled.");
  if (wallMeters / radiusMeters > 0.1) warnings.push("Wall/radius > 0.1: thin-shell approximation may be inaccurate.");
  if (stressUtilizationPercent !== null && stressUtilizationPercent >= 100) {
    warnings.push("The USER-ASSUMED membrane stress allowance is exceeded.");
  }
  warnings.push("Seal leakage, ALON fractures, flat plates, fatigue, temperature and gas chemistry are NOT modeled.");
  return Object.freeze({
    inputs: Object.freeze({insideAtm,outsideAtm,radiusMeters,thicknessMillimeters,
      assumedAllowableMPa,pathMeters,attenuationPerMeter}),
    pressureDifferenceAtm: insideAtm - outsideAtm,
    pressureDifferenceMPa: deltaPascal / 1e6,
    sphericalTensileStressMPa,
    cylindricalComparisonMPa,
    stressUtilizationPercent,
    projectedForceKilonewtons,
    passiveRetainedFraction,
    passiveFractionIsMaterialLifetime: false,
    envelopeIsValidated: false,
    warnings: Object.freeze(warnings)
  });
}

/** A manually advanced Au79-at-zero vessel using EXACTLY the canonical Kelvin engine. */
export function createMadreSapphon() {
  const kelvin = instantiateKelvin();
  const records = [];

  function current(inputs = {}) {
    return Object.freeze({
      identity: MADRE_SAPPHON,
      kelvin: kelvin.current(),
      measuredInModel: evaluateVessel(inputs),
      recordedTurns: records.length,
      remainingManualTurns: MADRE_SAPPHON.maxManualTransitions - records.length,
      symbolicSurfaces: Object.freeze([...negative, ...positive]),
      observerSlots: MADRE_SAPPHON.geometry.viewSlots
    });
  }
  function advance(inputs = {}) {
    // Validate BEFORE mutating Kelvin; avoids partial state change on bad input.
    const measurement = evaluateVessel(inputs);
    const from = kelvin.current();
    const to = kelvin.advance();
    const record = Object.freeze({
      sequence: records.length + 1,
      action: "human-triggered Kelvin 360-degree step",
      fromTurn: from.turn,
      toTurn: to.turn,
      fromShell: from.shell,
      toShell: to.shell,
      signedFace: to.signedTensorFace,
      pole: to.poleLabel,
      snapshot: measurement,
      observationClassification: "symbolic + parameterized engineering arithmetic, not laboratory data"
    });
    records.push(record);
    return Object.freeze({ state: to, record });
  }
  function ledger() {
    return {
      schema: "oasis.madre-sapphon.aa-nn-nn.live-kelvin.v1",
      identity: MADRE_SAPPHON,
      kelvin: kelvin.ledger(),
      records: records.map(x => ({ ...x })),
      scientificStatus: "local interactive symbolic and idealized engineering prototype; no physical claim"
    };
  }
  function report(inputs = {}) {
    return {
      identity: MADRE_SAPPHON,
      current: current(inputs),
      recordCount: records.length,
      originalKelvin: kelvin.report(),
      nextManualActionOnly: records.length < 128,
      noAutonomousExecution: true
    };
  }
  return Object.freeze({
    identity: MADRE_SAPPHON,
    current, advance, ledger, report
  });
}
