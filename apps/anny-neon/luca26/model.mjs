/*
 * LUCA-26 symbolic lineage simulator. NOT a reconstructed LUCA sequence.
 * The 20 amino-acid letters and DNA codons are biological conventions;
 * the 26-slot architecture and toroidal display are KET design choices.
 *
 * Codon substitutions may preserve translated amino acids. Deleting or
 * replacing symbols is explicitly marked degraded/unknown, not "survived".
 */
export const AA20 = Object.freeze([
  {code:'A',name:'Alanine',codons:['GCT','GCC','GCA','GCG'],family:'nonpolar'},
  {code:'R',name:'Arginine',codons:['CGT','CGC','CGA','CGG','AGA','AGG'],family:'charged'},
  {code:'N',name:'Asparagine',codons:['AAT','AAC'],family:'polar'},
  {code:'D',name:'Aspartic acid',codons:['GAT','GAC'],family:'charged'},
  {code:'C',name:'Cysteine',codons:['TGT','TGC'],family:'polar'},
  {code:'Q',name:'Glutamine',codons:['CAA','CAG'],family:'polar'},
  {code:'E',name:'Glutamic acid',codons:['GAA','GAG'],family:'charged'},
  {code:'G',name:'Glycine',codons:['GGT','GGC','GGA','GGG'],family:'nonpolar'},
  {code:'H',name:'Histidine',codons:['CAT','CAC'],family:'charged'},
  {code:'I',name:'Isoleucine',codons:['ATT','ATC','ATA'],family:'nonpolar'},
  {code:'L',name:'Leucine',codons:['TTA','TTG','CTT','CTC','CTA','CTG'],family:'nonpolar'},
  {code:'K',name:'Lysine',codons:['AAA','AAG'],family:'charged'},
  {code:'M',name:'Methionine',codons:['ATG'],family:'nonpolar'},
  {code:'F',name:'Phenylalanine',codons:['TTT','TTC'],family:'nonpolar'},
  {code:'P',name:'Proline',codons:['CCT','CCC','CCA','CCG'],family:'nonpolar'},
  {code:'S',name:'Serine',codons:['TCT','TCC','TCA','TCG','AGT','AGC'],family:'polar'},
  {code:'T',name:'Threonine',codons:['ACT','ACC','ACA','ACG'],family:'polar'},
  {code:'W',name:'Tryptophan',codons:['TGG'],family:'nonpolar'},
  {code:'Y',name:'Tyrosine',codons:['TAT','TAC'],family:'polar'},
  {code:'V',name:'Valine',codons:['GTT','GTC','GTA','GTG'],family:'nonpolar'}
]);
export const DNA4=Object.freeze(['A','C','T','G']);
export const POLARITY2=Object.freeze(['−','+']);
export const ANCESTOR=AA20.map(x=>x.code).join('')+'|ACTG|−+';
export const CODE_INDEX=Object.freeze(Object.fromEntries(AA20.flatMap(amino=>amino.codons.map(c=>[c,amino.code]))));

// A single shared 4³ codon field sits BELOW every selected residue n.
// 64 DNA triplets total: 61 sense codons + 3 translation STOP signals.
// This is not 64 codons per amino acid, and not a reconstructed LUCA genome.
export const STOP_CODONS=Object.freeze(['TAA','TAG','TGA']);
export const CODON_CUBE=Object.freeze(DNA4.flatMap((first,a)=>
  DNA4.flatMap((second,b)=>
    DNA4.map((third,c)=>{
      const codon=first+second+third;
      return Object.freeze({
        codon,first,second,third,coordinate:Object.freeze([a,b,c]),
        meaning:CODE_INDEX[codon]??'STOP',isStop:STOP_CODONS.includes(codon)
      });
    })
  )
));
export const CODON_LAYERS=Object.freeze(DNA4.map((base,index)=>Object.freeze({
  base,index,codons:Object.freeze(CODON_CUBE.filter(x=>x.first===base))
})));

export function transformFrame({generation=0,distill=0,polarity='+',mutations=[],lostBases=[]}={}) {
  const tick=Math.max(0,Math.trunc(Number(generation)||0));
  const loss=Math.min(100,Math.max(0,Number(distill)||0));
  const damaged=new Set(mutations);
  const missingBases=new Set(lostBases);
  const erasedCount=Math.min(7,Math.max(0,Math.floor((loss-60)/6)));
  const erasedPositions=new Set(Array.from({length:erasedCount},(_,j)=>(j*7+3)%20));
  const decoded=AA20.map((amino,i)=>{
    const alternatives=amino.codons;
    const chosen=alternatives[(tick+i+(polarity==='+'?1:0))%alternatives.length];
    const replaced=damaged.has(i);
    const codon=replaced?AA20[(i+1)%20].codons[0]:chosen;
    const erased=erasedPositions.has(i);
    const filtered=[...codon].some(x=>missingBases.has(x));
    const observed=erased||filtered?null:CODE_INDEX[codon]??null;
    return {index:i,code:amino.code,name:amino.name,codon:erased?'···':filtered?'×××':codon,observed,
      original:chosen,erased,filtered,mutated:replaced,match:observed===amino.code};
  });
  const matches=decoded.filter(x=>x.match).length;
  const missing=decoded.filter(x=>x.observed===null).length;
  const changed=20-matches-missing;
  const basis=DNA4.filter(x=>!missingBases.has(x)).length;
  const fidelity=matches+basis+2;
  const state=fidelity===26?'PRESERVED':
    (missing+changed<=5&&basis===4?'DEGRADED':'UNKNOWN');
  return {
    tick,loss,polarity,decoded,matched:matches,missing,changed,basis,fidelity,state,erasedCount,
    carriers:decoded.map(x=>x.codon).join(' '),ancestral:ANCESTOR,
    reversible:erasedCount===0&&changed===0&&basis===4,
    note:state==='PRESERVED'
      ?'Synonymous DNA codon changes retain all 20 decoded residues and the six framing positions.'
      :state==='DEGRADED'
      ?'Some ancestral residue information was altered or erased; exact reconstruction is not established.'
      :'Too much ancestral information or base framing is missing to establish continuity.'
  };
}
