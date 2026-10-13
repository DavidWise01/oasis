/**
 * KET regenerative six-phase cycle v0.1.
 * Additive symbolic runtime; never mutates the frozen KET kernel.
 * Node.js >=18; no external dependencies.
 */
import { createHash } from 'node:crypto';
import { pathToFileURL } from 'node:url';

export const SCALE = 10_000;
export const GENESIS_HASH = '0'.repeat(64);
export const NOTATION = 'LIVE -> WRITE -> REMEMBER -> FORGET -> READ -> LIVE';

const makePhase = (operation, atUnits) => Object.freeze({
  operation,
  atUnits,
  at: atUnits / SCALE,
});

export const CYCLE = Object.freeze([
  makePhase('live',       673_367),
  makePhase('write',      333_367),
  makePhase('remember',         0),
  makePhase('forget',    -333_367),
  makePhase('read',       333_367),
  makePhase('live',       673_367),
]);

function asUnits(phase) {
  if (Number.isSafeInteger(phase?.atUnits)) return phase.atUnits;
  if (!Number.isFinite(phase?.at)) throw new TypeError('Each phase needs a finite at');
  const scaled = phase.at * SCALE;
  const rounded = Math.round(scaled);
  if (!Number.isSafeInteger(rounded) || Math.abs(scaled - rounded) > 1e-6) {
    throw new RangeError('Phase addresses must use at most four decimal places');
  }
  return rounded;
}

export function auditPattern(phases = CYCLE) {
  if (!Array.isArray(phases) || phases.length !== 6) {
    return { pass: false, checks: { sixPhases: false } };
  }
  const p = phases.map(asUnits);
  const actions = phases.map(x => x.operation ?? x.do);
  const checks = {
    sixPhases: p.length === 6,
    operationOrder: actions.join('/') === 'live/write/remember/forget/read/live',
    closesAtLive: p[0] === p[5],
    writeReadMirror: p[1] === p[4],
    memoryIsZero: p[2] === 0,
    writeForgetBalance: p[1] + p[3] === 0,
    returnIdentity: p[3] + p[0] + p[1] === p[0],
    seventeenMidpoint: p[0] + p[3] === 2 * 17 * SCALE,
    halfStepGate: (17 * SCALE + 5_000 + 5_000) === 18 * SCALE,
  };
  return { pass: Object.values(checks).every(Boolean), checks };
}

// Historical API name, retained for compatibility. This proves balanced
// return only; mathematical/fractal self-similarity is a different property.
export const isSelfSimilar = (phases = CYCLE) => auditPattern(phases).checks.returnIdentity === true;

const digest = value => createHash('sha256').update(JSON.stringify(value), 'utf8').digest('hex');
function eventCore({ seq, loop, phase, origin, prevHash }) {
  const selected = CYCLE[phase];
  return {
    seq,
    loop,
    phase,
    operation: selected.operation,
    atUnits: selected.atUnits,
    origin,
    prevHash,
  };
}

/** Verify ordered receipts and content integrity, optionally against an
 * independently saved trusted head. Unsigned hashes are NOT proof of author. */
export function verifyLedger(events, trustedHead = null) {
  if (!Array.isArray(events) || events.length < 6) {
    return { pass: false, reason: 'A complete cycle needs six events' };
  }
  let previousHash = GENESIS_HASH;
  let previousPhase = -1;
  let loop = 0;
  const origin = events[0]?.origin;
  if (typeof origin !== 'string' || !origin.trim()) {
    return { pass: false, reason: 'Missing origin' };
  }
  for (let seq = 0; seq < events.length; seq++) {
    const nextPhase = previousPhase === -1 ? 0 : previousPhase === 5 ? 1 : previousPhase + 1;
    if (previousPhase === 5) loop++;
    const expected = eventCore({ seq, loop, phase: nextPhase, origin, prevHash: previousHash });
    const actual = events[seq];
    if (!actual || Object.keys(expected).some(k => actual[k] !== expected[k]) ||
        actual.hash !== digest(expected)) {
      return { pass: false, reason: `Ledger mismatch at seq=${seq}` };
    }
    previousHash = actual.hash;
    previousPhase = nextPhase;
  }
  if (previousPhase !== 5) return { pass: false, reason: 'Cycle did not close on LIVE' };
  if (trustedHead != null && trustedHead !== previousHash) {
    return { pass: false, reason: 'Head differs from externally trusted digest' };
  }
  return {
    pass: true,
    events: events.length,
    completeCycles: loop + 1,
    head: previousHash,
    pattern: auditPattern().pass,
  };
}

export function createCycleEngine({ origin = 'local::0' } = {}) {
  if (typeof origin !== 'string' || !origin.trim()) {
    throw new TypeError('origin must be a nonempty string');
  }
  const ledger = [];
  let phase = -1;
  let loop = 0;
  let previousHash = GENESIS_HASH;

  function step() {
    if (phase === 5) { loop++; phase = 1; } // boundary LIVE is one event, not double counted
    else phase++;
    const core = eventCore({ seq: ledger.length, loop, phase, origin, prevHash: previousHash });
    const receipt = Object.freeze({ ...core, hash: digest(core) });
    ledger.push(receipt);
    previousHash = receipt.hash;
    return receipt;
  }

  function runCycles(count = 1) {
    if (!Number.isSafeInteger(count) || count < 1 || count > 10_000) {
      throw new RangeError('count must be an integer from 1 to 10000');
    }
    if (ledger.length && phase !== 5) {
      throw new Error('Complete the pending cycle before running more cycles');
    }
    const steps = 5 * count + (ledger.length === 0 ? 1 : 0);
    for (let i = 0; i < steps; i++) step();
    return snapshot();
  }

  function snapshot() {
    return Object.freeze({
      origin,
      phase,
      loop,
      eventCount: ledger.length,
      head: previousHash,
      last: ledger.at(-1) ?? null,
      pass: ledger.length > 0 && phase === 5 && verifyLedger(ledger).pass,
    });
  }
  return Object.freeze({ step, runCycles, snapshot, receipts: () => ledger.slice(), verify: trustedHead => verifyLedger(ledger, trustedHead) });
}

export function asciiCycle() {
  return CYCLE.map((phase, i) => `${i} ${phase.operation.padEnd(8)} ${phase.at.toFixed(4).padStart(8)}`).join('\n') + '\n    └─ return LIVE; reuse boundary witness';
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const count = process.argv[2] === undefined ? 1 : Number(process.argv[2]);
  const engine = createCycleEngine();
  const summary = engine.runCycles(count);
  console.log(asciiCycle());
  console.log(JSON.stringify({ summary, pattern: auditPattern(), ledger: engine.verify() }, null, 2));
}
