"""Read-only replay audit of saved pixels, hashes, masks and color metadata."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
from pixel_theme import VERSION,read_image,sha,transform,normalize_options


def verify(record_path,source=None,output=None):
    path=Path(record_path);r=json.loads(path.read_text());base=path.parent
    if r.get('schema')!='pixel-theme/v2' or r.get('tool_version')!=VERSION:
        raise ValueError('Unsupported record schema or tool version')
    src=Path(source) if source else base/r['source']
    dst=Path(output) if output else base/r['output']
    src_bytes,src_im,a=read_image(src);out_bytes,out_im,b=read_image(dst)
    opts=r['options'];opts=normalize_options(opts['kind'],opts['mode'],opts['chroma_tolerance'],opts['protected_regions'],opts['color_map'])
    expected,mask=transform(a,opts)
    mask_bytes=(base/r['mask']).read_bytes()
    actual_mask=np.array(Image.open(base/r['mask']))
    checks={
        'source_file_hash':sha(src_bytes)==r['source_sha256'],
        'output_file_hash':sha(out_bytes)==r['output_sha256'],
        'mask_file_hash':sha(mask_bytes)==r['mask_sha256'],
        'dimensions':a.shape==b.shape and list(src_im.size)==r['dimensions'],
        'exact_transform_replay':np.array_equal(b,expected),
        'exact_selection_mask':np.array_equal(actual_mask,mask.astype(np.uint8)*255),
        'alpha_unchanged':np.array_equal(a[:,:,3],b[:,:,3]),
        'source_pixel_hash':sha(a.tobytes())==r['source_rgba_sha256'],
        'output_pixel_hash':sha(b.tobytes())==r['output_rgba_sha256'],
        'script_version_hash':sha(Path(__file__).with_name('pixel_theme.py').read_bytes())==r['script_sha256'],
        'color_metadata_preserved':all(src_im.info.get(k)==out_im.info.get(k) for k in ['icc_profile','gamma','srgb','chromaticity','exif']),
    }
    if a.shape==b.shape:checks['unselected_pixels_unchanged']=np.array_equal(a[~mask],b[~mask])
    if opts['mode']=='neutral-invert' and not opts['color_map']:
        restored=b.copy()
        if restored.shape==a.shape:
            restored[mask,:3]=255-restored[mask,:3]
        checks['inverse_with_saved_mask_restores_pixels']=np.array_equal(restored,a)
    result={'passed':all(checks.values()),'checks':checks,'visual_review':r.get('visual_review','pending'),
        'claim_boundary':'Checks exact transformation relative to the supplied source. Does not authenticate that source or prove visual equivalence.'}
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('record',type=Path);p.add_argument('--source',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    try:r=verify(a.record,a.source,a.output)
    except (ValueError,OSError,KeyError,TypeError) as e:p.exit(2,str(e)+'\n')
    print(json.dumps(r,indent=2));raise SystemExit(0 if r['passed'] else 1)


if __name__=='__main__':main()
