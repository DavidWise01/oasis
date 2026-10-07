const fs = require('fs');
const bytes = fs.readFileSync('/mnt/data/ringyboxy_kernel_v6.wasm');

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
  if (w.install_canonical_fence(10, 0xAAA00010) !== 1) throw new Error('install N failed');
  if (w.open_replica(10, 0xAAA00010) !== 1) throw new Error('open N failed');
  if (w.install_canonical_fence(11, 0xBBB00011) !== 1) throw new Error('rollover failed');
  if (w.try_commit_unsafe(1, 1, 3, 1, 1) !== 1 || w.state() !== 1)
    throw new Error('stale-open exploit not reproduced');
  pass++;

  w.reset();
  w.install_canonical_fence(20, 0xAAA00020);
  w.open_replica(20, 0xAAA00020);
  w.install_canonical_fence(21, 0xBBB00021);
  if (w.try_commit_strict(1, 1, 3, 1, 1) !== 0 || w.state() !== 0)
    throw new Error('strict stale lease committed');
  pass++;

  if (w.refresh_replica(21, 0xBBB00021) !== 1) throw new Error('refresh failed');
  if (w.try_commit_strict(1, 1, 3, 1, 1) !== 1 || w.state() !== 1)
    throw new Error('fresh lease failed');
  pass++;

  w.reset();
  w.install_canonical_fence(30, 0x12345678);
  if (w.open_replica(30, 0x12345678) !== 1) throw new Error('open 30 failed');
  w.install_canonical_fence(30, 0x87654321);
  if (w.refresh_replica(30, 0x12345678) !== 0)
    throw new Error('wrong digest refreshed');
  if (w.try_commit_strict(2, 2, 3, 1, 1) !== 0)
    throw new Error('same-epoch stale digest committed');
  pass++;

  if (w.install_canonical_fence(29, 0x11111111) !== 0)
    throw new Error('canonical epoch rollback accepted');
  pass++;

  const rounds = 500000;
  const rand = rng(0xFECE006);
  let unsafeStaleCommits = 0;
  let strictStaleCommits = 0;
  let strictFreshCommits = 0;
  let epochRollovers = 0;
  let digestOnlyRollovers = 0;
  let aWins = 0, bWins = 0;

  const t0 = process.hrtime.bigint();

  for (let i = 0; i < rounds; i++) {
    const child = (rand() & 1) ? 1 : 2;
    const baseEpoch = 1000 + (rand() % 1000000);
    const baseDigest = (0xA0000000 ^ rand()) >>> 0;
    const mode = rand() & 1;

    const nextEpoch = mode === 0 ? baseEpoch + 1 : baseEpoch;
    const nextDigest = (baseDigest ^ (mode === 0 ? 0x01000101 : 0x00010001)) >>> 0;
    if (mode === 0) epochRollovers++; else digestOnlyRollovers++;

    w.reset();
    w.install_canonical_fence(baseEpoch, baseDigest);
    w.open_replica(baseEpoch, baseDigest);
    w.install_canonical_fence(nextEpoch, nextDigest);
    if (w.try_commit_unsafe(child, child, 3, 1, 1) === 1)
      unsafeStaleCommits++;

    w.reset();
    w.install_canonical_fence(baseEpoch, baseDigest);
    w.open_replica(baseEpoch, baseDigest);
    w.install_canonical_fence(nextEpoch, nextDigest);

    if (w.try_commit_strict(child, child, 3, 1, 1) === 1)
      strictStaleCommits++;

    if (w.refresh_replica(nextEpoch, nextDigest) !== 1)
      throw new Error('stress refresh failed');
    if (w.try_commit_strict(child, child, 3, 1, 1) === 1) {
      strictFreshCommits++;
      if (child === 1) aWins++; else bWins++;
    }
  }

  const t1 = process.hrtime.bigint();
  const seconds = Number(t1 - t0) / 1e9;

  if (unsafeStaleCommits !== rounds)
    throw new Error(`unsafe stale commits=${unsafeStaleCommits}/${rounds}`);
  if (strictStaleCommits !== 0)
    throw new Error(`strict stale commits=${strictStaleCommits}`);
  if (strictFreshCommits !== rounds)
    throw new Error(`strict fresh commits=${strictFreshCommits}/${rounds}`);
  pass++;

  console.log(`NODE=${process.version}`);
  console.log(`WASM_ENGINE=V8 WebAssembly`);
  console.log(`PASS_ASSERT_GROUPS=${pass}`);
  console.log(`STALE_OPEN_FENCE_ROLLOVER=REPRODUCED`);
  console.log(`STRESS_ROUNDS=${rounds}`);
  console.log(`EPOCH_ROLLOVERS=${epochRollovers}`);
  console.log(`DIGEST_ONLY_ROLLOVERS=${digestOnlyRollovers}`);
  console.log(`UNSAFE_STALE_LEASE_COMMITS=${unsafeStaleCommits}`);
  console.log(`STRICT_STALE_LEASE_COMMITS=${strictStaleCommits}`);
  console.log(`STRICT_FRESH_LEASE_COMMITS=${strictFreshCommits}`);
  console.log(`A_FINAL=${aWins}`);
  console.log(`B_FINAL=${bWins}`);
  console.log(`SECONDS=${seconds.toFixed(6)}`);
  console.log(`ROUNDS_PER_SEC=${Math.round(rounds/seconds)}`);
  console.log(`RESULT=xe / STALE OPEN LEASE AFTER FENCE ROLLOVER FAIL`);
  console.log(`RESULT2=0e / PER-COMMIT EPOCH+DIGEST FENCING PASS`);
})();
