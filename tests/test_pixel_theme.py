import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np
from PIL import Image,PngImagePlugin

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from pixel_theme import adapt,read_image
from verify_theme import verify


class PixelThemeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.pixels=np.array([[[255,255,255,255],[0,0,0,100],[237,71,151,255]],[[1,2,3,255],[127,127,127,255],[30,130,210,0]]],dtype=np.uint8)
        self.src=self.root/'source.png';Image.fromarray(self.pixels).save(self.src)
        self.original_bytes=self.src.read_bytes()

    def tearDown(self):self.tmp.cleanup()

    def run_transform(self,name='out',**kw):
        opts={'kind':'line-art','mode':'neutral-invert','tolerance':0,'protect':[],'mapping':{}};opts.update(kw)
        return adapt(self.src,self.root/(name+'.png'),**opts)

    def test_exact_known_pixels_and_alpha(self):
        self.run_transform();b=np.array(Image.open(self.root/'out.png'))
        self.assertEqual(b[0,0].tolist(),[0,0,0,255]);self.assertEqual(b[0,1].tolist(),[255,255,255,100]);self.assertEqual(b[1,1].tolist(),[128,128,128,255])
        np.testing.assert_array_equal(b[0,2],self.pixels[0,2]);np.testing.assert_array_equal(b[1,2],self.pixels[1,2]);np.testing.assert_array_equal(b[:,:,3],self.pixels[:,:,3])

    def test_tolerance_and_protected_pixels(self):
        self.run_transform(tolerance=16,protect=['0,1,1,1']);b=np.array(Image.open(self.root/'out.png'));np.testing.assert_array_equal(b[1,0],self.pixels[1,0]);self.assertTrue(verify(self.root/'out.json')['passed'])

    def test_double_inversion(self):
        self.run_transform(tolerance=16);self.src=self.root/'out.png';self.run_transform('restored',tolerance=16);np.testing.assert_array_equal(np.array(Image.open(self.root/'restored.png')),self.pixels)

    def test_measurement_keep_is_byte_identical(self):
        self.run_transform(kind='measurement',mode='keep');self.assertEqual((self.root/'out.png').read_bytes(),self.original_bytes);self.assertTrue(verify(self.root/'out.json')['passed'])

    def test_measurement_inversion_refused(self):
        with self.assertRaises(ValueError):self.run_transform(kind='measurement')

    def test_keep_recoloring_refused(self):
        with self.assertRaises(ValueError):self.run_transform(mode='keep',mapping={'#000000':'#abcdef'})

    def test_color_collision_refused(self):
        with self.assertRaises(ValueError):self.run_transform(mapping={'#ed4797':'#ffffff'})

    def test_exact_color_map(self):
        self.run_transform(mapping={'#ed4797':'#abcdef'});self.assertEqual(np.array(Image.open(self.root/'out.png'))[0,2,:3].tolist(),[171,205,239]);self.assertTrue(verify(self.root/'out.json')['passed'])

    def test_every_sidecar_collision_refused(self):
        for suffix in ['.png','.json','.mask.png','.comparison.png']:
            p=self.root/('out'+suffix);p.write_bytes(b'do not overwrite')
            with self.assertRaises(ValueError):self.run_transform()
            self.assertEqual(p.read_bytes(),b'do not overwrite');p.unlink()

    def test_source_unchanged(self):
        self.run_transform();self.assertEqual(self.src.read_bytes(),self.original_bytes)

    def test_sixteen_bit_refused(self):
        self.src=self.root/'high.png';Image.fromarray(np.array([[0,65535]],dtype=np.uint16)).save(self.src)
        with self.assertRaises(ValueError):self.run_transform()

    def test_palette_input_refused(self):
        self.src=self.root/'palette.png';Image.new('P',(4,4)).save(self.src)
        with self.assertRaises(ValueError):self.run_transform()

    def test_nonidentity_orientation_refused(self):
        exif=Image.Exif();exif[274]=6;Image.fromarray(self.pixels).save(self.src,exif=exif)
        with self.assertRaises(ValueError):self.run_transform()

    def test_grayscale_profile_not_silently_reinterpreted(self):
        Image.new('L',(4,4),127).save(self.src,icc_profile=b'grayscale-profile-test')
        with self.assertRaises(ValueError):self.run_transform()

    def test_invalid_rectangles_refused(self):
        for rectangle in ['0,0,0,1','-1,0,1,1','2,1,2,1','0,0,1']:
            with self.assertRaises(ValueError):self.run_transform(protect=[rectangle])

    def test_precision_and_color_metadata(self):
        info=PngImagePlugin.PngInfo();info.add(b'gAMA',b'\x00\x00\xb1\x8f');info.add(b'sRGB',b'\x00')
        Image.fromarray(self.pixels).save(self.src,pnginfo=info)
        self.run_transform();self.assertTrue(verify(self.root/'out.json')['passed'])

    def test_output_tamper_detected_even_if_file_hash_updated(self):
        self.run_transform();p=self.root/'out.png';b=np.array(Image.open(p));b[0,2,0]=5;Image.fromarray(b).save(p)
        rec=self.root/'out.json';r=json.loads(rec.read_text());r['output_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();rec.write_text(json.dumps(r))
        result=verify(rec);self.assertFalse(result['passed']);self.assertFalse(result['checks']['exact_transform_replay'])

    def test_mask_tamper_detected(self):
        self.run_transform();Image.new('L',(3,2),0).save(self.root/'out.mask.png');self.assertFalse(verify(self.root/'out.json')['passed'])

    def test_random_image_inverse_and_unselected_pixels(self):
        a=np.random.default_rng(7).integers(0,256,(67,91,4),dtype=np.uint8);a[:10,:,0:3]=127;Image.fromarray(a).save(self.src)
        self.run_transform(tolerance=16);self.assertTrue(verify(self.root/'out.json')['passed'])

    def test_cli_and_optimized_python(self):
        r=subprocess.run([sys.executable,'-O',str(ROOT/'scripts/pixel_theme.py'),str(self.src),str(self.root/'out.png'),'--kind','line-art'],capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr)
        r=subprocess.run([sys.executable,str(ROOT/'scripts/verify_theme.py'),str(self.root/'out.json')],capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr)


if __name__=='__main__':unittest.main()
