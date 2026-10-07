
const fs = require('fs');
const bytes = fs.readFileSync('/mnt/data/ringyboxy_kernel_v7.wasm');

function rng(seed) {
  let x = seed >>> 0;
  return () => {
    x ^= x << 13; x >>>= 0;
    x ^= x >>> 17; x >>>= 0;
    x ^= x << 5; x >>>= 0;
    return x >>> 0;
  };
}

(async () => {
  const mod = await WebAssembly.instantiate(bytes, {});
  const w = mod.instance.exports;
  let pass = 0;

  w.reset();
  w.install_canonical_fence(40, 0xAAA00040);
  if (w.open_replica(40, 0xAAA00040) !== 1) throw new Error('open N failed');
  if (w.prepare(1, 1, 3, 1, 1) !== 1) throw new Error('prepare N failed');
  w.install_canonical_fence(41, 0xBBB00041);
  if (w.unsafe_finalize() !== 1 || w.state() !== 1)
    throw new Error('unsafe in-flight exploit not reproduced');
  pass++;

  w.reset();
  w.install_canonical_fence(50, 0xAAA00050);
  w.open_replica(50, 0xAAA00050);
  if (w.prepare(1, 1, 3, 1, 1) !== 1) throw new Error('strict prepare failed');
  w.install_canonical_fence(51, 0xBBB00051);
  if (w.strict_finalize() !== 0 || w.state() !== 0)
    throw new Error('strict epoch rollover committed');
  pass++;

  w.reset();
  w.install_canonical_fence(60, 0x11112222);
  w.open_replica(60, 0x11112222);
  if (w.prepare(2, 2, 3, 1, 1) !== 1) throw new Error('digest prepare failed');
  w.install_canonical_fence(60, 0x33334444);
  if (w.strict_finalize() !== 0 || w.state() !== 0)
    throw new Error('strict digest rollover committed');
  pass++;

  w.reset();
  w.install_canonical_fence(70, 0x77770070);
  w.open_replica(70, 0x77770070);
  if (w.prepare(2, 2, 2, 1, 1) !== 1) throw new Error('stable prepare failed');
  if (w.strict_finalize() !== 1 || w.state() !== 2)
    throw new Error('stable strict finalize failed');
  pass++;

  w.reset();
  w.install_canonical_fence(80, 0xAAAA0080);
  w.open_replica(80, 0xAAAA0080);
  w.prepare(1, 1, 3, 1, 1);
  w.install_canonical_fence(81, 0xBBBB0081);
  if (w.strict_finalize() !== 0 || w.prepared_state() !== 0)
    throw new Error('stale prepared transaction not cleared');
  if (w.refresh_replica(81, 0xBBBB0081) !== 1) throw new Error('refresh failed');
  if (w.prepare(1, 1, 3, 1, 1) !== 1) throw new Error('reprepare failed');
  if (w.strict_finalize() !== 1 || w.state() !== 1)
    throw new Error('fresh reprepare finalize failed');
  pass++;

  const rounds = 600000;
  const rand = rng(0x7A11C0DE);
  let unsafeRolloverCommits = 0;
  let strictRolloverCommits = 0;
  let strictStableCommits = 0;
  let strictFreshRetryCommits = 0;
  let epochRollover = 0;
  let digestRollover = 0;
  let aWins = 0, bWins = 0;

  const t0 = process.hrtime.bigint();

  for (let i = 0; i < rounds; i++) {
    const child = (rand() & 1) ? 1 : 2;
    const baseEpoch = 1000 + (rand() % 1000000);
    const baseDigest = (0xA5000000 ^ rand()) >>> 0;
    const mode = rand() & 1;

    const nextEpoch = mode === 0 ? baseEpoch + 1 : baseEpoch;
    const nextDigest = (baseDigest ^ (mode === 0 ? 0x01010101 : 0x00010001)) >>> 0;
    if (mode === 0) epochRollover++; else digestRollover++;

    w.reset();
    w.install_canonical_fence(baseEpoch, baseDigest);
    w.open_replica(baseEpoch, baseDigest);
    if (w.prepare(child, child, 3, 1, 1) !== 1)
      throw new Error('unsafe stress prepare failed');
    w.install_canonical_fence(nextEpoch, nextDigest);
    if (w.unsafe_finalize() === 1) unsafeRolloverCommits++;

    w.reset();
    w.install_canonical_fence(baseEpoch, baseDigest);
    w.open_replica(baseEpoch, baseDigest);
    if (w.prepare(child, child, 3, 1, 1) !== 1)
      throw new Error('strict stress prepare failed');
    w.install_canonical_fence(nextEpoch, nextDigest);
    if (w.strict_finalize() === 1) strictRolloverCommits++;

    if (w.refresh_replica(nextEpoch, nextDigest) !== 1)
      throw new Error('strict stress refresh failed');
    if (w.prepare(child, child, 3, 1, 1) !== 1)
      throw new Error('strict stress reprepare failed');
    if (w.strict_finalize() === 1) {
      strictFreshRetryCommits++;
      if (child === 1) aWins++; else bWins++;
    }

    w.reset();
    w.install_canonical_fence(baseEpoch, baseDigest);
    w.open_replica(baseEpoch, baseDigest);
    if (w.prepare(child, child, 2, 1, 1) !== 1)
      throw new Error('stable stress prepare failed');
    if (w.strict_finalize() === 1) strictStableCommits++;
  }

  const t1 = process.hrtime.bigint();
  const seconds = Number(t1 - t0) / 1e9;

  if (unsafeRolloverCommits !== rounds)
    throw new Error(`unsafe rollover commits=${unsafeRolloverCommits}/${rounds}`);
  if (strictRolloverCommits !== 0)
    throw new Error(`strict rollover commits=${strictRolloverCommits}`);
  if (strictStableCommits !== rounds)
    throw new Error(`strict stable commits=${strictStableCommits}/${rounds}`);
  if (strictFreshRetryCommits !== rounds)
    throw new Error(`strict fresh retry commits=${strictFreshRetryCommits}/${rounds}`);
  pass++;

  console.log(`NODE=${process.version}`);
  console.log(`WASM_ENGINE=V8 WebAssembly`);
  console.log(`PASS_ASSERT_GROUPS=${pass}`);
  console.log(`INFLIGHT_FENCE_ROLLOVER=REPRODUCED`);
  console.log(`STRESS_ROUNDS=${rounds}`);
  console.log(`EPOCH_ROLLOVERS=${epochRollover}`);
  console.log(`DIGEST_ONLY_ROLLOVERS=${digestRollover}`);
  console.log(`UNSAFE_INFLIGHT_ROLLOVER_COMMITS=${unsafeRolloverCommits}`);
  console.log(`STRICT_INFLIGHT_ROLLOVER_COMMITS=${strictRolloverCommits}`);
  console.log(`STRICT_STABLE_COMMITS=${strictStableCommits}`);
  console.log(`STRICT_FRESH_RETRY_COMMITS=${strictFreshRetryCommits}`);
  console.log(`A_FINAL=${aWins}`);
  console.log(`B_FINAL=${bWins}`);
  console.log(`SECONDS=${seconds.toFixed(6)}`);
  console.log(`ROUNDS_PER_SEC=${Math.round(rounds/seconds)}`);
  console.log(`RESULT=xe / PREPARE-THEN-ROLLOVER TOCTOU FAIL`);
  console.log(`RESULT2=0e / FINAL-FENCE RECHECK BEFORE PARENT-CONSUME PASS`);
})();
