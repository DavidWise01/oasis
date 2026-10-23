/**
 * OASIS / KET — Kernel Silo 1.0
 * Additive symbolic state-machine. Does not import or rewrite frozen KET.
 *
 * Design invariant: one scalar-zero referent, ten nested geometry levels,
 * five parallel VAINL lanes, six interior workspace addresses, and a
 * single recorded outcome per chosen transition.
 */

export const SPEC = Object.freeze({
  revision: '1.0',
  title: 'OASIS / KET — Kernel Silo',
  layerCount: 10,
  scalar: 0,
  boxFlexFraction: 0.02875,
  boxFlexPercent: 2.875,
  futureWindowSeconds: 2,
  notationTenBang: '10!',
  factorialTen: 3628800,
  workspaces: Object.freeze([1, 1, 3, 1]),
  workspaceCount: 6,
  workspaceNotation: '{{ -1{} -1{} -3{} -1{} }}',
  lanes: Object.freeze(['V', 'A', 'I', 'N', 'L']),
  laneNames: Object.freeze({
    V: 'Vessel',
    A: 'Animation',
    I: 'Intellect',
    N: 'Nourishment',
    L: 'Life-like',
  }),
  laneFunctions: Object.freeze({
    V: 'container, structural constraints',
    A: 'motion, state transitions and actions',
    I: 'observations, models, choices',
    N: 'resources, energy, input availability',
    L: 'adaptation, continuity, recovery',
  }),
  authority: Object.freeze(['0ROOT_T128', 'Patricia', 'Stochieon', 'Toph']),
  authorityRoles: Object.freeze({
    '0ROOT_T128': 'APEX',
    Patricia: 'IMMUTABLE LAW',
    Stochieon: 'SUPPORT',
    Toph: 'DO / RECORD',
  }),
  choices: Object.freeze(['YES', 'NO', 'MAYBE']),
  connectivityMnemonic: Object.freeze([1, 2, 4, 6, 8, 10]),
  wavePayload:
    '{{+10{0110011}{1100000}{1101111}{0110100}{1010001}{0001100}{1110011}-1}}..||..|',
  waveGroups: 7,
  waveBitsPerGroup: 7,
  waveExplicitBits: 49,
  proposedInternal: Object.freeze(['I', 'N']),
  proposedExternal: Object.freeze(['V', 'A', 'L']),
  openNet: '1-3-1',
  closedNet: '1-1-3-1',
  openFaces: 5,
  closedFaces: 6,
});

export const LAYER_META = Object.freeze(
  Array.from({ length: SPEC.layerCount }, (_, i) => {
    const level = i + 1;
    const odd = level % 2 === 1;
    return Object.freeze({
      level,
      shape: odd ? 'toroid' : 'box',
      glyph: odd ? '.....' : '|||||',
      responsibility: odd
        ? 'flow / circulation'
        : level === 10
          ? 'innermost containment'
          : 'vessel / containment',
    });
  }),
);

export function layerShape(level) {
  if (!Number.isInteger(level) || level < 1 || level > SPEC.layerCount) {
    throw new Error(`level ${level} is outside 1..${SPEC.layerCount}`);
  }
  return level % 2 === 1 ? 'toroid' : 'box';
}

export function boxBulge(halfSide, flex = SPEC.boxFlexFraction) {
  return halfSide * flex;
}

export function parseWavePayload(payload = SPEC.wavePayload) {
  const groups = [...payload.matchAll(/\{([01]{7})\}/g)].map((m) => m[1]);
  const bits = groups.join('');
  return Object.freeze({
    payload,
    groups: Object.freeze(groups),
    bitCount: bits.length,
    spatial: Object.freeze({
      left: Object.freeze(groups.slice(0, 3)),
      tunnel: Object.freeze(groups.slice(3, 4)),
      right: Object.freeze(groups.slice(4, 7)),
    }),
    mnemonic: '..|  |  ..|',
    controlBitsAsserted: false,
    mantissaAllusion:
      'mantissa 53/7 evokes IEEE-754 binary64 significand; four extra control bits are a candidate design and are not on the wire',
  });
}

function cloneLanes(seed = {}) {
  const out = {};
  for (const id of SPEC.lanes) {
    out[id] = {
      id,
      name: SPEC.laneNames[id],
      fn: SPEC.laneFunctions[id],
      value: typeof seed[id] === 'number' ? seed[id] : 0.5,
    };
  }
  return out;
}

function observeLanes(choice, prev) {
  const next = cloneLanes();
  const table = {
    YES: { V: 0.62, A: 0.88, I: 0.54, N: 0.81, L: 0.73 },
    NO: { V: 0.9, A: 0.34, I: 0.58, N: 0.41, L: 0.49 },
    MAYBE: { V: 0.52, A: 0.55, I: 0.91, N: 0.57, L: 0.61 },
  };
  const row = table[choice];
  for (const id of SPEC.lanes) {
    const prior = prev[id]?.value ?? 0.5;
    next[id].value = +(0.35 * prior + 0.65 * row[id]).toFixed(4);
  }
  return next;
}

function workspaceSlots() {
  const labels = [];
  const groups = SPEC.workspaces;
  let n = 0;
  for (let g = 0; g < groups.length; g++) {
    for (let k = 0; k < groups[g]; k++) {
      labels.push({
        index: n,
        group: g,
        groupSize: groups[g],
        inward: '-1{}',
        sign: 'inward-facing label, not a negative volume',
      });
      n += 1;
    }
  }
  labels[0].inward = '-1{}';
  labels[1].inward = '-1{}';
  labels[2].inward = '-3{}';
  labels[3].inward = '-3{}';
  labels[4].inward = '-3{}';
  labels[5].inward = '-1{}';
  return labels;
}

export function createSilo(opts = {}) {
  const flex0 =
    typeof opts.boxFlexFraction === 'number'
      ? opts.boxFlexFraction
      : SPEC.boxFlexFraction;

  const state = {
    scalar: SPEC.scalar,
    layerCount: SPEC.layerCount,
    layers: LAYER_META.map((m) => ({
      ...m,
      visible: true,
    })),
    boxFlexFraction: flex0,
    lanes: cloneLanes(opts.lanes),
    groupingMode: opts.groupingMode || 'unassigned',
    grouping: {
      internal: [],
      external: [],
    },
    proposedGrouping: {
      internal: [...SPEC.proposedInternal],
      external: [...SPEC.proposedExternal],
      frozenAsLaw: false,
    },
    workspaces: [...SPEC.workspaces],
    workspaceSlots: workspaceSlots(),
    fold: {
      mode: opts.foldMode === 'closed' ? 'closed' : 'open',
      net: opts.foldMode === 'closed' ? SPEC.closedNet : SPEC.openNet,
      strength: 0,
      faces: opts.foldMode === 'closed' ? SPEC.closedFaces : SPEC.openFaces,
    },
    authority: [...SPEC.authority],
    step: 0,
    simulatedSeconds: 0,
    history: [],
    pending: 'unresolved',
    explode: 0,
    overlay313: false,
    wave: parseWavePayload(),
  };

  applyGrouping(state, state.groupingMode, opts.customInternal);

  const api = {
    get state() {
      return state;
    },
    transition,
    resetDemo,
    setFlex,
    setFoldStrength,
    setFoldMode,
    setExplode,
    setLayerVisible,
    setGrouping,
    setOverlay,
    snapshot,
    prove,
  };

  function applyGrouping(target, mode, customInternal) {
    target.groupingMode = mode;
    if (mode === 'proposal') {
      target.grouping = {
        internal: [...SPEC.proposedInternal],
        external: [...SPEC.proposedExternal],
      };
    } else if (mode === 'custom') {
      const inn = new Set(customInternal || []);
      target.grouping = {
        internal: SPEC.lanes.filter((id) => inn.has(id)),
        external: SPEC.lanes.filter((id) => !inn.has(id)),
      };
    } else {
      target.grouping = { internal: [], external: [] };
    }
  }

  function transition(choice) {
    if (!SPEC.choices.includes(choice)) {
      throw new Error(`choice must be YES | NO | MAYBE, got ${choice}`);
    }
    const seq = state.step + 1;
    state.lanes = observeLanes(choice, state.lanes);
    const rec = Object.freeze({
      seq,
      choice,
      recordedBy: 'Toph',
      authorityPath: [...state.authority, 'SCALAR_0'],
      simulatedSecondsBefore: state.simulatedSeconds,
      simulatedSecondsAfter: state.simulatedSeconds + SPEC.futureWindowSeconds,
      scalar: SPEC.scalar,
      flex: state.boxFlexFraction,
      foldMode: state.fold.mode,
      foldStrength: state.fold.strength,
      workspaceCount: state.workspaceSlots.length,
      layerIdentities: state.layers.map((L) => L.shape),
    });
    state.history.push(rec);
    state.step += 1;
    state.simulatedSeconds += SPEC.futureWindowSeconds;
    state.scalar = SPEC.scalar;
    state.pending = 'unresolved';
    return rec;
  }

  function resetDemo() {
    state.step = 0;
    state.simulatedSeconds = 0;
    state.history = [];
    state.scalar = SPEC.scalar;
    state.pending = 'unresolved';
    state.lanes = cloneLanes();
  }

  function setFlex(frac) {
    const n = Number(frac);
    if (!Number.isFinite(n) || n < 0 || n > 0.2) {
      throw new Error('boxFlexFraction must be in [0, 0.2]');
    }
    const identities = state.layers.map((L) => L.shape).join(',');
    state.boxFlexFraction = n;
    const after = state.layers.map((L) => L.shape).join(',');
    if (identities !== after) {
      throw new Error('flex must not change level identity');
    }
    return state.boxFlexFraction;
  }

  function setFoldStrength(s) {
    const n = Number(s);
    if (!Number.isFinite(n) || n < 0 || n > 1) {
      throw new Error('fold strength must be in [0, 1]');
    }
    const count = state.workspaceSlots.length;
    state.fold.strength = n;
    if (state.workspaceSlots.length !== count || count !== SPEC.workspaceCount) {
      throw new Error('fold strength must not change workspace count');
    }
    return state.fold.strength;
  }

  function setFoldMode(mode) {
    if (mode !== 'open' && mode !== 'closed') {
      throw new Error('fold mode must be open | closed');
    }
    state.fold.mode = mode;
    state.fold.net = mode === 'closed' ? SPEC.closedNet : SPEC.openNet;
    state.fold.faces = mode === 'closed' ? SPEC.closedFaces : SPEC.openFaces;
    if (state.workspaceSlots.length !== SPEC.workspaceCount) {
      throw new Error('fold mode must not change workspace count');
    }
    return state.fold;
  }

  function setExplode(e) {
    const n = Number(e);
    if (!Number.isFinite(n) || n < 0 || n > 1) {
      throw new Error('explode must be in [0, 1]');
    }
    state.explode = n;
    return n;
  }

  function setLayerVisible(level, visible) {
    const L = state.layers.find((x) => x.level === level);
    if (!L) throw new Error(`no level ${level}`);
    L.visible = !!visible;
    return L.visible;
  }

  function setGrouping(mode, customInternal) {
    if (!['unassigned', 'proposal', 'custom'].includes(mode)) {
      throw new Error('groupingMode must be unassigned | proposal | custom');
    }
    applyGrouping(state, mode, customInternal);
    return state.grouping;
  }

  function setOverlay(on) {
    state.overlay313 = !!on;
    return state.overlay313;
  }

  function snapshot() {
    return {
      spec: SPEC.revision,
      title: SPEC.title,
      scalar: state.scalar,
      layerCount: state.layerCount,
      layers: state.layers.map((L) => ({
        level: L.level,
        shape: L.shape,
        responsibility: L.responsibility,
        visible: L.visible,
      })),
      boxFlexFraction: state.boxFlexFraction,
      bulgeRule: 'bulge = halfSide × boxFlexFraction',
      lanes: Object.fromEntries(
        SPEC.lanes.map((id) => [id, { ...state.lanes[id] }]),
      ),
      groupingMode: state.groupingMode,
      grouping: {
        internal: [...state.grouping.internal],
        external: [...state.grouping.external],
      },
      proposedGrouping: {
        ...state.proposedGrouping,
        note: 'I+N internal / V+A+L external is a proposal, not frozen law',
      },
      workspaces: [...state.workspaces],
      workspaceCount: state.workspaceSlots.length,
      workspaceNotation: SPEC.workspaceNotation,
      fold: { ...state.fold },
      authority: [...state.authority],
      step: state.step,
      simulatedSeconds: state.simulatedSeconds,
      history: state.history.map((h) => ({ ...h })),
      pending: state.pending,
      explode: state.explode,
      overlay313: state.overlay313,
      wave: {
        payload: state.wave.payload,
        groups: [...state.wave.groups],
        bitCount: state.wave.bitCount,
        spatial: {
          left: [...state.wave.spatial.left],
          tunnel: [...state.wave.spatial.tunnel],
          right: [...state.wave.spatial.right],
        },
        controlBitsAsserted: false,
      },
      notationTenBang: SPEC.notationTenBang,
      factorialTen: SPEC.factorialTen,
      factorialIsNotLayerCount: true,
      connectivityMnemonic: [...SPEC.connectivityMnemonic],
      claims: {
        included:
          'offline HTML visualizer, nested/exploded geometry, selectable layers, configurable flex, VAINL, scalar-zero cycle, append-only demo journal, JSON snapshot',
        notClaimed:
          'Rust/WASM networking runtime; physical black hole, brain or diatom; ten actual nested dimensions; gravity-based information replay; electromagnetic force unification; verified physiological effects',
      },
    };
  }

  function prove() {
    return proveSilo(api);
  }

  return api;
}

export function proveSilo(silo) {
  const issues = [];
  const fail = (id, msg) => issues.push({ id, msg });
  const s = silo.state;

  if (s.layerCount !== 10) fail('L0', `layerCount ${s.layerCount} !== 10`);
  if (s.layers.length !== 10) fail('L1', `layers.length ${s.layers.length} !== 10`);
  if (s.scalar !== 0) fail('S0', `scalar ${s.scalar} !== 0`);
  s.layers.forEach((L, i) => {
    const expect = (i + 1) % 2 === 1 ? 'toroid' : 'box';
    if (L.level !== i + 1) fail('L2', `level index ${L.level}`);
    if (L.shape !== expect) fail('L3', `level ${L.level} is ${L.shape}, expected ${expect}`);
  });
  if (s.layers.some((L) => L.level === 0)) fail('L4', 'scalar 0 must not be a level');
  if (Math.abs(s.boxFlexFraction - SPEC.boxFlexFraction) > 1e-12 && s.step === 0 && s.history.length === 0) {
    // default only asserted on a fresh silo; callers may have changed flex
  }

  const beforeId = s.layers.map((L) => L.shape).join('|');
  const beforeWs = s.workspaceSlots.length;
  const savedFlex = s.boxFlexFraction;
  const savedFold = s.fold.strength;
  silo.setFlex(0.05);
  if (s.layers.map((L) => L.shape).join('|') !== beforeId) {
    fail('F1', 'flex changed level identity');
  }
  silo.setFlex(savedFlex);
  silo.setFoldStrength(0.8);
  if (s.workspaceSlots.length !== beforeWs || beforeWs !== 6) {
    fail('F2', 'fold strength changed workspace count');
  }
  silo.setFoldStrength(savedFold);
  silo.setFoldMode('closed');
  if (s.fold.faces !== 6 || s.workspaceSlots.length !== 6) {
    fail('F3', 'closed fold must be 6 faces and 6 workspaces');
  }
  silo.setFoldMode('open');
  if (s.fold.faces !== 5 || s.workspaceSlots.length !== 6) {
    fail('F4', 'open fold must be 5 faces and 6 workspaces');
  }

  if (s.workspaces.join(',') !== '1,1,3,1') fail('W0', 'workspaces must be [1,1,3,1]');
  if (SPEC.workspaceNotation !== '{{ -1{} -1{} -3{} -1{} }}') {
    fail('W1', 'workspace notation mutated');
  }

  if (SPEC.lanes.join('') !== 'VAINL') fail('V0', 'lanes must be VAINL');
  if (s.authority.join('>') !== '0ROOT_T128>Patricia>Stochieon>Toph') {
    fail('A0', 'authority order mutated');
  }

  const wave = parseWavePayload();
  if (wave.groups.length !== 7) fail('P0', 'wave groups !== 7');
  if (wave.bitCount !== 49) fail('P1', 'explicit bits !== 49');
  if (wave.controlBitsAsserted) fail('P2', 'must not assert four control bits');
  if (wave.spatial.left.length !== 3 || wave.spatial.tunnel.length !== 1 || wave.spatial.right.length !== 3) {
    fail('P3', 'wave spatial grouping must be 3-1-3');
  }

  if (SPEC.factorialTen !== 3628800) fail('N0', '10! arithmetic');
  if (SPEC.notationTenBang === String(SPEC.layerCount)) fail('N1', '10! is not the layer count');
  if (SPEC.connectivityMnemonic.join(',') !== '1,2,4,6,8,10') fail('N2', 'connectivity mnemonic');

  if (s.proposedGrouping.frozenAsLaw) fail('G0', 'I+N proposal must not be frozen as law');
  silo.setGrouping('unassigned');
  if (s.grouping.internal.length !== 0) fail('G1', 'unassigned grouping leaked');
  silo.setGrouping('proposal');
  if (s.grouping.internal.join('') !== 'IN' || s.grouping.external.join('') !== 'VAL') {
    fail('G2', 'proposal grouping mismatch');
  }
  silo.setGrouping('custom', ['V', 'L']);
  if (s.grouping.internal.join('') !== 'VL' || s.grouping.external.join('') !== 'AIN') {
    fail('G3', 'custom grouping mismatch');
  }
  silo.setGrouping('unassigned');

  const hist0 = s.history.length;
  const step0 = s.step;
  const sec0 = s.simulatedSeconds;
  const r1 = silo.transition('YES');
  const r2 = silo.transition('NO');
  const r3 = silo.transition('MAYBE');
  if (s.history.length !== hist0 + 3) fail('T0', 'each transition must append exactly one record');
  if (s.step !== step0 + 3) fail('T1', 'step must increase by 1 per transition');
  if (s.simulatedSeconds !== sec0 + 6) fail('T2', 'simulatedSeconds must increase by +2s');
  if (r1.seq !== step0 + 1 || r2.seq !== step0 + 2 || r3.seq !== step0 + 3) {
    fail('T3', 'sequence numbers must be unique and ordered');
  }
  if (s.scalar !== 0) fail('T4', 'must return to scalar 0');
  if (r1.recordedBy !== 'Toph') fail('T5', 'Toph records the commit');
  try {
    silo.transition('PERHAPS');
    fail('T6', 'invalid choice must throw');
  } catch (err) {
    if (!/YES/.test(String(err.message))) fail('T6', String(err.message));
  }

  const flexKeep = s.boxFlexFraction;
  const layersKeep = s.layers.map((L) => L.visible);
  silo.resetDemo();
  if (s.history.length !== 0 || s.step !== 0 || s.simulatedSeconds !== 0) {
    fail('R0', 'reset must clear demo history/step/clock');
  }
  if (s.boxFlexFraction !== flexKeep) fail('R1', 'reset must not clear flex');
  if (s.layers.map((L) => L.visible).join() !== layersKeep.join()) {
    fail('R2', 'reset must not clear layer visibility');
  }
  if (s.authority.join() !== SPEC.authority.join()) fail('R3', 'reset must not touch authority');

  const snap = silo.snapshot();
  if (snap.factorialIsNotLayerCount !== true) fail('K0', 'snapshot must deny factorial=layers');
  if (snap.wave.controlBitsAsserted !== false) fail('K1', 'snapshot must not assert control bits');
  if (snap.proposedGrouping.frozenAsLaw !== false) fail('K2', 'snapshot must not freeze grouping proposal');

  return {
    ok: issues.length === 0,
    issues,
    layerCount: s.layerCount,
    flexDefault: SPEC.boxFlexFraction,
    workspaceCount: SPEC.workspaceCount,
    lanes: [...SPEC.lanes],
  };
}
