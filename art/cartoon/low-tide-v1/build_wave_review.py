"""Prepare pixel-exact native wave captures for browser playback."""
import argparse
import hashlib
import io
import json
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def checked_image(path, expected):
    raw = path.read_bytes()
    if sha(raw) != expected:
        raise ValueError(f'{path.name}: native PNG identity differs')
    return Image.open(io.BytesIO(raw)).convert('RGB')


def encode_lossless(image):
    out = io.BytesIO()
    image.save(out, format='WEBP', lossless=True, method=4)
    raw = out.getvalue()
    if Image.open(io.BytesIO(raw)).convert('RGB').tobytes() != image.tobytes():
        raise ValueError('lossless review image pixel readback differs')
    return raw


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a = p.parse_args()
    out = a.output.resolve()
    (out/'images').mkdir(parents=True,exist_ok=True)
    (out/'reports').mkdir(exist_ok=True)
    clips = []
    files = {}
    patch_rectangles = [(0,0,1280,240),(258,646,1280,768)]
    def store_image(im):
        identity=sha(str(im.size).encode()+im.tobytes())
        name=f'images/{identity}.webp'
        if name not in files:
            raw=encode_lossless(im)
            (out/name).write_bytes(raw)
            files[name]={'sha256':sha(raw),'rgb_sha256':sha(im.tobytes()),'size':list(im.size)}
        return name
    for case,title in [('none','No decoration'),('clover','St Patrick\'s clovers')]:
        sides = {}
        duration = 0
        base_report=json.loads((a.candidate/case/'smoke/report.json').read_bytes())
        first=base_report['displays'][0]
        base=checked_image(a.candidate/case/'smoke'/first['file'],first['png_sha256'])
        base_name=store_image(base)
        for side,folder in [('before',a.baseline),('after',a.candidate)]:
            source_folder = folder/case/'smoke'
            report_path = source_folder/'report.json'
            report_raw = report_path.read_bytes()
            report = json.loads(report_raw)
            report_name = f'reports/{case}-{side}.json'
            (out/report_name).write_bytes(report_raw)
            times = {}
            for row in report['displays']:
                times[row['time_ms']] = row
            timeline = []
            cached = {}
            for time,row in sorted(times.items()):
                if row['file'] not in cached:
                    path = source_folder/row['file']
                    im = checked_image(path,row['png_sha256'])
                    identity = sha(im.tobytes())
                    if identity != row['pixels_sha256']:
                        raise ValueError(f'{path.name}: native RGB identity differs')
                    patches=[]
                    reconstructed=base.copy()
                    for rect in patch_rectangles:
                        patch=im.crop(rect)
                        name=store_image(patch)
                        patches.append({'file':name,'origin':list(rect[:2])})
                        reconstructed.paste(patch,rect[:2])
                    if reconstructed.tobytes()!=im.tobytes():
                        raise ValueError(f'{path.name}: reconstructed native frame differs')
                    cached[row['file']] = {'patches':patches,'native_rgb_sha256':identity}
                saved = cached[row['file']]
                if timeline and timeline[-1]['native_rgb_sha256']==saved['native_rgb_sha256']:
                    continue
                timeline.append({'time_ms':time,**saved,'ordinal':row['ordinal'],
                                 'phases':row['phases']})
            duration = max(duration,report['duration_ms'])
            sides[side] = {'timeline':timeline,'report':report_name,
                           'report_sha256':sha(report_raw),'archive_sha256':report['archive_sha256']}
        clips.append({'id':case,'title':title,'duration_ms':duration,'base':base_name,**sides})
    manifest = {'title':'Low-tide Cartoon waves','human_approved':False,'clips':clips,'files':files,
                'builder_sha256':sha(Path(__file__).read_bytes()),
                'scope':'Actual native displays at recorded tick times. Consecutive identical images omitted; final display at a shared timestamp wins. Shared base plus two lossless patches reconstruct each complete native RGB frame exactly, verified before publication.',
                'reuse':'Nine island phases reuse the approved white ripples with common family registrations; three rock-ring phases adapt their style to the separate rock.',
                'baseline':'Approved low-tide beach and rock with old low-tide fallback waves. It is not the approved high-tide Cartoon wave set.'}
    (out/'manifest.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
    print(json.dumps({'clips':len(clips),'unique_images':len(files),
                      'image_bytes':sum((out/name).stat().st_size for name in files),
                      'manifest_sha256':sha((out/'manifest.json').read_bytes())}))


if __name__=='__main__':
    main()
