/**
 * KET Astrophage full-stack adapter v1.0 — ADDITIVE, no kernel mutation.
 * A reversible UTF-8 -> two-symbol base-44 bridge to the 8 x 208 OSIMODEL bus.
 * Symbolic contract; not a physical chemical, biological, or quantum simulation.
 */
import { createHash } from 'node:crypto';
import { addressOf, tokenAt, audit as audit44 } from '../character-register-44/register.mjs';
import { createCycleEngine, auditPattern } from '../regenerative-loop/ket-cycle-v01/cycle.mjs';

export const VERSION = '1.0.0';
export const LANES = Object.freeze([... 'OSIMODEL']);
export const BUS_STATES = 208;
export const ADDRESS_CAPACITY = LANES.length * BUS_STATES; // 1,664 logical lane/state positions
export const FIELD_SOURCE = "ASTROPHAGE FIELD -+UUUU | | uuuu -+\n{ Na+ (589nm #FFD42A) { }\n  Cl- (IR teal 850nm #2AE5D3) { }\n  → NaCl {\n    MYCELIUM {\n      CYCAD {\n        DIATOME 10000001 {\n          3×BEAR\n        }\n      }\n    }\n  }\n}";
const sha256 = str => createHash('sha256').update(str, 'utf8').digest('hex');
const deepFreeze = obj => {
  if (obj && typeof obj === 'object' && !Object.isFrozen(obj)) {
    Object.values(obj).forEach(deepFreeze);
    Object.freeze(obj);
  }
  return obj;
};

export const FIELD = deepFreeze({
  name: 'ASTROPHAGE FIELD',
  boundary: '-+UUUU | | uuuu -+',
  source: FIELD_SOURCE,
  registers: {
    material: 17,
    lightSubaddresses: '17.01..17.99',
    symbolCount: 44,
    busStatesPerLane: BUS_STATES,
    busLanes: LANES.join(''),
    diatomeAddress: 129,
  },
  inputs: [
    { id: 'Na+', atomicNumber: 11, displayHex: '#FFD42A', annotatedWavelengthNm: 589, annotation: 'Neutral sodium emission reference; not an Na+ emission line' },
    { id: 'Cl-', atomicNumber: 17, displayHex: '#2AE5D3', annotatedWavelengthNm: 850, annotation: 'Near-infrared display proxy, not visible teal at 850 nm' },
  ],
  association: 'NaCl',
  hierarchy: ['MYCELIUM', 'CYCAD', 'DIATOME'],
  diatomeBits: '10000001',
  bearObservers: [
    { id: 'BEAR-0', angleRad: 0 },
    { id: 'BEAR-1', angleRad: 2 * Math.PI / 3 },
    { id: 'BEAR-2', angleRad: 4 * Math.PI / 3 },
  ],
  interpretation: 'Symbolic containment/control topology, not literal biological nesting or particle conversion',
});

/** Every byte 0..255 -> two 44-register addresses; high digit 0..5. */
export function encodeText44(text) {
  if (typeof text !== 'string') throw new TypeError('text must be a string');
  const bytes = new TextEncoder().encode(text);
  const out = [];
  for (const byte of bytes) out.push(Math.floor(byte / 44), byte % 44);
  return out;
}
export function decodeText44(addresses) {
  if (!Array.isArray(addresses) || addresses.length % 2 !== 0) {
    throw new TypeError('addresses must be an even-length array');
  }
  const bytes = new Uint8Array(addresses.length / 2);
  for (let i = 0; i < addresses.length; i += 2) {
    const high = addresses[i], low = addresses[i + 1];
    // Also exercises authoritative 44-symbol registry bounds on both digits.
    tokenAt(high); tokenAt(low);
    const byte = high * 44 + low;
    if (high > 5 || byte > 255) throw new RangeError('noncanonical byte pair');
    bytes[i / 2] = byte;
  }
  return new TextDecoder('utf-8', { fatal: true }).decode(bytes);
}
export function encodeTokens44(text) {
  return encodeText44(text).map(tokenAt);
}
export function decodeTokens44(tokens) {
  if (!Array.isArray(tokens)) throw new TypeError('tokens must be an array');
  return decodeText44(tokens.map(addressOf));
}
export function routeToBus(addresses) {
  if (!Array.isArray(addresses)) throw new TypeError('addresses must be an array');
  return addresses.map((state, ordinal) => {
    tokenAt(state); // 0..43 subset of 208 states
    const lane = ordinal % LANES.length;
    return Object.freeze({ ordinal, lane, laneSymbol: LANES[lane], state, busAddress: lane * BUS_STATES + state });
  });
}
export function unrouteFromBus(packet) {
  if (!Array.isArray(packet)) throw new TypeError('packet must be an array');
  const addresses = packet.map((entry, ordinal) => {
    const lane = ordinal % LANES.length;
    if (!entry || entry.ordinal !== ordinal || entry.lane !== lane ||
        entry.laneSymbol !== LANES[lane] || !Number.isInteger(entry.state) ||
        entry.busAddress !== lane * BUS_STATES + entry.state ||
        entry.busAddress < 0 || entry.busAddress >= ADDRESS_CAPACITY) {
      throw new RangeError('invalid or reordered OSIMODEL packet');
    }
    tokenAt(entry.state);
    return entry.state;
  });
  return addresses;
}
export function canonicalFieldJSON() { return JSON.stringify(FIELD); }
export function executeFullStack({ origin = 'local::0', cycles = 1 } = {}) {
  if (!Number.isSafeInteger(cycles) || cycles < 1 || cycles > 10_000) throw new RangeError('invalid cycle count');
  if (!audit44().indexed || !auditPattern().pass) throw new Error('upstream KET module audit failed');
  const payload = canonicalFieldJSON();
  const tokens = encodeText44(payload);
  const packet = routeToBus(tokens);
  const restored = decodeText44(unrouteFromBus(packet));
  if (restored !== payload) throw new Error('field failed lossless round trip');
  const cycle = createCycleEngine({ origin });
  const summary = cycle.runCycles(cycles);
  const verified = cycle.verify(summary.head);
  if (!verified.pass) throw new Error('cycle ledger verification failed');
  return Object.freeze({
    version: VERSION,
    fieldSha256: sha256(FIELD_SOURCE),
    payloadSha256: sha256(payload),
    tokenCount: tokens.length,
    busSlots: ADDRESS_CAPACITY,
    laneCount: LANES.length,
    cycles: verified.completeCycles,
    ledgerEvents: verified.events,
    ledgerHead: verified.head,
    verified: verified.pass && restored === payload,
  });
}
