#!/usr/bin/env python3
"""Observed Gaia DR3 stars -> Sgr A*-Sun stations. Never fills missing stars."""
import argparse
import csv
import json
import math
from pathlib import Path

RA0, DEC0 = map(math.radians, (266.41683, -29.00781))
UNIT = (math.cos(DEC0)*math.cos(RA0), math.cos(DEC0)*math.sin(RA0), math.sin(DEC0))
DIST_PC = 8277.0
STATIONS = 729
REQUIRED = ('source_id', 'ra', 'dec', 'distance_gspphot',
            'distance_gspphot_lower', 'distance_gspphot_upper', 'ruwe')


def coord_projection(ra_deg, dec_deg, distance_pc):
    r, d = math.radians(ra_deg), math.radians(dec_deg)
    star = (math.cos(d)*math.cos(r), math.cos(d)*math.sin(r), math.sin(d))
    c = max(-1.0, min(1.0, sum(a*b for a, b in zip(UNIT, star))))
    return distance_pc*c, distance_pc*math.sqrt(max(0.0, 1.0-c*c))


def observe(input_csv, output_dir, max_offset_pc=50.0, max_relative_ci=0.6):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    observed = []
    rejects = {'malformed': 0, 'duplicate_source_id': 0, 'invalid_distance_ci': 0,
               'imprecise_distance_ci': 0, 'ruwe_quality': 0,
               'outside_line_extent': 0, 'outside_corridor': 0}
    seen = set()
    total = 0
    with open(input_csv, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        missing = set(REQUIRED).difference(reader.fieldnames or ())
        if missing:
            raise ValueError('Missing Gaia DR3 columns: ' + ', '.join(sorted(missing)))
        for rec in reader:
            total += 1
            try:
                ident = rec['source_id'].strip()
                if not ident: raise ValueError('empty ID')
                ra, dec, dis, lo, hi, ruwe = [float(rec[k]) for k in REQUIRED[1:]]
                if not all(map(math.isfinite, (ra, dec, dis, lo, hi, ruwe))):
                    raise ValueError('nonfinite')
            except (ValueError, TypeError, KeyError):
                rejects['malformed'] += 1
                continue
            if ident in seen:
                rejects['duplicate_source_id'] += 1
                continue
            seen.add(ident)
            if not (0 < lo <= dis <= hi):
                rejects['invalid_distance_ci'] += 1
                continue
            relative_width = (hi-lo)/dis
            if relative_width > max_relative_ci:
                rejects['imprecise_distance_ci'] += 1
                continue
            if not (0 < ruwe <= 1.4):
                rejects['ruwe_quality'] += 1
                continue
            along, offset = coord_projection(ra, dec, dis)
            if not (0 < along < DIST_PC):
                rejects['outside_line_extent'] += 1
                continue
            if offset > max_offset_pc:
                rejects['outside_corridor'] += 1
                continue
            index = round((DIST_PC-along)/DIST_PC*(STATIONS-1))
            index = max(0, min(STATIONS-1, index))
            observed.append({'source_id': ident, 'ra_deg': round(ra, 7),
               'dec_deg': round(dec, 7), 'distance_median_pc': round(dis, 4),
               'distance_p16_pc': round(lo, 4), 'distance_p84_pc': round(hi, 4),
               'ruwe': round(ruwe, 4), 'along_sun_pc': round(along, 4),
               'perpendicular_offset_pc': round(offset, 4),
               'station_id': index+1, 'origin': 'Gaia DR3 GSP-Phot',
               'distance_is_estimate': 'true', 'mass_solar': ''})
    observed.sort(key=lambda s:(s['station_id'], s['perpendicular_offset_pc'],s['source_id']))
    closest = {}
    for s in observed:
        closest.setdefault(s['station_id'],s)
    for name, records, fields in [
      ('gaia_accepted_observations.csv', observed,
       ['source_id','ra_deg','dec_deg','distance_median_pc','distance_p16_pc',
        'distance_p84_pc','ruwe','along_sun_pc','perpendicular_offset_pc',
        'station_id','origin','distance_is_estimate','mass_solar']),
      ('gaia_729_station_witnesses.csv',
       [{'station_id': i+1,
         'station_from_sgra_pc': round(i*DIST_PC/(STATIONS-1), 4),
         'station_from_sun_pc': round(DIST_PC-i*DIST_PC/(STATIONS-1), 4),
         'witness_source_id': closest.get(i+1,{}).get('source_id',''),
         'witness_offset_pc': closest.get(i+1,{}).get('perpendicular_offset_pc',''),
         'status': 'observed_candidate' if i+1 in closest else 'NO_CATALOG_MATCH',
         'is_star_at_exact_station': 'false'} for i in range(STATIONS)],
       ['station_id','station_from_sgra_pc','station_from_sun_pc',
        'witness_source_id','witness_offset_pc','status','is_star_at_exact_station'])]:
        with open(output_dir/name,'w',newline='',encoding='utf-8') as f:
            wr = csv.DictWriter(f,fieldnames=fields)
            wr.writeheader()
            wr.writerows(records)
    result = {'input_rows': total, 'accepted_observed_stars': len(observed),
       'occupied_stations': len(closest), 'unoccupied_stations': STATIONS-len(closest),
       'rejections': rejects, 'corridor_radius_pc':max_offset_pc,
       'maximum_relative_distance_ci':max_relative_ci,'station_count':STATIONS,
       'reference_center_pc':DIST_PC,'line_ra_dec_deg':[266.41683,-29.00781],
       'gaia_archive_query_executed_by_this_script':False,
       'field_mass_not_computed':'No validated mass and velocity field in this input',
       'station_equality':'Model bin membership, not a measured star at its exact center',
       'source_attribution':'ESA Gaia DR3 / DPAC; photometric GSP-Phot distance estimate'}
    with open(output_dir/'gaia_ingest_audit.json','w',encoding='utf-8') as f:
        json.dump(result,f,indent=2)
        f.write('\n')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('gaia_csv',help='Actual CSV exported from Gaia TAP query')
    p.add_argument('--out',default='gaia_ingest_output')
    p.add_argument('--offset-pc',type=float,default=50)
    p.add_argument('--max-ci',type=float,default=0.6)
    args=p.parse_args()
    if args.offset_pc<=0 or args.max_ci<=0:
        p.error('offset-pc and max-ci must be positive')
    print(json.dumps(observe(args.gaia_csv,args.out,args.offset_pc,args.max_ci),indent=2))
if __name__=='__main__':main()
