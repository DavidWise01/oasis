(() => {
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  const state = {
    tool:'brush',
    drawing:false,
    start:null,
    snapshot:null,
    history:[],
    future:[],
    grid:false,
    commands:[]
  };

  const $ = id => document.getElementById(id);
  const color = $('color'), fillColor = $('fillColor'), width = $('width'), opacity = $('opacity');

  function saveHistory(){
    state.history.push(canvas.toDataURL('image/png'));
    if(state.history.length>50) state.history.shift();
    state.future.length=0;
  }
  function restore(url){
    const img = new Image();
    img.onload=()=>{ctx.clearRect(0,0,canvas.width,canvas.height);ctx.drawImage(img,0,0)};
    img.src=url;
  }
  saveHistory();

  function pos(ev){
    const r=canvas.getBoundingClientRect();
    return {x:(ev.clientX-r.left)*(canvas.width/r.width),y:(ev.clientY-r.top)*(canvas.height/r.height)};
  }
  function style(){
    ctx.lineWidth=+width.value;
    ctx.strokeStyle=color.value;
    ctx.fillStyle=fillColor.value;
    ctx.globalAlpha=+opacity.value;
    ctx.lineCap='round';ctx.lineJoin='round';
  }
  function redrawGrid(){
    if(!state.grid) return;
    ctx.save(); ctx.globalAlpha=.12; ctx.lineWidth=1; ctx.strokeStyle='#000';
    for(let x=0;x<canvas.width;x+=50){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,canvas.height);ctx.stroke()}
    for(let y=0;y<canvas.height;y+=50){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(canvas.width,y);ctx.stroke()}
    ctx.restore();
  }
  canvas.addEventListener('pointerdown', ev=>{
    const p=pos(ev); state.drawing=true; state.start=p; state.snapshot=ctx.getImageData(0,0,canvas.width,canvas.height);
    style();
    if(state.tool==='brush'||state.tool==='eraser'){
      ctx.beginPath();ctx.moveTo(p.x,p.y);
    }
  });
  canvas.addEventListener('pointermove', ev=>{
    const p=pos(ev); $('cursorReadout').textContent=`x:${Math.round(p.x)} y:${Math.round(p.y)}`;
    if(!state.drawing) return;
    style();
    if(state.tool==='brush'){
      ctx.globalCompositeOperation='source-over';ctx.lineTo(p.x,p.y);ctx.stroke();
    } else if(state.tool==='eraser'){
      ctx.globalCompositeOperation='destination-out';ctx.lineWidth=+width.value*2;ctx.lineTo(p.x,p.y);ctx.stroke();ctx.globalCompositeOperation='source-over';
    } else if(['line','rect','circle'].includes(state.tool)){
      ctx.putImageData(state.snapshot,0,0); style();
      const x=state.start.x,y=state.start.y,w=p.x-x,h=p.y-y;
      if(state.tool==='line'){ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(p.x,p.y);ctx.stroke()}
      if(state.tool==='rect'){ctx.beginPath();ctx.rect(x,y,w,h);ctx.fill();ctx.stroke()}
      if(state.tool==='circle'){ctx.beginPath();ctx.ellipse(x+w/2,y+h/2,Math.abs(w/2),Math.abs(h/2),0,0,Math.PI*2);ctx.fill();ctx.stroke()}
    }
  });
  canvas.addEventListener('pointerup', ev=>{
    if(!state.drawing) return;
    state.drawing=false;
    if(state.tool==='text'){
      const p=pos(ev); const t=prompt('Text');
      if(t){style();ctx.font=`${Math.max(14,+width.value*5)}px ui-monospace, monospace`;ctx.fillStyle=color.value;ctx.fillText(t,p.x,p.y)}
    }
    redrawGrid(); saveHistory();
  });

  document.querySelectorAll('[data-tool]').forEach(b=>b.onclick=()=>{
    document.querySelectorAll('[data-tool]').forEach(x=>x.classList.remove('active'));
    b.classList.add('active');state.tool=b.dataset.tool;
  });

  $('undoBtn').onclick=()=>{
    if(state.history.length<=1)return;
    state.future.push(state.history.pop());restore(state.history[state.history.length-1]);
  };
  $('redoBtn').onclick=()=>{
    if(!state.future.length)return;
    const x=state.future.pop();state.history.push(x);restore(x);
  };
  $('clearBtn').onclick=()=>{
    ctx.clearRect(0,0,canvas.width,canvas.height);ctx.fillStyle='white';ctx.fillRect(0,0,canvas.width,canvas.height);saveHistory();
  };
  $('gridBtn').onclick=()=>{state.grid=!state.grid;redrawGrid();saveHistory()};

  function center(){return {x:canvas.width/2,y:canvas.height/2}}
  function neon(){
    saveHistory();style();const c=center();ctx.save();ctx.translate(c.x,c.y);
    for(let r=70;r<=330;r+=52){
      ctx.beginPath();
      for(let i=0;i<6;i++){const a=Math.PI/3*i;const x=Math.cos(a)*r,y=Math.sin(a)*r;i?ctx.lineTo(x,y):ctx.moveTo(x,y)}
      ctx.closePath();ctx.stroke();
    }
    for(let i=0;i<6;i++){const a=Math.PI/3*i;ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(Math.cos(a)*360,Math.sin(a)*360);ctx.stroke()}
    ctx.restore();state.commands.push({op:'NEON',at:Date.now()});saveHistory();
  }
  function pocket(){
    saveHistory();style();const c=center();ctx.save();ctx.translate(c.x,c.y);
    ctx.strokeRect(-330,-190,660,380);
    ctx.font='32px ui-monospace, monospace';ctx.fillStyle=color.value;ctx.textAlign='center';
    ctx.fillText('P(ocket [[*-+\\\\_U_U_U_U*\\\\_-+]]',0,-120);
    for(let i=0;i<4;i++){ctx.beginPath();ctx.arc(-135+i*90,0,28,0,Math.PI*2);ctx.stroke();ctx.fillText('U',-135+i*90+1,11)}
    ctx.fillText('PER → CEPT → ION',0,120);ctx.restore();state.commands.push({op:'POCKET',at:Date.now()});saveHistory();
  }
  function ouro(){
    saveHistory();style();const c=center();ctx.save();ctx.translate(c.x,c.y);
    const R=290;
    for(let i=0;i<11;i++){
      const a=-Math.PI/2+i*(Math.PI*2/11),x=Math.cos(a)*R,y=Math.sin(a)*R;
      ctx.beginPath();ctx.arc(x,y,26,0,Math.PI*2);ctx.fill();ctx.stroke();
      ctx.fillStyle=color.value;ctx.font='16px ui-monospace';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(String(i).padStart(2,'0'),x,y);
      ctx.fillStyle=fillColor.value;
    }
    ctx.beginPath();ctx.arc(0,0,R,0,Math.PI*2);ctx.stroke();
    ctx.fillStyle=color.value;ctx.font='22px ui-monospace';ctx.fillText('OUROBOROS / OSI 00–10',0,0);
    ctx.restore();state.commands.push({op:'OUROBOROS',at:Date.now()});saveHistory();
  }
  function rootGlyph(){
    saveHistory();style();const c=center();ctx.save();ctx.font='72px ui-monospace';ctx.textAlign='center';ctx.fillStyle=color.value;
    ctx.fillText('-+ 0 0 +-',c.x,c.y);ctx.restore();state.commands.push({op:'ROOT0',at:Date.now()});saveHistory();
  }
  function perception(){
    saveHistory();style();const c=center();ctx.save();ctx.translate(c.x,c.y);ctx.textAlign='center';ctx.font='28px ui-monospace';ctx.fillStyle=color.value;
    ctx.fillText('PER  — did it happen?',0,-70);ctx.fillText('CEPT — are you sure?',0,0);ctx.fillText('ION  — ignite / patty',0,70);
    ctx.restore();state.commands.push({op:'PERCEPTION',at:Date.now()});saveHistory();
  }
  $('neonBtn').onclick=neon;$('pocketBtn').onclick=pocket;$('ouroBtn').onclick=ouro;$('rootGlyphBtn').onclick=rootGlyph;$('perceptionBtn').onclick=perception;

  function metadata(includePrivate=true){
    const base={
      schema:'OaSIs.Art.Root0.Arch.v00',
      architecture:{iso:'|',humanCarbon:'||',neon:'|||',root:'00',ring:'00-10',substrate:'-i',cortex:'+c'},
      creator:$('creator').value.trim(),
      carbonId:$('carbon').value.trim(),
      title:$('title').value.trim(),
      sourceToken:$('sourceToken').value.trim(),
      license:$('license').value.trim(),
      contribution:Number($('contribution').value||0),
      paymentRoute:$('payment').value.trim()||null,
      publicRelease:$('publicRelease').checked,
      commands:state.commands,
      createdAt:new Date().toISOString()
    };
    if(includePrivate) base.privatePocket={notes:$('privateNotes').value,canvasPng:canvas.toDataURL('image/png')};
    return base;
  }
  function download(name,blob){
    const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);
  }
  $('exportPngBtn').onclick=()=>canvas.toBlob(b=>download((($('title').value||'oasis-art').replace(/[^\w.-]+/g,'_'))+'.png',b),'image/png');
  $('exportProjectBtn').onclick=()=>download('oasis-private-project.json',new Blob([JSON.stringify(metadata(true),null,2)],{type:'application/json'}));
  $('exportPublicBtn').onclick=()=>{
    const m=metadata(false);
    if(!m.publicRelease){alert('Enable “Release public artifact” first.');return}
    download('oasis-public-provenance.json',new Blob([JSON.stringify(m,null,2)],{type:'application/json'}));
  };
  $('saveLocalBtn').onclick=()=>{localStorage.setItem('oasis-art-project',JSON.stringify(metadata(true)));alert('Saved locally in this browser.')};
  $('loadLocalBtn').onclick=()=>{const raw=localStorage.getItem('oasis-art-project');if(!raw)return alert('No local project found.');loadProject(JSON.parse(raw))};
  $('importProject').onchange=async e=>{const f=e.target.files[0];if(!f)return;loadProject(JSON.parse(await f.text()))};

  function loadProject(p){
    $('creator').value=p.creator||'';$('carbon').value=p.carbonId||'';$('title').value=p.title||'';
    $('sourceToken').value=p.sourceToken||'';$('license').value=p.license||'';$('contribution').value=p.contribution??10000;
    $('payment').value=p.paymentRoute||'';$('publicRelease').checked=!!p.publicRelease;
    $('privateNotes').value=p.privatePocket?.notes||'';state.commands=p.commands||[];
    if(p.privatePocket?.canvasPng) restore(p.privatePocket.canvasPng);
    updateRelease();
  }
  function updateRelease(){
    $('publicState').textContent=$('publicRelease').checked?'ON':'OFF';
    $('privateState').textContent='SEALED';
  }
  $('publicRelease').onchange=updateRelease;

  ctx.fillStyle='white';ctx.fillRect(0,0,canvas.width,canvas.height);
  ctx.fillStyle='#111';ctx.font='36px ui-monospace';ctx.textAlign='center';ctx.fillText('OaSIs / Root0 Arch',canvas.width/2,canvas.height/2-20);
  ctx.font='20px ui-monospace';ctx.fillText('| ISO    || HUMAN/CARBON    ||| NEON',canvas.width/2,canvas.height/2+30);
  saveHistory(); updateRelease();
})();