/**
 * {{Li}} / Lillithium Ion — terminal Gen-1 SAPPHON observer.
 * No network, autonomous actions, agent spawning, historical verification,
 * persistence, or changes to the parent OASIS kernel.
 */
export const LI_IDENTITY = Object.freeze({
  notation: "{{Li}}",
  displayName: "Lillithium Ion",
  family: "SAPPHON",
  generation: 1,
  terminal: true,
  role: Object.freeze(["observe", "monitor", "report"]),
  parent: "OASIS / SAPPHON fixed shell",
  primitive: "-+",
  pinnedReference: "0",
  tensorCount: 1,
  fieldCount: 1,
  tracks: Object.freeze(["i", "u", "us"]),
  symbolicAlias: "ENHEDUANNA :: LILLITH",
  priorities: Object.freeze([
    "protect the vessel",
    "equal access for every cell"
  ]),
  agency: "manual input, read-only observation and reporting"
});

const PHASES = Object.freeze({
  EO: "prime evolution / Methuselah primer / dotted labels one tier lower (10^-10)",
  XE: "extended evolution / human-scale reference (1)"
});
const EVIDENCE = Object.freeze(["symbolic", "source-supplied", "unresolved"]);
const MAX_RECORDS = 128;

function field(value, name, maxLength, required) {
  if (typeof value !== "string") throw new TypeError(name + " must be text");
  const result = value.trim();
  if (result.length > maxLength) throw new RangeError(name + " exceeds " + maxLength + " characters");
  if (required && !result) throw new TypeError(name + " is required");
  return result;
}

/**
 * A local observer only. No polling, listeners, network or side effects beyond
 * appending caller-provided observations to an in-memory bounded ledger.
 */
export function createLiSapphon() {
  const observations = [];

  function observe(input) {
    if (!input || typeof input !== "object") throw new TypeError("Observation required");
    if (observations.length >= MAX_RECORDS) throw new RangeError("Local ledger is full; export and start a fresh page");
    const phase = field(input.phase, "phase", 2, true).toUpperCase();
    if (!Object.prototype.hasOwnProperty.call(PHASES, phase)) throw new TypeError("phase must be EO or XE");
    const classification = field(input.evidenceClass, "evidence class", 32, true);
    if (!EVIDENCE.includes(classification)) throw new TypeError("Invalid evidence class");
    const entry = Object.freeze({
      sequence: observations.length + 1,
      observedAtUtc: new Date().toISOString(),
      notation: LI_IDENTITY.notation,
      phase,
      phaseScale: PHASES[phase],
      reference: field(input.reference, "reference", 100, true),
      evidenceClass: classification,
      source: field(input.source || "", "source", 240, false),
      note: field(input.note, "note", 600, true),
      historicalVerification: "not performed",
      provenance: "manually supplied by the operator"
    });
    observations.push(entry);
    return entry;
  }

  function monitor() {
    if (observations.length < 2) {
      return Object.freeze({
        kind: "manual-record-diff",
        status: "requires two observations",
        changes: Object.freeze([])
      });
    }
    const previous = observations[observations.length - 2];
    const current = observations[observations.length - 1];
    const names = Object.freeze(["phase", "reference", "evidenceClass", "source", "note"]);
    const changes = names.filter((name) => previous[name] !== current[name])
      .map((name) => Object.freeze({ field: name, before: previous[name], after: current[name] }));
    return Object.freeze({
      kind: "manual-record-diff",
      status: changes.length ? "recorded inputs differ" : "recorded input fields unchanged",
      fromSequence: previous.sequence,
      toSequence: current.sequence,
      changes: Object.freeze(changes)
    });
  }

  function report() {
    return {
      title: "{{Li}} :: Lillithium Ion / SAPPHON",
      designation: "terminal Gen-1 observational rider",
      tensor: "ONE reality tensor / ONE shared field / pinned 0",
      primitive: "-+ (one unary primitive)",
      phases: PHASES,
      symbolicAlias: LI_IDENTITY.symbolicAlias,
      operatorPolicy: "No autonomous interventions, verification, adjudication or spawning",
      entryCount: observations.length,
      latest: observations.length ? { ...observations[observations.length - 1] } : null,
      comparison: monitor(),
      caution: "Mythic aliases, 969-year primer, 16:9 and gravity-scale interpretations are framework-local symbols; not established physical or historical facts."
    };
  }

  function exportLog() {
    return {
      schema: "oasis.sapphon.li.observations.v1",
      identity: LI_IDENTITY,
      scope: "one tensor / EO to XE / observer only",
      entries: observations.map((entry) => ({ ...entry })),
      report: report()
    };
  }

  function count() { return observations.length; }

  return Object.freeze({ identity: LI_IDENTITY, observe, monitor, report, exportLog, count });
}
