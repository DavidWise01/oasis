
const fs = require('fs');
const bytes = fs.readFileSync('/mnt/data/ringyboxy_kernel_v8.wasm');

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

  // 1) Reproduce unsafe crash window:
  // A consumes parent, process crashes before ACK, recovery trusts ACK absence
  // and therefore boots empty. B can now consume the same parent.
  {
    w.boot_empty();
    if (w.commit_no_ack(1, 1001) !== 1) throw new Error('unsafe initial A commit failed');

    // crash before ACK; broken recovery infers "no ACK => no commit"
    w.boot_empty();

    if (w.commit_no_ack(2, 2002) !== 1 || w.committed_child_state() !== 2)
      throw new Error('unsafe ACK-window fork not reproduced');
    pass++;
  }

  // 2) Strict recovery: durable A commit is restored before serving work.
  {
    w.boot_empty();
    if (w.commit_no_ack(1, 3003) !== 1) throw new Error('strict initial A failed');

    // External durable ledger snapshot at commit point:
    const durableChild = w.committed_child_state();
    const durableTxid = w.committed_txid_state();

    // crash before ACK
    w.boot_empty();

    // recovery uses durable commit, not ACK state
    if (w.restore_commit(durableChild, durableTxid) !== 1)
      throw new Error('strict restore failed');

    if (w.commit_no_ack(2, 4004) !== 0)
      throw new Error('sibling committed after durable restore');

    // exact replay of original transaction is idempotently accepted
    if (w.commit_no_ack(1, 3003) !== 1)
      throw new Error('exact replay failed');

    if (w.ack_commit(3003) !== 1 || w.ack_txid_state() !== 3003)
      throw new Error('ACK after recovery failed');
    pass++;
  }

  // 3) Same child but different txid is not an exact replay.
  {
    w.boot_empty();
    w.commit_no_ack(1, 5005);
    if (w.commit_no_ack(1, 5006) !== 0)
      throw new Error('same-child different-txid was treated as replay');
    pass++;
  }

  // 4) ACK mismatch cannot rewrite canonical commit identity.
  {
    w.boot_empty();
    w.commit_no_ack(2, 6006);
    if (w.ack_commit(7007) !== 0)
      throw new Error('foreign ACK accepted');
    if (w.committed_child_state() !== 2 || w.committed_txid_state() !== 6006)
      throw new Error('foreign ACK mutated commit');
    pass++;
  }

  const rounds = 500000;
  const rand = rng(0xACCA11ED);

  let unsafeForks = 0;
  let strictSiblingEscapes = 0;
  let strictExactReplayFailures = 0;
  let strictAckFailures = 0;
  let aFirst = 0;
  let bFirst = 0;

  const t0 = process.hrtime.bigint();

  for (let i = 0; i < rounds; i++) {
    const first = (rand() & 1) ? 1 : 2;
    const sibling = first === 1 ? 2 : 1;
    if (first === 1) aFirst++; else bFirst++;

    const txid = ((rand() | 1) >>> 0) || 1;
    const siblingTxid = ((rand() | 1) >>> 0) || 3;

    // UNSAFE: commit happens, crash before ACK, recovery boots empty.
    w.boot_empty();
    if (w.commit_no_ack(first, txid) !== 1)
      throw new Error('unsafe stress initial commit failed');

    w.boot_empty(); // broken ACK-derived recovery
    if (w.commit_no_ack(sibling, siblingTxid) === 1)
      unsafeForks++;

    // STRICT: snapshot durable commit immediately after commit.
    w.boot_empty();
    if (w.commit_no_ack(first, txid) !== 1)
      throw new Error('strict stress initial commit failed');

    const durableChild = w.committed_child_state();
    const durableTxid = w.committed_txid_state();

    // Crash before ACK.
    w.boot_empty();

    if (w.restore_commit(durableChild, durableTxid) !== 1)
      throw new Error('strict stress restore failed');

    if (w.commit_no_ack(sibling, siblingTxid) === 1)
      strictSiblingEscapes++;

    if (w.commit_no_ack(first, txid) !== 1)
      strictExactReplayFailures++;

    if (w.ack_commit(txid) !== 1)
      strictAckFailures++;
  }

  const t1 = process.hrtime.bigint();
  const seconds = Number(t1 - t0) / 1e9;

  if (unsafeForks !== rounds)
    throw new Error(`unsafe forks=${unsafeForks}/${rounds}`);
  if (strictSiblingEscapes !== 0)
    throw new Error(`strict sibling escapes=${strictSiblingEscapes}`);
  if (strictExactReplayFailures !== 0)
    throw new Error(`strict replay failures=${strictExactReplayFailures}`);
  if (strictAckFailures !== 0)
    throw new Error(`strict ACK failures=${strictAckFailures}`);

  pass++;

  console.log(`NODE=${process.version}`);
  console.log(`WASM_ENGINE=V8 WebAssembly`);
  console.log(`PASS_ASSERT_GROUPS=${pass}`);
  console.log(`POST-COMMIT_PRE-ACK_CRASH=REPRODUCED`);
  console.log(`STRESS_ROUNDS=${rounds}`);
  console.log(`UNSAFE_ACK_DERIVED_RECOVERY_FORKS=${unsafeForks}`);
  console.log(`STRICT_SIBLING_ESCAPES=${strictSiblingEscapes}`);
  console.log(`STRICT_EXACT_REPLAY_FAILURES=${strictExactReplayFailures}`);
  console.log(`STRICT_ACK_FAILURES=${strictAckFailures}`);
  console.log(`A_FIRST=${aFirst}`);
  console.log(`B_FIRST=${bFirst}`);
  console.log(`SECONDS=${seconds.toFixed(6)}`);
  console.log(`ROUNDS_PER_SEC=${Math.round(rounds/seconds)}`);
  console.log(`RESULT=xe / ACK-AS-COMMIT-TRUTH RECOVERY FAIL`);
  console.log(`RESULT2=0e / DURABLE-COMMIT-FIRST + IDEMPOTENT-ACK PASS`);
})();
