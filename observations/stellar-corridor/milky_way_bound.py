#!/usr/bin/env python3
"""Reproduce a 729-station MWPotential2014-*shape* Galactic midplane field.

Not the canonical galpy MWPotential2014 normalization. The bulge/disk/halo
radial force shapes are re-normalized to 233 km/s at R0=8277 pc after
subtracting the 4.297e6-solar-mass Sgr A* point-source contribution.

Uses only Python standard library. No individual stars are assigned masses.
"""
import csv
import json
import math
import argparse
from pathlib import Path

R0 = 8277.0            # pc
V0 = 233000.0          # m/s
PC = 3.0856775814913673e16
GM_SUN = 1.3271244e20
GM_BH = GM_SUN * 4.297e6
N = 729
LY_PER_PC = 3.26156
FRACTIONS = (.05, .60, .35)

def regularized_gamma_p_0p6(x):
    """P(0.6,x) using stable lower series / upper continued fraction."""
    if x <= 0:
        return 0.0
    a = 0.6
    factor = math.exp(-x + a * math.log(x) - math.lgamma(a))
    if x < a+1.0:
        ap, total = a, 1.0/a
        delta = total
        for _ in range(1000):
            ap += 1
            delta *= x/ap
            total += delta
            if abs(delta) < 1e-14*abs(total):
                break
        return min(1.0, max(0.0, factor*total))
    b, c, d = x+1-a, 1e300, 1/(x+1-a)
    h = d
    for i in range(1, 1001):
        an = -i*(i-a)
        b += 2
        d = an*d+b
        if abs(d)<1e-300:
            d=1e-300
        c = b+an/c
        if abs(c)<1e-300:
            c=1e-300
        d=1/d
        change=d*c
        h*=change
        if abs(change-1)<1e-14:
            break
    return min(1.0, max(0.0, 1-factor*h))

def shapes(r):
    """Positive radial magnitudes up to free amplitude (units: pc^-2)."""
    if r <= 0:
        raise ValueError("no point-mass field at the center")
    bulge = regularized_gamma_p_0p6((r/1900)**2)/r**2
    disk = r/(r*r+3280*3280)**1.5
    x = r/16000.0
    halo = (math.log1p(x)-x/(1+x))/r**2
    return bulge, disk, halo

SOLAR_SHAPES = shapes(R0)
TARGET = V0**2/(R0*PC)
BH_SOLAR = GM_BH/(R0*PC)**2
EXTERNAL_SOLAR = TARGET-BH_SOLAR

def field(r):
    """Positive inward acceleration at midplane radius r (pc)."""
    if r <= 0:
        return None
    sh = shapes(r)
    bulge, disk, halo = [
        EXTERNAL_SOLAR*FRACTIONS[i]*sh[i]/SOLAR_SHAPES[i]
        for i in range(3)
    ]
    bh = GM_BH/(r*PC)**2
    total = bh+bulge+disk+halo
    return dict(bh=bh, bulge=bulge, disk=disk, halo=halo,
                total=total, circular_km_s=math.sqrt(total*r*PC)/1000,
                bh_fraction=bh/total)

def rows():
    return [(n+1, n*R0/(N-1), field(n*R0/(N-1)))
            for n in range(N)]

def check():
    assert abs(regularized_gamma_p_0p6((1000/1900)**2)
               -0.4685563844016277)<1e-12
    at_sun=field(R0)
    assert math.isclose(at_sun["circular_km_s"],233,rel_tol=1e-13)
    assert math.isclose(at_sun["total"],TARGET,rel_tol=1e-13)
    assert math.isclose(field(R0/2)["bh"]/BH_SOLAR,4,rel_tol=1e-13)
    assert math.isclose(field(R0*2)["bh"]/BH_SOLAR,.25,rel_tol=1e-13)
    assert len(rows())==729 and rows()[0][2] is None
    for n,r,f in rows()[1:]:
        assert all(math.isfinite(v) and v>=0 for v in f.values())
    return dict(solar_acceleration_m_s2=at_sun["total"],
                solar_circular_velocity_km_s=at_sun["circular_km_s"],
                sgraw_to_sun_fraction=at_sun["bh_fraction"],
                finite_stations=728,undefined_center_stations=1)

def output_csv(path):
    columns = ["station_from_sgra","radius_pc","radius_ly","g_bh_m_s2",
               "g_bulge_m_s2","g_disk_m_s2","g_halo_m_s2",
               "g_total_m_s2","v_circular_model_km_s","bh_share_total",
               "star_by_star_mass_field","status"]
    with open(path,"w",newline="",encoding="utf-8") as handle:
        out=csv.writer(handle,lineterminator="\n")
        out.writerow(columns)
        for n,r,f in rows():
            value=(lambda k: format(f[k],".12e") if f else "")
            out.writerow((n,format(r,".8f"),format(r*LY_PER_PC,".5f"),
                          value("bh"),value("bulge"),value("disk"),
                          value("halo"),value("total"),value("circular_km_s"),
                          value("bh_fraction"),"",
                          "MODEL_EXTRAPOLATION_NO_CATALOG_STELLAR_MASSES"
                          if f else "CENTER_UNDEFINED"))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",default="",help="optional path to write 729-row CSV")
    args=parser.parse_args()
    audit=check()
    if args.out:
        output_csv(args.out)
    print(json.dumps(audit,indent=2))

if __name__=="__main__":
    main()
