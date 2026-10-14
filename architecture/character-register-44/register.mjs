/**
 * KET 44-position symbolic register — additive v0.1, 2026-10-13.
 * 0 is the address of "n"; 1..43 retain the user-provided ordering.
 * ".0x" is exactly one opaque custom token, not a numeric hex literal.
 * No physical/temporal/chemical interpretation is encoded here.
 */
export const TOKENS = Object.freeze([
  'n',
  ...'abcdefghijklm',
  ...'opqrstuvwx',
  'y', 'z', ...'12345678',
  '9', '>', '|', ':', '"', '^', '(', '-', '+', '.0x',
]);
export const SCALE = 44;
const ADDRESSES = new Map(TOKENS.map((token, address) => [token, address]));

if (TOKENS.length !== SCALE || ADDRESSES.size !== SCALE) {
  throw new Error('Registry must contain 44 distinct tokens');
}

export function addressOf(token) {
  if (!ADDRESSES.has(token)) throw new RangeError(`Unknown token: ${String(token)}`);
  return ADDRESSES.get(token);
}
export function tokenAt(address) {
  if (!Number.isInteger(address) || address < 0 || address >= SCALE) {
    throw new RangeError(`Invalid register address: ${String(address)}`);
  }
  return TOKENS[address];
}
export function encode(tokens) {
  if (!Array.isArray(tokens)) throw new TypeError('Expected an array of tokens');
  return tokens.map(addressOf);
}
export function decode(addresses) {
  if (!Array.isArray(addresses)) throw new TypeError('Expected an array of integer addresses');
  return addresses.map(tokenAt);
}
/** Greedy lexical conversion; a standalone '0' is intentionally invalid. */
export function tokenize(text) {
  if (typeof text !== 'string') throw new TypeError('Expected text');
  const result = [];
  for (let i = 0; i < text.length;) {
    const token = text.startsWith('.0x', i) ? '.0x' : text[i];
    result.push(tokenAt(addressOf(token)));
    i += token.length;
  }
  return result;
}
export function untokenize(tokens) {
  return decode(encode(tokens)).join('');
}
export function audit() {
  return Object.freeze({
    size: TOKENS.length,
    unique: ADDRESSES.size === TOKENS.length,
    anchor: tokenAt(0),
    first: tokenAt(1),
    last: tokenAt(43),
    indexed: TOKENS.every((token, i) => addressOf(token) === i),
    canonical: Object.freeze([...TOKENS]),
  });
}

if (import.meta.url === `file://${process.argv[1]}`) {
  console.log(JSON.stringify(audit(), null, 2));
}
