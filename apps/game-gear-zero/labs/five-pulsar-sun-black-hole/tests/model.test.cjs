#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),assert=require('node:assert/strict');
const html=fs.readFileSync(path.resolve(__dirname,'../index.html'),'utf8');
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
assert.equal(scripts.length,4);
const env={window:{}};for(const script of scripts.slice(0,3))vm.runInNewContext(script,env);
const {GyroMath:M,SeaCableMath:SEA,PulsarGroundMath:PG}=env.window;
const base={rates:{...M.DEFAULT_RATES},levels:{G:3,R:3,B:3,P:3},zSlip:0};
const C=SEA.defaults(),B=PG.defaults();let assertions=0;
const ok=(p,msg)=>{assert.ok(p,msg);assertions++};
const close=(actual,want,eps,msg)=>ok(Math.abs(actual-want)<=eps,msg+' '+actual+' expected '+want);
for(let tick=0;tick<=2048;tick++){
 const time=tick/64,g=PG.sample(base,time,C,B);
 close(g.cable.gyro.residual,0,1e-10,'gyro baseline '+tick);
 close(g.pulsars.phaseDeviation,0,1e-10,'pulsars match reference '+tick);
 close(g.sunResidual,0,1e-10,'grounded sun baseline '+tick);
 ok(g.pulsars.emission>0,'emitters radiate while locked '+tick);
 ok(!g.flare,'no spurious flare '+tick);
 ok(Object.keys(g.pulsars.nodes).length===5,'five pulsars '+tick);
 ok(Object.values(g.pulsars.nodes).every(p=>PG.GLYPHS.includes(p.symbol)),'valid [-!+] state '+tick);
 if(tick>24)close(g.cable.returned,1.8,1e-9,'returned emission '+tick);
}
for(let i=0;i<256;i++){
 const levels=M.fromId(i),state={...base,levels},g=PG.sample(state,1.25,C,B);
 ok(M.stateId(levels)===i,'256 clover states '+i);
 ok(g.pulsars.emission>=0,'no negative emitted light '+i);
}
for(let tick=64;tick<224;tick++){
 const time=tick/64,protectedCase=PG.sample(base,time,{...C,purpleExtra:8},B),
  openCase=PG.sample(base,time,{...C,purpleExtra:8},{...B,connected:false});
 ok(protectedCase.rawStress>0.5,'disturbance enters sun '+tick);
 close(protectedCase.absorbed,B.capacity,1e-9,'ground drains to cap '+tick);
 ok(protectedCase.sunResidual<0.3&&!protectedCase.flare,'ground protects against modeled flare '+tick);
 close(openCase.absorbed,0,1e-12,'disconnected ground draws nothing '+tick);
 ok(openCase.sunResidual>0.5&&openCase.flare,'unprotected sun flares '+tick);
 ok(protectedCase.pulsars.emission>0,'pulsars still emit '+tick);
}
const weak=PG.sample(base,1.25,{...C,purpleExtra:8},{...B,capacity:0.10});
ok(weak.flare,'undersized ground allows flare');
const full=PG.sample(base,1.25,{...C,purpleExtra:8},{...B,capacity:2});
ok(!full.flare&&full.sunResidual<1e-9,'high-capacity ground drains stress');
const relock=PG.sample(base,1.25,C,{...B,connected:false});
ok(!relock.flare&&relock.sunResidual<1e-9,'relock restores zero without ground');
for(const name of ['v','w']){
 const a=PG.pulses(base,0).nodes[name],b=PG.pulses(base,.35).nodes[name];
 ok(a.rate===0&&b.rate===0&&a.phase!==b.phase,'zero-turn witness '+name+' still pulses');
}
console.log('PASS '+assertions+' five-pulsar/ground checks');
