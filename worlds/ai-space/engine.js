"use strict";
(() => {
  const KEY = "oasis.ai-space.v01";
  const worlds = [
    {id:"ud0",name:"UD0 / Universe David 0",purpose:"First fully built external universe. Palindromeda five worlds, 64 domains, DU1 agent ecosphere. Linked read-only; no model execution.",url:"https://davidwise01.github.io/ud0/"},
    {id:"u1-du0",name:"U1 / Du0",purpose:"Existing -mObiUs narrative world; six evidence/story channels retained as a world boundary.",url:"../u1-du0/"},
    {id:"studio",name:"Creation Studio",purpose:"Isolated prototypes, design, writing, media and generative experiments.",url:"../../apps/tattoo/"},
    {id:"sandbox",name:"Research Sandbox",purpose:"Candidate hypotheses and verification tasks; no automatic truth promotion.",url:""}
  ];
  const defaults=()=>({version:1,agents:[
    {id:"seed-observe",name:"Archivist / Observer",world:"u1-du0",lane:"observe",type:"manual"},
    {id:"seed-create",name:"Maker / Creator",world:"studio",lane:"create",type:"manual"}
  ],events:[],proposals:[],selected:null});
  let state;
  try {
    const value=JSON.parse(localStorage.getItem(KEY)||"null");
    state=value&&value.version===1&&Array.isArray(value.events)&&Array.isArray(value.proposals)&&Array.isArray(value.agents)?value:defaults();
  } catch (_) {state=defaults();}
  const el=id=>document.getElementById(id);
  const persist=()=>{try{localStorage.setItem(KEY,JSON.stringify(state));}catch(_){status("Storage unavailable; use Export to preserve this session.");}};
  const status=msg=>{el("status").textContent=msg;};
  const validWorld=id=>worlds.some(w=>w.id===id);
  const safeId=()=>("a-"+Date.now().toString(36)+"-"+Math.random().toString(36).slice(2,8));
  const encode=x=>new TextEncoder().encode(x);
  async function digest(s) {
    if(!globalThis.crypto?.subtle) throw new Error("Secure-context crypto is required for witness hashes. Use HTTPS or localhost.");
    const a=await crypto.subtle.digest("SHA-256",encode(s));
    return Array.from(new Uint8Array(a),x=>x.toString(16).padStart(2,"0")).join("");
  }
  function lastHash(){return state.events.length?state.events[state.events.length-1].hash:"GENESIS";}
  async function append(type, data){
    const entry={index:state.events.length,at:new Date().toISOString(),type,data,prev:lastHash()};
    entry.hash=await digest(JSON.stringify(entry));
    state.events.push(entry);persist();render();return entry;
  }
  function field(parent,name,value){const node=document.createElement(name);node.textContent=value;parent.append(node);return node;}
  function fillSelect(id,items,valueKey,labelKey){
    const select=el(id),value=select.value;select.replaceChildren();
    items.forEach(item=>{const o=document.createElement("option");o.value=item[valueKey];o.textContent=item[labelKey];select.append(o);});
    if(items.some(item=>item[valueKey]===value))select.value=value;
  }
  function render(){
    fillSelect("world",worlds,"id","name");fillSelect("agentWorld",worlds,"id","name");
    const selectedWorld=el("world").value;
    fillSelect("agent",state.agents.filter(a=>a.world===selectedWorld),"id","name");
    el("worldCount").textContent=String(worlds.length);
    el("agentCount").textContent=String(state.agents.length);
    el("eventCount").textContent=String(state.events.length);
    const list=el("worlds");list.replaceChildren();
    worlds.forEach(w=>{
      const card=document.createElement("article");card.className="world";
      field(card,"small",w.id.toUpperCase());field(card,"h3",w.name);field(card,"p",w.purpose);
      field(card,"small",state.agents.filter(a=>a.world===w.id).length+" registered agents");
      if(w.url){const a=document.createElement("a");a.href=w.url;a.textContent="Open world →";card.append(a);}
      list.append(card);
    });
    const ledger=el("ledger");ledger.replaceChildren();
    state.events.slice(-35).reverse().forEach(e=>{
      const item=document.createElement("li");
      field(item,"span",e.index+" / "+e.type+" / "+e.at+" / "+e.hash.slice(0,16));
      ledger.append(item);
    });
    const pending=state.proposals.find(p=>p.id===state.selected);
    el("result").textContent=pending?JSON.stringify(pending,null,2):"No selected proposal.";
  }
  async function action(fn){
    const buttons=[...document.querySelectorAll("button")];buttons.forEach(b=>b.disabled=true);
    try {await fn();}catch(e){status("HOLD: "+e.message);}finally{buttons.forEach(b=>b.disabled=false);render();}
  }
  async function make(kind){
    const agent=state.agents.find(a=>a.id===el("agent").value);
    const world=el("world").value,request=el("intent").value.trim();
    if(!agent||agent.world!==world)throw Error("Select a registered agent in this world.");
    if(agent.lane!==kind)throw Error("Agent is assigned to the other lane. Separation enforced.");
    if(!request)throw Error("Enter an observation or creation request.");
    if(request.length>2000)throw Error("Request too long.");
    const proposal={id:safeId(),world,agent:agent.id,lane:kind,request,status:"HOLD",witness:null,
      output:kind==="observe"?
      "Observation task queued for external agent; no live retrieval performed.":
      "Creation specification recorded; no external model was executed."};
    state.proposals.push(proposal);state.selected=proposal.id;
    await append("PROPOSE",{id:proposal.id,world,agent:agent.id,lane:kind,request});
    status("HOLD: proposal recorded. Witness is required before a human commit.");
  }
  async function witness(){
    const p=state.proposals.find(p=>p.id===state.selected);
    if(!p)throw Error("No selected proposal.");
    if(p.status!=="HOLD")throw Error("Only held proposals can be witnessed.");
    const agent=state.agents.find(a=>a.id===p.agent);
    if(!agent||agent.world!==p.world||agent.lane!==p.lane)throw Error("Agent assignment changed; HOLD.");
    const proof=await digest(JSON.stringify({id:p.id,agent:p.agent,world:p.world,request:p.request,lane:p.lane}));
    p.witness={proof,scope:"proposal-integrity-only",by:"local-runtime"};
    p.status="WITNESSED";
    await append("WITNESS",{id:p.id,proof,scope:"proposal-integrity-only"});
    status("WITNESSED: local proposal integrity only. A person must still approve any commit.");
  }
  async function commit(){
    const p=state.proposals.find(p=>p.id===state.selected);
    if(!p||p.status!=="WITNESSED"||!p.witness)throw Error("Missing valid witnessed proposal; HOLD.");
    const proof=await digest(JSON.stringify({id:p.id,agent:p.agent,world:p.world,request:p.request,lane:p.lane}));
    if(p.witness.proof!==proof)throw Error("Witness integrity failure; HOLD.");
    p.status="COMMITTED";
    await append("HUMAN_COMMIT",{id:p.id,witness:proof,world:p.world});
    status("COMMITTED: authorized local demo event only. No canonical kernel state changed.");
  }
  async function register(){
    const name=el("newAgent").value.trim(),world=el("agentWorld").value,lane=el("agentLane").value,type=el("agentType").value;
    if(!name||name.length>70||!validWorld(world)||!["observe","create"].includes(lane)||!["manual","local","api","wasm"].includes(type))throw Error("Invalid agent registry fields.");
    if(state.agents.length>=100)throw Error("Demo capacity reached (100 agents).");
    const agent={id:safeId(),name,world,lane,type,connection:"unconnected"};
    state.agents.push(agent);await append("REGISTER_AGENT",{...agent});
    el("newAgent").value="";el("world").value=world;render();el("agent").value=agent.id;
    status("Registered "+name+" in "+world+". External execution remains disconnected.");
  }
  async function verifyLedger(){
    let previous="GENESIS";
    for(const [index,e] of state.events.entries()){
      if(e.index!==index||e.prev!==previous)throw Error("Ledger chain broken at event "+index);
      const {hash,...body}=e;
      if(await digest(JSON.stringify(body))!==hash)throw Error("Hash mismatch at event "+index);
      previous=hash;
    }
    return true;
  }
  el("world").addEventListener("change",render);
  el("observe").addEventListener("click",()=>action(()=>make("observe")));
  el("create").addEventListener("click",()=>action(()=>make("create")));
  el("witness").addEventListener("click",()=>action(witness));
  el("commit").addEventListener("click",()=>action(commit));
  el("register").addEventListener("click",()=>action(register));
  el("export").addEventListener("click",()=>action(async()=>{
    await verifyLedger();
    const blob=new Blob([JSON.stringify({format:"oasis.ai-space.v01",...state},null,2)],{type:"application/json"});
    const url=URL.createObjectURL(blob),a=document.createElement("a");a.href=url;a.download="oasis-ai-space-ledger.json";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    status("Exported validated local event ledger and registry.");
  }));
  el("reset").addEventListener("click",()=>action(async()=>{
    if(!confirm("Reset local demo records in this browser? Export first to keep a copy."))return;
    state=defaults();persist();status("Local demo reset. Previously exported records are unaffected.");
  }));
  render();
  verifyLedger().then(()=>status("READY: locally stored event chain verified. Agents disconnected.")).catch(e=>status("HOLD: "+e.message+"; export records before reset."));
})();
