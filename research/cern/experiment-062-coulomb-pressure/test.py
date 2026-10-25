import math,json
from pathlib import Path
alpha=7.2973525643e-3
md=1875.612945
mu=md/2
hbarc=197.3269804
JperMeV=1e6*1.602176634e-19
Q=2*md-3727.3794118
r_fm=4
barrier=alpha*hbarc/r_fm
energies_keV=(1,10,100,400)
rows=[]
for keV in energies_keV:
 E=keV/1000
 beta=math.sqrt(2*E/mu)
 eta=alpha/beta
 factor=math.exp(-2*math.pi*eta)
 assert 0<factor<1
 rows.append({'collision_keV':keV,'gamow_factor':factor,'classically_below_barrier':E<barrier})
assert all(rows[i]['gamow_factor']<rows[i+1]['gamow_factor'] for i in range(3))
assert rows[0]['classically_below_barrier'] and not rows[-1]['classically_below_barrier']
radius_m=1e-6
V=4*math.pi*radius_m**3/3
pressure=Q*JperMeV/(3*V)
assert abs(3*pressure*V-Q*JperMeV)/(Q*JperMeV)<1e-14
assert 0.3<barrier<0.4 and 23<Q<24
result={'experiment':'PRIM-062','status':'PASS','coulomb_barrier_MeV_at_4fm':barrier,'dd_to_He4_gamma_Q_MeV':Q,'gamow_energy_scan':rows,'hypothetical_cavity_radius_m':radius_m,'isotropic_photon_pressure_Pa_if_energy_thermalized':pressure,'scope':'semiclassical screening only, no fusion-rate prediction'}
Path(__file__).with_name('results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
