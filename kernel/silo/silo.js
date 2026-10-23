/**
 * OASIS / KET Kernel Silo visualizer.
 * WebGL2 first, canvas 2D fallback. No CDN. Frozen ket.mjs is not imported.
 */
import {
  SPEC,
  createSilo,
  boxBulge,
} from './silo-kernel.mjs';

const silo = createSilo();
const $ = (id) => document.getElementById(id);
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

const q = new URLSearchParams(location.search);
if (q.has('explode')) silo.setExplode(clamp01(Number(q.get('explode'))));
if (q.has('flex')) silo.setFlex(clampFlex(Number(q.get('flex'))));
if (q.has('fold')) silo.setFoldStrength(clamp01(Number(q.get('fold'))));
if (q.get('closed') === '1') silo.setFoldMode('closed');
if (q.get('overlay') === '1') silo.setOverlay(true);
if (q.get('grouping')) {
  try { silo.setGrouping(q.get('grouping')); } catch { /* keep unassigned */ }
}
if (q.get('commit')) {
  for (const raw of q.get('commit').split(',')) {
    const ch = raw.trim().toUpperCase();
    if (SPEC.choices.includes(ch)) silo.transition(ch);
  }
}

const cam = {
  yaw: 0.62,
  pitch: 0.42,
  dist: 6.4,
  dragging: false,
  lastX: 0,
  lastY: 0,
};

const TORUS_COL = [
  [0.45, 0.82, 1.00],
  [0.38, 0.78, 0.98],
  [0.42, 0.86, 0.92],
  [0.55, 0.80, 1.00],
  [0.62, 0.90, 1.00],
];
const BOX_COL = [
  [0.95, 0.78, 0.42],
  [0.90, 0.72, 0.35],
  [0.98, 0.82, 0.48],
  [0.86, 0.68, 0.32],
  [1.00, 0.86, 0.55],
];

const field = $('field');
const foldCanvas = $('foldNet');
let gl = null;
let gpu = null;
let renderer = 'canvas2d';
let autoOn = q.get('auto') === '1';
let autoMs = Number($('speed').value) || 2000;
let lastAuto = 0;
let autoPick = 0;
let t0 = performance.now();
let deviateOn = q.get('deviate') !== '0';
let deviateAmp = q.has('damp') ? clamp01(Number(q.get('damp'))) : 0.78;
let lastCommitAt = -1e9;
let drawTime = 0;
const CHOICE_TINT = {
  YES: [0.95, 0.82, 0.32],
  NO: [0.85, 0.40, 0.42],
  MAYBE: [1.00, 0.70, 0.22],
};
const LANE_TINT = {
  V: [0.95, 0.78, 0.42],
  A: [0.45, 0.84, 1.00],
  I: [0.78, 0.61, 1.00],
  N: [0.23, 0.80, 0.69],
  L: [0.85, 0.52, 0.48],
};
const evo = { on: q.get('evolve') !== '0', fossils: [] };
function fossilFrom(rec) {
  return {
    seq: rec.seq,
    choice: rec.choice,
    yaw: hash01(rec.seq * 3.14) * Math.PI * 2,
    tilt: (hash01(rec.seq * 8.2) - 0.5) * 0.55,
  };
}
function remember(rec) {
  evo.fossils.push(fossilFrom(rec));
  if (evo.fossils.length > 14) evo.fossils.shift();
}
for (const rec of silo.state.history) remember(rec);
if (silo.state.history.length) lastCommitAt = 0;
function fossilDrift() {
  let tx = 0, tz = 0;
  for (const f of evo.fossils) {
    const s = f.choice === 'YES' ? 1 : f.choice === 'NO' ? -1 : 0.25;
    tx += s * 0.035;
    tz += f.choice === 'MAYBE' ? 0.04 : -0.01;
  }
  return { tx, tz };
}

function clamp01(n) {
  return Number.isFinite(n) ? Math.min(1, Math.max(0, n)) : 0;
}
function clampFlex(n) {
  return Number.isFinite(n) ? Math.min(0.2, Math.max(0, n)) : SPEC.boxFlexFraction;
}

function layerRadius(level, explode) {
  const t = (level - 1) / 9;
  return 2.05 * (1 - t * 0.70) + explode * 0.52 * (11 - level);
}

/* ---------- matrices (column-major, y-up, right-handed) ---------- */
function ident(o = new Float32Array(16)) {
  o.set([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]);
  return o;
}
function mul(out, a, b) {
  const r = new Float32Array(16);
  for (let c = 0; c < 4; c++) {
    const b0 = b[c * 4], b1 = b[c * 4 + 1], b2 = b[c * 4 + 2], b3 = b[c * 4 + 3];
    r[c * 4]     = a[0] * b0 + a[4] * b1 + a[8]  * b2 + a[12] * b3;
    r[c * 4 + 1] = a[1] * b0 + a[5] * b1 + a[9]  * b2 + a[13] * b3;
    r[c * 4 + 2] = a[2] * b0 + a[6] * b1 + a[10] * b2 + a[14] * b3;
    r[c * 4 + 3] = a[3] * b0 + a[7] * b1 + a[11] * b2 + a[15] * b3;
  }
  out.set(r);
  return out;
}
function perspective(out, fovy, aspect, near, far) {
  const f = 1 / Math.tan(fovy / 2);
  out.fill(0);
  out[0] = f / aspect;
  out[5] = f;
  out[10] = (far + near) / (near - far);
  out[11] = -1;
  out[14] = (2 * far * near) / (near - far);
}
function lookAt(out, eye, center, up) {
  let zx = eye[0] - center[0], zy = eye[1] - center[1], zz = eye[2] - center[2];
  let zl = Math.hypot(zx, zy, zz) || 1;
  zx /= zl; zy /= zl; zz /= zl;
  let xx = up[1] * zz - up[2] * zy;
  let xy = up[2] * zx - up[0] * zz;
  let xz = up[0] * zy - up[1] * zx;
  let xl = Math.hypot(xx, xy, xz) || 1;
  xx /= xl; xy /= xl; xz /= xl;
  const yx = zy * xz - zz * xy;
  const yy = zz * xx - zx * xz;
  const yz = zx * xy - zy * xx;
  out.set([
    xx, yx, zx, 0,
    xy, yy, zy, 0,
    xz, yz, zz, 0,
    -(xx * eye[0] + xy * eye[1] + xz * eye[2]),
    -(yx * eye[0] + yy * eye[1] + yz * eye[2]),
    -(zx * eye[0] + zy * eye[1] + zz * eye[2]),
    1,
  ]);
}
function translate(out, x, y, z) {
  ident(out);
  out[12] = x; out[13] = y; out[14] = z;
  return out;
}
function scaleM(out, x, y, z) {
  ident(out);
  out[0] = x; out[5] = y; out[10] = z;
  return out;
}
function rotateX(out, a) {
  const c = Math.cos(a), s = Math.sin(a);
  ident(out);
  out[5] = c; out[6] = s; out[9] = -s; out[10] = c;
  return out;
}
function rotateY(out, a) {
  const c = Math.cos(a), s = Math.sin(a);
  ident(out);
  out[0] = c; out[2] = -s; out[8] = s; out[10] = c;
  return out;
}
function rotateZ(out, a) {
  const c = Math.cos(a), s = Math.sin(a);
  ident(out);
  out[0] = c; out[1] = s; out[4] = -s; out[5] = c;
  return out;
}
function aimY(out, dx, dy, dz) {
  const ylen = Math.hypot(dx, dy, dz) || 1;
  const yx = dx / ylen, yy = dy / ylen, yz = dz / ylen;
  const ref = Math.abs(yy) < 0.92 ? [0, 1, 0] : [1, 0, 0];
  let xx = ref[1] * yz - ref[2] * yy;
  let xy = ref[2] * yx - ref[0] * yz;
  let xz = ref[0] * yy - ref[1] * yx;
  const xl = Math.hypot(xx, xy, xz) || 1;
  xx /= xl; xy /= xl; xz /= xl;
  const zx = xy * yz - xz * yy;
  const zy = xz * yx - xx * yz;
  const zz = xx * yy - xy * yx;
  out.set([xx, xy, xz, 0, yx, yy, yz, 0, zx, zy, zz, 0, 0, 0, 0, 1]);
  return out;
}
function normalFromModel(m) {
  return new Float32Array([m[0], m[1], m[2], m[4], m[5], m[6], m[8], m[9], m[10]]);
}
function fract(n) { return n - Math.floor(n); }
function hash01(n) { return fract(Math.sin(n * 127.1) * 43758.5453123); }
function layerPose(level, elapsed) {
  const lanes = silo.state.lanes;
  const A = lanes.A.value, Vv = lanes.V.value, I = lanes.I.value;
  const N = lanes.N.value, Lf = lanes.L.value;
  const bloom = Math.max(0, 1 - (elapsed - lastCommitAt) / 900);
  const recover = 1 - Lf * 0.62;
  const amp = (deviateOn ? deviateAmp : 0) * recover * (0.42 + A * 0.9) * (0.72 + bloom * 0.85);
  const vessel = 1 - Vv * 0.38;
  const h = hash01(level * 17.31 + silo.state.step * 0.37);
  const h2 = hash01(level * 9.17 + 4.2);
  const t = reduced ? silo.state.step * 0.51 : elapsed * 0.00042 * (0.35 + A);
  const last = silo.state.history.length ? silo.state.history[silo.state.history.length - 1].choice : '';
  const maybe = last === 'MAYBE' ? 1.35 : 1;
  const noHold = last === 'NO' ? 0.55 : 1;
  const yesHeat = last === 'YES' ? 1.2 : 1;
  const foldTwist = silo.state.fold.strength * (level % 2 === 0 ? 0.55 : 0.18);
  return {
    tilt: amp * vessel * maybe * (0.16 + h * 0.58) * Math.sin(t * 0.9 + h2 * 6.283),
    roll: amp * vessel * 0.24 * Math.cos(t * 0.7 + h * 5.1),
    precess: t * (0.55 + h * 0.8) + h2 * 3.1 + foldTwist,
    spin: t * (1.15 - Vv * 0.75) * (level % 2 === 1 ? 1 : -0.62),
    ox: amp * vessel * noHold * 0.32 * ((11 - level) / 10) * Math.sin(t * 0.65 + h * 8) + (evo.on ? fossilDrift().tx * (0.3 + level * 0.04) : 0),
    oy: amp * 0.11 * Math.sin(t * 1.15 + level + I),
    oz: amp * vessel * noHold * 0.32 * ((11 - level) / 10) * Math.cos(t * 0.5 + h2 * 5) + (evo.on ? fossilDrift().tz * (0.3 + level * 0.04) : 0),
    sx: 1 + amp * 0.2 * (N - 0.5) * yesHeat,
    sy: 1 + amp * 0.09 * (h - 0.5),
    sz: 1 - amp * 0.17 * (N - 0.5),
    amp,
  };
}

/* ---------- meshes ---------- */
function meshTorus(R, r, su, sv, col) {
  const pos = [], nrm = [], rgb = [], idx = [];
  for (let i = 0; i <= su; i++) {
    const th = (i / su) * Math.PI * 2;
    const ct = Math.cos(th), st = Math.sin(th);
    for (let j = 0; j <= sv; j++) {
      const ph = (j / sv) * Math.PI * 2;
      const cp = Math.cos(ph), sp = Math.sin(ph);
      pos.push((R + r * cp) * ct, r * sp, (R + r * cp) * st);
      nrm.push(cp * ct, sp, cp * st);
      rgb.push(col[0], col[1], col[2]);
    }
  }
  const stride = sv + 1;
  for (let i = 0; i < su; i++) {
    for (let j = 0; j < sv; j++) {
      const a = i * stride + j;
      const b = a + stride;
      idx.push(a, b, a + 1, b, b + 1, a + 1);
    }
  }
  return pack(pos, nrm, rgb, idx);
}

function meshFlexBox(h, bulge, div, col) {
  const pos = [], nrm = [], rgb = [], idx = [];
  const faces = [
    { n: [1, 0, 0], t: [0, 1, 0], b: [0, 0, 1] },
    { n: [-1, 0, 0], t: [0, 1, 0], b: [0, 0, -1] },
    { n: [0, 1, 0], t: [1, 0, 0], b: [0, 0, -1] },
    { n: [0, -1, 0], t: [1, 0, 0], b: [0, 0, 1] },
    { n: [0, 0, 1], t: [1, 0, 0], b: [0, 1, 0] },
    { n: [0, 0, -1], t: [1, 0, 0], b: [0, -1, 0] },
  ];
  for (const f of faces) {
    const base = pos.length / 3;
    for (let i = 0; i <= div; i++) {
      for (let j = 0; j <= div; j++) {
        const u = (i / div) * 2 - 1;
        const v = (j / div) * 2 - 1;
        const puff = bulge * (1 - u * u) * (1 - v * v);
        const x = f.n[0] * (h + puff) + f.t[0] * u * h + f.b[0] * v * h;
        const y = f.n[1] * (h + puff) + f.t[1] * u * h + f.b[1] * v * h;
        const z = f.n[2] * (h + puff) + f.t[2] * u * h + f.b[2] * v * h;
        const nx = f.n[0] + f.t[0] * (-2 * u * bulge * (1 - v * v) / Math.max(h, 1e-6)) * 0.5;
        const ny = f.n[1] + f.t[1] * (-2 * u * bulge * (1 - v * v) / Math.max(h, 1e-6)) * 0.5;
        const nz = f.n[2] + f.t[2] * (-2 * u * bulge * (1 - v * v) / Math.max(h, 1e-6)) * 0.5;
        const nl = Math.hypot(nx, ny, nz) || 1;
        pos.push(x, y, z);
        nrm.push(nx / nl, ny / nl, nz / nl);
        rgb.push(col[0], col[1], col[2]);
      }
    }
    const s = div + 1;
    for (let i = 0; i < div; i++) {
      for (let j = 0; j < div; j++) {
        const a = base + i * s + j;
        const b = a + s;
        idx.push(a, b, a + 1, b, b + 1, a + 1);
      }
    }
  }
  return pack(pos, nrm, rgb, idx);
}

function meshSphere(r, su, sv, col) {
  const pos = [], nrm = [], rgb = [], idx = [];
  for (let i = 0; i <= sv; i++) {
    const ph = (i / sv) * Math.PI;
    const sp = Math.sin(ph), cp = Math.cos(ph);
    for (let j = 0; j <= su; j++) {
      const th = (j / su) * Math.PI * 2;
      const x = sp * Math.cos(th), y = cp, z = sp * Math.sin(th);
      pos.push(r * x, r * y, r * z);
      nrm.push(x, y, z);
      rgb.push(col[0], col[1], col[2]);
    }
  }
  const stride = su + 1;
  for (let i = 0; i < sv; i++) {
    for (let j = 0; j < su; j++) {
      const a = i * stride + j;
      const b = a + stride;
      idx.push(a, b, a + 1, b, b + 1, a + 1);
    }
  }
  return pack(pos, nrm, rgb, idx);
}

function meshCylinder(r, h, seg, col) {
  const pos = [], nrm = [], rgb = [], idx = [];
  const y0 = -h / 2, y1 = h / 2;
  for (let i = 0; i <= seg; i++) {
    const th = (i / seg) * Math.PI * 2;
    const c = Math.cos(th), s = Math.sin(th);
    pos.push(r * c, y0, r * s, r * c, y1, r * s);
    nrm.push(c, 0, s, c, 0, s);
    rgb.push(col[0], col[1], col[2], col[0], col[1], col[2]);
  }
  for (let i = 0; i < seg; i++) {
    const a = i * 2;
    idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2);
  }
  return pack(pos, nrm, rgb, idx);
}

function pack(pos, nrm, rgb, idx) {
  const n = pos.length / 3;
  const v = new Float32Array(n * 9);
  for (let i = 0; i < n; i++) {
    const o = i * 9;
    v[o] = pos[i * 3]; v[o + 1] = pos[i * 3 + 1]; v[o + 2] = pos[i * 3 + 2];
    v[o + 3] = nrm[i * 3]; v[o + 4] = nrm[i * 3 + 1]; v[o + 5] = nrm[i * 3 + 2];
    v[o + 6] = rgb[i * 3]; v[o + 7] = rgb[i * 3 + 1]; v[o + 8] = rgb[i * 3 + 2];
  }
  return { v, i: new Uint16Array(idx), count: idx.length };
}

const VS = `#version 300 es
precision highp float;
layout(location=0) in vec3 aPos;
layout(location=1) in vec3 aNrm;
layout(location=2) in vec3 aCol;
uniform mat4 uMVP;
uniform mat4 uM;
uniform mat3 uN;
out vec3 vW;
out vec3 vN;
out vec3 vC;
void main(){
  vec4 w = uM * vec4(aPos, 1.0);
  vW = w.xyz;
  vN = normalize(uN * aNrm);
  vC = aCol;
  gl_Position = uMVP * vec4(aPos, 1.0);
}`;

const FS = `#version 300 es
precision highp float;
in vec3 vW;
in vec3 vN;
in vec3 vC;
uniform vec3 uEye;
uniform vec3 uL0;
uniform vec3 uL1;
uniform float uAlpha;
uniform float uGlow;
uniform float uTime;
uniform float uIri;
uniform vec3 uTint;
uniform float uTintMix;
out vec4 o;
void main(){
  vec3 n = normalize(vN);
  vec3 view = normalize(uEye - vW);
  if (dot(n, view) < 0.0) n = -n;
  float wrap = 0.5 + 0.5 * dot(n, normalize(uL0));
  float fill = 0.5 + 0.5 * dot(n, normalize(uL1));
  float hemi = 0.42 + 0.58 * n.y;
  float rim = pow(1.0 - max(dot(n, view), 0.0), 2.2);
  vec3 base = mix(vC, uTint, uTintMix);
  vec3 col = base * (0.16 + 0.48 * wrap + 0.22 * fill + 0.22 * hemi);
  col += vec3(0.55, 0.88, 1.0) * rim * 0.32;
  float band = sin(vW.x * 2.8 + vW.z * 1.7 + uTime * 0.85 + n.y * 4.0);
  col += vec3(0.25, 0.62, 1.0) * band * uIri * rim;
  col += base * uGlow;
  o = vec4(col, uAlpha);
}`;

function compile(ctx, type, src) {
  const sh = ctx.createShader(type);
  ctx.shaderSource(sh, src);
  ctx.compileShader(sh);
  if (!ctx.getShaderParameter(sh, ctx.COMPILE_STATUS)) {
    throw new Error(ctx.getShaderInfoLog(sh) || 'shader');
  }
  return sh;
}

function initGL() {
  const ctx = field.getContext('webgl2', {
    alpha: false,
    antialias: true,
    depth: true,
    powerPreference: 'high-performance',
  });
  if (!ctx) return false;
  const prog = ctx.createProgram();
  ctx.attachShader(prog, compile(ctx, ctx.VERTEX_SHADER, VS));
  ctx.attachShader(prog, compile(ctx, ctx.FRAGMENT_SHADER, FS));
  ctx.linkProgram(prog);
  if (!ctx.getProgramParameter(prog, ctx.LINK_STATUS)) {
    throw new Error(ctx.getProgramInfoLog(prog) || 'link');
  }
  const u = (name) => ctx.getUniformLocation(prog, name);
  gpu = {
    ctx,
    prog,
    uMVP: u('uMVP'),
    uM: u('uM'),
    uN: u('uN'),
    uEye: u('uEye'),
    uL0: u('uL0'),
    uL1: u('uL1'),
    uAlpha: u('uAlpha'),
    uGlow: u('uGlow'),
    uTime: u('uTime'),
    uIri: u('uIri'),
    uTint: u('uTint'),
    uTintMix: u('uTintMix'),
    buffers: new Map(),
  };
  ctx.enable(ctx.DEPTH_TEST);
  ctx.enable(ctx.BLEND);
  ctx.blendFunc(ctx.SRC_ALPHA, ctx.ONE_MINUS_SRC_ALPHA);
  ctx.disable(ctx.CULL_FACE);
  gl = ctx;
  renderer = 'webgl2';
  return true;
}

function gpuMesh(key, mesh) {
  let b = gpu.buffers.get(key);
  if (!b) {
    b = {
      vao: gl.createVertexArray(),
      vb: gl.createBuffer(),
      ib: gl.createBuffer(),
      count: 0,
    };
    gpu.buffers.set(key, b);
  }
  gl.bindVertexArray(b.vao);
  gl.bindBuffer(gl.ARRAY_BUFFER, b.vb);
  gl.bufferData(gl.ARRAY_BUFFER, mesh.v, gl.DYNAMIC_DRAW);
  gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, b.ib);
  gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, mesh.i, gl.DYNAMIC_DRAW);
  const stride = 36;
  gl.enableVertexAttribArray(0);
  gl.vertexAttribPointer(0, 3, gl.FLOAT, false, stride, 0);
  gl.enableVertexAttribArray(1);
  gl.vertexAttribPointer(1, 3, gl.FLOAT, false, stride, 12);
  gl.enableVertexAttribArray(2);
  gl.vertexAttribPointer(2, 3, gl.FLOAT, false, stride, 24);
  b.count = mesh.count;
  gl.bindVertexArray(null);
  return b;
}

let geomKey = '';
function rebuildGeom() {
  const flex = silo.state.boxFlexFraction;
  const key = flex.toFixed(5);
  if (key === geomKey && gpu.buffers.has('torus0')) return;
  geomKey = key;
  for (let i = 0; i < 5; i++) {
    gpuMesh('torus' + i, meshTorus(1, 0.085, 64, 18, TORUS_COL[i]));
    gpuMesh('box' + i, meshFlexBox(1, boxBulge(1, flex), 8, BOX_COL[i]));
  }
  gpuMesh('core', meshSphere(1, 24, 16, [1.0, 0.95, 0.78]));
  gpuMesh('tunnel', meshCylinder(1, 1, 28, [0.85, 0.92, 1.0]));
  gpuMesh('ringL', meshTorus(1, 0.1, 56, 14, [0.55, 0.95, 0.75]));
  gpuMesh('ringR', meshTorus(1, 0.1, 56, 14, [0.95, 0.70, 0.45]));
  gpuMesh('filY', meshCylinder(1, 1, 14, [0.95, 0.82, 0.32]));
  gpuMesh('filN', meshCylinder(1, 1, 14, [0.85, 0.40, 0.42]));
  gpuMesh('filM', meshCylinder(1, 1, 14, [1.00, 0.70, 0.22]));
  gpuMesh('bead', meshSphere(1, 16, 12, [1.0, 1.0, 1.0]));
  gpuMesh('spoke', meshCylinder(1, 1, 10, [0.92, 0.78, 0.48]));
}

const P = new Float32Array(16);
const V = new Float32Array(16);
const M = new Float32Array(16);
const MVP = new Float32Array(16);
const TMP = new Float32Array(16);
const RX = new Float32Array(16);
const RY = new Float32Array(16);
const RZ = new Float32Array(16);
const RS = new Float32Array(16);
const RT = new Float32Array(16);
const R1 = new Float32Array(16);
const eye = [0, 0, 0];

function poseModel(level, elapsed, sx, sy, sz) {
  const p = layerPose(level, elapsed);
  scaleM(RS, sx * p.sx, sy * p.sy, sz * p.sz);
  rotateZ(RZ, p.spin);
  rotateX(RX, p.tilt);
  rotateY(RY, p.precess + p.roll);
  translate(RT, p.ox, p.oy, p.oz);
  mul(R1, RZ, RS);
  mul(R1, RX, R1);
  mul(R1, RY, R1);
  mul(M, RT, R1);
  return M;
}

function framedDist() {
  const extra = silo.state.explode * 5.2 + (silo.state.overlay313 ? 1.6 : 0) + (deviateOn ? deviateAmp * 1.5 : 0);
  return cam.dist + extra;
}
function cameraEye() {
  const dist = framedDist();
  const cp = Math.cos(cam.pitch), sp = Math.sin(cam.pitch);
  const cy = Math.cos(cam.yaw), sy = Math.sin(cam.yaw);
  eye[0] = dist * sy * cp;
  eye[1] = dist * sp;
  eye[2] = dist * cy * cp;
}

function drawMesh(name, model, alpha, glow, tint, tintMix) {
  const b = gpu.buffers.get(name);
  if (!b) return;
  mul(MVP, V, model);
  mul(MVP, P, MVP);
  gl.uniformMatrix4fv(gpu.uMVP, false, MVP);
  gl.uniformMatrix4fv(gpu.uM, false, model);
  gl.uniformMatrix3fv(gpu.uN, false, normalFromModel(model));
  gl.uniform1f(gpu.uAlpha, alpha);
  gl.uniform1f(gpu.uGlow, glow);
  gl.uniform1f(gpu.uTime, drawTime);
  gl.uniform1f(gpu.uIri, evo.on ? 0.42 : 0.07);
  gl.uniform3fv(gpu.uTint, tint || [1, 1, 1]);
  gl.uniform1f(gpu.uTintMix, tintMix || 0);
  gl.bindVertexArray(b.vao);
  gl.drawElements(gl.TRIANGLES, b.count, gl.UNSIGNED_SHORT, 0);
}

function drawFilament(name, dx, dy, dz, len, radius, alpha, glow) {
  scaleM(RS, radius, len, radius);
  aimY(RY, dx, dy, dz);
  translate(RT, dx * len * 0.5, dy * len * 0.5, dz * len * 0.5);
  mul(R1, RY, RS);
  mul(M, RT, R1);
  drawMesh(name, M, alpha, glow);
}

function drawGL(elapsed) {
  const w = field.width, h = field.height;
  gl.viewport(0, 0, w, h);
  gl.clearColor(0.012, 0.031, 0.047, 1);
  gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
  perspective(P, Math.PI / 4.4, w / Math.max(h, 1), 0.12, 48);
  cameraEye();
  lookAt(V, eye, [0, 0, 0], [0, 1, 0]);
  gl.useProgram(gpu.prog);
  gl.uniform3fv(gpu.uEye, eye);
  gl.uniform3f(gpu.uL0, 0.45, 0.82, 0.35);
  gl.uniform3f(gpu.uL1, -0.62, 0.18, -0.42);
  rebuildGeom();
  drawTime = elapsed * 0.001;

  const explode = silo.state.explode;
  const pulse = reduced ? 0.08 : 0.08 + 0.06 * Math.sin(elapsed * 0.003);
  const outer = layerRadius(1, explode);
  const last = silo.state.history.length ? silo.state.history[silo.state.history.length - 1].choice : '';
  const emerge = Math.min(1, 0.4 + silo.state.step * 0.07);

  scaleM(TMP, 0.038, outer * 2.15, 0.038);
  drawMesh('tunnel', TMP, 0.22, 0.04);

  if (evo.on) {
    const fossils = evo.fossils;
    for (let i = 0; i < fossils.length; i++) {
      const f = fossils[i];
      const age = (i + 1) / fossils.length;
      const sc = 0.55 + age * 1.35 + explode * 0.2;
      rotateY(RY, f.yaw);
      rotateX(RX, f.tilt);
      scaleM(RS, sc, sc * 0.22, sc);
      mul(R1, RX, RS);
      mul(M, RY, R1);
      const tint = CHOICE_TINT[f.choice] || CHOICE_TINT.MAYBE;
      drawMesh('torus0', M, 0.05 + age * 0.07, 0.04, tint, 0.85);
    }
  }

  for (let level = 10; level >= 1; level--) {
    const L = silo.state.layers[level - 1];
    if (!L.visible) continue;
    const R = layerRadius(level, explode);
    const odd = L.shape === 'toroid';
    const k = Math.floor((level - 1) / 2);
    const born = Math.min(1, emerge + (11 - level) * 0.05);
    if (odd) {
      poseModel(level, elapsed, R, R, R);
      drawMesh('torus' + k, M, (0.23 + (11 - level) * 0.018) * born, 0.03);
    } else {
      const hs = R * 0.62;
      poseModel(level, elapsed, hs, hs, hs);
      drawMesh('box' + k, M, (0.19 + (11 - level) * 0.016) * born, 0.02);
      if (evo.on) {
        const p = layerPose(level, elapsed);
        const nSpokes = level;
        for (let s = 0; s < nSpokes; s++) {
          const a = (s / nSpokes) * Math.PI * 2 + p.precess;
          drawFilament('spoke', Math.cos(a), 0.04, Math.sin(a), hs * 1.08, 0.011, 0.16 * born, 0.03);
        }
      }
    }
  }

  const I = silo.state.lanes.I.value;
  const cone = 0.55 + I * 0.9;
  const spin = reduced ? 0 : elapsed * 0.00055;
  const triad = [
    { name: 'filY', choice: 'YES', a: 0.00 + spin, w: 0.42 },
    { name: 'filN', choice: 'NO', a: 2.094 + spin * 0.7, w: -0.18 },
    { name: 'filM', choice: 'MAYBE', a: 4.189 - spin * 0.4, w: 0.22 },
  ];
  for (const f of triad) {
    const lit = last === f.choice;
    const len = (lit ? 1.55 : 0.72) * cone;
    const dx = Math.cos(f.a) * 0.85;
    const dy = f.w;
    const dz = Math.sin(f.a) * 0.85;
    drawFilament(f.name, dx, dy, dz, len, lit ? 0.028 : 0.016, lit ? 0.72 : 0.18, lit ? 0.22 : 0.04);
  }

  const since = Math.max(0, elapsed - lastCommitAt);
  const windowT = evo.on ? Math.min(1, (since % 2000) / 2000) : 0;
  if (evo.on) {
    const wr = 0.14 + windowT * 0.62;
    scaleM(M, wr, wr, wr);
    drawMesh('bead', M, 0.07 + (1 - windowT) * 0.06, 0.12, [0.55, 0.9, 1.0], 1);
  }

  if (evo.on) {
    const lanes = SPEC.lanes;
    for (let i = 0; i < lanes.length; i++) {
      const id = lanes[i];
      const val = silo.state.lanes[id].value;
      const ang = (reduced ? silo.state.step * 0.4 : elapsed * 0.00065 * (0.45 + val)) + i * 1.2566;
      const rad = 0.62 + val * 1.15 + explode * 0.35;
      const y = (val - 0.5) * 0.85;
      translate(RT, Math.cos(ang) * rad, y, Math.sin(ang) * rad);
      const br = 0.055 + val * 0.05;
      scaleM(RS, br, br, br);
      mul(M, RT, RS);
      drawMesh('bead', M, 0.72, 0.18, LANE_TINT[id], 1);
    }
    const groups = silo.state.wave.groups;
    for (let g = 0; g < groups.length; g++) {
      const ones = groups[g].split('1').length - 1;
      const pop = ones / 7;
      const y = (g - 3) * outer * 0.24;
      translate(RT, 0, y, 0);
      const br = 0.028 + pop * 0.045;
      scaleM(RS, br, br, br);
      mul(M, RT, RS);
      const tint = g < 3 ? [0.4, 0.95, 0.7] : g === 3 ? [1, 1, 1] : [0.95, 0.7, 0.35];
      drawMesh('bead', M, 0.35 + pop * 0.4, 0.1, tint, 1);
    }
  }

  const cs = 0.075 + pulse * 0.04;
  scaleM(M, cs, cs, cs);
  gl.disable(gl.DEPTH_TEST);
  drawMesh('core', M, 1, 0.45 + pulse);
  gl.enable(gl.DEPTH_TEST);

  if (silo.state.overlay313) {
    const sep = 1.55 + explode * 0.35;
    const pL = layerPose(3, elapsed);
    const pR = layerPose(7, elapsed);
    translate(TMP, -sep + pL.ox * 0.4, pL.oy * 0.4, pL.oz * 0.4);
    scaleM(RS, 0.52, 0.52, 0.52);
    rotateY(RY, pL.precess * 0.4);
    mul(R1, RY, RS);
    mul(M, TMP, R1);
    drawMesh('ringL', M, 0.5, 0.1);
    translate(TMP, sep + pR.ox * 0.4, pR.oy * 0.4, pR.oz * 0.4);
    scaleM(RS, 0.52, 0.52, 0.52);
    rotateY(RY, pR.precess * 0.4);
    mul(R1, RY, RS);
    mul(M, TMP, R1);
    drawMesh('ringR', M, 0.5, 0.1);
    const rotZ90 = new Float32Array([
      0, 1, 0, 0,
      -1, 0, 0, 0,
      0, 0, 1, 0,
      0, 0, 0, 1,
    ]);
    scaleM(TMP, 0.03, sep * 2.1, 0.03);
    mul(M, rotZ90, TMP);
    drawMesh('tunnel', M, 0.28, 0.04);
  }
}

function draw2D(elapsed) {
  const ctx = field.getContext('2d');
  const w = field.width, h = field.height;
  ctx.fillStyle = '#03080c';
  ctx.fillRect(0, 0, w, h);
  const cx = w * 0.5, cy = h * 0.52;
  const s = Math.min(w, h) * 0.145;
  const explode = silo.state.explode;
  ctx.strokeStyle = 'rgba(230,240,255,0.22)';
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.moveTo(cx, cy - layerRadius(1, explode) * s * 1.05);
  ctx.lineTo(cx, cy + layerRadius(1, explode) * s * 1.05);
  ctx.stroke();
  for (let level = 1; level <= 10; level++) {
    const L = silo.state.layers[level - 1];
    if (!L.visible) continue;
    const p = layerPose(level, elapsed || 0);
    const R = layerRadius(level, explode) * s;
    const ox = p.ox * s * 0.85, oy = -p.oy * s * 0.85;
    if (L.shape === 'toroid') {
      ctx.strokeStyle = `rgba(115,213,255,${0.35 + (11 - level) * 0.04})`;
      ctx.lineWidth = Math.max(1.4, 9 - level * 0.55);
      ctx.beginPath();
      ctx.ellipse(cx + ox, cy + oy, R * p.sx, R * 0.36 * p.sz, p.precess * 0.25, 0, Math.PI * 2);
      ctx.stroke();
    } else {
      const hs = R * 0.62;
      const b = boxBulge(hs, silo.state.boxFlexFraction);
      ctx.save();
      ctx.translate(cx + ox, cy + oy);
      ctx.rotate(p.spin * 0.35);
      ctx.strokeStyle = `rgba(242,200,107,${0.4 + (11 - level) * 0.03})`;
      ctx.lineWidth = 1.6;
      ctx.beginPath();
      roundedRect(ctx, -hs * p.sx, -hs * 0.72 * p.sy, hs * 2 * p.sx, hs * 1.44 * p.sy, Math.max(4, b * 2.2));
      ctx.stroke();
      ctx.restore();
    }
  }
  if (silo.state.overlay313) {
    const sep = (2.55 + explode * 0.9) * s * 0.45;
    ctx.strokeStyle = 'rgba(85,230,170,0.7)';
    ctx.lineWidth = 5;
    ctx.beginPath(); ctx.ellipse(cx - sep, cy, s * 0.55, s * 0.2, 0, 0, Math.PI * 2); ctx.stroke();
    ctx.strokeStyle = 'rgba(240,160,80,0.7)';
    ctx.beginPath(); ctx.ellipse(cx + sep, cy, s * 0.55, s * 0.2, 0, 0, Math.PI * 2); ctx.stroke();
    ctx.strokeStyle = 'rgba(255,255,255,0.35)';
    ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(cx - sep, cy); ctx.lineTo(cx + sep, cy); ctx.stroke();
  }
  if (evo.on) {
    for (let i = 0; i < evo.fossils.length; i++) {
      const f = evo.fossils[i];
      const age = (i + 1) / evo.fossils.length;
      const col = f.choice === 'YES' ? '242,200,107' : f.choice === 'NO' ? '216,132,122' : '255,176,58';
      ctx.strokeStyle = `rgba(${col},${0.12 + age * 0.2})`;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.ellipse(cx, cy, (0.7 + age * 1.2) * s, (0.22 + age * 0.35) * s, f.yaw * 0.2, 0, Math.PI * 2);
      ctx.stroke();
    }
    const lanes = SPEC.lanes;
    for (let i = 0; i < lanes.length; i++) {
      const id = lanes[i];
      const val = silo.state.lanes[id].value;
      const ang = (elapsed || 0) * 0.00065 + i * 1.2566;
      const rad = (0.62 + val * 1.15) * s * 0.55;
      ctx.fillStyle = id === 'V' ? '#f2c86b' : id === 'A' ? '#73d5ff' : id === 'I' ? '#c79bff' : id === 'N' ? '#3acdb0' : '#d8847a';
      ctx.beginPath();
      ctx.arc(cx + Math.cos(ang) * rad, cy + Math.sin(ang) * rad * 0.4, 4 + val * 3, 0, Math.PI * 2);
      ctx.fill();
    }
    const wt = Math.min(1, (Math.max(0, (elapsed || 0) - lastCommitAt) % 2000) / 2000);
    ctx.strokeStyle = `rgba(115,213,255,${0.2 + (1 - wt) * 0.25})`;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(cx, cy, (0.14 + wt * 0.62) * s, 0, Math.PI * 2);
    ctx.stroke();
  }
  ctx.fillStyle = '#fff4c8';
  ctx.beginPath();
  ctx.arc(cx, cy, 5, 0, Math.PI * 2);
  ctx.fill();
}

function roundedRect(ctx, x, y, w, h, r) {
  const rr = Math.min(r, w / 2, h / 2);
  ctx.moveTo(x + rr, y);
  ctx.arcTo(x + w, y, x + w, y + h, rr);
  ctx.arcTo(x + w, y + h, x, y + h, rr);
  ctx.arcTo(x, y + h, x, y, rr);
  ctx.arcTo(x, y, x + w, y, rr);
  ctx.closePath();
}

/* ---------- fold net ---------- */
function lerp(a, b, t) { return a + (b - a) * t; }
function drawFold() {
  const ctx = foldCanvas.getContext('2d');
  const w = foldCanvas.width, h = foldCanvas.height;
  ctx.fillStyle = '#05090d';
  ctx.fillRect(0, 0, w, h);
  const t = silo.state.fold.strength;
  const closed = silo.state.fold.mode === 'closed';
  const size = 56;
  const cx = w * 0.5, cy = h * (closed ? 0.56 : 0.50);
  const net = { V: [0, 0], A: [-1, 0], N: [1, 0], I: [0, -1], L: [0, 1], lid: [0, -2] };
  const iso = { V: [0, 0], A: [-0.78, 0.26], N: [0.78, 0.26], I: [0, -0.68], L: [0, 0.68], lid: [0, -1.22] };
  const faces = [
    { id: 'V', col: '#f2c86b' },
    { id: 'A', col: '#73d5ff' },
    { id: 'N', col: '#3acdb0' },
    { id: 'I', col: '#c79bff' },
    { id: 'L', col: '#d8847a' },
  ];
  if (closed) faces.unshift({ id: 'lid', col: '#e8f1ea' });
  ctx.font = '12px ui-monospace, Consolas, monospace';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  for (const f of faces) {
    const a = net[f.id], b = iso[f.id];
    const miss = deviateOn ? (hash01(f.id.charCodeAt(0) * 3.1 + silo.state.step) - 0.5) * 7 * deviateAmp : 0;
    const px = cx + lerp(a[0], b[0], t) * size + miss;
    const py = cy + lerp(a[1], b[1], t) * size + miss * 0.4;
    const fw = size * (0.92 - t * 0.12);
    const fh = size * (0.92 - t * 0.12);
    ctx.fillStyle = '#0c1418';
    ctx.strokeStyle = f.col;
    ctx.lineWidth = 1.7;
    ctx.beginPath();
    ctx.rect(px - fw / 2, py - fh / 2, fw, fh);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = f.col;
    ctx.fillText(f.id, px, py);
  }
  ctx.fillStyle = '#8aa093';
  ctx.font = '9px ui-monospace, Consolas, monospace';
  ctx.fillText(SPEC.workspaceNotation + '  ·  ' + silo.state.workspaceSlots.length + ' addr', cx, h - 16);
}

/* ---------- UI ---------- */
function buildLayers() {
  const host = $('layers');
  host.innerHTML = '';
  for (const L of silo.state.layers) {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'layer-btn';
    b.dataset.level = String(L.level);
    b.setAttribute('aria-pressed', L.visible ? 'true' : 'false');
    b.innerHTML = String(L.level).padStart(2, '0') + '<small>' + (L.shape === 'toroid' ? 'TOR' : 'BOX') + '</small>';
    b.addEventListener('click', () => {
      silo.setLayerVisible(L.level, !L.visible);
      b.setAttribute('aria-pressed', L.visible ? 'true' : 'false');
      syncHud();
    });
    host.appendChild(b);
  }
}

function buildVainl() {
  const host = $('vainl');
  host.innerHTML = '';
  for (const id of SPEC.lanes) {
    const row = document.createElement('div');
    row.className = 'lane ' + id;
    row.innerHTML = `<span class="id">${id}</span><span class="bar"><i id="bar${id}"></i></span><span id="val${id}">0.50</span>`;
    host.appendChild(row);
  }
  const custom = $('customGroup');
  custom.innerHTML = '';
  for (const id of SPEC.lanes) {
    const lab = document.createElement('label');
    lab.innerHTML = `<input type="checkbox" data-lane="${id}"> ${id} internal`;
    custom.appendChild(lab);
  }
  custom.addEventListener('change', () => {
    if ($('grouping').value !== 'custom') return;
    const inn = [...custom.querySelectorAll('input:checked')].map((x) => x.dataset.lane);
    silo.setGrouping('custom', inn);
    syncHud();
  });
}

function syncLanes() {
  for (const id of SPEC.lanes) {
    const v = silo.state.lanes[id].value;
    const bar = $('bar' + id);
    const val = $('val' + id);
    if (bar) bar.style.width = (v * 100).toFixed(1) + '%';
    if (val) val.textContent = v.toFixed(2);
  }
}

function syncHud() {
  const s = silo.state;
  $('hudScalar').textContent = String(s.scalar);
  $('hudStep').textContent = String(s.step);
  $('hudTime').textContent = 'NOW  +' + s.simulatedSeconds + 's recorded';
  $('hudChoice').textContent = s.history.length
    ? 'last ' + s.history[s.history.length - 1].choice
    : 'pending unresolved';
  $('hudGeom').textContent = s.layers
    .filter((L) => L.visible)
    .map((L) => String(L.level).padStart(2, '0') + (L.shape === 'toroid' ? '○' : '□'))
    .join(' ');
  $('hudFlex').textContent = (deviateOn ? 'DEVIATE ' + Math.round(deviateAmp * 100) + '% · ' : 'COAXIAL · ') + 'flex ' + (s.boxFlexFraction * 100).toFixed(3) + '%';
  $('hudRenderer').textContent = renderer.toUpperCase();
  $('mScalar').textContent = String(s.scalar);
  $('mStep').textContent = s.step + ' / ' + s.simulatedSeconds + 's';
  $('mFlex').textContent = (s.boxFlexFraction * 100).toFixed(3) + '%';
  $('mWs').textContent = String(s.workspaceSlots.length);
  $('mFold').textContent = s.fold.net;
  $('mHist').textContent = String(s.history.length);
  if ($('mDev')) $('mDev').textContent = (deviateOn ? 'ON ' : 'OFF ') + Math.round(deviateAmp * 100) + '%';
  if ($('mFoss')) $('mFoss').textContent = String(evo.fossils.length);
  $('netLabel').textContent = s.fold.net + ' ' + s.fold.mode.toUpperCase();
  $('explodeOut').textContent = Math.round(s.explode * 100) + '%';
  $('flexOut').textContent = (s.boxFlexFraction * 100).toFixed(3) + '%';
  $('foldOut').textContent = Math.round(s.fold.strength * 100) + '%';
  $('btnOpen').setAttribute('aria-pressed', s.fold.mode === 'open' ? 'true' : 'false');
  $('btnClosed').setAttribute('aria-pressed', s.fold.mode === 'closed' ? 'true' : 'false');
  $('btnOverlay').setAttribute('aria-pressed', s.overlay313 ? 'true' : 'false');
  $('btnAuto').setAttribute('aria-pressed', autoOn ? 'true' : 'false');
  if ($('btnDeviate')) $('btnDeviate').setAttribute('aria-pressed', deviateOn ? 'true' : 'false');
  if ($('btnEvolve')) $('btnEvolve').setAttribute('aria-pressed', evo.on ? 'true' : 'false');
  if ($('deviateOut')) $('deviateOut').textContent = Math.round(deviateAmp * 100) + '%';
  const lit = s.layerCount === 10 && s.workspaceSlots.length === 6 && s.scalar === 0;
  $('pillLit').className = 'pill' + (lit ? ' lit' : ' wall');
  $('pillLit').textContent = lit ? 'LIT software contract' : 'WALL contract broken';
  syncLanes();
  syncJournal();
}

function syncJournal() {
  const host = $('journal');
  const hist = silo.state.history;
  if (!hist.length) {
    host.innerHTML = '<li class="empty">No commits. Choose YES / NO / MAYBE.</li>';
    return;
  }
  host.innerHTML = hist
    .slice()
    .reverse()
    .map(
      (r) =>
        `<li class="event"><time>#${String(r.seq).padStart(3, '0')}</time><div><b>${r.choice}</b> · Toph · ${r.simulatedSecondsAfter}s · scalar ${r.scalar}</div></li>`,
    )
    .join('');
}

function commit(choice) {
  const rec = silo.transition(choice);
  remember(rec);
  lastCommitAt = performance.now() - t0;
  syncHud();
}

function downloadJson() {
  const blob = new Blob([JSON.stringify(silo.snapshot(), null, 2)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'oasis-ket-silo-snapshot.json';
  a.click();
  URL.revokeObjectURL(a.href);
}

function fit(canvas) {
  const dpr = Math.min(2, devicePixelRatio || 1);
  const r = canvas.getBoundingClientRect();
  const w = Math.max(1, Math.floor(r.width * dpr));
  const h = Math.max(1, Math.floor(r.height * dpr));
  if (canvas.width !== w || canvas.height !== h) {
    canvas.width = w;
    canvas.height = h;
  }
}

function onPointerDown(ev) {
  cam.dragging = true;
  cam.lastX = ev.clientX;
  cam.lastY = ev.clientY;
  field.setPointerCapture(ev.pointerId);
}
function onPointerMove(ev) {
  if (!cam.dragging) return;
  const dx = ev.clientX - cam.lastX;
  const dy = ev.clientY - cam.lastY;
  cam.lastX = ev.clientX;
  cam.lastY = ev.clientY;
  cam.yaw += dx * 0.008;
  cam.pitch = Math.max(-1.15, Math.min(1.15, cam.pitch + dy * 0.008));
}
function onPointerUp() { cam.dragging = false; }
function onWheel(ev) {
  ev.preventDefault();
  cam.dist = Math.max(3.2, Math.min(14, cam.dist + ev.deltaY * 0.004));
}

function wire() {
  buildLayers();
  buildVainl();
  $('btnYes').onclick = () => commit('YES');
  $('btnNo').onclick = () => commit('NO');
  $('btnMaybe').onclick = () => commit('MAYBE');
  $('btnAuto').onclick = () => { autoOn = !autoOn; lastAuto = performance.now(); syncHud(); };
  $('btnReset').onclick = () => { silo.resetDemo(); evo.fossils = []; lastCommitAt = -1e9; syncHud(); };
  $('btnJson').onclick = downloadJson;
  $('btnOverlay').onclick = () => { silo.setOverlay(!silo.state.overlay313); syncHud(); };
  $('btnDeviate').onclick = () => { deviateOn = !deviateOn; syncHud(); };
  $('btnEvolve').onclick = () => { evo.on = !evo.on; syncHud(); };
  $('deviate').oninput = (e) => { deviateAmp = Number(e.target.value) / 100; syncHud(); };
  $('btnOpen').onclick = () => { silo.setFoldMode('open'); syncHud(); };
  $('btnClosed').onclick = () => { silo.setFoldMode('closed'); syncHud(); };
  $('explode').oninput = (e) => { silo.setExplode(Number(e.target.value) / 100); syncHud(); };
  $('flex').oninput = (e) => {
    silo.setFlex(Number(e.target.value) / 10000);
    geomKey = '';
    syncHud();
  };
  $('fold').oninput = (e) => { silo.setFoldStrength(Number(e.target.value) / 100); syncHud(); };
  $('speed').oninput = (e) => { autoMs = Number(e.target.value); $('speedOut').textContent = String(autoMs); };
  $('grouping').onchange = (e) => {
    const mode = e.target.value;
    $('customGroup').hidden = mode !== 'custom';
    if (mode === 'custom') {
      const inn = [...$('customGroup').querySelectorAll('input:checked')].map((x) => x.dataset.lane);
      silo.setGrouping('custom', inn);
    } else {
      silo.setGrouping(mode);
    }
    syncHud();
  };
  field.addEventListener('pointerdown', onPointerDown);
  field.addEventListener('pointermove', onPointerMove);
  field.addEventListener('pointerup', onPointerUp);
  field.addEventListener('pointercancel', onPointerUp);
  field.addEventListener('wheel', onWheel, { passive: false });

  $('explode').value = String(Math.round(silo.state.explode * 100));
  $('flex').value = String(silo.state.boxFlexFraction * 10000);
  $('fold').value = String(Math.round(silo.state.fold.strength * 100));
  $('deviate').value = String(Math.round(deviateAmp * 100));
  $('deviateOut').textContent = Math.round(deviateAmp * 100) + '%';
  $('grouping').value = silo.state.groupingMode;
  $('customGroup').hidden = silo.state.groupingMode !== 'custom';
  if (autoOn) $('btnAuto').setAttribute('aria-pressed', 'true');
  $('btnDeviate').setAttribute('aria-pressed', deviateOn ? 'true' : 'false');
  syncHud();
}

function tick(now) {
  const elapsed = now - t0;
  fit(field);
  if (gl) drawGL(elapsed);
  else draw2D(elapsed);
  fit(foldCanvas);
  drawFold();
  if (autoOn && now - lastAuto >= autoMs) {
    lastAuto = now;
    const picks = SPEC.choices;
    commit(picks[autoPick % 3]);
    autoPick += 1;
  }
  requestAnimationFrame(tick);
}

try {
  if (!initGL()) renderer = 'canvas2d';
} catch (err) {
  console.warn('WebGL2 failed, canvas 2D fallback', err);
  gl = null;
  renderer = 'canvas2d';
}
wire();
requestAnimationFrame(tick);

window.OASIS_KET_SILO = { silo, SPEC, cam, renderer, evo, get deviateOn() { return deviateOn; } };
