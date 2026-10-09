/** P3.30: 366-slot calendar ring repeated four times, split 183 + 183. */
export const CYCLE=366,HALF=183,YEARS=4,CAPACITY=CYCLE*YEARS;
export function slot(index){
 if(!Number.isInteger(index)||index<0||index>=CAPACITY)throw new RangeError('slot');
 const year=Math.floor(index/CYCLE),local=index%CYCLE;
 return {index,year,daySlot:local+1,sign:local<HALF?-1:1,half:local<HALF?0:1};
}
export function inverse(year,daySlot){
 if(!Number.isInteger(year)||year<0||year>=YEARS||!Number.isInteger(daySlot)||daySlot<1||daySlot>CYCLE)throw new RangeError('calendar address');
 return year*CYCLE+daySlot-1;
}
export function leap(year){return year%4===0&&(year%100!==0||year%400===0);}
export function realCalendar(startYear){
 if(!Number.isInteger(startYear)||startYear<1||startYear>9995)throw new RangeError('year');
 const positions=[],vacant=[];
 for(let offset=0;offset<YEARS;offset++)for(let day=1;day<=CYCLE;day++){
  const logical=inverse(offset,day);
  (day<=365||leap(startYear+offset)?positions:vacant).push(logical);
 }
 return {startYear,totalDays:positions.length,vacantSlots:vacant,capacity:CAPACITY};
}
