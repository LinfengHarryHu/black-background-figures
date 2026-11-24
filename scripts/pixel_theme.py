"""Deterministic color adaptation of 8-bit PNG line art; no generative model."""
import argparse
import hashlib
import io
import json
import platform
import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, PngImagePlugin, __version__ as PILLOW_VERSION

VERSION = '0.2.0'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rgb(value):
    if not isinstance(value, str) or len(value) != 7 or value[0] != '#':
        raise ValueError('Colors must use #RRGGBB')
    return tuple(int(value[i:i+2], 16) for i in (1, 3, 5))


def read_image(path):
    data = Path(path).read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n' or data[12:16] != b'IHDR':
        raise ValueError('Input must be PNG; export a documented 8-bit presentation copy first')
    if data[24] != 8 or data[25] not in (0, 2, 4, 6):
        raise ValueError('Only 8-bit L, LA, RGB or RGBA PNG is supported; no silent precision conversion')
    im = Image.open(io.BytesIO(data))
    if getattr(im, 'n_frames', 1) != 1:
        raise ValueError('Animated PNG is not supported')
    if im.getexif().get(274, 1) != 1:
        raise ValueError('Non-identity EXIF orientation is not supported')
    im.load()
    return data, im, np.array(im.convert('RGBA'))


def normalize_options(kind, mode, tolerance, protect, mapping):
    if kind not in ('line-art', 'measurement') or mode not in ('neutral-invert', 'keep'):
        raise ValueError('Unsupported kind or mode')
    if not 0 <= tolerance <= 32:
        raise ValueError('Chroma tolerance must be in [0, 32]')
    if mode == 'keep' and mapping:
        raise ValueError('Keep mode cannot remap colors')
    if kind == 'measurement' and mode != 'keep':
        raise ValueError('Measurement images must be retained unchanged')
    if not isinstance(mapping, dict):
        raise ValueError('Color map must be an object of exact #RRGGBB pairs')
    normalized = {}
    for old, new in mapping.items():
        rgb(old); rgb(new)
        if old.lower() in normalized:
            raise ValueError('Duplicate normalized source color')
        normalized[old.lower()] = new.lower()
    regions = []
    for rect in protect:
        r = [int(x) for x in rect.split(',')] if isinstance(rect, str) else list(rect)
        if len(r) != 4 or any(type(x) is not int for x in r) or min(r[:2]) < 0 or min(r[2:]) <= 0:
            raise ValueError('Protected rectangles require nonnegative x,y and positive width,height')
        regions.append(r)
    return {'kind':kind,'mode':mode,'chroma_tolerance':tolerance,'protected_regions':regions,'color_map':normalized}


def transform(original, opts):
    result = original.copy()
    height, width = original.shape[:2]
    eligible = np.ones((height,width), dtype=bool)
    for x,y,w,h in opts['protected_regions']:
        if x+w > width or y+h > height:
            raise ValueError('Protected region is outside the source image')
        eligible[y:y+h,x:x+w] = False
    channels = original[:,:,:3].astype(np.int16)
    selected = eligible & (channels.max(2)-channels.min(2) <= opts['chroma_tolerance'])
    if opts['mode'] == 'neutral-invert':
        result[selected,:3] = 255-original[selected,:3]
    else:
        selected[:] = False
    for old,new in opts['color_map'].items():
        mask = eligible & np.all(original[:,:,:3] == rgb(old),axis=2)
        result[mask,:3] = rgb(new)
        selected |= mask
    # Refuse color maps that merge distinct colors actually present in the image.
    # This is conservative; it does not prove human perceptual distinguishability.
    if opts['color_map']:
        pairs = np.unique(np.concatenate((original[:,:,:3],result[:,:,:3]),axis=2).reshape(-1,6),axis=0)
        destinations = {}
        for row in pairs:
            src,dst = tuple(row[:3]),tuple(row[3:])
            if dst in destinations and destinations[dst] != src:
                raise ValueError('Color map would merge distinct observed source colors')
            destinations[dst] = src
    if not np.array_equal(original[:,:,3],result[:,:,3]):
        raise ValueError('Alpha invariant failed')
    if not np.array_equal(original[~selected],result[~selected]) or not np.array_equal(original[~eligible],result[~eligible]):
        raise ValueError('Unselected/protected pixel invariant failed')
    return result,selected


def color_metadata(data, im):
    info = PngImagePlugin.PngInfo()
    retained = []
    pos = 8
    while pos < len(data):
        size = struct.unpack('>I',data[pos:pos+4])[0]
        tag = data[pos+4:pos+8]
        if tag in (b'gAMA',b'sRGB',b'cHRM',b'pHYs'):
            info.add(tag,data[pos+8:pos+8+size]); retained.append(tag.decode('ascii'))
        pos += size+12
    kw = {'pnginfo':info}
    for key in ('icc_profile','exif'):
        if key in im.info:
            kw[key] = im.info[key]; retained.append(key)
    return kw,retained


def exclusive_write(path, data):
    with Path(path).open('xb') as f:
        f.write(data)


def png_bytes(im, **kwargs):
    buf=io.BytesIO();im.save(buf,format='PNG',**kwargs);return buf.getvalue()


def adapt(source, output, **options):
    source,output=Path(source),Path(output)
    if source.resolve() == output.resolve() or output.suffix.lower() != '.png':
        raise ValueError('Output must be a different .png file')
    stem=output.with_suffix('')
    paths=[output,Path(str(stem)+'.mask.png'),Path(str(stem)+'.comparison.png'),Path(str(stem)+'.json')]
    if any(p.exists() for p in paths):
        raise ValueError('Output or audit sidecar exists; choose a new variant name')
    opts=normalize_options(**options)
    data,im,original=read_image(source)
    if opts['mode']!='keep' and im.mode in ('L','LA') and 'icc_profile' in im.info:
        raise ValueError('Grayscale ICC profiles require a separately documented RGB export')
    result,mask=transform(original,opts)
    kw,retained=color_metadata(data,im)
    out_bytes=data if opts['mode']=='keep' else png_bytes(Image.fromarray(result),**kw)
    decoded=np.array(Image.open(io.BytesIO(out_bytes)).convert('RGBA'))
    if not np.array_equal(decoded,result):
        raise ValueError('Encoded output differs from expected pixels')
    mask_bytes=png_bytes(Image.fromarray(mask.astype(np.uint8)*255))
    # Transparent artwork is displayed against the same checkerboard in both panels.
    h,w=original.shape[:2];yy,xx=np.indices((h,w));gray=np.where((xx//12+yy//12)%2,175,220).astype(np.uint8)
    bg=Image.fromarray(np.dstack([gray,gray,gray,np.full_like(gray,255)]))
    pair=Image.new('RGB',(w*2,h+40),'#202020')
    for offset,arr in [(0,original),(w,result)]:
        panel=Image.alpha_composite(bg,Image.fromarray(arr)).convert('RGB');pair.paste(panel,(offset,40))
    draw=ImageDraw.Draw(pair);draw.text((8,12),'ORIGINAL',fill='white');draw.text((w+8,12),'ADAPTED',fill='white')
    record={'schema':'pixel-theme/v2','tool_version':VERSION,'script_sha256':sha(Path(__file__).read_bytes()),
        'environment':{'python':platform.python_version(),'numpy':np.__version__,'pillow':PILLOW_VERSION},
        'source':source.name,'output':output.name,'mask':paths[1].name,'comparison':paths[2].name,
        'source_sha256':sha(data),'output_sha256':sha(out_bytes),'mask_sha256':sha(mask_bytes),
        'source_mode':im.mode,'decoded_mode':'RGBA','dimensions':list(im.size),'options':opts,
        'source_rgba_sha256':sha(original.tobytes()),'output_rgba_sha256':sha(result.tobytes()),
        'pixels_selected':int(mask.sum()),'pixels_modified':int(np.any(original!=result,axis=2).sum()),
        'retained_color_metadata':retained,'alpha_unchanged':True,'unselected_pixels_unchanged':True,
        'resampling':False,'generative_model_used':False,'visual_review':'pending',
        'claim_boundary':'Exact specified color transform, not proof of perceptual or scientific equivalence.'}
    if Path(source).read_bytes()!=data:
        raise ValueError('Source changed while processing')
    output.parent.mkdir(parents=True,exist_ok=True)
    payloads=[out_bytes,mask_bytes,png_bytes(pair),(json.dumps(record,indent=2)+'\n').encode()]
    for p,b in zip(paths,payloads):exclusive_write(p,b)
    return record


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--kind',choices=['line-art','measurement'],required=True)
    p.add_argument('--mode',choices=['neutral-invert','keep'],default='neutral-invert')
    p.add_argument('--chroma-tolerance',type=int,default=0)
    p.add_argument('--protect',action='append',default=[],help='x,y,width,height in input pixels')
    p.add_argument('--color-map',type=Path,help='Exact RGB map; overrides inversion for matching original colors')
    a=p.parse_args()
    try:
        mapping=json.loads(a.color_map.read_text()) if a.color_map else {}
        record=adapt(a.source,a.output,kind=a.kind,mode=a.mode,tolerance=a.chroma_tolerance,protect=a.protect,mapping=mapping)
    except (ValueError,OSError,TypeError) as e:p.exit(2,str(e)+'\n')
    print(json.dumps(record,indent=2))


if __name__=='__main__':main()
