"use strict";
(async()=>{
  const $=id=>document.getElementById(id);
  const categories=[
    ["agent",/(^|[-_.])(agent|aeon|sapphon|assistant|avatar|bot|perceptron)([-_.]|$)/i],
    ["engine",/(^|[-_.])(kernel|engine|haci|quorum|lattice|register|cipher|mobius|ring|torroid|toroid)([-_.]|$)/i],
    ["world",/(^|[-_.])(world|universe|space|studio|game|terra|story|academia)([-_.]|$)/i],
    ["tool",/(^|[-_.])(tool|server|api|bridge|protocol|runtime|storage|atlas)([-_.]|$)/i]
  ];
  let items=[],scope="";
  const classify=r=>{
    if(r.archived)return "unreviewed";
    const name=r.name||"";
    return categories.find(([label,re])=>re.test(name))?.[0]||"unreviewed";
  };
  function el(tag,txt,cls){const x=document.createElement(tag);x.textContent=txt||"";if(cls)x.className=cls;return x;}
  function render(){
    const q=$("search").value.toLowerCase().trim(),k=$("kind").value;
    const filtered=items.filter(r=>(k==="all"||classify(r)===k)&&[r.name,r.description,r.repository].filter(Boolean).join(" ").toLowerCase().includes(q));
    filtered.sort((a,b)=>a.name.localeCompare(b.name)*($("sort").value==="za"?-1:1));
    $("count").textContent=items.length.toLocaleString();$("shown").textContent=filtered.length.toLocaleString();$("coverage").textContent=scope;
    const dest=$("results");dest.replaceChildren();
    filtered.slice(0,240).forEach(r=>{
      const c=el("article","","card"),type=classify(r);
      c.append(el("span",type+" · unreviewed","chip"));
      const h=el("h2");const a=el("a",r.name);a.href=r.url;a.target="_blank";a.rel="noopener noreferrer";h.append(a);c.append(h);
      c.append(el("p",r.description||"No description supplied.","small"));
      c.append(el("div",(r.archived?"Archived · ":"")+(r.fork?"Fork · ":"")+"Not connected","small"));
      dest.append(c);
    });
    $("status").textContent=filtered.length>240?"Showing first 240 matches. Narrow your search to find more.":filtered.length+" matching repositories; all classifications provisional.";
  }
  try{
    let data;let full=false;
    try{
      const r=await fetch("github-discovery-full.json",{cache:"no-store"});
      if(r.ok){data=await r.json();full=true;}
    }catch(_){}
    if(!data){const r=await fetch("github-discovery.json",{cache:"no-store"});if(!r.ok)throw Error("No discovery catalog published");data=await r.json();}
    items=data.repositories||[];scope=full?"Full crawl":"100-result sample";
    $("search").addEventListener("input",render);$("kind").addEventListener("change",render);$("sort").addEventListener("change",render);render();
  }catch(e){$("status").textContent="Catalog unavailable: "+e.message;}
})();
