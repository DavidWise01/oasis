#!/usr/bin/env python3
"""Test065: synthetic regression. NOT evidence about historical glyphs."""
import unittest
from PIL import Image

TARGETS=('K8','L8','M8','N8','M9','N9')

def crop_grid(img,cell,box):
    col=int(cell[1:])-1; row=ord(cell[0])-ord('A')
    x0,y0,x1,y1=box
    return img.crop((round(x0+(x1-x0)*col/16),round(y0+(y1-y0)*row/16),round(x0+(x1-x0)*(col+1)/16),round(y0+(y1-y0)*(row+1)/16)))
def code16(im):
    im=im.convert('L').resize((4,4),Image.Resampling.BOX)
    return ''.join('1' if x<128 else '0' for x in im.getdata())
def fixture():
    im=Image.new('L',(256,256),255)
    for cell in TARGETS:
        x=(int(cell[1:])-1)*16; y=(ord(cell[0])-65)*16
        for yy in range(y+4,y+12):
            for xx in range(x+4,x+12): im.putpixel((xx,yy),0)
    return im
class SyntheticAtlasTests(unittest.TestCase):
    def test_targets(self):
        im=fixture()
        for c in TARGETS:
            glyph=crop_grid(im,c,(0,0,256,256))
            self.assertEqual(glyph.size,(16,16))
            self.assertEqual(glyph.getpixel((8,8)),0)
            self.assertEqual(glyph.getpixel((0,0)),255)
    def test_blank_control(self):
        self.assertEqual(code16(crop_grid(fixture(),'J8',(0,0,256,256))),'0'*16)
    def test_identical_zero_distance(self):
        im=fixture()
        for c in TARGETS:
            bits=code16(crop_grid(im,c,(0,0,256,256)))
            self.assertEqual(sum(a!=b for a,b in zip(bits,bits)),0)
    def test_single_mutation_locality(self):
        a=fixture();b=fixture()
        for y in range(12*16,13*16):
            for x in range(7*16,8*16):b.putpixel((x,y),0)
        distance=lambda c:sum(x!=y for x,y in zip(code16(crop_grid(a,c,(0,0,256,256))),code16(crop_grid(b,c,(0,0,256,256)))))
        self.assertGreater(distance('M8'),0)
        for c in TARGETS:
            if c!='M8':self.assertEqual(distance(c),0)
    def test_address_orientation(self):
        im=fixture()
        self.assertEqual(im.getpixel((7*16+8,10*16+8)),0)
if __name__=='__main__':unittest.main(verbosity=2)
