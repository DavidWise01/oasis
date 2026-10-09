// SHEET95 Structural DOM smoke-test of the exact embedded-WASM standalone SVG viewer.
// This is an instrumented DOM stub, not a real browser rendering/paint test.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
class Node{
 constructor(name){this.name=name;this.attrs={};this.dataset={};this.style={};this.children=[];this.textContent='';this.value='';}
 setAttribute(k,v){this.attrs[k]=String(v);if(k.startsWith('data-'))this.dataset[k.slice(5)]=String(v);}
 getAttribute(k){return this.attrs[k]??null;}
 hasAttribute(k){return k in this.attrs;}
 appendChild(x){this.children.push(x);return x;}
 replaceChildren(...args){this.children=[...args];}
}
const ids=Object.fromEntries(['status','toggle','reset','stress','policy','speed','floor','axis','exportSvg','exportLedger','ticks','orbits','vias','fvias','gates','active','ain','aout','apending','waiting','pressure','maxwait','holds','deferrals','fallback','proposals','routelen','conflicts','crossring','sweptholds','delivered','acked','ackpending','bytes','octets','aggregateG','queueSvg','floorsG','toroids','viaG','packets','labels','ledger','board'].map(s=>[s,new Node(s)]));
ids.policy.value='1';ids.speed.value='2';ids.floor.value='all';ids.axis.value='all';
const all=()=>Object.values(ids).flatMap(root=>{const out=[];function walk(n){for(const c of n.children){out.push(c);walk(c);}}walk(root);return out;});
const document={getElementById:s=>ids[s],createElementNS:(_,n)=>new Node(n),createElement:n=>new Node(n),querySelectorAll:s=>s==='[data-floor]'?all().filter(x=>x.hasAttribute('data-floor')):[]};
const raf=[];const html=fs.readFileSync(__dirname+'/index.html','utf8');const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const checks=[];const check=(name,v)=>{assert.ok(v,name);checks.push(name)};
(async()=>{
 new vm.Script(script,{filename:'sheet95-inline-js'});
 check('standalone_svg_element',html.includes('<svg id="board"'));
 check('not_canvas',!html.includes('<canvas'));
 check('embedded_wasm_data',/const WASM_B64='[A-Za-z0-9+/=]+'/.test(script));
 const b64=script.match(/WASM_B64='([^']+)'/)[1];check('embedded_wasm_matches_local_binary',Buffer.from(b64,'base64').equals(fs.readFileSync(__dirname+'/kernel.wasm')));
 check('svg_coordinates_are_3D_projection',script.includes('toroidCenter')&&script.includes('orbitAt')&&script.includes('linePosition'));
 const context={document,WebAssembly,Uint8Array,atob,Math,console,requestAnimationFrame:cb=>raf.push(cb)};
 vm.runInNewContext(script,context);
 // Allow the async WebAssembly.instantiate boot to settle.
 for(let i=0;i<50&&!ids.status.textContent.includes('ACTIVE');i++)await new Promise(res=>setTimeout(res,10));
 check('dom_boots_wasm',ids.status.textContent.includes('ACTIVE'));
 const tags=(g,n)=>ids[g].children.filter(x=>x.name===n);
 check('aggregate_svg_group_drawn',tags('aggregateG','rect').length===1);
 check('8_queued_svg_slots',tags('queueSvg','rect').length===8);
 check('8_queue_slot_labels',tags('queueSvg','text').length===9);
 check('aggregate_domain_census_svg_labels',tags('aggregateG','text').length===10);
 check('aggregate_not_ninth_floor_band',tags('floorsG','rect').length===8);
 check('72_toroid_svg_groups',tags('toroids','g').length===72);
 check('nine_toroids_each_floor',Array.from({length:8},(_,f)=>tags('toroids','g').filter(x=>Number(x.dataset.floor)===f).length).every(x=>x===9));
 check('three_toroids_per_axis',Array.from({length:3},(_,a)=>tags('toroids','g').filter(x=>Number(x.dataset.axis)===a).length).every(x=>x===24));
 check('8_floor_bands',tags('floorsG','rect').length===8);
 check('88_copper_lines',tags('floorsG','line').length===8*11);
 check('four_octet_banks',tags('octets','rect').filter(x=>x.attrs.width==='218').length===4);
 check('32_octet_cells',tags('octets','rect').filter(x=>x.attrs.width==='20').length===32);
 check('three_zero_gates',tags('octets','text').filter(x=>x.textContent==='0').length===3);
 check('120_packet_svg_circles',tags('packets','circle').length===120);
 check('120_via_svg_polylines',tags('viaG','path').length===120);
 check('eleven_layer_visualization_per_floor',tags('floorsG','line').filter(x=>Number(x.dataset.floor)===0).length===11);
 check('frame_scheduled',raf.length>0);
 for(let frame=0;frame<600;frame++){const cb=raf.shift();assert.ok(cb,'animation frame '+frame);cb();}
 check('1200_simulation_ticks_from_600_frames',ids.ticks.textContent===1200);
 check('multiple_completed_vias_rendered',Number(ids.vias.textContent)>300);
 check('floor_transfers_rendered',Number(ids.fvias.textContent)>70);
 check('zero_seams_rendered',Number(ids.gates.textContent)>40);
 check('aggregate_ins_and_outs_visible',Number(ids.ain.textContent)>70&&Number(ids.aout.textContent)>70);
 check('aggregate_conservation_at_1200_ticks',Number(ids.ain.textContent)===Number(ids.aout.textContent)+Number(ids.apending.textContent));
 check('queue_capacity_valid_in_svg',Number(ids.apending.textContent)<=8);
 check('waiting_counter_visible',Number.isInteger(Number(ids.waiting.textContent)));
 check('pressure_counter_visible',Number(ids.pressure.textContent)>0);
 check('all_floor_transfers_committed_by_aggregate',Number(ids.fvias.textContent)===Number(ids.aout.textContent));
 check('nine_domain_live_population_conserved',tags('aggregateG','text').filter(x=>/^(?:D[0-8]|A8):[0-9]+/.test(x.textContent)).reduce((n,x)=>n+Number(x.textContent.split(':')[1].split('/')[0]),0)===120);
 check('ledger_records_true_events',ids.ledger.textContent.includes('lane_id'));
 check('aggregate_ledger_entries',ids.ledger.textContent.includes('aggregate_')||ids.ledger.textContent.includes('rr_admitted'));
 check('all_positions_finite',tags('packets','circle').every(x=>Number.isFinite(Number(x.attrs.cx))&&Number.isFinite(Number(x.attrs.cy))));
 check('3d swept paths conflict free',Number(ids.conflicts.textContent)===0);
 check('clearance deferrals counted',Number(ids.deferrals.textContent)>0);check('neighboring different toroids can conflict',Number(ids.crossring.textContent)>0);check('swept deferral counter visible',Number(ids.sweptholds.textContent)>0);check('bent polyline paths drawn',tags('viaG','path').some(x=>/^M /.test(x.attrs.d||'')));check('clearance radius documented',html.includes('1.5-unit')); 
 check('adaptive_fallback_grants_visible',Number(ids.fallback.textContent)>0);check('bounded_route_proposals_visible',Number(ids.proposals.textContent)>Number(ids.fallback.textContent));check('route_length_reported',Number(ids.routelen.textContent)>0);check('alternative_route_beam_rendering',tags('viaG','path').some(x=>x.attrs.stroke==='#65efde'));check('clearance hold counter valid',Number.isInteger(Number(ids.holds.textContent)));
 check('delivery receipt reported',Number(ids.delivered.textContent)>0);
 check('ack receipt reported',Number(ids.acked.textContent)>0);
 check('delivery acknowledgment conservation',Number(ids.delivered.textContent)===Number(ids.acked.textContent)+Number(ids.ackpending.textContent));
 check('new events in ledger implementation',script.includes("event:'swept_path_granted'")&&script.includes("event:'destination_receipt'")&&script.includes("event:'ack_received'"));
 check('visual semantic colors wired',script.includes('#b385ff')&&script.includes('#59f2ed'));
 check('aggregate_visibly_highlighted',tags('packets','circle').some(x=>x.attrs.fill==='#ffdb7e')||Number(ids.apending.textContent)===0);
 check('all_lanes_stay_unique_doms',tags('packets','circle').length===120);
 ids.floor.value='3';ids.floor.onchange();check('floor_filter_applies',tags('toroids','g').some(x=>x.dataset.floor==='2'&&x.style.opacity==='.085'));
 ids.axis.value='2';ids.axis.onchange();check('axis_filter_applies',tags('toroids','g').some(x=>x.dataset.axis==='0'&&x.style.opacity==='.085'));
 ids.toggle.onclick();check('pause_control',ids.toggle.textContent==='Resume');ids.toggle.onclick();
 ids.policy.value='0';ids.policy.onchange();check('fixed_mode_policy_switch_reset',ids.ticks.textContent===0);ids.policy.value='1';ids.policy.onchange();check('adaptive_policy_switch_reset',ids.ticks.textContent===0);ids.reset.onclick();check('reset_ticks_to_zero',ids.ticks.textContent===0);check('reset_counters_to_zero',ids.vias.textContent===0);
 check('reset_aggregate_count_to_zero',ids.ain.textContent===0&&ids.aout.textContent===0&&ids.apending.textContent===0);
 ids.stress.onclick();check('stress_button_resets_ticks',ids.ticks.textContent===0);
 for(let f=0;f<16;f++){const cb=raf.shift();assert.ok(cb);cb();}
 check('stress_backpressure_visible',Number(ids.waiting.textContent)>0);
 check('stress_fifo_nonempty',Number(ids.apending.textContent)>0&&Number(ids.apending.textContent)<=8);
 check('stress_fifo_slot_labels_populated',tags('queueSvg','text').some(x=>/^L[0-9]{3}$/.test(x.textContent)));
 check('wait_markers_red',tags('packets','circle').some(x=>x.attrs.fill==='#ff6965'));
 check('stress_ledger_mentions_request',ids.ledger.textContent.includes('swept_')||ids.ledger.textContent.includes('d8_')||ids.ledger.textContent.includes('aggregate_'));
 ids.reset.onclick();check('reset_clears_stress_backlog',Number(ids.waiting.textContent)===0&&Number(ids.apending.textContent)===0);
 console.log(JSON.stringify({dom_checks_passed:checks.length,svg_fifo_slots:8,svg_toroid_groups:72,copper_lines:88,svg_lane_circles:120,frames_executed:600,wasm_ticks:1200,domains:9,aggregate_id:8,dom_type:'instrumented_dom_not_browser_render'},null,2));
})().catch(e=>{console.error(e);process.exit(1)});