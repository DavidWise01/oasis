// SHEET96 actual compiled WASM: compare 1 vs 2 D8 service channels.
const fs=require('fs'),assert=require('assert'),crypto=require('crypto');
const bytes=fs.readFileSync(__dirname+'/kernel.wasm');
(async()=>{
 const {instance}=await WebAssembly.instantiate(bytes,{}),w=instance.exports;
 const checks={};const ok=(n,pass)=>{checks[n]=!!pass;assert.ok(pass,n)};
 const digest=(v)=>crypto.createHash('sha256').update(JSON.stringify(v)).digest('hex');
 const population=()=>Array.from({length:9},(_,d)=>w.get_domain_entries(d)-w.get_domain_exits(d)).reduce((a,b)=>a+b,0);
 const snapshot=()=>Array.from({length:120},(_,i)=>[w.get_floor(i),w.get_ring(i),w.get_copper(i),w.get_bank(i),w.get_domain(i),w.get_phase(i),w.get_hops(i),w.get_progress(i),w.get_route_mode(i),w.get_delivery_seq(i),w.get_ack_seq(i)]);
 function trace({stress=false,channels=1,ticks=2200,holdPolicy=1}){
  w.set_service_channels(channels);w.set_policy(holdPolicy);if(stress)w.stress_all();else w.reset();
  let errors=0,maxConflict=0,maxQueue=0,maxBusy=0,immutableErrors=0,seenAll=new Set(),viaPrev=Array(120).fill(null);
  const milestones=[]; let totalAckDelay=0,ackEvents=0;
  for(let t=0;t<ticks;t++){
   const before=Array.from({length:120},(_,i)=>w.get_ack_seq(i));
   w.step();let queue=0,waiting=0,ackPending=0,active=0,delivered=0,acked=0;
   for(let i=0;i<120;i++){
    const ph=w.get_phase(i),d=w.get_domain(i),f=w.get_floor(i),mode=w.get_route_mode(i);
    if(f<0||f>=8||d<0||d>8||mode<0||mode>3)errors++;
    seenAll.add(f+':'+w.get_ring(i));
    queue+=ph===2;waiting+=ph===3;active+=ph===1;ackPending+=ph===5;
    delivered+=w.get_delivery_seq(i);acked+=w.get_ack_seq(i);
    if(w.get_ack_seq(i)>w.get_delivery_seq(i)||w.get_delivery_seq(i)-w.get_ack_seq(i)>1)errors++;
    if(viaPrev[i]!==null&&ph===1&&viaPrev[i]!==mode)immutableErrors++;
    viaPrev[i]=ph===1?mode:null;
    if(w.get_ack_seq(i)>before[i]){ackEvents++;totalAckDelay+=t+1;}
   }
   let conflict=w.get_swept_conflicts();maxConflict=Math.max(maxConflict,conflict);
   maxQueue=Math.max(maxQueue,queue);
   maxBusy=Math.max(maxBusy,w.get_peak_busy_channels());
   if(queue!==w.get_queue_count()||waiting!==w.get_waiting()||ackPending!==w.get_ack_pending()||delivered!==w.get_deliveries()||acked!==w.get_acks()||population()!==120||conflict!==0||queue>8||w.get_aggregate_in()!==w.get_aggregate_out()+queue||w.get_floor_vias()!==w.get_deliveries()||w.get_deliveries()!==w.get_aggregate_out()||w.get_service_channels()!==channels)errors++;
   if((t+1)%550===0)milestones.push({tick:t+1,acks:w.get_acks(),queue:w.get_queue_count(),waiting:w.get_waiting(),active_vias:active});
  }
  const neverAcked=Array.from({length:120},(_,i)=>w.get_ack_seq(i)).filter(v=>v===0).length;
  return {stress,channels,ticks,errors,immutableErrors,maxConflict,maxQueue,maxBusy,addresses:seenAll.size,neverAcked,stats:{orbits:w.get_orbits(),vias:w.get_vias(),floor_vias:w.get_floor_vias(),aggregate_in:w.get_aggregate_in(),aggregate_out:w.get_aggregate_out(),queue:w.get_queue_count(),waiting:w.get_waiting(),max_wait_ticks:w.get_max_wait_ticks(),waiter_ticks:w.get_waiter_ticks(),deferrals:w.get_clearance_deferrals(),cross_ring_deferrals:w.get_swept_cross_ring_deferrals(),alternatives:w.get_adaptive_grants(),delivered:w.get_deliveries(),acks:w.get_acks(),ack_pending:w.get_ack_pending(),service_by_silo:Array.from({length:8},(_,d)=>w.get_service_silo(d)),service_busy_ticks:w.get_channel_busy_ticks(),peak_busy_channels:w.get_peak_busy_channels()},milestones,state_digest:digest(snapshot())};
 }
 ok('compiled WebAssembly magic',bytes.subarray(0,4).toString('hex')==='0061736d');
 ok('120 lane identities',w.get_lanes()===120);ok('8 silos/9 domains',w.get_floors()===8&&w.get_domains()===9);ok('72 toroids',w.get_toroids()===9);ok('D8 aggregate remains eight slots',w.get_queue_capacity()===8);ok('each D8 worker takes eight ticks',w.get_aggregate_ticks()===8);ok('swept clearance remains 1.5 units',w.get_swept_radius_milli()===1500);ok('same four adaptive via candidates',w.get_max_adaptive_displacement_milli()===3600);
 const serialNormal=trace({channels:1}),serialStress=trace({channels:1,stress:true}),dualNormal=trace({channels:2}),dualStress=trace({channels:2,stress:true});
 for(const [name,r] of Object.entries({serialNormal,serialStress,dualNormal,dualStress})){
  ok(name+' runtime invariants',r.errors===0);ok(name+' immutable via shapes',r.immutableErrors===0);ok(name+' zero swept conflicts',r.maxConflict===0);ok(name+' 72 toroid addresses',r.addresses===72);ok(name+' queue peak <=8',r.maxQueue<=8);ok(name+' all 8 silos serviced',r.stats.service_by_silo.every(x=>x>0));ok(name+' modeled ACK receipts conserved',r.stats.delivered===r.stats.acks+r.stats.ack_pending);
 }
 ok('serial remains single working server',serialStress.maxBusy===1);
 ok('two-server policy uses second channel',dualStress.maxBusy===2);
 ok('serial serves every active source domain',serialStress.stats.service_by_silo.every(n=>n>0));
 ok('dual serves all silo sources',dualStress.stats.service_by_silo.every(x=>x>0));
 ok('serial completes initial burst for all 120 lane IDs',serialStress.neverAcked===0);
 ok('dual completes initial burst for all 120 lane IDs',dualStress.neverAcked===0);
 ok('dual improves completed handoffs in normal',dualNormal.stats.acks>serialNormal.stats.acks);
 ok('dual improves completed handoffs in stress',dualStress.stats.acks>serialStress.stats.acks);
 ok('dual reduces cumulative upstream waiting in stress',dualStress.stats.waiter_ticks<serialStress.stats.waiter_ticks);
 // Replay both policies against identical initial conditions; record hash equality.
 const replayNormal=trace({channels:2}),replayStress=trace({channels:2,stress:true});
 ok('normal deterministic replay',dualNormal.state_digest===replayNormal.state_digest);
 ok('stress deterministic replay',dualStress.state_digest===replayStress.state_digest);
 ok('D8 channel choice non-destructive to queue size',w.get_queue_capacity()===8);
 const out={schema:'oasis/sheet96/aggregate-throughput-recovery-v01',status:'verified',binary_bytes:bytes.length,all_checks:checks,passed:Object.values(checks).filter(Boolean).length,total:Object.keys(checks).length,serialNormal,serialStress,dualNormal,dualStress,
 notes:['Two parallel logical service workers are an explicit capacity upgrade; cannot claim admission-only throughput gains','Each transaction still takes 8 service ticks and queue capacity remains 8','All ACKs are internal simulated receipts, not real delivery']};
 fs.writeFileSync(__dirname+'/results.json',JSON.stringify(out,null,2)+'\n');
 console.log(JSON.stringify({passed:out.passed,total:out.total,serial_normal_acks:serialNormal.stats.acks,dual_normal_acks:dualNormal.stats.acks,serial_stress_acks:serialStress.stats.acks,dual_stress_acks:dualStress.stats.acks,serial_stress_waiter_ticks:serialStress.stats.waiter_ticks,dual_stress_waiter_ticks:dualStress.stats.waiter_ticks,stress_service_by_silo:dualStress.stats.service_by_silo},null,2));
})().catch(e=>{console.error(e);process.exitCode=1});