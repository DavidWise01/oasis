#!/usr/bin/env python3
"""Bound 07: independent mirror-quadrant HI velocities and a separate toy m=2 potential.

Read *frozen*, previously sourced Bound 06 H I pairs and Bound 04 729-station
radial acceleration; no stars, velocities, or force measurements are fabricated.

Outputs:
  BOUND07_HI_MIRROR_ODD_20261027.csv
  BOUND07_729_M2_POTENTIAL_SCENARIO_20261027.csv

Usage:
  python azimuthal_bound07.py --self-test
  python azimuthal_bound07.py --out bound07_reproduced

The mass potential is a selectable hypothesis only. Do NOT infer gravitational
forces from H I terminal velocities without a dynamical model and uncertainties.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path

R0_GAS_KPC = 8.122
R_BAR_KPC = 4.5
PHI_BAR = math.radians(25.0)
EPSILON = 0.02     # Scenario, NOT measured or fitted to these points.
V_REF = 233000.0   # m/s; amplitude scale, NOT an observed bar pattern speed.
KPC_M = 3.0856775814913673e19
STATIONS = 729

def toy_perturbation(r_kpc, phi_rad, epsilon=EPSILON):
    """Returns (delta radial acceleration, delta azimuthal acceleration), SI.

    delta Phi = eps*V_REF^2*f(R)*cos(2(phi-PHI_BAR))
    f(R) = (R/R_BAR)^2 * exp[1-(R/R_BAR)^2]
    g_R = -partial_R(delta Phi), g_phi = -(1/R)partial_phi(delta Phi)
    """
    if r_kpc <= 0:
        raise ValueError("R must be > 0: BH center is undefined")
    u = r_kpc/R_BAR_KPC
    envelope = u*u*math.exp(1-u*u)
    d_envelope_dr_kpc = envelope*(2/r_kpc-2*r_kpc/R_BAR_KPC**2)
    ang = 2*(phi_rad-PHI_BAR)
    delta_radial = (-epsilon*V_REF**2*d_envelope_dr_kpc
                    *math.cos(ang)/KPC_M)
    delta_azimuth = (2*epsilon*V_REF**2*envelope
                     *math.sin(ang)/(r_kpc*KPC_M))
    return delta_radial, delta_azimuth

def potential(r_kpc, phi_rad, epsilon=EPSILON):
    u = r_kpc/R_BAR_KPC
    return epsilon*V_REF**2*u*u*math.exp(1-u*u)*math.cos(
        2*(phi_rad-PHI_BAR))

def check():
    r, phi = 6.0, 0.4
    dr, dp = toy_perturbation(r,phi)
    dx, da = 1e-5, 1e-6
    num_dr = -(potential(r+dx,phi)-potential(r-dx,phi))/(2*dx*KPC_M)
    num_dp = -(potential(r,phi+da)-potential(r,phi-da))/(2*da*r*KPC_M)
    assert math.isclose(dr,num_dr,rel_tol=1e-8)
    assert math.isclose(dp,num_dp,rel_tol=1e-8)
    d2=toy_perturbation(r,phi,0.01)
    assert math.isclose(d2[0],dr/2,rel_tol=1e-12)
    assert math.isclose(d2[1],dp/2,rel_tol=1e-12)
    assert toy_perturbation(r,phi,0)==(0.0,0.0)
    return {"finite_difference_gradients":"PASS",
            "epsilon_linearity":"PASS","zero_epsilon_null":"PASS"}

def measured_mirror_records(audit):
    result = []
    for i,row in enumerate(audit["anchors"],1):
        r=(row["q1r"]+row["q4r"])/2
        if not 0<r<R0_GAS_KPC:
            raise ValueError("tangent geometry invalid for R="+str(r))
        phi=math.acos(r/R0_GAS_KPC)
        v1,v4=row["q1"],row["q4"]
        even=(v1+v4)/2
        odd=(v1-v4)/2
        result.append({
            "bin":i,"r_eilers_kpc":row["r"],
            "r_q1_kpc":row["q1r"],"v_q1_km_s":v1,
            "source_q1_line":row["q1line"],"r_q4_kpc":row["q4r"],
            "v_q4_km_s":v4,"source_q4_line":row["q4line"],
            "mirror_radius_mean_kpc":r,
            "tangent_longitude_abs_deg":math.degrees(math.asin(r/R0_GAS_KPC)),
            "tangent_phi_abs_deg":math.degrees(phi),
            "v_even_km_s":even,"v_odd_km_s":odd,
            "conditional_m2_sine_coefficient_km_s":odd/math.sin(2*phi),
            "conditional_delta_centripetal_proxy_m_s2":
                ((v1*v1-v4*v4)*1e6)/(r*KPC_M),
            "has_velocity_uncertainties":"NO",
            "inferred_force_from_gas":"",
            "status":"OBSERVED_VELOCITY_DIAGNOSTIC_ONLY"
        })
    assert len(result)==5
    assert [1 if a["v_odd_km_s"]>0 else -1 for a in result]==[
        1,1,1,-1,-1]
    return result

def radial_model_rows(path):
    with open(path,encoding="utf-8",newline="") as fp:
        rows=list(csv.DictReader(fp))
    if len(rows)!=STATIONS:
        raise ValueError(f"Expected 729 frozen baseline stations, got {len(rows)}")
    return rows

def modeled_station_records(rows):
    out=[]
    for i,row in enumerate(rows):
        R=float(row["radius_pc"])/1000
        if i==0:
            assert R==0 and not row["g_total_m_s2"]
            out.append({
                "station_from_sgra":1,"radius_kpc":0,"baseline_inward_gR_m_s2":"",
                "bar_angle_deg":25,"epsilon_scenario":EPSILON,
                "axis_bar_delta_gR_m_s2":"","axis_bar_gphi_m_s2":"",
                "axis_total_signed_gR_m_s2":"","axis_total_signed_gphi_m_s2":"",
                "mirror_phi_abs_deg":"","Q1_bar_delta_gR_m_s2":"",
                "Q1_bar_gphi_m_s2":"","Q4_bar_delta_gR_m_s2":"",
                "Q4_bar_gphi_m_s2":"","physical_observed_mass_for_station":"",
                "status":"UNDEFINED_CENTER_NO_POINT_MASS_FIELD"})
            continue
        base=float(row["g_total_m_s2"])
        dr,dp=toy_perturbation(R,0)
        p=math.acos(R/R0_GAS_KPC) if R<=R0_GAS_KPC else None
        q1=toy_perturbation(R,p) if p is not None else (None,None)
        q4=toy_perturbation(R,-p) if p is not None else (None,None)
        out.append({
            "station_from_sgra":i+1,"radius_kpc":R,
            "baseline_inward_gR_m_s2":base,
            "bar_angle_deg":25,"epsilon_scenario":EPSILON,
            "axis_bar_delta_gR_m_s2":dr,"axis_bar_gphi_m_s2":dp,
            "axis_total_signed_gR_m_s2":-base+dr,
            "axis_total_signed_gphi_m_s2":dp,
            "mirror_phi_abs_deg":math.degrees(p) if p is not None else "",
            "Q1_bar_delta_gR_m_s2":q1[0] if p is not None else "",
            "Q1_bar_gphi_m_s2":q1[1] if p is not None else "",
            "Q4_bar_delta_gR_m_s2":q4[0] if p is not None else "",
            "Q4_bar_gphi_m_s2":q4[1] if p is not None else "",
            "physical_observed_mass_for_station":"",
            "status":"TOY_QUADRUPOLE_NO_BAR_MASS_FIT"})
    assert len(out)==729
    assert out[0]["axis_total_signed_gR_m_s2"]==""
    assert out[-1]["Q1_bar_gphi_m_s2"]==""
    return out

def save_rows(path, data):
    with open(path,"w",newline="",encoding="utf-8") as fp:
        writer=csv.DictWriter(fp,fieldnames=list(data[0]),lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bound06",default="BOUND06_R0_HI_AUDIT_20261027.json")
    parser.add_argument("--baseline",default="SGRA_EARTH_729_MW_COMPONENTS_20261027.csv")
    parser.add_argument("--out",default="")
    parser.add_argument("--self-test",action="store_true")
    a=parser.parse_args()
    report=check()
    if a.self_test:
        print(json.dumps(report,indent=2))
        return
    observed=measured_mirror_records(json.loads(Path(a.bound06).read_text()))
    stations=modeled_station_records(radial_model_rows(a.baseline))
    if a.out:
        out=Path(a.out)
        out.mkdir(parents=True,exist_ok=True)
        save_rows(out/"BOUND07_HI_MIRROR_ODD_20261027.csv",observed)
        save_rows(out/"BOUND07_729_M2_POTENTIAL_SCENARIO_20261027.csv",stations)
    report.update({
       "gas_mirror_sample_pairs":len(observed),
       "numerical_model_stations":len(stations),
       "odd_signs":[1 if v["v_odd_km_s"]>0 else -1 for v in observed],
       "caution":"Velocity odd modes are not gravitational acceleration measurements.",
       "model_status":"Unfitted toy bar potential; model calibration not preserved for epsilon != 0."})
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    main()
