import { AA20, DNA4, ANCESTOR, CODON_LAYERS, transformFrame } from './model.mjs';

const $ = id => document.getElementById(id);
const state = {
  tick:0, distill:24, rate:1, mode:'all', polarity:'+',
  mutations:new Set(), lostBases:new Set(), playing:false, trace:[],
  selectedIndex:0, selectedCodon:'GCT'
};
const canvas=$('chamber');
const ctx=canvas.getContext('2d',{alpha:false});
const prefersReduced=window.matchMedia('(prefers-reduced-motion: reduce)');
let sceneWidth=1,sceneHeight=1,frame=null,timer=null,origin=performance.now();

function logEvent(action,detail) {
  state.trace.unshift({tick:state.tick,action,detail});
  state.trace=state.trace.slice(0,11);
  $('events').replaceChildren();
  for (const item of state.trace) {
    const li=document.createElement('li');
    const num=document.createElement('span');
    num.textContent='T'+String(item.tick).padStart(3,'0');
    li.append(num,document.createTextNode(item.action+' · '+item.detail));
    $('events').append(li);
  }
}

function updateFrame(log=false) {
  frame=transformFrame({
    generation:state.tick,distill:state.distill,polarity:state.polarity,
    mutations:state.mutations,lostBases:state.lostBases
  });
  $('score').textContent=frame.fidelity+'/26';
  $('generation').textContent=String(state.tick).padStart(3,'0');
  $('mutations').textContent=String(frame.changed).padStart(2,'0');
  $('losses').textContent=String(frame.missing).padStart(2,'0');
  const tag=$('state-tag');
  tag.textContent=frame.state;
  tag.className='status-tag'+(frame.state==='DEGRADED'?' warn':frame.state==='UNKNOWN'?' fail':'');
  $('distill-value').textContent=String(Math.round(state.distill)).padStart(2,'0')+'%';
  $('time-value').textContent=state.rate.toFixed(2)+'×';
  $('polarity-value').textContent=state.polarity;
  $('hud-mode').textContent='FORM: '+({all:'{ ( [ ] ) }',amoeba:'{ }',toroid:'( [ ] )',box:'[ ]'}[state.mode]);
  $('hud-time').textContent='TICK: '+String(state.tick).padStart(3,'0')+' · OBSERVER RATE: '+state.rate.toFixed(2)+'×';
  $('hud-loss').textContent='DISTILLATION: '+String(Math.round(state.distill)).padStart(2,'0')+'%';
  $('lineage-note').textContent=frame.note;
  const symbols=frame.decoded.map(x=>x.observed??'·').join('');
  const carrier=frame.decoded.map(x=>x.codon).join(' ');
  $('frame-readout').textContent=[
    'ANCESTOR  '+ANCESTOR,
    'DECODED   '+symbols+'|'+DNA4.filter(x=>!state.lostBases.has(x)).join('')+'|−+',
    'CARRIER   '+carrier,
    'PROTECTED '+frame.matched+'/20 amino-acid identities · '+frame.basis+'/4 DNA bases · 2/2 operators',
    'CONTEXT   '+Math.max(0,100-state.distill).toFixed(0)+'% (symbolic non-core annotation)',
    'RESULT    '+frame.state+' · '+frame.fidelity+'/26'
  ].join('\n');
  for(const button of $('aa-grid').querySelectorAll('button')){
    const i=Number(button.dataset.index);
    const row=frame.decoded[i];
    button.classList.toggle('lost',row.observed===null);
    button.setAttribute('aria-pressed',String(state.mutations.has(i)));
    button.dataset.selected=String(state.selectedIndex===i);
    button.querySelector('small').textContent=row.codon;
    button.title=row.name+' · '+(row.match?'decoded intact':row.observed===null?'missing':'identity changed')+
       ' · click to '+(state.mutations.has(i)?'restore':'mutate');
    button.setAttribute('aria-label',button.title);
  }
  for(const button of $('bases').querySelectorAll('button')){
    button.setAttribute('aria-pressed',String(state.lostBases.has(button.dataset.base)));
  }
  $('aa-summary').textContent=frame.matched+'/20 residue identities decoded · tap to select and mutate / restore';
  updateCodonInspector();
  if(log) logEvent(frame.state,'AA '+frame.matched+'/20 · bases '+frame.basis+'/4 · rate '+state.rate.toFixed(2)+'×');
  if(prefersReduced.matches)drawScene(performance.now());
}

function buildCodonCube(){
  const host=$('codon-layers');
  // n chooses the highlighted translation target; one common 4×4×4 field
  // exists under every amino acid, never sixty-four codons per residue.
  for(const layer of CODON_LAYERS){
    const section=document.createElement('section');
    section.className='codon-layer';
    section.setAttribute('aria-label','First base '+layer.base+', 16 codons');
    const heading=document.createElement('div');
    heading.className='codon-layer-title';
    const first=document.createElement('span');
    first.textContent='FIRST BASE / '+layer.base;
    const tally=document.createElement('span');tally.className='micro';
    tally.textContent='4 × 4 = 16';
    heading.append(first,tally);
    const grid=document.createElement('div');grid.className='codon-grid';
    for(const item of layer.codons){
      const b=document.createElement('button');
      b.className='codon-cell';b.type='button';
      b.dataset.codon=item.codon;
      b.dataset.meaning=item.meaning;
      b.dataset.first=item.first;
      b.dataset.second=item.second;
      b.dataset.third=item.third;
      const code=document.createElement('strong');
      code.textContent=item.codon;
      const meaning=document.createElement('small');
      meaning.textContent=item.meaning==='STOP'?'STOP':item.meaning;
      b.append(code,meaning);
      b.addEventListener('click',()=>{
        state.selectedCodon=item.codon;
        if(!item.isStop){
          const i=AA20.findIndex(x=>x.code===item.meaning);
          if(i>=0)state.selectedIndex=i;
        }
        updateFrame();
        logEvent('CODON '+item.codon,
          item.isStop?'STOP / termination signal':
          'Decodes to '+AA20[state.selectedIndex].name+' ('+item.meaning+')');
      });
      grid.append(b);
    }
    section.append(heading,grid);
    host.append(section);
  }
}

function updateCodonInspector(){
  const residue=AA20[state.selectedIndex]||AA20[0];
  const picked=CODON_LAYERS.flatMap(x=>x.codons).find(x=>x.codon===state.selectedCodon);
  $('codon-parent').textContent=String(state.selectedIndex+1).padStart(2,'0')+
    ' · '+residue.name+' ('+residue.code+')';
  $('codon-selected').textContent=picked?.codon??'—';
  const unavailable=picked&&[...picked.codon].some(base=>state.lostBases.has(base));
  $('codon-explanation').textContent=!picked?'No DNA triplet selected.':
    picked.isStop?picked.codon+' is a STOP codon, signalling translation termination.':
    picked.codon+' decodes to '+AA20.find(x=>x.code===picked.meaning)?.name+
    ' ('+picked.meaning+'). '+(unavailable?'This carrier contains a currently removed base.':
      picked.meaning===residue.code?'It encodes selected n.':'Selecting it changes the inspected n.');
  $('codon-synonyms').textContent='n = '+residue.code+' · '+
    residue.codons.length+' of 64 codons: '+residue.codons.join(' · ');
  for(const b of $('codon-layers').querySelectorAll('button')){
    const codon=b.dataset.codon;
    b.dataset.match=String(residue.codons.includes(codon));
    b.dataset.active=String(codon===state.selectedCodon);
    b.dataset.unavailable=String([...codon].some(base=>state.lostBases.has(base)));
    b.dataset.stop=String(b.dataset.meaning==='STOP');
    b.setAttribute('aria-pressed',String(codon===state.selectedCodon));
    b.setAttribute('aria-label',codon+' → '+(b.dataset.meaning==='STOP'?'translation stop':
       b.dataset.meaning)+'; '+(residue.codons.includes(codon)?'matches selected residue':
       'different residue')+(b.dataset.unavailable==='true'?'; base missing':''));
  }
}

function buildSymbols(){
  const grid=$('aa-grid');
  AA20.forEach((acid,i)=>{
    const b=document.createElement('button');
    b.type='button';
    b.className='aa';
    b.dataset.index=String(i);
    const letter=document.createElement('strong');letter.textContent=acid.code;
    const codon=document.createElement('small');codon.textContent=acid.codons[0];
    b.append(letter,codon);
    b.addEventListener('click',()=>{
      state.selectedIndex=i;
      state.selectedCodon=acid.codons[0];
      if(state.mutations.has(i))state.mutations.delete(i);
      else state.mutations.add(i);
      updateFrame();
      logEvent(state.mutations.has(i)?'MUTATE '+acid.code:'RESTORE '+acid.code,
        state.mutations.has(i)?'Codon rewritten to a different residue':'Ancestral residue identity restored');
    });
    grid.append(b);
  });
  const basebox=$('bases');
  DNA4.forEach(base=>{
    const b=document.createElement('button');
    b.type='button';b.className='base';b.textContent=base;b.dataset.base=base;
    b.addEventListener('click',()=>{
      if(state.lostBases.has(base)) state.lostBases.delete(base);
      else state.lostBases.add(base);
      updateFrame();logEvent('DNA '+base,state.lostBases.has(base)?'Carrier base removed':'Carrier base restored');
    });
    basebox.append(b);
  });
}

function pressState(selector,key,value){
  document.querySelectorAll(selector).forEach(b=>
    b.setAttribute('aria-pressed',String(b.dataset[key]===value)));
}
function stopPlayback(){
  if(timer!==null){clearTimeout(timer);timer=null}
  state.playing=false;
  $('play').textContent='▶ PLAY';
  $('play').setAttribute('aria-pressed','false');
}
function queueTick(){
  if(!state.playing)return;
  timer=setTimeout(()=>{
    state.tick+=1;
    updateFrame();
    logEvent('REFOLD',frame.state+' · synonymous carrier cycle '+state.tick);
    queueTick();
  },Math.max(180,Math.round(980/state.rate)));
}
function startPlayback(){
  state.playing=true;
  $('play').textContent='Ⅱ PAUSE';
  $('play').setAttribute('aria-pressed','true');
  queueTick();
}
function feedback(message){$('action-feedback').textContent=message}

function bindControls(){
  $('distill').addEventListener('input',e=>{
    state.distill=Number(e.target.value);updateFrame();
  });
  $('distill').addEventListener('change',()=>{
    logEvent('DISTILL '+state.distill+'%',frame.state);
  });
  $('time-rate').addEventListener('input',e=>{
    state.rate=Number(e.target.value);
    updateFrame();
    if(state.playing){clearTimeout(timer);queueTick()}
  });
  $('time-rate').addEventListener('change',()=>logEvent('CLOCK',state.rate.toFixed(2)+'× observer rate'));
  document.querySelectorAll('[data-polarity]').forEach(b=>b.addEventListener('click',()=>{
    state.polarity=b.dataset.polarity;
    pressState('[data-polarity]','polarity',state.polarity);
    updateFrame();logEvent('OPERATOR',state.polarity==='+'?'Forward codon mapping':'Reverse codon mapping');
  }));
  document.querySelectorAll('[data-mode]').forEach(b=>b.addEventListener('click',()=>{
    state.mode=b.dataset.mode;
    pressState('[data-mode]','mode',state.mode);
    updateFrame();
    logEvent('VIEW',state.mode+' glyph projection');
  }));
  $('step').addEventListener('click',()=>{
    state.tick+=1;updateFrame();
    logEvent('REFOLD',frame.state+' · manual generation '+state.tick);
  });
  $('play').addEventListener('click',()=>state.playing?stopPlayback():startPlayback());
  $('repair').addEventListener('click',()=>{
    stopPlayback();
    state.tick=0;state.distill=24;state.rate=1;state.polarity='+';state.mode='all';
    state.mutations.clear();state.lostBases.clear();
    state.selectedIndex=0;state.selectedCodon='GCT';
    $('distill').value='24';$('time-rate').value='1';
    pressState('[data-polarity]','polarity','+');pressState('[data-mode]','mode','all');
    state.trace=[];updateFrame();logEvent('GENESIS','LUCA-26 ancestral reference restored');
    feedback('Restored symbolic ancestor. The previous session trace was reset by request.');
  });
  $('copy').addEventListener('click',async()=>{
    const dump=[
      'KET :: LUCA-26 / TEMPORAL LINEAGE',
      'Glyph: { ( [ 20 AA | ACTG | −+ ] ) }',
      'Note: invented symbolic ancestor, not a reconstructed LUCA sequence.',
      $('frame-readout').textContent,
      ...state.trace.map(e=>'T'+e.tick+' '+e.action+' '+e.detail)
    ].join('\n');
    try{await navigator.clipboard.writeText(dump);feedback('Copied the current symbolic lineage and session trace.')}
    catch(e){feedback('Clipboard unavailable; select and copy the decoded carrier readout.')}
  });
  document.addEventListener('visibilitychange',()=>{
    if(document.hidden&&state.playing){stopPlayback();feedback('Playback paused while tab was hidden.')}
  });
}

function resize(){
  if(!ctx)return;
  const rect=canvas.getBoundingClientRect();
  sceneWidth=Math.max(1,rect.width);
  sceneHeight=Math.max(1,rect.height);
  const dpr=Math.min(2,window.devicePixelRatio||1);
  canvas.width=Math.floor(sceneWidth*dpr);
  canvas.height=Math.floor(sceneHeight*dpr);
  ctx.setTransform(dpr,0,0,dpr,0,0);
  if(prefersReduced.matches)drawScene(performance.now());
}
function ellipseArc(cx,cy,rx,ry,start,end){
  ctx.beginPath();ctx.ellipse(cx,cy,rx,ry,0,start,end);ctx.stroke();
}
function drawAmoeba(cx,cy,time,rad){
  ctx.save();
  const soft=ctx.createRadialGradient(cx,cy,rad*.38,cx,cy,rad*1.23);
  soft.addColorStop(0,'rgba(168,92,255,.014)');
  soft.addColorStop(.8,'rgba(150,86,234,.036)');
  soft.addColorStop(1,'rgba(159,100,250,0)');
  ctx.fillStyle=soft;ctx.beginPath();ctx.arc(cx,cy,rad*1.3,0,Math.PI*2);ctx.fill();
  for(let shell=0;shell<2;shell++){
    ctx.beginPath();
    for(let i=0;i<=180;i++){
      const a=i*Math.PI*2/180;
      const w=(Math.sin(a*5+time*.6)+.5*Math.sin(a*11-time*.42)+.29*Math.cos(a*17+time*.7))*rad*.033;
      const rr=rad*(shell?1:.92)+w;
      const x=cx+Math.cos(a)*rr,y=cy+Math.sin(a)*rr*.81;
      if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
    }
    ctx.closePath();
    ctx.strokeStyle=shell?'rgba(208,120,255,.52)':'rgba(120,165,255,.37)';
    ctx.shadowColor='#b071ff';ctx.shadowBlur=shell?17:6;ctx.lineWidth=shell?2.1:1;
    ctx.stroke();
    if(shell){ctx.fillStyle='rgba(127,68,207,.044)';ctx.fill();}
  }
  for(let i=0;i<34;i++){
    const a=i*2.3999+time*.018,rr=rad*(.86+.13*Math.sin(i*8.1+time*.3));
    const x=cx+rr*Math.cos(a),y=cy+rr*.81*Math.sin(a);
    ctx.fillStyle=i%3?'rgba(209,149,250,.25)':'rgba(97,235,252,.40)';
    ctx.beginPath();ctx.arc(x,y,i%5===0?2.6:1.3,0,Math.PI*2);ctx.fill();
  }
  ctx.restore();
}
function project(x,y,z,rotY,rotX,cx,cy,scale){
  const ay=Math.cos(rotY),by=Math.sin(rotY);
  const ax=Math.cos(rotX),bx=Math.sin(rotX);
  const px=x*ay-z*by,pz=x*by+z*ay;
  const py=y*ax-pz*bx,depth=y*bx+pz*ax;
  const perspective=3.2/(3.2+depth*.29);
  return [cx+px*scale*perspective,cy+py*scale*perspective,depth];
}
function drawToroid(cx,cy,time,scale){
  const rotY=time*.43;
  const rotX=-.75+Math.sin(time*.17)*.17;
  const ring=(u,v)=>{
    const R=1.20,r=.43;
    return project((R+r*Math.cos(v))*Math.cos(u),
      (R+r*Math.cos(v))*Math.sin(u),r*Math.sin(v),rotY,rotX,cx,cy,scale);
  };
  ctx.save();
  ctx.globalCompositeOperation='screen';
  for(let j=0;j<17;j++){
    const v=j*Math.PI*2/17;
    ctx.beginPath();
    for(let i=0;i<=150;i++){
      const p=ring(i*Math.PI*2/150,v);
      if(i===0)ctx.moveTo(p[0],p[1]);else ctx.lineTo(p[0],p[1]);
    }
    const light=.18+.26*(.5+.5*Math.cos(v+time*.2));
    ctx.strokeStyle=j%3===0?'rgba(114,242,221,'+light+')':'rgba(80,170,255,'+light+')';
    ctx.lineWidth=j%3===0?1.7:.8;
    ctx.shadowBlur=j%3===0?9:0;ctx.shadowColor='#5de2ff';
    ctx.stroke();
  }
  for(let j=0;j<44;j++){
    const u=j*Math.PI*2/44;
    ctx.beginPath();
    for(let i=0;i<=50;i++){
      const p=ring(u,i*Math.PI*2/50);
      if(i===0)ctx.moveTo(p[0],p[1]);else ctx.lineTo(p[0],p[1]);
    }
    ctx.shadowBlur=j%7===0?11:0;
    ctx.strokeStyle=j%4===0?'rgba(192,125,255,.47)':'rgba(101,185,255,.20)';
    ctx.lineWidth=j%7===0?1.4:.7;ctx.stroke();
  }
  for(let k=0;k<26;k++){
    const u=(k/26)*Math.PI*2+time*(state.polarity==='+'?.15:-.15);
    const v=(k*1.618%1)*Math.PI*2;
    const p=ring(u,v),c=k<20?'#d0a0ff':k<24?'#8ef0ff':'#ffd5a7';
    ctx.beginPath();ctx.fillStyle=c;ctx.shadowColor=c;ctx.shadowBlur=k%4===0?13:6;
    ctx.arc(p[0],p[1],k<20?2.15:3.1,0,Math.PI*2);ctx.fill();
  }
  ctx.restore();
}
function drawCenterBox(cx,cy,time,size){
  const bw=size*1.17,bh=size*.94;
  ctx.save();ctx.translate(cx,cy);
  ctx.rotate(state.mode==='box'?0:Math.sin(time*.23)*.045);
  for(let i=3;i>=1;i--){
    ctx.save();
    ctx.rotate(i*.11+Math.sin(time*.18)*.025);
    ctx.strokeStyle='rgba(121,198,255,'+(.075+.025*i)+')';
    ctx.lineWidth=1;ctx.strokeRect(-bw*.49-i*6,-bh*.51-i*5,bw+i*12,bh+i*10);
    ctx.restore();
  }
  ctx.shadowColor=frame?.state==='PRESERVED'?'#72f6b5':frame?.state==='DEGRADED'?'#ffbf7a':'#ff708f';
  ctx.shadowBlur=30;
  const bg=ctx.createLinearGradient(-bw/2,-bh/2,bw/2,bh/2);
  bg.addColorStop(0,'rgba(23,31,66,.96)');bg.addColorStop(1,'rgba(17,31,52,.98)');
  ctx.fillStyle=bg;ctx.strokeStyle=frame?.state==='PRESERVED'?'#80f1c3':frame?.state==='DEGRADED'?'#ffbf7a':'#ff708f';
  ctx.lineWidth=2;ctx.beginPath();
  if(ctx.roundRect)ctx.roundRect(-bw/2,-bh/2,bw,bh,9);
  else ctx.rect(-bw/2,-bh/2,bw,bh);
  ctx.fill();ctx.stroke();ctx.shadowBlur=0;
  ctx.textAlign='center';ctx.textBaseline='middle';
  ctx.fillStyle='#afe2e9';ctx.font='700 '+Math.max(11,Math.round(size*.085))+'px ui-monospace,monospace';
  ctx.fillText('LUCA · 26',0,-bh*.36);
  const rows=[frame?frame.decoded.slice(0,10).map(d=>d.observed??'·').join(' '):'',
    frame?frame.decoded.slice(10).map(d=>d.observed??'·').join(' '):''];
  ctx.fillStyle='#ead7ff';ctx.font=Math.max(10,Math.round(size*.078))+'px ui-monospace,monospace';
  ctx.fillText(rows[0],0,-bh*.12);ctx.fillText(rows[1],0,bh*.10);
  ctx.fillStyle='#98dfeb';ctx.font='700 '+Math.max(12,Math.round(size*.096))+'px ui-monospace,monospace';
  ctx.fillText(DNA4.filter(x=>!state.lostBases.has(x)).join('')+'  |  −+',0,bh*.31);
  ctx.restore();
}
function drawCodonSubstrate(cx,cy,time,span){
  // Visual 4×4×4 carrier layer UNDER n and its invariant box.
  // First, second, third bases are the three projected cube axes.
  ctx.save();
  const residue=AA20[state.selectedIndex]||AA20[0];
  const pts=CODON_LAYERS.flatMap(layer=>layer.codons).map(item=>{
    const [a,b,c]=item.coordinate;
    const wobble=Math.sin(time*.33)*.08;
    const x=(b-1.5)*span*.42+(a-1.5)*span*(.23+wobble);
    const y=(c-1.5)*span*.22+(a-1.5)*span*.15;
    return {...item,x:cx+x,y:cy+y};
  });
  ctx.strokeStyle='rgba(105,182,243,.24)';
  ctx.lineWidth=.7;
  for(const p of pts){
    const [a,b,c]=p.coordinate;
    if(b<3){
      const q=pts.find(x=>x.coordinate[0]===a&&x.coordinate[1]===b+1&&x.coordinate[2]===c);
      if(q){ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(q.x,q.y);ctx.stroke();}
    }
    if(c<3){
      const q=pts.find(x=>x.coordinate[0]===a&&x.coordinate[1]===b&&x.coordinate[2]===c+1);
      if(q){ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(q.x,q.y);ctx.stroke();}
    }
  }
  for(const p of pts){
    const matched=residue.codons.includes(p.codon);
    const unavailable=[...p.codon].some(letter=>state.lostBases.has(letter));
    const active=p.codon===state.selectedCodon;
    const color=p.isStop?'#ff7c9f':matched?'#65ffd0':'#73b5e2';
    ctx.beginPath();ctx.arc(p.x,p.y,active?3.8:matched?2.8:1.5,0,Math.PI*2);
    ctx.fillStyle=color;ctx.globalAlpha=unavailable?0.22:((matched||active)?1:0.55);
    if(active||matched){ctx.shadowBlur=active?14:9;ctx.shadowColor=color;}
    ctx.fill();ctx.shadowBlur=0;
  }
  ctx.globalAlpha=1;
  ctx.fillStyle='#add0ed';ctx.textAlign='center';
  ctx.font='10px ui-monospace,monospace';
  ctx.fillText('{{n}} ↓ {{4³}} · 64 TRIPLETS',cx,cy+span*.65);
  ctx.restore();
}

function drawScene(ts){
  if(!ctx)return;
  const w=sceneWidth,h=sceneHeight;
  ctx.clearRect(0,0,w,h);
  const bg=ctx.createRadialGradient(w*.5,h*.50,8,w*.5,h*.51,Math.max(w,h)*.7);
  bg.addColorStop(0,'#14253e');bg.addColorStop(.60,'#0b1430');bg.addColorStop(1,'#070e21');
  ctx.fillStyle=bg;ctx.fillRect(0,0,w,h);
  const time=prefersReduced.matches?1.7:(ts-origin)*.001*state.rate;
  const cx=w*.50,cy=h*.53;
  const dimension=Math.min(w,h);
  for(let k=0;k<75;k++){
    const px=((k*179.6+53)%997)/997*w,py=((k*317.8+89)%997)/997*h;
    const p=.25+.4*(.5+.5*Math.sin(time*.44+k));
    ctx.fillStyle='rgba(157,215,255,'+p.toFixed(2)+')';ctx.fillRect(px,py,1.1,1.1);
  }
  const amoeba=state.mode==='all'||state.mode==='amoeba';
  const toroid=state.mode==='all'||state.mode==='toroid';
  const box=state.mode==='all'||state.mode==='box'||state.mode==='toroid';
  if(amoeba)drawAmoeba(cx,cy,time,dimension*.46);
  if(toroid)drawToroid(cx,cy,time,dimension*.22);
  if(box)drawCenterBox(cx,cy,time,Math.max(105,dimension*(state.mode==='box'?.48:.34)));
  if(box)drawCodonSubstrate(cx,Math.min(h-83,cy+dimension*.35),time,dimension*.13);
  ctx.save();
  ctx.textAlign='center';
  ctx.fillStyle='#b0cce5';ctx.font='10px ui-monospace,monospace';
  ctx.fillText(state.mode==='all'?'{ AMOEBA → ( TOROID → [ INVARIANT ] ) }':
    ({amoeba:'{ ADAPTIVE FIELD }',toroid:'( TIME / DISTILLATION VESSEL )',box:'[ ANCESTRAL REGISTER ]'}[state.mode]),cx,h-21);
  ctx.restore();
}
function animation(t){drawScene(t);if(!prefersReduced.matches)requestAnimationFrame(animation)}

buildSymbols();
buildCodonCube();
bindControls();
updateFrame();
logEvent('GENESIS','20 AA | ACTG | −+ instantiated');
resize();
if(typeof ResizeObserver!=='undefined')new ResizeObserver(resize).observe(canvas);
else window.addEventListener('resize',resize);
if(!prefersReduced.matches)requestAnimationFrame(animation);
