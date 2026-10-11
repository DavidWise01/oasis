import hashlib, io, unittest
from PIL import Image, ImageDraw, ImageEnhance
N=16; SIZE=256; TARGETS=('K8','L8','M8','N8','M9','N9')
def atlas():
    im=Image.new('L',(SIZE,SIZE),255)
    d=ImageDraw.Draw(im)
    for cell in TARGETS:
        r=ord(cell[0])-65; c=int(cell[1:])-1
        x,y=c*16,r*16
        d.rectangle((x+4,y+4,x+11,y+11),fill=32)
    return im
def crop(im,cell,bounds=(0,0,SIZE,SIZE)):
    r=ord(cell[0])-65;c=int(cell[1:])-1
    x0,y0,x1,y1=bounds
    return im.crop((round(x0+(x1-x0)*c/16),round(y0+(y1-y0)*r/16),round(x0+(x1-x0)*(c+1)/16),round(y0+(y1-y0)*(r+1)/16)))
def code(im,t=128):
    return ''.join('1' if v<t else '0' for v in im.resize((4,4),Image.Resampling.BOX).getdata())
def mismatch(a,b):return sum(x!=y for x,y in zip(a,b))
def signature(im):
    b=io.BytesIO(); im.save(b,format='PNG'); return hashlib.sha256(b.getvalue()).hexdigest()
def registered_errors(a,b,bounds_a=(0,0,SIZE,SIZE),bounds_b=(0,0,SIZE,SIZE),threshold=128):
    return {cell:mismatch(code(crop(a,cell,bounds_a),threshold),code(crop(b,cell,bounds_b),threshold)) for cell in TARGETS}
class Test066(unittest.TestCase):
    def test_exact_copy(self):
        a=atlas(); self.assertEqual(signature(a),signature(a.copy()));self.assertTrue(all(v==0 for v in registered_errors(a,a.copy()).values()))
    def test_reencoding_not_independent(self):
        a=atlas();rgb=a.convert('RGB');self.assertNotEqual(signature(a),signature(rgb));self.assertEqual(a.convert('RGB').tobytes(),rgb.tobytes())
    def test_shift_detected(self):
        a=atlas();shift=Image.new('L',(SIZE,SIZE),255);shift.paste(a,(4,0));errors=registered_errors(a,shift)
        self.assertTrue(any(v>0 for v in errors.values()))
    def test_shift_compensated_interior(self):
        a=atlas();shift=Image.new('L',(SIZE+8,SIZE),255);shift.paste(a,(4,0))
        errors=registered_errors(a,shift,bounds_b=(4,0,260,256));self.assertEqual(sum(errors.values()),0)
    def test_bad_bounds_raise_mismatch(self):
        a=atlas();self.assertGreater(sum(registered_errors(a,a,bounds_b=(8,0,264,256)).values()),0)
    def test_threshold_stable_far_from_boundary(self):
        a=atlas()
        for t in (96,112,128,144,160):
            self.assertTrue(all(v==0 for v in registered_errors(a,a,threshold=t).values()))
    def test_threshold_sensitive_near_boundary(self):
        a=atlas();p=crop(a,'M8');q=p.point(lambda v: 126 if v<100 else v)
        self.assertNotEqual(code(q,96),code(q,160))
    def test_photometric_changes_not_new_capture(self):
        a=atlas();b=ImageEnhance.Contrast(a).enhance(1.2)
        self.assertEqual(a.size,b.size)
        self.assertTrue(all(v==0 for v in registered_errors(a,b).values()))
    def test_geometry_not_proven_by_hash_difference(self):
        a=atlas();b=a.copy();b.putpixel((0,0),254)
        self.assertNotEqual(signature(a),signature(b));self.assertTrue(all(v==0 for v in registered_errors(a,b).values()))
    def test_exploratory_encoder_limit(self):
        a=atlas();u=crop(a,'M8');v=u.copy();v.putpixel((6,6),0)
        self.assertNotEqual(u.tobytes(),v.tobytes());self.assertEqual(code(u),code(v))
if __name__=='__main__':unittest.main(verbosity=2)
