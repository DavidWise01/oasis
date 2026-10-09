const M=(()=>{
/**
 * ROOT0 P3.4 — Au/Ag electrum fcc 10x10x10 physical candidate.
 * Lattice geometry is a new test attachment, not frozen ROOT0 v92 dynamics.
 * Gold/silver 79/21 is a user supplied *weight* mnemonic.
 * Converting it into physical mass fractions is an EXPLICIT optional assumption.
 * Optical n+ik and the surface voltage response are free experimental inputs.
 */
const FACTS=Object.freeze({
 userAlloyWeightAu:79,userAlloyWeightAg:21,siteGrid:10,
 massAu:196.966569,massAg:107.8682,
 aAuM:4.078e-10,aAgM:4.086e-10,
 planckLengthM:1.616255e-35,
 elementaryChargeC:1.602176634e-19,
 eps0:8.8541878128e-12,
 originalPotentialV:-0.211,
 earlierCipher:'..||..|....|||',cipherPositions:208,
 tensorAddresses:100_000_000
});
const DEFAULTS=Object.freeze({
 voltageV:-0.211,referenceV:0,gapM:10e-6,
 wavelengthM:600e-9,thicknessM:30e-9,
 nReal:0.5,kappa:3.0, surfaceResponseRadPerV:0,
 auWeight:79,agWeight:21,compositionBasis:'mass',
 gridN:10
});
const finite=(v,k)=>{if(typeof v!=='number'||!Number.isFinite(v))throw new RangeError(k+' must be finite');return v;};
function config(p={}){
 const z={...DEFAULTS,...p};
 for(const k of ['voltageV','referenceV','gapM','wavelengthM','thicknessM','nReal','kappa','surfaceResponseRadPerV','auWeight','agWeight'])finite(z[k],k);
 if(!(z.gapM>0&&z.wavelengthM>0&&z.thicknessM>=0&&z.kappa>=0&&z.nReal>0&&z.auWeight>=0&&z.agWeight>=0&&z.auWeight+z.agWeight>0))throw new RangeError('Invalid material/electrode geometry');
 if(!Number.isInteger(z.gridN)||z.gridN<1||z.gridN>20)throw new RangeError('Lattice gridN 1..20');
 if(!['mass','atomic'].includes(z.compositionBasis))throw new RangeError('compositionBasis must be mass or atomic');
 return z;
}
function atomicFractions(p={}){
 const z=config(p),wAu=z.auWeight/(z.auWeight+z.agWeight),wAg=1-wAu;
 const nAu=z.compositionBasis==='mass'?wAu/FACTS.massAu:wAu;
 const nAg=z.compositionBasis==='mass'?wAg/FACTS.massAg:wAg;
 const fAu=nAu/(nAu+nAg);
 return {fAu,fAg:1-fAu,recordedWeight:[z.auWeight,z.agWeight],assumedBasis:z.compositionBasis};
}
const signed32=(x,y,z)=>{
 let h=(Math.imul(x+1,73856093)^Math.imul(y+1,19349663)^Math.imul(z+1,83492791)^0x24121979)|0;
 h=Math.imul(h^(h>>>16),0x7feb352d);h=Math.imul(h^(h>>>15),0x846ca68b);return (h^(h>>>16))>>>0;
};
const FCC_BASIS=Object.freeze([[0,0,0],[0,1,1],[1,0,1],[1,1,0]]);
const NEAREST_FCC=Object.freeze(Array.from({length:3},(_,zero)=>{
 const axes=[0,1,2].filter(a=>a!==zero);
 return [-1,1].flatMap(a=>[-1,1].map(b=>{
  const shift=[0,0,0];shift[axes[0]]=a;shift[axes[1]]=b;return shift;
 }));
}).flat());
function buildFCC(p={}){
 const z=config(p),size=2*z.gridN,atoms=[];
 for(let cx=0;cx<z.gridN;cx++)for(let cy=0;cy<z.gridN;cy++)for(let cz=0;cz<z.gridN;cz++){
  for(const b of FCC_BASIS){const x=2*cx+b[0],y=2*cy+b[1],zz=2*cz+b[2];
   atoms.push({x,y,z:zz,rank:signed32(x,y,zz),element:'Ag'});
  }
 }
 const nAu=Math.round(atoms.length*atomicFractions(z).fAu);
 const byRank=[...atoms].sort((a,b)=>(a.rank-b.rank)||(a.x-b.x)||(a.y-b.y)||(a.z-b.z));
 for(let j=0;j<nAu;j++)byRank[j].element='Au';
 const byKey=new Map(atoms.map((a,i)=>[a.x+','+a.y+','+a.z,i]));
 const latticeParameterM=atomicFractions(z).fAu*FACTS.aAuM+atomicFractions(z).fAg*FACTS.aAgM;
 return {size,sites:atoms,nAu,nAg:atoms.length-nAu,byKey,unitCellCount:z.gridN**3,
  latticeParameterM,atomicFractions:atomicFractions(z),compositionBasis:z.compositionBasis};
}
function nearby(lattice,a){
 const n=lattice.size;
 return NEAREST_FCC.map(([dx,dy,dz])=>lattice.byKey.get([((a.x+dx)%n+n)%n,((a.y+dy)%n+n)%n,((a.z+dz)%n+n)%n].join(',')));
}
function latticeAudit(lattice){
 const N=lattice.sites.length;
 let defects=0,neighbors=0,inversionBrokenSpecies=0,degreeChecksum=0;
 for(let j=0;j<N;j++){
  const a=lattice.sites[j],indices=nearby(lattice,a);
  if(new Set(indices).size!==12||indices.some(x=>x===undefined||x===j))defects++;
  neighbors+=indices.length;degreeChecksum+=indices.reduce((s,x)=>s+x,0);
  const neg=[(lattice.size-a.x)%lattice.size,(lattice.size-a.y)%lattice.size,(lattice.size-a.z)%lattice.size].join(',');
  const opposite=lattice.byKey.get(neg);
  if(opposite===undefined)defects++;
  else if(lattice.sites[opposite].element!==a.element)inversionBrokenSpecies++;
 }
 return {sites:N,unitCells:lattice.unitCellCount,degree:12,directedBonds:neighbors,
  undirectedBonds:neighbors/2,neighborDefects:defects,inversionBrokenSpecies,
  averageGeometricInversion:true,speciesConfigurationCentrosymmetric:inversionBrokenSpecies===0};
}
const C=(re,im=0)=>({re,im});
const add=(a,b)=>C(a.re+b.re,a.im+b.im);
const sub=(a,b)=>C(a.re-b.re,a.im-b.im);
const mul=(a,b)=>C(a.re*b.re-a.im*b.im,a.re*b.im+a.im*b.re);
const div=(a,b)=>{const d=b.re*b.re+b.im*b.im;return C((a.re*b.re+a.im*b.im)/d,(a.im*b.re-a.re*b.im)/d);};
const abs2=a=>a.re*a.re+a.im*a.im;
const expi=(real,imag=0)=>C(Math.exp(-imag)*Math.cos(real),Math.exp(-imag)*Math.sin(real));
function slabOptics(p={}){
 const z=config(p),N=C(z.nReal,z.kappa),one=C(1),k0=2*Math.PI/z.wavelengthM;
 const r=div(sub(one,N),add(one,N));
 const q=expi(2*k0*z.nReal*z.thicknessM,2*k0*z.kappa*z.thicknessM);
 const phase=expi(k0*z.nReal*z.thicknessM,k0*z.kappa*z.thicknessM);
 const denom=sub(one,mul(mul(r,r),q));
 const transmission=div(mul(div(mul(C(4),N),mul(add(one,N),add(one,N))),phase),denom);
 const reflection=div(mul(r,sub(one,q)),denom);
 const T=abs2(transmission),R=abs2(reflection),A=1-T-R;
 // Plane-parallel free-standing film, vacuum on both sides. Multiple reflections included.
 return {transmission,reflection,T,R,A,energyBalance:T+R+A,
  opticalIntensityDecayLengthM:z.kappa>0?z.wavelengthM/(4*Math.PI*z.kappa):null,
  bareExponentialTransmissionProxy:Math.exp(-4*Math.PI*z.kappa*z.thicknessM/z.wavelengthM),
  model:'ideal free-standing homogeneous complex-index film; interface multiple reflections; not measured electrum constants'};
}
function opticalBoundary(p={}){
 const z=config(p),f=atomicFractions(z),aM=f.fAu*FACTS.aAuM+f.fAg*FACTS.aAgM;
 const voltageDifferenceV=z.voltageV-z.referenceV,externalFieldVPerM=voltageDifferenceV/z.gapM;
 // bulk DC conductor: field screened in metal; external electrode gap supports E.
 const sheetChargeCPerM2=-FACTS.eps0*externalFieldVPerM;
 const surfaceSiteDensityM2=4/(Math.sqrt(3)*aM*aM);
 const surfaceElectronsPerAtom=Math.abs(sheetChargeCPerM2)/(FACTS.elementaryChargeC*surfaceSiteDensityM2);
 const surfacePhaseRad=z.surfaceResponseRadPerV*voltageDifferenceV;
 const slab=slabOptics(z);
 return {...slab,atomicFractions:f,aM,nearestNeighborM:aM/Math.sqrt(2),
  potentialDifferenceV:voltageDifferenceV,externalFieldVPerM,
  bulkStaticElectricFieldVPerM:0, bulkPockelsPhaseRad:0,
  surfaceSheetChargeCPerM2:sheetChargeCPerM2,surfaceSiteDensityM2,surfaceElectronsPerAtom,
  surfacePhaseRad,interfaceResponseDerivedFromCipher:false,
  latticeSeparationToPlanck:aM/FACTS.planckLengthM,
  vacuumWavelengthToPlanck:z.wavelengthM/FACTS.planckLengthM,
  vacuumWavelengthShiftFromDCVoltageM:0,
  physicallyReachesPlanck:false};
}
function requireBulkPockels(p={}){
 const {pockelsCoefficientMPerV=0,centrosymmetricAverage=true}=p;
 finite(pockelsCoefficientMPerV,'pockelsCoefficientMPerV');
 if(centrosymmetricAverage&&pockelsCoefficientMPerV!==0)throw new Error('Invalid: bulk electric-dipole Pockels coefficient assumed nonzero for centrosymmetric average electrum FCC');
 return pockelsCoefficientMPerV;
}

return {FACTS,DEFAULTS,config,atomicFractions,FCC_BASIS,NEAREST_FCC,buildFCC,nearby,latticeAudit,slabOptics,opticalBoundary,requireBulkPockels};
})();
export const {FACTS,DEFAULTS,config,atomicFractions,FCC_BASIS,NEAREST_FCC,buildFCC,nearby,latticeAudit,slabOptics,opticalBoundary,requireBulkPockels}=M;
