import { assess } from './verification.mjs';
const hash = x => x.repeat(64);
const goodPair = () => ({tick:0,time_ms:100,dut:1.0001,reference:1,bench:1.0001,delay_ms:10,
  coverage_factor:2,standard_uncertainty:{calibration:.001,repeatability:.0005,resolution:.0004,drift:.0006}});
const good = () => ({device_serial:'DUT',reference_serial:'REF',bench_serial:'BENCH',challenge_nonce:'nonce',
  injection_port:'port',capture_route:'route',original_capture_sha256:hash('a'),reference_capture_sha256:hash('b'),pairs:[goodPair(),{...goodPair(),tick:1,time_ms:110}]});
const ctx = {expected_device_serial:'DUT',expected_reference_serial:'REF',expected_bench_serial:'BENCH',expected_nonce:'nonce',
  expected_injection_port:'port',expected_capture_route:'route',max_expanded_error:.025,max_delay_ms:50,
  original_captures_authenticated:false,calibration_ancestry_authenticated:false,independent_reference_authenticated:false};
const edit=f=>{let p=good();f(p);return p};
const cases = [
 ['absent packet',null,'MISSING_MEASUREMENT_PAIRS'],
 ['wrong device',edit(p=>p.device_serial='DUT-2'),'DUT_IDENTITY_MISMATCH'],
 ['wrong reference',edit(p=>p.reference_serial='REF-2'),'REFERENCE_IDENTITY_MISMATCH'],
 ['wrong bench',edit(p=>p.bench_serial='BENCH-2'),'BENCH_IDENTITY_MISMATCH'],
 ['replayed nonce',edit(p=>p.challenge_nonce='replay'),'CHALLENGE_BINDING_FAILED'],
 ['wrong injection port',edit(p=>p.injection_port='other'),'SAME_PATH_NOT_ESTABLISHED'],
 ['bad capture hash',edit(p=>p.original_capture_sha256='bad'),'MISSING_ORIGINAL_CAPTURE_DIGEST'],
 ['nonmonotonic clock',edit(p=>p.pairs[1].time_ms=99),'NONMONOTONIC_ACQUISITION'],
 ['negative delay',edit(p=>p.pairs[0].delay_ms=-1),'RESPONSE_DELAY_OUT_OF_BOUNDS'],
 ['late response',edit(p=>p.pairs[0].delay_ms=51),'RESPONSE_DELAY_OUT_OF_BOUNDS'],
 ['invalid uncertainty',edit(p=>p.pairs[0].standard_uncertainty.calibration=-1),'INVALID_UNCERTAINTY_COMPONENTS'],
 ['invalid coverage factor',edit(p=>p.pairs[0].coverage_factor=0),'INVALID_COVERAGE_FACTOR'],
 ['DUT outside tolerance',edit(p=>p.pairs[0].dut=1.1),'DUT_INTERVAL_EXCEEDS_LIMIT'],
 ['bench outside tolerance',edit(p=>p.pairs[0].bench=1.1),'BENCH_INTERVAL_EXCEEDS_LIMIT'],
 ['bench contradiction',edit(p=>p.pairs[0].bench=1.1),'BENCH_DISAGREEMENT'],
 ['missing tolerance',good(),'MISSING_APPROVED_TOLERANCE',{max_expanded_error:undefined}],
 ['missing delay limit',good(),'MISSING_APPROVED_DELAY_LIMIT',{max_delay_ms:undefined}],
 ['unverified original capture',good(),'ORIGINAL_CAPTURES_UNAUTHENTICATED'],
 ['unverified calibration',good(),'CALIBRATION_ANCESTRY_UNAUTHENTICATED'],
 ['unverified independence',good(),'REFERENCE_INDEPENDENCE_UNAUTHENTICATED']
];
let passed=0;
for (const [name,p,reason,overrides] of cases) {
  const r=assess(p,{...ctx,...overrides});
  if (!r.reasons.includes(reason) || r.operational_authority!=='HOLD' || r.physical_act_allowed!==false) throw Error(name+': '+JSON.stringify(r));
  passed++;
}
const fake=assess(good(),{...ctx,original_captures_authenticated:true,calibration_ancestry_authenticated:true,independent_reference_authenticated:true});
if(fake.status!=='DOCUMENTARY_REVIEW_ONLY' || fake.operational_authority!=='HOLD' || fake.physical_act_allowed) throw Error('false physical authorization');
passed++;
console.log('AETHER-174 '+passed+'/21 synthetic checks PASS. Physical 0%, ACT HOLD.');
