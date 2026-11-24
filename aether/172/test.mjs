import {assess} from './verification.mjs';
const N=(id,kind,parents=[])=>({id,kind,parents});
const S=(role,node_id,d)=>({role,node_id,serial:'SERIAL-'+role,capture_sha256:d.repeat(64)});
const clean={nodes:[N('origin-d','root'),N('origin-r','root'),N('origin-b','root'),N('device-d','derived',['origin-d']),N('device-r','derived',['origin-r']),N('device-b','derived',['origin-b'])],sources:[S('DUT','device-d','a'),S('REFERENCE','device-r','b'),S('BENCH','device-b','c')],external_origin_authentication:false,original_hardware_capture_authentication:false};
const modify=f=>{const v=structuredClone(clean);f(v);return v};
const cases=[
['unverified origin',clean,'ORIGINS_NOT_INDEPENDENTLY_AUTHENTICATED'],
['unverified capture',clean,'CAPTURE_NOT_PHYSICALLY_AUTHENTICATED'],
['DUT reference shared root',modify(v=>v.nodes.find(n=>n.id==='device-r').parents=['origin-d']),'COMMON_ROOT_DUT_REFERENCE'],
['reference bench shared root',modify(v=>v.nodes.find(n=>n.id==='device-b').parents=['origin-r']),'COMMON_ROOT_REFERENCE_BENCH'],
['DUT bench shared root',modify(v=>v.nodes.find(n=>n.id==='device-b').parents=['origin-d']),'COMMON_ROOT_DUT_BENCH'],
['duplicate capture',modify(v=>v.sources[1].capture_sha256=v.sources[0].capture_sha256),'DUPLICATED_CAPTURE'],
['duplicate serial',modify(v=>v.sources[2].serial=v.sources[0].serial),'SHARED_DEVICE_SERIAL'],
['unresolved parent',modify(v=>v.nodes.find(n=>n.id==='device-r').parents=['unknown']),'UNKNOWN_ANCESTOR'],
['cycle',modify(v=>{v.nodes.find(n=>n.id==='device-r').parents=['cycle'];v.nodes.push(N('cycle','derived',['device-r']))}),'ANCESTRY_CYCLE'],
['orphan derived node',modify(v=>v.nodes.find(n=>n.id==='device-r').parents=[]),'DERIVED_WITHOUT_PARENT'],
['node ID conflict',modify(v=>v.nodes.push(N('origin-r','root'))),'DUPLICATE_NODE_ID'],
['duplicate role',modify(v=>v.sources[2].role='REFERENCE'),'DUPLICATE_SOURCE_ROLE'],
['invalid SHA',modify(v=>v.sources[1].capture_sha256='invalid'),'INVALID_CAPTURE_SHA256'],
['declared root has parent',modify(v=>v.nodes.find(n=>n.id==='origin-r').parents=['origin-d']),'ROOT_WITH_PARENTS']
];
let passed=0;for(const [label,p,error] of cases){const r=assess(p);if(!r.reasons.includes(error)||r.operational_authority!=='HOLD'||r.physical_act_allowed)throw Error('FAILED '+label+' '+JSON.stringify(r));passed++}
const forged=assess({...clean,external_origin_authentication:true,original_hardware_capture_authentication:true});
if(forged.status!=='DOCUMENTARY_REVIEW_ONLY'||forged.operational_authority!=='HOLD'||forged.physical_act_allowed)throw Error('false promotion');passed++;
console.log('AETHER-172: '+passed+'/15 synthetic ancestry cases passed; physical 0%; ACT HOLD.');
