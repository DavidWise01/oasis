// OASIS N184 · CERN-inspired four-observer lab v8.4
// Software lenses operating on the SAME CMS educational dimuon record.
// Names of real experiments label different analytical viewpoints only.
// No detector simulation, particle creation, physical Planck claim, or CERN endorsement.

export const REQUIRED_COLUMNS = Object.freeze([
'Run','Event','Type1','E1','px1','py1','pz1','pt1','eta1','phi1','Q1',
'Type2','E2','px2','py2','pz2','pt2','eta2','phi2','Q2','M'
]);
export const MODES = Object.freeze([
  {id:'ATLAS',title:'Energy and invariant mass',keys:['invariantMass','massResidual','totalEnergy'],units:['GeV','GeV','GeV']},
  {id:'ALICE',title:'Angular topology',keys:['deltaEta','deltaPhi','deltaR'],units:['','rad','']},
  {id:'CMS',title:'Transverse momentum consistency',keys:['scalarPt','ptResidual1','ptResidual2'],units:['GeV','GeV','GeV']},
  {id:'LHCb',title:'Charge and longitudinal direction',keys:['chargeProduct','etaMean','sumPz'],units:['','', 'GeV']}
]);
const NUMERIC=REQUIRED_COLUMNS.filter(x=>!['Type1','Type2'].includes(x));

export function parseCsvLine(line){
 const out=[];let current='',quoted=false;
 for(let i=0;i<line.length;i++){
  const ch=line[i];
  if(ch==='"'){
   if(quoted&&line[i+1]==='"'){current+='"';i++;}
   else quoted=!quoted;
  }else if(ch===','&&!quoted){out.push(current.trim());current='';}
  else current+=ch;
 }
 if(quoted)throw new Error('Unterminated quoted CSV field');
 out.push(current.trim());
 return out;
}
export function parseCMSCSV(text,{maxRows=25000,maxErrors=16}={}){
 if(typeof text!=='string')throw new TypeError('CSV input must be text');
 if(!Number.isInteger(maxRows)||maxRows<1||maxRows>100000)throw new RangeError('maxRows out of bounds');
 const lines=text.replace(/^\uFEFF/,'').split(/\r?\n/);
 const nonempty=lines.findIndex(x=>x.trim()&&!x.trim().startsWith('#'));
 if(nonempty<0)throw new Error('CSV is empty');
 const cols=parseCsvLine(lines[nonempty]).map(x=>x.trim());
 if(new Set(cols).size!==cols.length)throw new Error('Duplicate CSV column name');
 const missing=REQUIRED_COLUMNS.filter(x=>!cols.includes(x));
 if(missing.length)throw new Error('Missing CMS columns: '+missing.join(', '));
 const indices=Object.fromEntries(REQUIRED_COLUMNS.map(key=>[key,cols.indexOf(key)]));
 const records=[],errors=[];let seen=0,skipped=0,truncated=false;
 for(let i=nonempty+1;i<lines.length;i++){
  const line=lines[i].trim();
  if(!line||line.startsWith('#'))continue;
  if(records.length>=maxRows){truncated=true;break}
  seen++;
  try{
   const items=parseCsvLine(lines[i]);
   if(items.length!==cols.length)throw new Error('Expected '+cols.length+' columns; got '+items.length);
   const r={};for(const col of REQUIRED_COLUMNS)r[col]=items[indices[col]];
   for(const col of NUMERIC){
    if(r[col]==='')throw new Error('Empty numeric '+col);
    const n=Number(r[col]);
    if(!Number.isFinite(n))throw new Error('Nonfinite numeric '+col);
    r[col]=n;
   }
   if(!Number.isSafeInteger(r.Run)||!Number.isSafeInteger(r.Event))throw new Error('Unsafe event identifier');
   if(![-1,1].includes(r.Q1)||![-1,1].includes(r.Q2))throw new Error('Muon charges must be +/-1');
   if(r.E1<0||r.E2<0||r.M<0||r.pt1<0||r.pt2<0)throw new Error('Nonphysical negative magnitude');
   records.push(r);
  }catch(e){skipped++;if(errors.length<maxErrors)errors.push('line '+(i+1)+': '+e.message)}
 }
 return {records,header:cols,seen,skipped,truncated,errors,limit:maxRows};
}
export function deltaPhi(a,b){
 // Signed angular separation [-pi,pi], with -pi mapped to +pi by convention.
 let d=((a-b+Math.PI)%(2*Math.PI)+2*Math.PI)%(2*Math.PI)-Math.PI;
 if(d===-Math.PI)d=Math.PI;
 return d;
}
export function invariantMass(r){
 const E=r.E1+r.E2,px=r.px1+r.px2,py=r.py1+r.py2,pz=r.pz1+r.pz2;
 // Negative mass-squared can arise from inconsistent input/rounding.
 const m2=E*E-px*px-py*py-pz*pz;
 return m2>=0?Math.sqrt(m2):NaN;
}
export function observe(r,mode){
 switch(mode){
  case 'ATLAS':{
   const invariant=invariantMass(r);
   return {invariantMass:invariant,massResidual:invariant-r.M,totalEnergy:r.E1+r.E2};
  }
  case 'ALICE':{
   const dEta=r.eta1-r.eta2,dPhi=deltaPhi(r.phi1,r.phi2);
   return {deltaEta:dEta,deltaPhi:dPhi,deltaR:Math.hypot(dEta,dPhi)};
  }
  case 'CMS':{
   return {scalarPt:r.pt1+r.pt2,
    ptResidual1:Math.hypot(r.px1,r.py1)-r.pt1,
    ptResidual2:Math.hypot(r.px2,r.py2)-r.pt2};
  }
  case 'LHCb':{
   return {chargeProduct:r.Q1*r.Q2,etaMean:(r.eta1+r.eta2)/2,sumPz:r.pz1+r.pz2};
  }
  default:throw new Error('Unknown software observer: '+mode);
 }
}
export function analyzeEvent(r,selectedModes=MODES.map(x=>x.id)){
 const output={};let featureCount=0,finiteCount=0;
 for(const mode of selectedModes){
  const features=observe(r,mode);
  output[mode]=features;
  featureCount+=Object.keys(features).length;
  finiteCount+=Object.values(features).filter(Number.isFinite).length;
 }
 return {run:r.Run,event:r.Event,observers:output,featureCount,finiteCount,
  coverage:featureCount/(MODES.length*3),
  // This is designed feature coverage, not Shannon information or accuracy.
  coverageMeaning:'Share of 12 preselected observer features computed'};
}
export function analyzeDataset(records){
 if(!Array.isArray(records))throw new TypeError('records array expected');
 let massErrorSum=0,massErrorN=0,negativeM2=0,opposite=0,largestPt=0;
 for(const r of records){
  const m=invariantMass(r);
  if(Number.isFinite(m)){massErrorSum+=Math.abs(m-r.M);massErrorN++}else negativeM2++;
  if(r.Q1*r.Q2===-1)opposite++;
  largestPt=Math.max(largestPt,r.pt1,r.pt2);
 }
 return {count:records.length,oppositeSign:opposite,
  oppositeSignFraction:records.length?opposite/records.length:null,
  averageAbsoluteMassResidualGeV:massErrorN?massErrorSum/massErrorN:null,
  massResidualCount:massErrorN,negativeMassSquaredCount:negativeM2,
  largestMuonPtGeV:largestPt};
}
export function phaseAddress(index){
 if(!Number.isInteger(index)||index<0)throw new RangeError('index must be nonnegative integer');
 const microtick=index%240,cycle=Math.floor(index/240);
 return {cycle,microtick,phaseStep:Math.floor(microtick/3),subStep:microtick%3,
  sixSector:Math.floor(microtick/40),phaseAngleDegrees:microtick*1.5};
}
export function coverageComparison(r){
 const single=analyzeEvent(r,['CMS']),all=analyzeEvent(r);
 return {singleFeatures:single.featureCount,allFeatures:all.featureCount,
  singleCoverage:single.coverage,allCoverage:all.coverage,
  comparisonMeaning:'Coverage of twelve intentionally distinct calculated features, not discovery of information or independently measured particle tracks'};
}
