import {webcrypto} from 'node:crypto';
if(!globalThis.crypto)globalThis.crypto=webcrypto;
import {assess,canonical,hex,sha256,CAL_FIELDS,CAP_FIELDS} from './verification.mjs';
const enc=new TextEncoder(),raw=enc.encode('AETHER-188 mock data, NOT original physical instrumentation');
const keys=await Promise.all([0,1].map(()=>crypto.subtle.generateKey({name:'ECDSA',namedCurve:'P-256'},true,['sign','verify'])));
const jwk=await Promise.all(keys.map(k=>crypto.subtle.exportKey('jwk',k.publicKey)));
const sign=async (i,obj,fields)=>hex(new Uint8Array(await crypto.subtle.sign({name:'ECDSA',hash:'SHA-256'},keys[i].privateKey,enc.encode(canonical(obj,fields)))));
const registry=()=>new Map([['calibrator-demo',{jwk:jwk[0],root_id:'calibrator-root',operator_id:'calibration-operator'}]]);
const devices=()=>new Map([['device-demo-key',{jwk:jwk[1],device_serial:'DEVICE-188',clock_serial:'CLOCK-188',operator_id:'device-operator'}]]);
const policy=()=>({expected_device_serial:'DEVICE-188',expected_clock_serial:'CLOCK-188',expected_challenge_id:'CH-188',expected_challenge_nonce:'NONCE-188',expected_challenge_domain:'AETHER188',expected_samples:3,max_tick_span_ms:60000,max_clock_skew_ms:1000,used_nonces:new Set(),used_capture_ids:new Set(),calibrator_keys:registry(),device_keys:devices()});
async function make(){
 const calibration={schema:'AETHER-188/calibration-v1',calibration_id:'CAL-188',device_serial:'DEVICE-188',clock_serial:'CLOCK-188',issuer_id:'calibrator-demo',issuer_root_id:'calibrator-root',valid_from_utc:'2026-11-23T00:00:00Z',valid_until_utc:'2026-11-26T00:00:00Z',max_drift_ppm:50,tick_unit_ns:1000000,challenge_domain:'AETHER188'};
 const capture={schema:'AETHER-188/capture-v1',capture_id:'CAP-188',device_serial:'DEVICE-188',clock_serial:'CLOCK-188',calibration_sha256:await sha256(enc.encode(canonical(calibration,CAL_FIELDS))),challenge_id:'CH-188',challenge_nonce:'NONCE-188',challenge_issued_utc:'2026-11-24T20:00:00Z',challenge_expires_utc:'2026-11-24T20:02:00Z',captured_utc:'2026-11-24T20:01:00Z',first_tick:10000,last_tick:11000,sample_start:500,sample_end:502,raw_sha256:await sha256(raw),device_key_id:'device-demo-key'};
 return {raw_bytes:new Uint8Array(raw),calibration,capture,calibration_signature_hex:await sign(0,calibration,CAL_FIELDS),capture_signature_hex:await sign(1,capture,CAP_FIELDS)};
}
const original=await make(),p=()=>structuredClone(original);
const checkCases=[
 ['missing',null,policy(),'MISSING_BYTES_CALIBRATION_OR_CAPTURE'],
 ['empty bytes',(()=>{const v=p();v.raw_bytes=new Uint8Array();return v})(),policy(),'EMPTY_CAPTURE_BYTES'],
 ['capture byte flip',(()=>{const v=p();v.raw_bytes[0]^=1;return v})(),policy(),'CAPTURE_BYTE_SUBSTITUTION'],
 ['invalid schema',(()=>{const v=p();v.capture.schema='wrong';return v})(),policy(),'SCHEMA_MISMATCH'],
 ['device swap',(()=>{const v=p();v.capture.device_serial='ATTACK';return v})(),policy(),'DEVICE_IDENTITY_SUBSTITUTION'],
 ['clock swap',(()=>{const v=p();v.capture.clock_serial='ATTACK';return v})(),policy(),'CLOCK_IDENTITY_SUBSTITUTION'],
 ['challenge swapped',(()=>{const v=p();v.capture.challenge_id='old';return v})(),policy(),'CHALLENGE_BINDING_MISMATCH'],
 ['challenge replay',p(),{...policy(),used_nonces:new Set(['NONCE-188'])},'REPLAYED_CHALLENGE_NONCE'],
 ['capture replay',p(),{...policy(),used_capture_ids:new Set(['CAP-188'])},'REPLAYED_CAPTURE_ID'],
 ['challenge expired',(()=>{const v=p();v.capture.captured_utc='2026-11-24T20:05:00Z';return v})(),policy(),'EXPIRED_OR_UNISSUED_CHALLENGE'],
 ['invalid time',(()=>{const v=p();v.capture.captured_utc='invalid';return v})(),policy(),'INVALID_TIME_FORMAT'],
 ['calibration expired',(()=>{const v=p();v.calibration.valid_until_utc='2026-11-23T12:00:00Z';return v})(),policy(),'CALIBRATION_EXPIRED_AT_ACQUISITION'],
 ['tick rollback',(()=>{const v=p();v.capture.last_tick=9999;return v})(),policy(),'HARDWARE_TICK_ROLLBACK'],
 ['sample rollback',(()=>{const v=p();v.capture.sample_end=499;return v})(),policy(),'SAMPLE_COUNTER_ROLLBACK'],
 ['sample mismatch',(()=>{const v=p();v.capture.sample_end=503;return v})(),policy(),'SAMPLE_COUNT_MISMATCH'],
 ['tick-span too long',(()=>{const v=p();v.capture.last_tick=100000;return v})(),policy(),'CLOCK_TICK_SPAN_EXCEEDS_POLICY'],
 ['calibration altered',(()=>{const v=p();v.calibration.max_drift_ppm=60;return v})(),policy(),'CALIBRATION_RECORD_SUBSTITUTION'],
 ['calibration forged signature',(()=>{const v=p();v.calibration_signature_hex='00'.repeat(64);return v})(),policy(),'CALIBRATION_SIGNATURE_INVALID'],
 ['capture forged signature',(()=>{const v=p();v.capture_signature_hex='00'.repeat(64);return v})(),policy(),'CAPTURE_SIGNATURE_INVALID'],
 ['calibrator root mismatch',p(),{...policy(),calibrator_keys:new Map([['calibrator-demo',{jwk:jwk[0],root_id:'wrong-root',operator_id:'calibration-operator'}]])},'CALIBRATOR_ROOT_MISMATCH'],
 ['device signer binding',p(),{...policy(),device_keys:new Map([['device-demo-key',{jwk:jwk[1],device_serial:'OTHER',clock_serial:'CLOCK-188',operator_id:'device-operator'}]])},'DEVICE_KEY_BINDING_MISMATCH'],
 ['shared operator',p(),{...policy(),device_keys:new Map([['device-demo-key',{jwk:jwk[1],device_serial:'DEVICE-188',clock_serial:'CLOCK-188',operator_id:'calibration-operator'}]])},'SHARED_CALIBRATOR_DEVICE_OPERATOR'],
 ['revoked signer',p(),{...policy(),calibrator_keys:new Map([['calibrator-demo',{jwk:jwk[0],root_id:'calibrator-root',operator_id:'calibration-operator',revoked:true}]])},'REVOKED_SIGNING_KEY'],
 ['calibrator not independent',p(),policy(),'CALIBRATOR_NOT_EXTERNALLY_AUTHENTICATED'],
 ['instrument not authenticated',p(),policy(),'PHYSICAL_INSTRUMENT_NOT_AUTHENTICATED'],
 ['clock not calibrated physically',p(),policy(),'PHYSICAL_CLOCK_NOT_TRACEABLY_CALIBRATED'],
 ['original acquisition not authenticated',p(),policy(),'ORIGINAL_ACQUISITION_NOT_AUTHENTICATED']
];
let passed=0;
for(const [name,input,ctx,reason] of checkCases){
 const r=await assess(input,ctx);
 if(!r.reasons.includes(reason)||r.operational_authority!=='HOLD'||r.physical_act_allowed)throw Error(name+' '+JSON.stringify(r));
 passed++;
}
const clean=await assess(p(),policy());
if(!clean.calibration_signature_valid||!clean.capture_signature_valid||clean.operational_authority!=='HOLD')throw Error('valid signed synthetic fixture failed');
passed++;
const spoof=await assess(p(),{...policy(),external_calibrator_authenticated:true,physical_instrument_authenticated:true,physical_clock_traceability_authenticated:true,original_acquisition_authenticated:true});
if(spoof.decision!=='DOCUMENTARY_BINDING_ONLY'||spoof.operational_authority!=='HOLD'||spoof.physical_act_allowed)throw Error('mock trust flags wrongly authorize ACT');
passed++;
console.log('AETHER-188 '+passed+'/29 synthetic cases PASS; physical 0%, operational ACT HOLD.');
