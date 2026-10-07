const fs = require('fs');
const bytes = fs.readFileSync('/mnt/data/ringyboxy_kernel_v5.wasm');

async function fresh() {
  const m = await WebAssembly.instantiate(bytes, {});
  return m.instance.exports;
}

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
  let pass = 0;

  const CANON_EPOCH = 8;
  const CANON_DIGEST = 0x8A11CE01 >>> 0;

  {
    const left = await fresh();
    const right = await fresh();
    left.boot(); right.boot();

    left.install_snapshot(7, 0, 0x71110000);
    right.install_snapshot(CANON_EPOCH, 1, CANON_DIGEST);

    if (left.finish_recovery_fenced(7, 0x71110000) !== 1) throw new Error('left local open failed');
    if (right.finish_recovery_fenced(CANON_EPOCH, CANON_DIGEST) !== 1) throw new Error('right local open failed');

    const b = left.try_commit(2, 2, 3, 1, 1);
    const a = right.try_commit(1, 1, 3, 1, 1);

    if (b !== 1 || a !== 1 || left.state() !== 2 || right.state() !== 1)
      throw new Error('stale-snapshot fork not reproduced');
    pass++;
  }

  {
    const left = await fresh();
    const right = await fresh();
    left.boot(); right.boot();

    left.install_snapshot(7, 0, 0x71110000);
    right.install_snapshot(CANON_EPOCH, 1, CANON_DIGEST);

    if (left.finish_recovery_fenced(CANON_EPOCH, CANON_DIGEST) !== 0)
      throw new Error('stale replica opened');
    if (left.phase_state() !== 0)
      throw new Error('stale replica phase escaped CLOSED');
    if (left.try_commit(2, 2, 3, 1, 1) !== 0)
      throw new Error('stale replica committed while fenced');

    if (right.finish_recovery_fenced(CANON_EPOCH, CANON_DIGEST) !== 1)
      throw new Error('canonical replica failed to open');
    if (right.try_commit(2, 2, 3, 1, 1) !== 0)
      throw new Error('canonical replica accepted sibling');
    pass++;
  }

  {
    const w = await fresh();
    w.boot();
    w.install_snapshot(CANON_EPOCH, 0, 0xDEADBEEF);
    if (w.finish_recovery_fenced(CANON_EPOCH, CANON_DIGEST) !== 0)
      throw new Error('same-epoch wrong-digest opened');
    pass++;
  }

  {
    const w = await fresh();
    w.boot();
    w.install_snapshot(7, 0, 0x71110000);
    if (w.finish_recovery_fenced(CANON_EPOCH, CANON_DIGEST) !== 0)
      throw new Error('unexpected stale open');
    if (w.install_snapshot(CANON_EPOCH, 1, CANON_DIGEST) !== 1)
      throw new Error('canonical refresh failed');
    if (w.finish_recovery_fenced(CANON_EPOCH, CANON_DIGEST) !== 1)
      throw new Error('canonical refreshed open failed');
    if (w.try_commit(2, 2, 3, 1, 1) !== 0)
      throw new Error('sibling accepted after canonical refresh');
    pass++;
  }

  const rounds = 150000;
  const rand = rng(0x51A9E5E);
  let unsafeForks = 0;
  let strictStaleOpens = 0;
  let strictStaleCommits = 0;
  let strictCanonicalSiblingCommits = 0;
  let epochMismatchCases = 0;
  let digestMismatchCases = 0;

  const t0 = process.hrtime.bigint();

  for (let i = 0; i < rounds; i++) {
    const winner = (rand() & 1) ? 1 : 2;
    const sibling = winner === 1 ? 2 : 1;

    const canonEpoch = 100 + (rand() % 1000000);
    const canonDigest = (0xA5000000 ^ rand()) >>> 0;

    const mismatchType = rand() & 1;
    const staleEpoch = mismatchType === 0 ? canonEpoch - 1 : canonEpoch;
    const staleDigest = mismatchType === 0 ? (canonDigest ^ 0x01010101) >>> 0
                                           : (canonDigest ^ 0x00010001) >>> 0;
    if (staleEpoch !== canonEpoch) epochMismatchCases++;
    else digestMismatchCases++;

    {
      const stale = await fresh();
      const canon = await fresh();
      stale.boot(); canon.boot();

      stale.install_snapshot(staleEpoch, 0, staleDigest);
      canon.install_snapshot(canonEpoch, winner, canonDigest);

      stale.finish_recovery_fenced(staleEpoch, staleDigest);
      canon.finish_recovery_fenced(canonEpoch, canonDigest);

      const sr = stale.try_commit(sibling, sibling, 3, 1, 1);
      const cr = canon.try_commit(winner, winner, 3, 1, 1);
      if (sr === 1 && cr === 1 && stale.state() === sibling && canon.state() === winner)
        unsafeForks++;
    }

    {
      const stale = await fresh();
      const canon = await fresh();
      stale.boot(); canon.boot();

      stale.install_snapshot(staleEpoch, 0, staleDigest);
      canon.install_snapshot(canonEpoch, winner, canonDigest);

      if (stale.finish_recovery_fenced(canonEpoch, canonDigest) === 1)
        strictStaleOpens++;
      if (stale.try_commit(sibling, sibling, 3, 1, 1) === 1)
        strictStaleCommits++;

      if (canon.finish_recovery_fenced(canonEpoch, canonDigest) !== 1)
        throw new Error('canonical stress replica failed to open');
      if (canon.try_commit(sibling, sibling, 3, 1, 1) === 1)
        strictCanonicalSiblingCommits++;
    }
  }

  const t1 = process.hrtime.bigint();
  const seconds = Number(t1 - t0) / 1e9;

  if (unsafeForks !== rounds) throw new Error(`unsafe forks=${unsafeForks}/${rounds}`);
  if (strictStaleOpens !== 0) throw new Error(`strict stale opens=${strictStaleOpens}`);
  if (strictStaleCommits !== 0) throw new Error(`strict stale commits=${strictStaleCommits}`);
  if (strictCanonicalSiblingCommits !== 0) throw new Error(`strict canonical sibling commits=${strictCanonicalSiblingCommits}`);
  pass++;

  console.log(`NODE=${process.version}`);
  console.log(`WASM_ENGINE=V8 WebAssembly`);
  console.log(`PASS_ASSERT_GROUPS=${pass}`);
  console.log(`DIVERGENT_RECOVERY_SNAPSHOT_FORK=REPRODUCED`);
  console.log(`STRESS_ROUNDS=${rounds}`);
  console.log(`EPOCH_MISMATCH_CASES=${epochMismatchCases}`);
  console.log(`DIGEST_MISMATCH_CASES=${digestMismatchCases}`);
  console.log(`UNSAFE_LOCAL_SNAPSHOT_FORKS=${unsafeForks}`);
  console.log(`STRICT_STALE_REPLICA_OPENS=${strictStaleOpens}`);
  console.log(`STRICT_STALE_REPLICA_COMMITS=${strictStaleCommits}`);
  console.log(`STRICT_CANONICAL_SIBLING_COMMITS=${strictCanonicalSiblingCommits}`);
  console.log(`SECONDS=${seconds.toFixed(6)}`);
  console.log(`ROUNDS_PER_SEC=${Math.round(rounds/seconds)}`);
  console.log(`RESULT=xe / LOCAL RECOVERY-SNAPSHOT AUTHORITY FAIL`);
  console.log(`RESULT2=0e / COMMON EPOCH+DIGEST FENCE PASS`);
})();
