"""KET material-selection gyro prototype. Symbolic bridge + classical rigid-rotor model."""
from dataclasses import dataclass
from hashlib import sha256
from math import pi
from struct import pack

FRAME_LEN=257
BRIDGE_ADDRESS=257  # Logical unowned boundary, not a new payload byte
NEXT_ADDRESS=258

@dataclass(frozen=True)
class Material:
    name: str
    density_kg_m3: float
    youngs_modulus_gpa: float
    max_service_temp_c: float  # illustrative only, not a certification limit

# Representative approximate bulk values; alloy, process, orientation and temperature dependent.
MATERIALS={
    'aluminum_6061_t6':Material('6061-T6 aluminum',2700.,69.,150.),
    'titanium_grade5':Material('Ti-6Al-4V titanium',4430.,114.,300.),
    'steel_304':Material('304 stainless steel',8000.,193.,500.),
    'silicon':Material('single-crystal silicon',2330.,130.,150.),
}

def make_frame(ancestral:bytes,generation:int=0)->bytes:
    if len(ancestral)!=184 or not 0<=generation<2**32:raise ValueError('invalid ancestor/generation')
    return b'\xa1'+ancestral+pack('>I',generation)+sha256(ancestral).digest()+bytes(36)

def validate_frame(frame:bytes)->bool:
    return (len(frame)==FRAME_LEN and frame[:1]==b'\xa1' and
            frame[189:221]==sha256(frame[1:185]).digest() and
            frame[221:]==bytes(36))

def bridge(frame:bytes,material_key:str,radius_m:float,thickness_m:float,
           speed_rpm:float,service_temp_c:float=25.)->dict:
    if not validate_frame(frame):raise ValueError('invalid frozen frame')
    if material_key not in MATERIALS:raise KeyError(material_key)
    mat=MATERIALS[material_key]
    if not all(isinstance(x,(int,float)) and 0<x<1e7 for x in (radius_m,thickness_m,speed_rpm)):
        raise ValueError('invalid positive geometry/speed')
    if thickness_m>2*radius_m:raise ValueError('implausible disk proportions')
    if service_temp_c>mat.max_service_temp_c:raise ValueError('illustrative service temperature exceeded')
    mass=mat.density_kg_m3*pi*radius_m**2*thickness_m
    inertia=mass*radius_m**2/2
    omega=speed_rpm*2*pi/60
    return {'frame_sha256':sha256(frame).hexdigest(),
            'bridge_address':BRIDGE_ADDRESS,'bridge_owner':None,
            'next_generation_address':NEXT_ADDRESS,'capacity_scale':2,
            'material':mat.name,'mass_kg':mass,'inertia_kg_m2':inertia,
            'angular_momentum_kg_m2_s':inertia*omega,
            'kinetic_energy_j':0.5*inertia*omega**2,
            'youngs_modulus_gpa':mat.youngs_modulus_gpa}

def test():
    ancestor=bytes(range(184));frame=make_frame(ancestor)
    assert len(frame)==257 and validate_frame(frame)
    before=sha256(frame).digest()
    for key in MATERIALS:
        result=bridge(frame,key,.05,.005,3000)
        assert result['bridge_owner'] is None and result['next_generation_address']==258
        assert result['mass_kg']>0 and result['kinetic_energy_j']>0
    assert sha256(frame).digest()==before
    r=bridge(frame,'aluminum_6061_t6',.05,.005,3000)
    assert abs(r['mass_kg']-2700*pi*.05**2*.005)<1e-12
    assert abs(bridge(frame,'aluminum_6061_t6',.05,.005,6000)['kinetic_energy_j']/r['kinetic_energy_j']-4)<1e-12
    for corrupted in (frame[:-1],frame[:2]+bytes([frame[2]^1])+frame[3:]):
        try:bridge(corrupted,'steel_304',.05,.005,3000)
        except ValueError:pass
        else:raise AssertionError('corrupt frame accepted')
    print('PASS: 4 materials, frozen frame, bridge, energy scaling, corruption rejection')
    for key in MATERIALS:
        x=bridge(frame,key,.05,.005,3000)
        print(f"{key}: {x['mass_kg']:.5f} kg; E={x['kinetic_energy_j']:.3f} J")
if __name__=='__main__':test()
