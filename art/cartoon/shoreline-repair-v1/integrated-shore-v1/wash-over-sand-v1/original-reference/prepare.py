"""Exact supplied-original center phases; diagnostic palette, not color calibration."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
ARCHIVE = ROOT / 'art/cartoon/character-inventory-v1/reference-originals.zip'
ARCHIVE_SHA = 'b9a906dd6508b013e860c9ca7396b21ea78776f5c7d086b71f13f1ac530bd912'
MEMBERS = {6:'2aba9614280ffca6695098009adf5abc070329d49737088c69cc0a6c2a60b5df',
           7:'7158278ec5bd320cec6b5b89c9f7193d6e442f9091f86eb9f4a6cb11455f7952',
           8:'17738a8452aa3f7b758ffe4b59bb82c967d4f84a369a04f45a50fe771a6fbc73'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def png(image):
    out = io.BytesIO()
    image.save(out, format='PNG')
    return out.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    assert sha(ARCHIVE.read_bytes()) == ARCHIVE_SHA, 'original reference archive identity'
    outputs, rows = {}, []
    strip = Image.new('RGBA', (1280, 720), (75, 75, 75, 255))
    draw = ImageDraw.Draw(strip)
    with zipfile.ZipFile(ARCHIVE) as archive:
        for index, (frame, digest) in enumerate(MEMBERS.items()):
            member = f'native/BMP/BACKGRND.BMP/{frame:03}.png'
            raw = archive.read(member)
            assert sha(raw) == digest, f'{frame:03}: original member identity'
            native = Image.open(io.BytesIO(raw)).convert('RGBA')
            assert native.size == (160, 25), f'{frame:03}: original canvas'
            nearest = native.resize((1280, 200), Image.Resampling.NEAREST)
            # Independent every-pixel replication, including RGB under alpha0.
            assert all(nearest.getpixel((x,y)) == native.getpixel((x//8,y//8)) for y in range(200) for x in range(1280)), f'{frame:03}: exact nearest8 replication'
            guide = Image.new('RGBA', (1536, 1024), (0,0,0,0))
            guide.paste(nearest, (128, 360))
            assert guide.crop((128,360,1408,560)).tobytes() == nearest.tobytes(), f'{frame:03}: registered guide preserves pixels'
            outputs[f'{frame:03}-original-native.png'] = raw
            outputs[f'{frame:03}-original-nearest8.png'] = png(nearest)
            outputs[f'{frame:03}-original-guide.png'] = png(guide)
            strip.alpha_composite(nearest, (0, index*240+32))
            draw.text((8,index*240+6), f'Original {frame:03} | exact nearest8 | includes sand and water | diagnostic palette', fill='white')
            rows.append({'frame':frame,'member':member,'member_sha256':digest,'native_canvas':[160,25],
                         'native_origin':[364,319],'hd_origin':[728,638],'guide_canvas':[1536,1024],
                         'nearest_scale':8,'guide_offset':[128,360],
                         'guide_to_world_hd_affine':[.25,0,696,0,.25,548]})
    outputs['original-phase-strip.png'] = png(strip)
    record = {'schema_version':1,'scope':'Exact supplied-original center phase guidance, including changing sand and water. The palette is diagnostic, not calibrated original binary color.',
              'helper_sha256':sha(Path(__file__).read_bytes()),'archive':ARCHIVE.relative_to(ROOT).as_posix(),
              'archive_sha256':ARCHIVE_SHA,'frames':rows,'files_sha256':{p:sha(b) for p,b in outputs.items()},
              'checks':['Archive and three original member identities','Three native PNGs copied byte-exact','Every enlarged RGBA pixel independently checked against nearest8 source coordinate','Registered guide crop preserves all nearest8 RGBA bytes']}
    outputs['source.json'] = (json.dumps(record,indent=2)+'\n').encode()
    for name, raw in outputs.items():
        target = HERE / name
        if args.check:
            assert target.read_bytes() == raw, name+': fresh replay differs'
        else:
            assert not target.exists(), name+': refusing overwrite'
            target.write_bytes(raw)
    print(json.dumps({'status':'PASS','files':len(outputs),'check':args.check,'source_sha256':sha(outputs['source.json'])}))


if __name__ == '__main__':
    main()
