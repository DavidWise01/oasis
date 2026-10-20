/* Deterministic sea-cable regression, Node >=18, no npm required */
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),assert=require('node:assert/strict');
const html=fs.readFileSync(path.join(__dirname,'..','index.html'),'utf8');
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)];
assert.ok(scripts.length>=3,'Both pure models and viewer present');
const context={window:{}};vm.runInNewContext(scripts[0][1],context);vm.runInNewContext(scripts[1][1],context);
const {GyroMath:G,SeaCableMath:N}=context.window;
const base={rates:{v:0,w:0,x:360,y:360,z:720},levels:{G:3,R:3,B:3,P:3},zSlip:0};
const cfg=N.defaults();let checks=0;
function ok(good,msg){assert.ok(good,msg);checks++}
for(let i=0;i<=4096;i++){
 const n=N.sample(base,i/64,cfg);
 ok(n.gyro.residual<1e-10,'gyro lock at '+i);
 ok(n.returnResidual<1e-10,'four matched paths at '+i);
 ok(n.combinedResidual<1e-10,'center zero at '+i);
 ok(!n.flare,'no false flare at '+i);
 if(i>=cfg.delay){ok(Math.abs(n.returned-2*cfg.attenuation)<1e-10,'nonzero returned light '+i);ok(n.ready,'return active '+i)}
}
for(let i=16;i<240;i++){
 const skew=N.sample(base,i/64,{...cfg,purpleExtra:8});
 ok(skew.returnResidual>.6,'purple delay imbalance at '+i);
 ok(skew.flare,'stress-driven flare at '+i);
 ok(skew.combinedResidual>.45,'return impacts core at '+i);
 const disconnected=N.sample(base,i/64,{...cfg,purpleExtra:8,coupled:false});
 ok(disconnected.combinedResidual<1e-9&&!disconnected.flare,'bypass at '+i);
}
ok(N.sample(base,2.5,{...cfg,purpleExtra:8,gain:0}).combinedResidual<1e-9,'gain zero');
for(let address=0;address<256;address++){
 const level=G.fromId(address);
 ok(G.stateId(level)===address,'state roundtrip '+address);
}
for(const extra of [0,1,3,5,8,12,16]){
 const n=N.sample(base,2,{...cfg,purpleExtra:extra});
 ok(extra===0?n.returnResidual<1e-10:n.returnResidual>.01,'delay sweep '+extra);
}
ok(N.sample({...base,levels:{G:2,R:3,B:1,P:3}},2,cfg).returnResidual>.2,'unequal petal return');
console.log('PASS '+checks+'/'+checks+' deterministic assertions (including 256 RGBP states)');
