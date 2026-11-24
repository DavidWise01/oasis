/** AETHER-174: synthetic same-path uncertainty adjudicator; never authorizes hardware. */
export function assess(packet, context = {}) {
  const reasons = [];
  const add = (r) => reasons.push(r);
  const finish = () => ({
    status: reasons.length ? 'REJECT' : 'DOCUMENTARY_REVIEW_ONLY',
    reasons: [...new Set(reasons)].sort(),
    operational_authority: 'HOLD', physical_qualification_percent: 0,
    physical_act_allowed: false
  });
  if (!packet || !Array.isArray(packet.pairs) || packet.pairs.length === 0) {
    add('MISSING_MEASUREMENT_PAIRS'); return finish();
  }
  if (packet.device_serial !== context.expected_device_serial) add('DUT_IDENTITY_MISMATCH');
  if (packet.reference_serial !== context.expected_reference_serial) add('REFERENCE_IDENTITY_MISMATCH');
  if (packet.bench_serial !== context.expected_bench_serial) add('BENCH_IDENTITY_MISMATCH');
  if (!packet.challenge_nonce || packet.challenge_nonce !== context.expected_nonce) add('CHALLENGE_BINDING_FAILED');
  if (!packet.injection_port || packet.injection_port !== context.expected_injection_port ||
      !packet.capture_route || packet.capture_route !== context.expected_capture_route) add('SAME_PATH_NOT_ESTABLISHED');
  if (!/^[a-f0-9]{64}$/i.test(packet.original_capture_sha256 || '')) add('MISSING_ORIGINAL_CAPTURE_DIGEST');
  if (!/^[a-f0-9]{64}$/i.test(packet.reference_capture_sha256 || '')) add('MISSING_REFERENCE_CAPTURE_DIGEST');
  if (!Number.isFinite(context.max_expanded_error) || context.max_expanded_error < 0) add('MISSING_APPROVED_TOLERANCE');
  if (!Number.isFinite(context.max_delay_ms) || context.max_delay_ms <= 0) add('MISSING_APPROVED_DELAY_LIMIT');
  const observed = [];
  let previousTick = -1, previousTime = -Infinity;
  for (const p of packet.pairs) {
    if (!p || !Number.isSafeInteger(p.tick) || !Number.isFinite(p.time_ms) ||
        !Number.isFinite(p.dut) || !Number.isFinite(p.reference) || !Number.isFinite(p.bench) ||
        !Number.isFinite(p.delay_ms)) { add('MALFORMED_MEASUREMENT'); continue; }
    if (p.tick <= previousTick || p.time_ms <= previousTime) add('NONMONOTONIC_ACQUISITION');
    previousTick = p.tick; previousTime = p.time_ms;
    if (p.delay_ms < 0 || p.delay_ms > context.max_delay_ms) add('RESPONSE_DELAY_OUT_OF_BOUNDS');
    const u = p.standard_uncertainty;
    if (!u || !['calibration','repeatability','resolution','drift'].every(k => Number.isFinite(u[k]) && u[k] >= 0)) {
      add('INVALID_UNCERTAINTY_COMPONENTS'); continue;
    }
    if (!Number.isFinite(p.coverage_factor) || p.coverage_factor <= 0 || p.coverage_factor > 4) {
      add('INVALID_COVERAGE_FACTOR'); continue;
    }
    const combined = Math.hypot(u.calibration, u.repeatability, u.resolution, u.drift);
    const expanded = combined * p.coverage_factor;
    const dutResidual = Math.abs(p.dut - p.reference);
    const benchResidual = Math.abs(p.bench - p.reference);
    observed.push({tick:p.tick, dut_residual:dutResidual, bench_residual:benchResidual, expanded_uncertainty:expanded});
    if (dutResidual + expanded > context.max_expanded_error) add('DUT_INTERVAL_EXCEEDS_LIMIT');
    if (benchResidual + expanded > context.max_expanded_error) add('BENCH_INTERVAL_EXCEEDS_LIMIT');
    if (Math.abs(p.dut - p.bench) > context.max_expanded_error) add('BENCH_DISAGREEMENT');
  }
  if (context.original_captures_authenticated !== true) add('ORIGINAL_CAPTURES_UNAUTHENTICATED');
  if (context.calibration_ancestry_authenticated !== true) add('CALIBRATION_ANCESTRY_UNAUTHENTICATED');
  if (context.independent_reference_authenticated !== true) add('REFERENCE_INDEPENDENCE_UNAUTHENTICATED');
  const result = finish();
  result.diagnostic = observed; // numerical diagnostics: model data only
  return result;
}
