import {adjudicate} from './verification.mjs';
const H=x=>x.repeat(64);
const base=()=>({instrument_serial:'REF-177',challenge_id:'C-177',source_origin_id:'outside-177',original_capture_sha256:H('a'),events:[
{sequence:0,time_ms:10,event_id:'e0',action:'ACQUIRE',custodian_id:'lab-A',receipt_id:'r0',event_sha256:H('0'),capture_sha256:H('a'),previous_event_sha256:null},
{sequence:1,time_ms:20,event_id:'e1',action:'TRANSFER',custodian_id:'lab-A',to_custodian_id:'lab-B',receipt_id:'r1',event_sha256:H('1'),capture_sha256:H('a'),previous_event_sha256:H('0')},
{sequence:2,time_ms:30,event_id:'e2',action:'RECEIVE',custodian_id:'lab-B',receipt_id:'r2',event_sha256:H('2'),capture_sha256:H('a'),previous_event_sha256:H('1')},
{sequence:3,time_ms:40,event_id:'e3',action:'SEAL',custodian_id:'lab-B',receipt_id:'r3',event_sha256:H('3'),capture_sha256:H('a'),previous_event_sha256:H('2')} ]});
const ctx={expected_instrument_serial:'REF-177',expected_challenge_id:'C-177',dut_owned_origin_id:'DUT-root',expected_role:'REFERENCE',independent_origin_authenticated:false,original_hardware_bytes_authenticated:false,external_custody_receipts_authenticated:false};
const edit=f=>{let p=base();f(p);return p};
const cases=[
['empty',null,'MISSING_CUSTODY_EVENTS'],
['bad capture digest',edit(p=>p.original_capture_sha256='bad'),'INVALID_ORIGINAL_CAPTURE_DIGEST'],
['wrong instrument',edit(p=>p.instrument_serial='DUT'),'INSTRUMENT_MISMATCH'],
['wrong challenge',edit(p=>p.challenge_id='replay'),'CHALLENGE_MISMATCH'],
['missing origin',edit(p=>p.source_origin_id=''),'MISSING_SOURCE_ORIGIN'],
['self-origin',edit(p=>p.source_origin_id='DUT-root'),'SELF_ORIGIN_REFERENCE'],
['no acquisition',edit(p=>p.events[0].action='TRANSFER'),'MISSING_INITIAL_ACQUISITION'],
['counter gap',edit(p=>p.events[1].sequence=4),'NONCONTIGUOUS_SEQUENCE'],
['time reversal',edit(p=>p.events[1].time_ms=9),'NONMONOTONIC_TIME'],
['duplicate event ID',edit(p=>p.events[1].event_id='e0'),'DUPLICATE_OR_MISSING_EVENT_ID'],
['replay receipt',edit(p=>p.events[1].receipt_id='r0'),'REPLAYED_RECEIPT'],
['missing custodian',edit(p=>p.events[1].custodian_id=''),'MISSING_CUSTODIAN'],
['invalid event hash',edit(p=>p.events[1].event_sha256='invalid'),'INVALID_EVENT_DIGEST'],
['capture substitution',edit(p=>p.events[1].capture_sha256=H('b')),'CAPTURE_SUBSTITUTION'],
['broken custody predecessor',edit(p=>p.events[1].previous_event_sha256=H('c')),'BROKEN_CUSTODY_LINK'],
['invalid first link',edit(p=>p.events[0].previous_event_sha256=H('a')),'INVALID_GENESIS_LINK'],
['wrong receiver',edit(p=>p.events[2].custodian_id='lab-C'),'TRANSFER_RECEIPT_MISMATCH'],
['orphan receive',edit(p=>p.events[1].action='RECEIVE'),'UNMATCHED_RECEIVE'],
['missing transfer receipt',edit(p=>p.events[2].action='SEAL'),'MISSING_TRANSFER_RECEIPT'],
['invalid transfer destination',edit(p=>p.events[1].to_custodian_id='lab-A'),'INVALID_TRANSFER_DESTINATION'],
['unsealed escrow',edit(p=>p.events[3].action='TRANSFER'),'UNSEALED_CUSTODY'],
['origin unverified',base(),'ORIGIN_NOT_INDEPENDENTLY_AUTHENTICATED'],
['physical bytes unverified',base(),'ORIGINAL_BYTES_NOT_AUTHENTICATED'],
['external receipts unverified',base(),'RECEIPTS_NOT_EXTERNALLY_AUTHENTICATED']];
let passed=0;
for(const [name,p,reason] of cases){const r=adjudicate(p,ctx);if(!r.reasons.includes(reason)||r.operational_authority!=='HOLD'||r.physical_act_allowed)throw Error('FAIL '+name+': '+JSON.stringify(r));passed++}
const spoof=adjudicate(base(),{...ctx,independent_origin_authenticated:true,original_hardware_bytes_authenticated:true,external_custody_receipts_authenticated:true});
if(spoof.status!=='DOCUMENTARY_REVIEW_ONLY'||spoof.operational_authority!=='HOLD'||spoof.physical_act_allowed)throw Error('false physical promotion');passed++;
console.log('AETHER-177 '+passed+'/25 synthetic structural cases PASS; physical qualification 0%, operational HOLD.');
