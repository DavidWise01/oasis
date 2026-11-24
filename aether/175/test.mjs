import {assess} from './verification.mjs';
const H=x=>x.repeat(64);
const base=()=>({device_serial:'DUT',reference_serial:'REF',challenge_nonce:'N',clock_source_id:'CLOCK',dut_capture_sha256:H('a'),reference_capture_sha256:H('b'),alarm_capture_sha256:H('c'),samples:[{counter:1,time_ms:1000,dut:1,reference:1},{counter:2,time_ms:1100,dut:1.001,reference:1},{counter:3,time_ms:1200,dut:1.002,reference:1}],alarms:[]});
const policy={expected_device_serial:'DUT',expected_reference_serial:'REF',expected_nonce:'N',expected_clock_source:'CLOCK',max_drift_per_second:.05,alarm_threshold:.025,max_alarm_delay_ms:50,original_trace_authenticated:false,clock_calibration_authenticated:false,reference_independence_authenticated:false,physical_alarm_issuance_authenticated:false};
const edit=f=>{const x=base();f(x);return x};
const cases=[
['missing',null,'MISSING_DRIFT_TRACE'],
['DUT',edit(x=>x.device_serial='fake'),'INVALID_DEVICE_SERIAL'],
['REF',edit(x=>x.reference_serial='fake'),'INVALID_REFERENCE_SERIAL'],
['nonce',edit(x=>x.challenge_nonce='replay'),'INVALID_CHALLENGE_NONCE'],
['clock',edit(x=>x.clock_source_id='wrong'),'INVALID_CLOCK_SOURCE_ID'],
['DUT hash',edit(x=>x.dut_capture_sha256='x'),'INVALID_DUT_CAPTURE_SHA256'],
['REF hash',edit(x=>x.reference_capture_sha256='x'),'INVALID_REFERENCE_CAPTURE_SHA256'],
['alarm hash',edit(x=>x.alarm_capture_sha256='x'),'INVALID_ALARM_CAPTURE_SHA256'],
['drift limit',base(),'NO_APPROVED_DRIFT_LIMIT',{max_drift_per_second:undefined}],
['deadline',base(),'NO_APPROVED_ALARM_DEADLINE',{max_alarm_delay_ms:undefined}],
['threshold',base(),'NO_APPROVED_ALARM_THRESHOLD',{alarm_threshold:undefined}],
['alarm absent',edit(x=>x.alarms=null),'MISSING_ALARM_EVENT_LIST'],
['counter gap',edit(x=>x.samples[1].counter=7),'COUNTER_GAP'],
['clock rollback',edit(x=>x.samples[1].time_ms=999),'CLOCK_ROLLBACK'],
['drift',edit(x=>x.samples[1].dut=1.2),'DRIFT_LIMIT_EXCEEDED'],
['suppressed',edit(x=>x.samples[1].dut=1.1),'SUPPRESSED_ALARM'],
['delayed',edit(x=>{x.samples[1].dut=1.1;x.alarms=[{source_counter:2,issued_time_ms:1200,event_id:'alarm-2'}]}),'DELAYED_ALARM'],
['pre-trigger',edit(x=>{x.samples[1].dut=1.1;x.alarms=[{source_counter:2,issued_time_ms:1050,event_id:'alarm-2'}]}),'ALARM_PRECEDES_TRIGGER'],
['duplicate id',edit(x=>x.alarms=[{source_counter:2,issued_time_ms:1100,event_id:'a'},{source_counter:3,issued_time_ms:1200,event_id:'a'}]),'DUPLICATE_ALARM_EVENT_ID'],
['double trigger alarm',edit(x=>{x.samples[1].dut=1.1;x.alarms=[{source_counter:2,issued_time_ms:1110,event_id:'a'},{source_counter:2,issued_time_ms:1120,event_id:'b'}]}),'DUPLICATE_ALARM_FOR_TRIGGER'],
['original unverified',base(),'ORIGINAL_TRACE_UNAUTHENTICATED'],
['clock unverified',base(),'CLOCK_UNAUTHENTICATED'],
['reference unverified',base(),'REFERENCE_UNAUTHENTICATED'],
['physical alarm unverified',base(),'ALARM_ISSUANCE_UNAUTHENTICATED']
];
let passed=0;for(const [label,p,expected,overrides] of cases){const r=assess(p,{...policy,...overrides});if(!r.reasons.includes(expected)||r.operational_authority!=='HOLD'||r.physical_act_allowed)throw Error('FAIL '+label+' '+JSON.stringify(r));passed++}
const spoof=assess(base(),{...policy,original_trace_authenticated:true,clock_calibration_authenticated:true,reference_independence_authenticated:true,physical_alarm_issuance_authenticated:true});
if(spoof.status!=='DOCUMENTARY_REVIEW_ONLY'||spoof.operational_authority!=='HOLD'||spoof.physical_act_allowed)throw Error('false physical authority');
passed++;console.log('AETHER-175 '+passed+'/25 synthetic tests PASS, 0 physical samples, ACT HOLD.');
