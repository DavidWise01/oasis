/** AETHER-172: structural ancestry graph only. No client-side trust or ACT. */
export function assess(record){
 const errors=[];
 const reject=()=>({status:"REJECT",reasons:[...new Set(errors)].sort(),physical_qualification_percent:0,operational_authority:"HOLD",physical_act_allowed:false});
 if(!record || !Array.isArray(record.nodes) || !Array.isArray(record.sources))return {status:"REJECT",reasons:["INVALID_GRAPH"],physical_qualification_percent:0,operational_authority:"HOLD",physical_act_allowed:false};
 const nodes=new Map();
 for(const n of record.nodes){
   if(!n||typeof n.id!=="string"||!n.id||!Array.isArray(n.parents)||!["root","derived"].includes(n.kind)){errors.push("BAD_NODE");continue}
   if(nodes.has(n.id))errors.push("DUPLICATE_NODE_ID");
   nodes.set(n.id,n);
   if(n.kind==="root" && n.parents.length)errors.push("ROOT_WITH_PARENTS");
   if(n.kind==="derived" && n.parents.length===0)errors.push("DERIVED_WITHOUT_PARENT");
 }
 const rootsFor=(id,stack=new Set())=>{
   if(stack.has(id)){errors.push("ANCESTRY_CYCLE");return new Set()}
   const n=nodes.get(id);if(!n){errors.push("UNKNOWN_ANCESTOR");return new Set()}
   if(n.kind==="root")return new Set([id]);
   const next=new Set(stack);next.add(id);const roots=new Set();
   for(const parent of n.parents){for(const root of rootsFor(parent,next))roots.add(root)}
   return roots;
 };
 if(record.sources.length!==3)errors.push("THREE_SOURCE_ROLES_REQUIRED");
 const roles=new Set(),captures=new Set(),serials=new Set(),rootsByRole=new Map();
 for(const source of record.sources){
   if(!source||!["DUT","REFERENCE","BENCH"].includes(source.role)){errors.push("INVALID_ROLE");continue}
   if(roles.has(source.role))errors.push("DUPLICATE_SOURCE_ROLE");roles.add(source.role);
   for(const field of ["serial","capture_sha256","node_id"]){if(typeof source[field]!=="string"||!source[field])errors.push("MISSING_"+field.toUpperCase())}
   if(serials.has(source.serial))errors.push("SHARED_DEVICE_SERIAL");serials.add(source.serial);
   if(!/^[a-f0-9]{64}$/i.test(source.capture_sha256||""))errors.push("INVALID_CAPTURE_SHA256");
   if(captures.has(source.capture_sha256))errors.push("DUPLICATED_CAPTURE");captures.add(source.capture_sha256);
   rootsByRole.set(source.role,rootsFor(source.node_id));
 }
 if(roles.size!==3)errors.push("INCOMPLETE_ROLE_SET");
 for(const pair of [["DUT","REFERENCE"],["DUT","BENCH"],["REFERENCE","BENCH"]]){
   const a=rootsByRole.get(pair[0]),b=rootsByRole.get(pair[1]);
   if(a&&b&&[...a].some(x=>b.has(x)))errors.push("COMMON_ROOT_"+pair.join("_"));
 }
 // Structural ancestry declarations are untrusted even when distinct.
 if(record.external_origin_authentication!==true)errors.push("ORIGINS_NOT_INDEPENDENTLY_AUTHENTICATED");
 if(record.original_hardware_capture_authentication!==true)errors.push("CAPTURE_NOT_PHYSICALLY_AUTHENTICATED");
 return {status:errors.length?"REJECT":"DOCUMENTARY_REVIEW_ONLY",reasons:[...new Set(errors)].sort(),declared_roots:Object.fromEntries([...rootsByRole].map(([k,v])=>[k,[...v].sort()])),physical_qualification_percent:0,operational_authority:"HOLD",physical_act_allowed:false}
}
