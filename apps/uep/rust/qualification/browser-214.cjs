// UEP-214R: browser qualification, with explicit binary provenance limitation. .dlw
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');
const base=process.argv[2], binary=process.argv[3], mode=process.argv[4]||'full';
if(!base||!['full','negative'].includes(mode))throw Error('usage: browser URL binary-path full|negative');
const results=[];
const mark=(name)=>results.push(name);
async function status(page,s){await page.waitForFunction(x=>document.querySelector('#status').textContent.includes(x),s);}
async function empty(p){for(const id of ['due','carbon','ai'])assert.equal(await p.locator('#'+id).textContent(),'—');}
async function main(){
 const b=await chromium.launch({headless:true});
 try{
  if(mode==='full'){
   const p=await b.newPage();const errors=[];p.on('pageerror',e=>errors.push(String(e)));
   await p.goto(base);await status(p,'RUST WASM ACTIVE');
   for(const [id,value] of [['due','$20.50'],['carbon','$16.40'],['ai','$4.10']])assert.equal(await p.locator('#'+id).textContent(),value);
   mark('canonical native outputs');
   for(const v of ['bad','-1','1.2','18446744073709551616','']){
    await p.locator('#v').fill(v);await status(p,'HOLD');await empty(p);
   }mark('five invalid valuations clear all outputs');
   await p.locator('#v').fill('10000');await status(p,'RUST WASM ACTIVE');assert.equal(await p.locator('#due').textContent(),'$20.50');mark('valid input recovery');
   await p.locator('#n').fill('999');assert.equal(await p.locator('#due').textContent(),'$0.00');mark('negative boundary');
   await p.locator('#n').fill('0');await p.locator('#p').fill('0');assert.equal(await p.locator('#due').textContent(),'$0.00');mark('positive boundary');
   assert.deepEqual(errors,[]);mark('no uncaught page errors');
   await p.close();
  }
  for(const kind of ['missing','corrupt','empty-module']){
   const p=await b.newPage();
   await p.route('**/*.wasm',r=>kind==='missing'?r.fulfill({status:404,body:'missing'}):r.fulfill({status:200,contentType:'application/wasm',body:kind==='corrupt'?Buffer.from('invalid'):Buffer.from([0,97,115,109,1,0,0,0])}));
   await p.goto(base);
   await p.waitForFunction(()=>{const s=document.querySelector('#status').textContent;return s.includes('HOLD')&&!s.includes('loading')});
   await empty(p);await p.locator('#v').fill('99999');await empty(p);mark(kind+' binary fails closed after input change');await p.close();
  }
  console.log(JSON.stringify({mode,results,binarySha256:mode==='full'?crypto.createHash('sha256').update(fs.readFileSync(binary)).digest('hex'):null,actualPayments:0},null,2));
 }finally{await b.close()}
}
main().catch(e=>{console.error(e);process.exitCode=1});
