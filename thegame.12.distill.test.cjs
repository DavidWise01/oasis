'use strict';
// node --test thegame.12.distill.test.cjs
// Optional real browser run: DISTILL_BROWSER_CHECK=1 node --test thegame.12.distill.test.cjs
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const E=require('./thegame.12.distill.engine.js');
const stage=i=>i===0?E.initial():E.apply(E.initial(),{type:'level',level:i});
function finish(s){const result=E.solve(s);assert.equal(result.status,'solved');for(const action of result.actions)s=E.apply(s,action);return s;}

for(let i=0;i<E.LEVELS.length;i++)test('level '+(i+1)+' '+E.LEVELS[i].name+' reaches gi at par within its pulse budget',()=>{
  const start=stage(i),route=E.solve(start);let s=start;
  assert.equal(route.status,'solved');assert.ok(route.nodes<30000);
  assert.equal(route.actions.length,E.LEVELS[i].par);
  for(const action of route.actions)s=E.apply(s,action);
  assert.equal(E.phase(s),'solved');assert.equal(E.word(s.cells),'gi');assert.equal(E.count(s.cells),2);
  assert.ok(s.spent<=E.LEVELS[i].budget);assert.equal(s.moves,E.LEVELS[i].par);
  assert.equal(E.stars(s),3);assert.deepEqual(s.best[i],{stars:3,moves:E.LEVELS[i].par,pulses:s.spent});
  assert.deepEqual(E.restore(E.save(s)),s);
});

test('the final stage preserves David’s exact six-box stack',()=>{
  const s=stage(5);assert.deepEqual(Array.from({length:6},(_,i)=>s.cells.slice(i*2,i*2+2).map(E.letter).join('')),['gh','ab','mn','ab','mn','ab']);
  assert.equal(E.LEVELS[5].budget,6);
});

test('illegal shifts and matches leave the original state and register intact',()=>{
  const s=E.initial(),before=E.save(s);
  for(const action of [{type:'shift',index:2,delta:-1},{type:'shift',index:0,delta:2},{type:'shift',index:99,delta:1},{type:'ablate',a:0,b:1},{type:'level',level:6}])assert.throws(()=>E.apply(s,action));
  assert.equal(E.save(s),before);assert.throws(()=>{s.cells[0]=2;},TypeError);
});

test('crossed-wire diagonals reject even when both numbers are equal',()=>{
  const s=stage(2);assert.equal(s.cells[0],s.cells[3]);assert.equal(s.cells[1],s.cells[2]);
  assert.throws(()=>E.apply(s,{type:'ablate',a:0,b:3}),/within one X/);
  assert.throws(()=>E.apply(s,{type:'ablate',a:1,b:2}),/within one X/);
});

test('matching numbers across an X boundary cannot ablate',()=>{
  let s=E.initial();s=E.apply(s,{type:'shift',index:0,delta:1});
  // Equal-letter pairs from distant rows are never an edge, regardless of value.
  const custom={...s,cells:s.cells.map((v,i)=>i===4?s.cells[2]:v)};
  assert.equal(custom.cells[2],custom.cells[4]);
  assert.throws(()=>E.apply(custom,{type:'ablate',a:2,b:4}),/within one X/);
});

test('horizontal removal leaves holes and never collapses an unrelated box',()=>{
  const s=E.apply(E.initial(),{type:'ablate',a:2,b:3});
  assert.deepEqual(s.cells.slice(0,6),[7,8,0,0,13,13]);assert.equal(E.count(s.cells),10);
  assert.throws(()=>E.apply(s,{type:'ablate',a:2,b:3}));
});

test('vertical removal compresses each column in order and conserves survivors',()=>{
  const before=stage(1),after=E.apply(before,{type:'ablate',a:4,b:6});
  assert.deepEqual(after.cells,[1,1,2,2,4,7,5,9,0,4,0,5]);
  assert.equal(E.count(before.cells)-E.count(after.cells),2);
  assert.equal(after.moves,1);assert.equal(after.spent,0);
  assert.match(after.register.at(-1).detail,/compress/);
});

test('a used pulse cannot be spent again after the budget is exhausted',()=>{
  let s=E.initial();for(let i=0;i<3;i++)s=E.apply(s,{type:'shift',index:0,delta:1});
  assert.equal(E.remaining(s),0);assert.throws(()=>E.apply(s,{type:'shift',index:0,delta:1}),/No pulses/);
  assert.equal(E.solve(s).status,'no-solution');
});

test('undo returns the board, moves and energy without deleting register entries',()=>{
  const start=E.initial(),one=E.apply(start,{type:'shift',index:1,delta:1});
  const two=E.apply(one,{type:'ablate',a:2,b:3}),undo=E.apply(two,{type:'undo'}),back=E.apply(undo,{type:'undo'});
  assert.deepEqual(undo.cells,one.cells);assert.equal(undo.spent,one.spent);assert.equal(undo.moves,one.moves);
  assert.deepEqual(back.cells,start.cells);assert.equal(back.spent,0);assert.equal(back.moves,0);
  assert.equal(back.register.length,4);assert.deepEqual(back.register.slice(0,2),two.register);
  assert.throws(()=>E.apply(back,{type:'undo'}),/No move/);assert.deepEqual(E.restore(E.save(back)),back);
});

test('hint plans are legal after alternative moves, not just from the starting seed',()=>{
  for(let level=0;level<6;level++){
    let s=stage(level);const alternatives=E.pairs(s.cells);
    if(alternatives.length){const e=alternatives.at(-1);s=E.apply(s,{type:'ablate',a:e.a,b:e.b});}
    const route=E.solve(s);
    if(route.status==='solved'){for(const action of route.actions)s=E.apply(s,action);assert.equal(E.phase(s),'solved');}
    else assert.equal(route.status,'no-solution');
  }
});

test('bounded search reports a limit instead of a fabricated hint',()=>{
  const limited=E.solve(E.initial(),0);assert.equal(limited.status,'limit');assert.deepEqual(limited.actions,[]);
});

test('hint use reduces the award and cannot be undone away',()=>{
  const hint=E.apply(E.initial(),{type:'hint'}),s=finish(hint);assert.equal(E.stars(s),2);assert.equal(s.best[0].stars,2);
  const undone=E.apply(s,{type:'undo'});assert.equal(undone.hints,1);
  const twice=finish(E.apply(E.apply(E.initial(),{type:'hint'}),{type:'hint'}));assert.equal(E.stars(twice),1);
});

test('less efficient completion earns two stars; best results survive retry',()=>{
  let s=E.apply(E.initial(),{type:'shift',index:0,delta:1});s=E.apply(s,{type:'shift',index:0,delta:-1});s=finish(s);
  assert.equal(s.moves,8);assert.equal(E.stars(s),2);
  s=E.apply(s,{type:'restart'});assert.equal(s.best[0].stars,2);assert.equal(s.moves,0);assert.equal(s.spent,0);
  s=finish(s);assert.equal(s.best[0].stars,3);assert.equal(s.best[0].moves,6);
  const best=s.best;s=E.apply(s,{type:'undo'});assert.deepEqual(s.best,best);
});

test('entire campaign scores 18 stars and reloads from its replay register',()=>{
  let s=E.initial();
  for(let i=0;i<6;i++){if(i)s=E.apply(s,{type:'level',level:i});s=finish(s);}
  assert.equal(Object.values(s.best).reduce((total,b)=>total+b.stars,0),18);
  assert.deepEqual(E.restore(E.save(s)),s);
  assert.throws(()=>E.apply(s,{type:'shift',index:0,delta:1}),/stopped/);
});

test('corrupt saves, changed outcomes and skipped ordinals fail replay',()=>{
  const original=finish(E.initial());
  for(const mutate of [x=>x.version='wrong',x=>x.register[0].after='{}',x=>x.register[0].seq=9,x=>x.register[0].detail='renamed']){
    const data=JSON.parse(E.save(original));mutate(data);assert.throws(()=>E.restore(JSON.stringify(data)));
  }
  assert.throws(()=>E.restore('not JSON'));
});

test('page JavaScript parses and references the delivered campaign engine',()=>{
  const html=fs.readFileSync(path.join(__dirname,'thegame.12.distill.html'),'utf8');
  assert.ok(html.includes('src="./thegame.12.distill.engine.js"'));
  const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];assert.equal(scripts.length,1);
  for(const [,script]of scripts)new vm.Script(script);
});

test('browser: direct play, hint, undo, progression, sound, export and mobile layout',{
  skip:process.env.DISTILL_BROWSER_CHECK==='1'?false:'Optional: requires Playwright and Chromium.'
},async()=>{
  const http=require('node:http'),{chromium}=require('playwright');
  const server=http.createServer((req,res)=>{const name=req.url==='/'?'thegame.12.distill.html':req.url.slice(1);if(!['thegame.12.distill.html','thegame.12.distill.engine.js'].includes(name)){res.writeHead(404);res.end();return;}res.setHeader('Content-Type',name.endsWith('.js')?'application/javascript':'text/html');res.end(fs.readFileSync(path.join(__dirname,name)));});
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));let browser;
  try{
    browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1200,height:1050}}),errors=[];
    page.on('pageerror',e=>errors.push(e.message));await page.goto('http://127.0.0.1:'+server.address().port);
    assert.equal(await page.locator('[data-cell]').count(),12);assert.equal(await page.locator('[data-level]').count(),6);
    await page.locator('[data-cell="1"]').click();await page.locator('#plus').click();
    assert.match(await page.locator('[data-cell="1"]').getAttribute('aria-label'),/i, number 9/);
    await page.locator('#undo').click();assert.match(await page.locator('[data-cell="1"]').getAttribute('aria-label'),/h, number 8/);
    await page.locator('#hint').click();await page.waitForFunction(()=>!document.querySelector('#hint').disabled);
    assert.ok(await page.locator('.hint').count()>0);
    await page.locator('#retry').click();
    const route=E.solve(E.initial()).actions;let sim=E.initial();
    for(const a of route){
      if(a.type==='shift'){await page.locator('[data-cell="'+a.index+'"]').click();await page.locator(a.delta>0?'#plus':'#minus').click();}
      else{
        const selected=Number(await page.locator('.tile.selected').getAttribute('data-cell'));
        if(selected===a.a)await page.locator('[data-cell="'+a.b+'"]').click();
        else if(selected===a.b)await page.locator('[data-cell="'+a.a+'"]').click();
        else{await page.locator('[data-cell="'+a.a+'"]').click();await page.locator('[data-cell="'+a.b+'"]').click();}
      }
      sim=E.apply(sim,a);
    }
    assert.equal(await page.locator('#finish').isVisible(),true);assert.equal(await page.locator('#win-stars').textContent(),'★★★');
    await page.reload();assert.equal(await page.locator('#finish').isVisible(),true);assert.match(await page.locator('#total-stars').textContent(),/3 \/ 18/);
    const downloading=page.waitForEvent('download');await page.locator('#export').click();const download=await downloading;const chunks=[];for await(const chunk of await download.createReadStream())chunks.push(chunk);
    assert.equal(E.phase(E.restore(Buffer.concat(chunks).toString('utf8'))),'solved');
    await page.locator('#next').click();assert.equal(await page.locator('#level-name').textContent(),'The drop');
    await page.locator('#sound').click();assert.equal(await page.locator('#sound').getAttribute('aria-pressed'),'true');
    await page.setViewportSize({width:390,height:844});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true);
    if(process.env.DISTILL_SCREENSHOT)await page.screenshot({path:process.env.DISTILL_SCREENSHOT,fullPage:true});
    assert.deepEqual(errors,[]);
  }finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
});
