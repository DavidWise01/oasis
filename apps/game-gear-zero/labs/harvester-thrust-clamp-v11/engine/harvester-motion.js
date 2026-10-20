/* Harvester V11: normalized, deterministic finite-stroke powered carrier + clamp budget.
 * Source dynamics remain H10/V8. Hall witness is read only until actively commanded.
 * Units are dimensionless model units. No real newton, tesla, thrust device, gravity. */
(function(root){'use strict';
const DT=1/64;
const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
const defaults=()=>({position:0,velocity:0,modelTicks:0,driveWork:0,dragHeat:0,boundaryWork:0,workAbs:0,lastDrive:0,lastCommand:'IDLE',ledgerError:0});
const configDefaults=()=>({mass:1,thrust:3.0,load:.3,damping:.7,holdCapacity:1.25,disturbance:0,settleTolerance:.022,speedLimit:.08,minimumMargin:.18});
function validate(cfg){const c={...configDefaults(),...cfg};
 for(const k of ['mass','thrust','load','damping','holdCapacity','disturbance','settleTolerance','speedLimit','minimumMargin'])if(!Number.isFinite(c[k]))throw Error('invalid config '+k);
 if(c.mass<=0||c.thrust<0||c.load<0||c.damping<0||c.holdCapacity<0||c.disturbance<0)throw Error('invalid physical proxy parameters');
 return c;
}
function advance(prev,cfg,mode='APPROACH',ticks=1){
 const c=validate(cfg),ticksN=clamp(Math.floor(ticks),0,1024);
 if(!['APPROACH','RETRACT','PARK'].includes(mode))throw Error('unsupported motion '+mode);
 let s={...prev};
 for(let i=0;i<ticksN;i++){
  const x=s.position,v=s.velocity,m=c.mass,target=mode==='RETRACT'?0:mode==='PARK'?x:1;
  // Saturated powered PD servo with explicit payload-load compensation.
  const desired=mode==='PARK'?c.load-c.damping*v:c.load+10*(target-x)-5.5*v;
  const drive=clamp(desired,-c.thrust,c.thrust);
  // Viscous drag is implicit-midpoint; exact discrete work-energy relation before stops.
  const v2=(m*v+DT*(drive-c.load-.5*c.damping*v))/(m+.5*DT*c.damping);
  const avg=(v+v2)/2,rawX=x+DT*avg;
  const x2=clamp(rawX,0,1),hit=rawX!==x2;
  const nextV=hit?0:v2,dx=rawX-x;
  const powerWork=drive*dx,heat=c.damping*avg*avg*DT;
  const rawE=.5*m*v2*v2+c.load*rawX;
  const finalE=.5*m*nextV*nextV+c.load*x2;
  const boundary=rawE-finalE;
  s.position=x2;s.velocity=nextV;
  s.modelTicks++;
  s.driveWork+=powerWork;s.workAbs+=Math.abs(powerWork);
  s.dragHeat+=heat;s.boundaryWork+=boundary;
  s.lastDrive=drive;s.lastCommand=mode;
  // Fresh reference closure: K + U = K0+U0 + motor work - drag - boundary work.
  const currentE=.5*m*nextV*nextV+c.load*x2;
  s.ledgerError=currentE-(s.initialEnergy||0)-s.driveWork+s.dragHeat+s.boundaryWork;
 }
 return s;
}
function rebase(state,cfg){
 const c=validate(cfg);return {...state,driveWork:0,dragHeat:0,boundaryWork:0,workAbs:0,initialEnergy:.5*c.mass*state.velocity*state.velocity+c.load*state.position,ledgerError:0};
}
function snapshot(state,cfg,hall){
 const c=validate(cfg),s=state||defaults();
 const demand=c.load+c.disturbance+Math.abs(s.velocity)*.15;
 const margin=c.holdCapacity-demand;
 const docked=s.position>=1-c.settleTolerance;
 const slow=Math.abs(s.velocity)<=c.speedLimit;
 const forceSafe=margin>=c.minimumMargin;
 const coreReady=!hall||hall.ready;
 const blocked=[];
 if(!docked)blocked.push('POSITION');
 if(!slow)blocked.push('VELOCITY');
 if(!forceSafe)blocked.push('FORCE_BUDGET');
 if(!coreReady)blocked.push('HALL_INTERLOCK');
 return {...s,forceDemand:demand,forceMargin:margin,forceSafe,docked,slow,coreReady,
  travelReady:blocked.length===0,blocked,energy:.5*c.mass*s.velocity*s.velocity+c.load*s.position,
  appliedThrust:s.lastDrive,thrustLimit:c.thrust,holdCapacity:c.holdCapacity,
  units:'normalized model units; no physical force / gravity'};
}
function witness(hall,motion,cfg){
 const m=snapshot(motion,cfg,hall);
 const extra={position:m.docked,velocity:m.slow,force:m.forceSafe};
 const checks={...hall.checks,...extra};
 const failures=Object.keys(checks).filter(k=>!checks[k]);
 return {...hall,checks,failures,ready:failures.length===0,carrierMotion:m};
}
function control(clampEngine,clampState,hall,motion,cfg,action){
 const w=witness(hall,motion,cfg);
 if(action==='NEXT'&&clampState.phase==='APPROACH'&&!w.carrierMotion.travelReady){
  return {...clampState,reason:'CARRIER_NOT_DOCKED: '+w.carrierMotion.blocked.join('+')};
 }
 if(action==='NEXT'&&clampState.phase==='RELEASE'&&!(motion.position<=.02&&Math.abs(motion.velocity)<=.08)){
  return {...clampState,reason:'RETRACT_IN_PROGRESS'};
 }
 // When in non-attached approach, the base H10 stage may be entered before docking;
 // all later phases require the new position, speed and force-margin witnesses.
 return clampEngine.step(clampState,action,w);
}
root.HarvesterMotionV11={DT,defaults,configDefaults,validate,advance,rebase,snapshot,witness,control};
})(typeof window!=='undefined'?window:globalThis);
