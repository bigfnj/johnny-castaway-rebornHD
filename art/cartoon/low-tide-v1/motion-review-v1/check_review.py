import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from PIL import Image

root=Path.cwd()
folder=root/'art/cartoon/low-tide-v1/motion-review-v1'
manifest=json.loads((folder/'manifest.json').read_bytes())
sha=lambda raw:hashlib.sha256(raw).hexdigest()
images={}
for name,row in manifest['files'].items():
    path=folder/name
    assert sha(path.read_bytes())==row['sha256'],name
    im=Image.open(path).convert('RGB')
    assert list(im.size)==row['size'] and sha(im.tobytes())==row['rgb_sha256'],name
    images[name]=im

def verify_frames(data):
    count=0
    for clip in data['clips']:
        for side in ['before','after']:
            report_path=folder/clip[side]['report']
            if sha(report_path.read_bytes())!=clip[side]['report_sha256']:
                raise ValueError(report_path.name+': report identity')
            report=json.loads(report_path.read_bytes())
            times={r['time_ms']:r for r in report['displays']}
            expected=[]
            for time,row in sorted(times.items()):
                if expected and expected[-1]['pixels_sha256']==row['pixels_sha256']:
                    continue
                expected.append(row)
            if len(expected)!=len(clip[side]['timeline']):
                raise ValueError(clip['id']+'/'+side+': timeline count')
            for frame,record in zip(clip[side]['timeline'],expected):
                label=clip['id']+'/'+side+'/'+str(frame['ordinal'])
                if any(frame[k]!=record[k] for k in ['time_ms','phases','ordinal']):
                    raise ValueError(label+': native timing')
                full=images[clip['base']].copy()
                for patch in frame['patches']:
                    full.paste(images[patch['file']],patch['origin'])
                if sha(full.tobytes())!=record['pixels_sha256']:
                    raise ValueError(label+': native pixels')
                count+=1
    return count

count=verify_frames(manifest)
controls=[]
for name,message,edit in [
    ('wrong-time','native timing',lambda m:m['clips'][0]['after']['timeline'][0].update(time_ms=1)),
    ('shifted-patch','native pixels',lambda m:m['clips'][0]['after']['timeline'][0]['patches'][1].update(origin=[259,646])),
]:
    altered=copy.deepcopy(manifest)
    edit(altered)
    try:
        verify_frames(altered)
    except ValueError as error:
        if message not in str(error):
            raise
        controls.append({'control':name,'failure':str(error),'expected_failure':True})
    else:
        raise AssertionError(name+' survived')
assert verify_frames(manifest)==count
builder=root/'art/cartoon/low-tide-v1/build_wave_review.py'
spec=importlib.util.spec_from_file_location('review_builder',builder)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
png=root/'art/cartoon/low-tide-v1/native-v1/images/prewave-candidate.png'
try:
    module.checked_image(png,'0'*64)
except ValueError as error:
    assert png.name in str(error) and 'PNG identity' in str(error)
    controls.append({'control':'wrong-png-hash','failure':str(error),'expected_failure':True})
else:
    raise AssertionError('wrong-png-hash survived')
original_save=Image.Image.save
def wrong_save(self,fp,*args,**kwargs):
    return original_save(Image.new('RGB',self.size),fp,*args,**kwargs)
try:
    Image.Image.save=wrong_save
    module.encode_lossless(Image.new('RGB',(2,2),(200,100,50)))
except ValueError as error:
    assert 'pixel readback' in str(error)
    controls.append({'control':'wrong-encoded-pixels','failure':str(error),'expected_failure':True})
else:
    raise AssertionError('wrong-encoded-pixels survived')
finally:
    Image.Image.save=original_save
module.encode_lossless(Image.new('RGB',(2,2),(200,100,50)))
result={'status':'PASS','manifest_sha256':sha((folder/'manifest.json').read_bytes()),
        'review_html_sha256':sha((folder/'review.html').read_bytes()),
        'image_files_exact':len(images),'complete_native_frames_reconstructed':count,
        'controls':controls,'restored_positive':True,
        'scope':'Readback of preserved images, native reports, rendered frame reconstruction and timeline. Four in-memory damaged-input controls; no runtime mutation.'}
(folder/'checks.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
print(json.dumps(result))
