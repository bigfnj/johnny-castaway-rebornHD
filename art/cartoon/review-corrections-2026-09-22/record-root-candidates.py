"""Record this review's two local candidates without changing approvals."""
import hashlib
import json
from pathlib import Path
from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ART=ROOT/'art/cartoon'
rows={r['key']:r for r in json.loads((ART/'mermaid-expression-corrections-v1/review-data.json').read_text(encoding='utf-8-sig'))['assets']}
def pin(path):
    result={'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    if path.suffix=='.png':
        with Image.open(path) as im:
            result.update(canvas=list(im.size),mode=im.mode,alpha_range=list(im.convert('RGBA').getchannel('A').getextrema()))
    return result
specs=[('suzy','SSUZY1.BMP','004','004-upright-bottle-local-v1.png',
        'Hold the sunblock bottle upright; retain the exact approved inward belly curve and stacked legs.'),
       ('gift014','SMGIFT.BMP','014','014-generated-v1.png',
        'Extended hand palm up, open and ready to receive something being placed in it.')]
for folder,resource,frame,filename,change in specs:
    target=HERE/folder
    row=rows[f'{resource}-{frame}']
    previous=(ART/'visitor-leg-pose-corrections-v2/direct-composite-004-v3/004-composite-v3.png' if folder=='suzy'
              else ART/'mermaid-expression-corrections-v1/generation/SMGIFT.BMP/014-generated-v1.png')
    original=row['images']['original']
    entry={'resource':resource,'frame':frame,'original':original,'previous':pin(previous),
           'output':pin(target/filename),'status':'pending_review','requested_change':change,
           'request':pin(target/f'{frame}-request.json'),'appearance_approval':None}
    if folder=='gift014':
        record={'tool':'image_gen.imagegen','mode':'built-in','resource':resource,'frame':frame,
                'request':entry['request'],'output':entry['output'],'appearance_approval':None,
                'production_integrated':False,'native_motion_checked':False,
                'visual_review':'Open palm faces up with connected wrist; identity, small nearer hand and waterline retained.'}
        (target/f'{frame}-record.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    entry['record']=pin(target/f'{frame}-record.json')
    (target/'manifest.json').write_text(json.dumps({'entries':[entry]},indent=2)+'\n',encoding='utf-8')
    print(entry['resource'],entry['frame'],entry['output']['path'])
