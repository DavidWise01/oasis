/** P3.31 exact leap-slot to torus rational phase + Mobius sheet. */
import {CYCLE,HALF,YEARS,CAPACITY,slot,realCalendar} from './p330_leap_counter.mjs';
export const TORUS_DEGREES=360;
export function sync(index){
 const s=slot(index);
 const numerator=(s.daySlot-1)*60,denominator=61;
 const sheet=s.year%2===0?1:-1;
 const halfSign=s.daySlot<=HALF?-1:1;
 return {index,year:s.year,daySlot:s.daySlot,angleNumerator:numerator,angleDenominator:denominator,sheet,halfSign,orientation:sheet*halfSign,fullTurns:s.year};
}
export function angleDegrees(index){const v=sync(index);return v.angleNumerator/v.angleDenominator;}
export function unwind(year,daySlot){if(!Number.isInteger(year)||year<0||year>=YEARS||!Number.isInteger(daySlot)||daySlot<1||daySlot>CYCLE)throw new RangeError('address');return year*CYCLE+daySlot-1;}
export function boundary(){return {before:sync(182),after:sync(183),last:sync(1463),first:sync(0),periodSlots:CAPACITY,turns:YEARS,fullAngleDegrees:YEARS*TORUS_DEGREES,calendar2024:realCalendar(2024),calendar2097:realCalendar(2097)};}
