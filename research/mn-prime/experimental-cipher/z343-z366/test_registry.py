"""Z343-Z366 symbolic element names and RGB permutation colors."""
import csv,pathlib,re
from itertools import permutations
ROOTS=('nil','un','bi','tri','quad','pent','hex','sept','oct','enn')
LETTERS=('n','u','b','t','q','p','h','s','o','e')
COLORS=tuple(sorted(set(permutations((3,1,2)))))
def make(z):
 ds=tuple(map(int,str(z)));stem=''.join(ROOTS[d] for d in ds)
 name=(stem[:-1] if stem.endswith('i') else stem)+'ium'
 symbol=''.join(LETTERS[d] for d in ds).capitalize()
 rgb=COLORS[(z-343)%6]
 return dict(z=z,name=name.capitalize(),symbol=symbol,orientation=':'.join(map(str,rgb)),color_hex='#'+''.join(f'{85*x:02X}' for x in rgb),r=85*rgb[0],g=85*rgb[1],b=85*rgb[2],color_basis='symbolic_RGB_not_spectrum')
rows=[make(z) for z in range(343,367)]
checks={
 'count_24':len(rows)==24,
 'bounds':rows[0]['z']==343 and rows[-1]['z']==366,
 'continuous':[r['z'] for r in rows]==list(range(343,367)),
 'unique_z':len({r['z'] for r in rows})==24,
 'unique_symbols':len({r['symbol'] for r in rows})==24,
 'unique_names':len({r['name'] for r in rows})==24,
 'three_letter_symbols':all(len(r['symbol'])==3 for r in rows),
 'end_name':rows[-1]['name']=='Trihexhexium',
 'start_name':rows[0]['name']=='Triquadtrium',
 'six_rgb_colors':len({r['color_hex'] for r in rows})==6,
 'four_cycles':all(rows[i]['color_hex']==rows[i+6]['color_hex'] for i in range(18)),
 'channels_are_85_170_255':all(sorted([r['r'],r['g'],r['b']])==[85,170,255] for r in rows),
 'all_colors_valid_hex':all(re.fullmatch(r'#[0-9A-F]{6}',r['color_hex']) for r in rows),
 'occupancy_six':all(sum(map(int,r['orientation'].split(':')))==6 for r in rows),
 'not_wavelength':all(r['color_basis']=='symbolic_RGB_not_spectrum' for r in rows),
}
out=pathlib.Path(__file__).with_name('registry_z343_z366.csv')
with out.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
with out.open() as f:got=list(csv.DictReader(f))
checks['csv_roundtrip']=len(got)==24 and got[-1]['symbol']=='Thh'
for k,ok in checks.items():print(('PASS' if ok else 'FAIL'),k)
print(f'{sum(checks.values())}/{len(checks)} PASS')
assert all(checks.values())
