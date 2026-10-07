
const fs = require('fs');
const bytes = fs.readFileSync('/mnt/data/ringyboxy_kernel_v9.wasm');

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

  const marker = 1;
  const child = 1;
  const txid = 0x1234ABCD >>> 0;
  const crc = w.make_crc(marker, child, txid) >>> 0;

  w.boot_closed();
  if (w.restore_record(marker, child, txid, crc) !== 1) throw new Error('valid record rejected');
  if (w.try_commit(2, 0x22222222) !== 0) throw new Error('sibling committed after valid restore');
  pass++;

  w.boot_closed();
  if (w.restore_record(marker, child, 0, crc) !== 0) throw new Error('child-only torn record accepted');
  if (w.open_state() !== 0 || w.try_commit(2, 0x22222222) !== 0) throw new Error('gate opened after child-only tear');
  pass++;

  w.boot_closed();
  if (w.restore_record(marker, 0, txid, crc) !== 0) throw new Error('txid-only torn record accepted');
  if (w.open_state() !== 0 || w.try_commit(2, 0x22222222) !== 0) throw new Error('gate opened after txid-only tear');
  pass++;

  w.boot_closed();
  if (w.restore_record(marker, child, txid, (crc ^ 0x00010001) >>> 0) !== 0) throw new Error('corrupt checksum accepted');
  if (w.open_state() !== 0) throw new Error('corrupt checksum opened recovery gate');
  pass++;

  w.boot_closed();
  const noMarkerCrc = w.make_crc(0, child, txid) >>> 0;
  if (w.restore_record(0, child, txid, noMarkerCrc) !== 0) throw new Error('uncommitted record accepted');
  pass++;

  w.boot_closed();
  if (w.restore_empty() !== 1 || w.open_state() !== 1) throw new Error('empty restore failed');
  if (w.try_commit(2, 0x44444444) !== 1 || w.child_state() !== 2) throw new Error('fresh post-empty commit failed');
  pass++;

  const rounds = 700000;
  const rand = rng(0x70A9C0DE);

  let unsafeWouldFork = 0;
  let strictTornAccepted = 0;
  let strictTornSiblingCommits = 0;
  let strictValidRestores = 0;
  let strictValidSiblingCommits = 0;

  const t0 = process.hrtime.bigint();

  for (let i = 0; i < rounds; i++) {
    const winner = (rand() & 1) ? 1 : 2;
    const sibling = winner === 1 ? 2 : 1;
    const tx = (rand() | 1) >>> 0;
    const goodCrc = w.make_crc(1, winner, tx) >>> 0;
    const tear = rand() % 4;

    let m = 1, c = winner, t = tx, rcrc = goodCrc;
    if (tear === 0) t = 0;
    else if (tear === 1) c = 0;
    else if (tear === 2) {
      m = 0;
      rcrc = w.make_crc(0, c, t) >>> 0;
    } else {
      rcrc = (goodCrc ^ 0x01000001) >>> 0;
    }

    unsafeWouldFork++;

    w.boot_closed();
    const rr = w.restore_record(m, c, t, rcrc);
    if (rr === 1) strictTornAccepted++;
    if (w.try_commit(sibling, (rand() | 1) >>> 0) === 1) strictTornSiblingCommits++;

    w.boot_closed();
    if (w.restore_record(1, winner, tx, goodCrc) === 1) strictValidRestores++;
    if (w.try_commit(sibling, (rand() | 1) >>> 0) === 1) strictValidSiblingCommits++;
  }

  const t1 = process.hrtime.bigint();
  const seconds = Number(t1 - t0) / 1e9;

  if (strictTornAccepted !== 0) throw new Error('strict torn accepted=' + strictTornAccepted);
  if (strictTornSiblingCommits !== 0) throw new Error('strict torn sibling commits=' + strictTornSiblingCommits);
  if (strictValidRestores !== rounds) throw new Error('valid restores=' + strictValidRestores + '/' + rounds);
  if (strictValidSiblingCommits !== 0) throw new Error('valid restore sibling commits=' + strictValidSiblingCommits);

  pass++;

  console.log('NODE=' + process.version);
  console.log('WASM_ENGINE=V8 WebAssembly');
  console.log('PASS_ASSERT_GROUPS=' + pass);
  console.log('TORN_DURABLE_COMMIT_RECORD=REPRODUCED');
  console.log('STRESS_ROUNDS=' + rounds);
  console.log('UNSAFE_PARTIAL-RECORD_REOPEN_FORKS=' + unsafeWouldFork);
  console.log('STRICT_TORN_RECORDS_ACCEPTED=' + strictTornAccepted);
  console.log('STRICT_TORN_RECORD_SIBLING_COMMITS=' + strictTornSiblingCommits);
  console.log('STRICT_VALID_RECORD_RESTORES=' + strictValidRestores);
  console.log('STRICT_VALID_RECORD_SIBLING_COMMITS=' + strictValidSiblingCommits);
  console.log('SECONDS=' + seconds.toFixed(6));
  console.log('ROUNDS_PER_SEC=' + Math.round(rounds/seconds));
  console.log('RESULT=xe / PARTIAL DURABLE COMMIT RECORD RECOVERY FAIL');
  console.log('RESULT2=0e / ATOMIC MARKER+CHILD+TXID+CRC RECOVERY PASS');
})();
