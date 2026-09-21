/* TheGame: six boxes and one register. David Lee Wise's puzzle, playable rules v1. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.SixBox = factory();
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const VERSION = 'thegame-six-box-v1';
  const SEED = ['gh', 'ab', 'mn', 'ab', 'mn', 'ab'];
  const DIRECTIONS = ['W', 'N', 'E', 'S'];
  const letter = value => String.fromCharCode(96 + value);
  const orientation = row => row % 2 === 0 ? 'eo' : 'oe';
  function freeze(value) {
    if (value && typeof value === 'object' && !Object.isFrozen(value)) {
      Object.values(value).forEach(freeze);
      Object.freeze(value);
    }
    return value;
  }
  function seedCells() {
    return SEED.map((pair, row) => [...pair].map((ch, col) => ({
      id: 'b' + (row + 1) + '-' + col,
      value: ch.charCodeAt(0) - 96
    })));
  }
  function count(state) { return state.cells.flat().filter(Boolean).length; }
  // Scan from upper left straight down; then return to the top of the right column.
  function remaining(state) {
    const tokens = [];
    for (let col = 0; col < 2; col++) {
      for (let row = 0; row < 6; row++) if (state.cells[row][col]) tokens.push(state.cells[row][col]);
    }
    return tokens.map(token => letter(token.value)).join('');
  }
  function status(state) {
    if (state.needsCompression) return 'compress';
    const n = count(state);
    if (n === 2 && remaining(state) === 'gi') return 'solved';
    if (n === 0) return 'empty';
    if (n === 1) return 'one';
    return 'playing';
  }
  function snapshot(state) {
    return JSON.stringify({cells: state.cells, window: state.window, needsCompression: state.needsCompression});
  }
  function initial() {
    return freeze({cells: seedCells(), window: 0, needsCompression: false, register: []});
  }
  function coords(row, direction) {
    if (direction === 'N') return [[row, 0], [row, 1]];
    if (direction === 'S') return [[row + 1, 0], [row + 1, 1]];
    if (direction === 'W') return [[row, 0], [row + 1, 0]];
    if (direction === 'E') return [[row, 1], [row + 1, 1]];
    throw new Error('Choose a cardinal edge: N, S, E or W.');
  }
  function matches(state, row = state.window) {
    if (![0, 2, 4].includes(row)) throw new Error('The X groups are boxes 1+2, 3+4 and 5+6.');
    if (state.needsCompression) return [];
    return DIRECTIONS.flatMap(direction => {
      const points = coords(row, direction);
      const tokens = points.map(([r, c]) => state.cells[r][c]);
      return tokens.every(Boolean) && tokens[0].value === tokens[1].value
        ? [{direction, row, points, value: tokens[0].value, axis: direction === 'W' || direction === 'E' ? 'vertical' : 'horizontal'}]
        : [];
    });
  }
  function locate(state, id) {
    for (let row = 0; row < 6; row++) {
      for (let col = 0; col < 2; col++) if (state.cells[row][col]?.id === id) return [row, col];
    }
    throw new Error('Choose a letter that is still on the board.');
  }
  function apply(state, input) {
    if (!input || typeof input.type !== 'string') throw new Error('Missing move.');
    const action = JSON.parse(JSON.stringify(input));
    const before = snapshot(state);
    const next = {cells: state.cells.map(row => row.map(token => token ? {...token} : null)),
      window: state.window, needsCompression: state.needsCompression, register: [...state.register]};
    let detail;
    if (action.type === 'restart') {
      next.cells = seedCells(); next.window = 0; next.needsCompression = false;
      detail = 'New round · gh / ab / mn / ab / mn / ab';
    } else {
      const phase = status(state);
      if (phase !== 'playing' && phase !== 'compress') throw new Error('This round has stopped. Start a new round to play again.');
      if (state.needsCompression && action.type !== 'compress') throw new Error('Compress the vertical gaps before the next move.');
      if (action.type === 'shift') {
        if (action.delta !== 1 && action.delta !== -1) throw new Error('A letter move is exactly +1 or −1.');
        const [row, col] = locate(state, action.id);
        const token = next.cells[row][col];
        const prior = token.value;
        if (prior + action.delta < 1 || prior + action.delta > 26) throw new Error('The numbered alphabet runs from a=1 to z=26.');
        token.value += action.delta;
        detail = letter(prior) + '(' + prior + ') ' + (action.delta > 0 ? '+1' : '−1') + ' → ' + letter(token.value) + '(' + token.value + ') · box ' + (row + 1);
      } else if (action.type === 'focus') {
        if (![0, 2, 4].includes(action.row)) throw new Error('Choose one of the three four-slot X groups.');
        if (action.row === state.window) throw new Error('That X is already selected.');
        next.window = action.row;
        detail = 'X → boxes ' + (action.row + 1) + ' + ' + (action.row + 2);
      } else if (action.type === 'scan') {
        next.window = (state.window + 2) % 6;
        detail = 'Scan down → X ' + (next.window / 2 + 1) + (next.window === 0 ? ' · back to upper left' : '');
      } else if (action.type === 'ablate') {
        const match = matches(state).find(item => item.direction === action.direction);
        if (!match) throw new Error('Only equal numbers on a cardinal edge can ablate.');
        for (const [row, col] of match.points) next.cells[row][col] = null;
        next.needsCompression = match.axis === 'vertical';
        detail = match.direction + ' · ' + letter(match.value) + '(' + match.value + ') × 2 → _ _ · ' + match.axis;
        if (match.axis === 'vertical') detail += ' · compression ready';
        else detail += ' · holes stay';
      } else if (action.type === 'compress') {
        if (!state.needsCompression) throw new Error('Compression follows a vertical ablation.');
        for (let col = 0; col < 2; col++) {
          const live = next.cells.map(row => row[col]).filter(Boolean);
          for (let row = 0; row < 6; row++) next.cells[row][col] = live[row] || null;
        }
        next.needsCompression = false; next.window = 0;
        detail = 'Compress _ upward in each column · preserve order · return X to upper left';
      } else throw new Error('Unknown move.');
    }
    next.register.push({seq: next.register.length + 1, action, before, after: snapshot(next), detail});
    return freeze(next);
  }
  function save(state) { return JSON.stringify({version: VERSION, register: state.register}); }
  function restore(text) {
    const data = JSON.parse(text);
    if (data.version !== VERSION || !Array.isArray(data.register) || data.register.length > 50000) {
      throw new Error('This is not a supported six-box register.');
    }
    let state = initial();
    for (const entry of data.register) {
      const next = apply(state, entry.action);
      const expected = next.register[next.register.length - 1];
      if (entry.seq !== expected.seq || entry.before !== expected.before || entry.after !== expected.after || entry.detail !== expected.detail) {
        throw new Error('Register mismatch at move ' + expected.seq + '.');
      }
      state = next;
    }
    return state;
  }
  return freeze({VERSION, SEED, initial, apply, matches, count, remaining, status, snapshot, save, restore, letter, orientation});
});
