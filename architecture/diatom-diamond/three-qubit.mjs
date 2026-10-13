// GHZ-equivalent 3-qubit pure statevector simulation. NOT physical quantum hardware.
// Computational branch bit i_branch is distinct from immutable {{i}} identity.
export const QUBITS = Object.freeze(['i_branch','d+','d-']);
export const BASIS = Object.freeze(['000','001','010','011','100','101','110','111']);
export const STATE = Object.freeze([0,Math.SQRT1_2,0,0,0,0,Math.SQRT1_2,0]);
export function probability(index){
 if (!Number.isInteger(index)||index<0||index>7) throw new RangeError('basis index must be 0..7');
 return STATE[index]**2;
}
export function distribution(){return BASIS.map((basis,i)=>({basis,probability:probability(i)}));}
export function reducedSingle(qubit){
 if(!Number.isInteger(qubit)||qubit<0||qubit>2) throw new RangeError('qubit must be 0..2');
 const rho=[[0,0],[0,0]];
 for(let j=0;j<8;j++) for(let k=0;k<8;k++){
  const bj=BASIS[j],bk=BASIS[k];
  if([...bj].every((b,m)=>m===qubit || b===bk[m]))
   rho[Number(bj[qubit])][Number(bk[qubit])]+=STATE[j]*STATE[k];
 }
 return rho;
}
export function purity(qubit){
 const rho=reducedSingle(qubit);
 return rho[0][0]**2+rho[1][1]**2+2*rho[0][1]*rho[1][0];
}
export function measure(r){
 if(typeof r!=='number'||r<0||r>=1) throw new RangeError('sample r must be [0,1)');
 return r<.5?'001':'110';
}
