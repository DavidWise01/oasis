#!/usr/bin/env node
/* Zero-dependency verification against embedded engine in the HTML. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(path.join(__dirname,'..','index.html'),'utf8');
const source=html.match(/<script id="gyro-engine">([\s\S]*?)<\/script>/)?.[1];
assert.ok(source,'inline gyro-engine exists');
const scope={window:{}};vm.runInNewContext(source,scope);
const M=scope.window.GyroMath,base={rates:{v:0,w:0,x:360,y:360,z:720},levels:{G:3,R:3,B:3,P:3},zSlip:0};
let checks=0;const ok=(yes,name)=>{assert.ok(yes,name);checks++};
for(let k=0;k<=1440;k++){
 const m=M.model(base,k/1440);
 ok(m.residual<1e-12,'locked residual '+k);
 ok(m.containment>.9999999,'containment '+k);
 ok(Math.abs(m.emission-2)<1e-12,'constant emitted signal '+k);
 ok(!m.flare,'no false flares '+k);
 ok(m.id===255,'4^4 address '+k);
}
for(let n=0;n<256;n++){const levels=M.fromId(n);ok(M.stateId(levels)===n,'roundtrip '+n);ok(Object.values(levels).every(x=>x>=0&&x<=3),'base-four bounds '+n)}
const drift={rates:{...base.rates},levels:{...base.levels},zSlip:45};
for(const t of [0,.125,.25,.5,.75,1]){
 const m=M.model(drift,t);ok(m.residual>.30,'45 degree crown slip');ok(m.flare,'slip flare')
}
const weak={rates:{...base.rates},levels:{...base.levels,P:1},zSlip:0};
ok(M.model(weak,.25).residual>.3,'purple brace imbalance');
ok(M.model(weak,.25).flare,'purple brace flare');
const detune={rates:{...base.rates,x:390},levels:{...base.levels},zSlip:0};
ok(M.model(detune,0).residual<1e-12,'rate detuning initially aligned');
ok(M.model(detune,1).residual>.2,'rate detuning accumulates');
const crown={rates:{...base.rates,z:765},levels:{...base.levels},zSlip:0};
ok(M.model(crown,1).crown>.3,'two-to-one axial crown detune');
console.log(checks+'/'+checks+' PASS — five gyros, 256 states, 1,441 samples');
