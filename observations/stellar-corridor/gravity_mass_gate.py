#!/usr/bin/env python3
"""Optional measured-mass vector gravity gate; empty masses are unknown, not zero."""
import argparse
import csv
import json
import math
from urllib.parse import urlparse

PC = 3.0856775814913673e16
GM_SUN = 1.3271244e20
RA0 = math.radians(266.41683)
DEC0 = math.radians(-29.00781)
U = (math.cos(DEC0)*math.cos(RA0),
     math.cos(DEC0)*math.sin(RA0), math.sin(DEC0))


def parse_float(record, *keys):
    for key in keys:
        v = record.get(key)
        if v is not None and str(v).strip():
            x = float(v)
            if not math.isfinite(x):
                raise ValueError("nonfinite: " + key)
            return x
    raise ValueError("missing: " + "/".join(keys))


def field_vector(ra_deg, dec_deg, dist_pc, mass_msun):
    """Newtonian acceleration on the Sun due to one distant point mass, m/s2."""
    if not 0 < dist_pc or not 0 < mass_msun:
        raise ValueError("positive distance and mass required")
    ra, dec = math.radians(ra_deg), math.radians(dec_deg)
    scale = GM_SUN*mass_msun/(dist_pc*PC)**2
    return (scale*math.cos(dec)*math.cos(ra),
            scale*math.cos(dec)*math.sin(ra),
            scale*math.sin(dec))


def vetted_url(url):
    try:
        p = urlparse(url)
        return p.scheme in ('http', 'https') and bool(p.netloc)
    except (ValueError, TypeError):
        return False


def integrate(csv_path):
    total = 0
    accepted = 0
    skipped_unknown_mass = 0
    rejected = 0
    duplicate = 0
    ids = set()
    vec = [0.0, 0.0, 0.0]
    with open(csv_path, encoding="utf-8-sig", newline="") as fp:
        reader = csv.DictReader(fp)
        required = {'source_id', 'ra_deg', 'dec_deg'}
        if not required.issubset(reader.fieldnames or ()):
            raise ValueError("required: source_id,ra_deg,dec_deg")
        for row in reader:
            total += 1
            identity = (row.get('source_id') or '').strip()
            mass = (row.get('mass_msun') or row.get('mass_solar') or '').strip()
            evidence = (row.get('mass_source_uri') or '').strip()
            if not mass:
                skipped_unknown_mass += 1
                continue
            if not vetted_url(evidence):
                rejected += 1
                continue
            if not identity:
                rejected += 1
                continue
            if identity in ids:
                duplicate += 1
                continue
            try:
                ra = parse_float(row, 'ra_deg')
                dec = parse_float(row, 'dec_deg')
                distance = parse_float(row, 'distance_median_pc', 'dist_sun_pc', 'distance_pc')
                m = float(mass)
                if not math.isfinite(m) or not (0 <= ra < 360 and -90 <= dec <= 90):
                    raise ValueError('unphysical')
                new_vec = field_vector(ra, dec, distance, m)
            except (ValueError, TypeError):
                rejected += 1
                continue
            ids.add(identity)
            accepted += 1
            for i, val in enumerate(new_vec):
                vec[i] += val
    radial = sum(a*b for a, b in zip(vec,U))
    magnitude = math.sqrt(sum(x*x for x in vec))
    return {
      "total_records": total,
      "accepted_mass_sourced_records": accepted,
      "skipped_unknown_mass_records": skipped_unknown_mass,
      "rejected_mass_or_position_records": rejected,
      "rejected_duplicate_source_records": duplicate,
      "vector_acceleration_equatorial_m_s2": vec,
      "radial_toward_sgra_acceleration_m_s2": radial,
      "vector_magnitude_m_s2": magnitude,
      "physical_claim": "PARTIAL CATALOG POINT-MASS SUM ONLY",
      "coverage_warning": "NOT the Milky Way total field: omits unseen stars, gas, dark matter, and incomplete catalogs",
      "empty_mass_semantics": "UNKNOWN NOT ZERO",
      "mass_provenance": "A valid mass_source_uri records a citation; its scientific accuracy still requires independent checking",
      "coordinate_note": "Approximate heliocentric inertial geometry at catalog epoch, no proper-motion propagation",
    }


def self_test():
    v = field_vector(0, 0, 1, 1)
    assert abs(math.sqrt(sum(t*t for t in v)) -
               GM_SUN/PC**2) < 1e-28
    n = field_vector(180, 0, 1, 1)
    assert abs(v[0]+n[0]) < 1e-25
    assert field_vector(0, 0, 2, 1)[0] == v[0]/4
    assert field_vector(0, 0, 1, .25)[0] == v[0]/4
    assert not vetted_url('invented-citation')
    print('PASS: inverse-square, mass quarter, opposing-vector cancellation, provenance gate')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mass_csv', nargs='?', help='CSV with actual cited masses; blank means unknown')
    parser.add_argument('--out', default='')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.mass_csv:
        parser.error('provide mass_csv or --self-test')
    result = integrate(args.mass_csv)
    data = json.dumps(result, indent=2) + '\n'
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as fp:
            fp.write(data)
    print(data, end='')


if __name__ == '__main__':
    main()
