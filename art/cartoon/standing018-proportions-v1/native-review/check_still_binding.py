"""One changed-but-valid PNG control for this still-review handoff, in fresh scratch."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from PIL import Image

HERE=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--positive-review',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    assert not a.output.exists(),'preserve still-binding control'
    script=HERE/'build_still.py';digest=sha(script.read_bytes())
    before=json.loads((a.positive_review/'review-record.json').read_bytes())
    assert before['builder_sha256']==digest,'completed positive uses current builder'
    a.output.mkdir(parents=True);staged=a.output/'candidate';staged.mkdir()
    for name in ('summary.json','preparation.json'):shutil.copyfile(a.candidate/name,staged/name)
    full=staged/'front_arc/full';full.mkdir(parents=True)
    for name in ('report.json','display-001.png'):shutil.copyfile(a.candidate/'front_arc/full'/name,full/name)
    png=full/'display-001.png';original=png.read_bytes()
    with Image.open(png) as im:
        im=im.convert('RGB');r,g,b=im.getpixel((0,0));im.putpixel((0,0),(r^1,g,b));im.save(png)
    altered=sha(png.read_bytes())
    def run(name):
        cmd=[sys.executable,'-B',str(script),'--candidate',str(staged),'--output',str(a.output/name)]
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
        (a.output/(name+'.stdout.txt')).write_text(r.stdout,encoding='utf-8');(a.output/(name+'.stderr.txt')).write_text(r.stderr,encoding='utf-8')
        assert 'WITNESS build_still.py SHA256='+digest in r.stdout,'executed builder witness'
        return r,cmd
    negative,cmd=run('altered-input')
    wanted='AssertionError: bound018 PNG:revised:'+str(png)
    assert negative.returncode==1 and wanted in negative.stderr and negative.stderr.count('AssertionError:')==1,'exact one revised PNG binding rejection'
    png.write_bytes(original)
    restored,restore_cmd=run('restored-positive')
    assert restored.returncode==0 and 'PASS three exact native018 still panels' in restored.stdout,'restored positive builder'
    result={'status':'PASS','control':'changed valid display-001.png with stale capture report','negative':'FIRED','exact_failure':wanted,
        'positive_before_record_sha256':sha((a.positive_review/'review-record.json').read_bytes()),'restored_positive':True,
        'executed_builder_sha256':digest,'checker_sha256':sha(Path(__file__).read_bytes()),'altered_png_sha256':altered,
        'original_png_sha256':sha(original),'commands':[cmd,restore_cmd],'scope':'Copied candidate data only; actual captures and publication unchanged.'}
    (a.output/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('PASS one changed-valid-PNG handoff control: exact revised PNG failure; restored positive passed')

if __name__=='__main__':main()
