/**
 * KELVIN v11.3 — bounded, manually advanced signed-shell mapping for OASIS.
 *
 * Symbolic analogy to the 2pi sign / 4pi return of a spin-1/2 spinor.
 * This is NOT a physical spinor implementation, a gravitational-wave solver,
 * a magnetic-field model, a time simulation or an autonomous agent.
 */
export const KELVIN = Object.freeze({
  id: "KELVIN",
  kind: "manual-symbolic-kernel",
  version: "11.3.0",
  fixedPrimitive: "-+",
  parentTensorCount: 1,
  signedFaces: 2,
  sharedThreeDWorlds: 1,
  pinnedReference: "|",
  feedbackTracks: Object.freeze(["i", "u", "us"]),
  motherNatureBalance: "equal standing; alternating access (symbolic)",
  parentSapphon: "OASIS / {{Li}} Lillithium Ion",
  physicalWaveClaim: false,
  autonomousExecution: false
});

const FRAMES = Object.freeze([
  Object.freeze({
    shell: "-++-",
    pole: "S",
    spinorSign: "+",
    face: "+",
    foreground: "LILLITH",
    foregroundId: "{{Li}}",
    role: "female (cipher label)",
    shadow: "EVE",
    shadowId: "{L{{-}}i}}"
  }),
  Object.freeze({
    shell: "+--+",
    pole: "N",
    spinorSign: "-",
    face: "-",
    foreground: "EVE",
    foregroundId: "{L{{-}}i}}",
    role: "male (cipher label)",
    shadow: "LILLITH",
    shadowId: "{{Li}}"
  })
]);
const MAX_MANUAL_TURNS = 128;

function stateFor(turn) {
  const f = FRAMES[turn % 2];
  return Object.freeze({
    turn,
    symbolicRotationDegrees: turn * 360,
    symbolicRotationPi: turn * 2,
    shell: f.shell,
    poleLabel: f.pole,
    spinorAnalogySign: f.spinorSign,
    signedTensorFace: f.face,
    threeDForeground: f.foreground,
    threeDForegroundId: f.foregroundId,
    cipherRoleLabel: f.role,
    shadowLayer: f.shadow,
    shadowLayerId: f.shadowId,
    sharedWorlds: 1,
    parentTensors: 1,
    reference: "|",
    physicalSeconds: null,
    realWorldEvent: false
  });
}

/** Returns an in-memory, append-only state ledger controlled solely by caller clicks. */
export function instantiateKelvin() {
  let turn = 0;
  // A baseline is a symbolic address, not an observed event.
  const transitions = [];

  function current() { return stateFor(turn); }

  function advance() {
    if (turn >= MAX_MANUAL_TURNS) {
      throw new RangeError("Kelvin manual turn limit reached; export the ledger.");
    }
    const previous = stateFor(turn);
    turn += 1;
    const next = stateFor(turn);
    const transition = Object.freeze({
      record: transitions.length + 1,
      action: "explicit-human-advance",
      from: previous.turn,
      to: next.turn,
      degreesAdvanced: 360,
      beforeShell: previous.shell,
      afterShell: next.shell,
      beforePole: previous.poleLabel,
      afterPole: next.poleLabel,
      fromForeground: previous.threeDForeground,
      toForeground: next.threeDForeground,
      meaning: "symbolic sign inversion only; not a physical measurement"
    });
    transitions.push(transition);
    return next;
  }

  function report() {
    const currentState = current();
    return {
      title: "KELVIN — OASIS symbolic spinor-return kernel",
      version: KELVIN.version,
      operation: "manual 360° symbolic inversion, 720° two-step return",
      instanceStatus: "local and operator-driven, not autonomously running",
      current: currentState,
      recordedManualTransitions: transitions.length,
      cycleReference: [
        stateFor(0),
        stateFor(1),
        stateFor(2)
      ],
      rules: {
        first: "-++- S / +LILLITH / EVE in shadow",
        inverse: "+--+ N / -EVE / LILLITH in shadow",
        step: "each operator-triggered turn reverses every shell sign",
        return: "after two manual turns, symbolic shell and foreground return",
        duration: "unassigned; angles are symbolic labels rather than elapsed time",
        equality: "1:1 standing; same 3D field",
        provenance: "OASIS signed sisters v11.2, user v11.3 signed shells"
      },
      scientificCaution: "The 2pi spinor sign and 4pi return are real representation-theory properties; shell strings, pole labels, sisters and gravity-wave interpretation are symbolic only."
    };
  }

  function ledger() {
    return {
      schema: "oasis.kelvin.signed-shells.v1",
      identity: KELVIN,
      baseline: stateFor(0),
      transitions: transitions.map((e) => ({ ...e })),
      report: report()
    };
  }

  return Object.freeze({ identity: KELVIN, current, advance, report, ledger });
}
