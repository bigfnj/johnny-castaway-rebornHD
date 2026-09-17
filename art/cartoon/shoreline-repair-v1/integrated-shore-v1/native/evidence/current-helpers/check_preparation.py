"""Execute focused private-package binding controls in fresh Python processes."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
from PIL import Image
from capture import HERE,ROOT,FRAMES,package_pair,sha,require,save

def main():
    p=argparse.ArgumentParser();p.add_argument('--runtime-root',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    require(not a.output.exists(),'fresh preparation control output');a.output.mkdir(parents=True)
    original={p.name:sha(p.read_bytes()) for p in (a.runtime_root/'BMP/BACKGRND.BMP').glob('*.png')}
    package_pair(a.baseline,a.candidate)
    controls=[]
    for name,expected in (('same_canvas006_from008','runtime frame/report binding:6'),('changed_approved_ground','exact approved static ground retained')):
        folder=a.output/name;runtime=folder/'runtime';images=runtime/'BMP/BACKGRND.BMP';images.mkdir(parents=True)
        for frame in FRAMES:shutil.copyfile(a.runtime_root/f'BMP/BACKGRND.BMP/{frame:03}.png',images/f'{frame:03}.png')
        report=json.loads((a.runtime_root/'export-report.json').read_bytes())
        if name=='same_canvas006_from008':shutil.copyfile(images/'008.png',images/'006.png')
        else:
            with Image.open(images/'000.png') as source:im=source.convert('RGBA')
            point=next((x,y) for y in range(im.height) for x in range(im.width) if im.getpixel((x,y))[3]==255)
            rgba=im.getpixel(point);im.putpixel(point,((rgba[0]+1)%256,*rgba[1:]));im.save(images/'000.png')
            report['frames'][0]['sha256']=sha((images/'000.png').read_bytes())
        save(runtime/'export-report.json',report)
        command=[sys.executable,'-B',str(HERE/'prepare.py'),'--baseline',str(a.baseline.resolve()),'--runtime-root',str(runtime.resolve()),'--output',str((folder/'package').resolve())]
        run=subprocess.run(command,capture_output=True,text=True,timeout=30)
        (folder/'stdout.txt').write_text(run.stdout,encoding='utf-8');(folder/'stderr.txt').write_text(run.stderr,encoding='utf-8')
        require(run.returncode!=0 and 'ValueError: integrated shore: '+expected in run.stderr,'fresh-process named preparation refusal:'+name)
        controls.append({'name':name,'status':'FIRED','exit_code':run.returncode,'witness':expected,'command':command,
          'prepare_sha256':sha((HERE/'prepare.py').read_bytes()),'capture_sha256':sha((HERE/'capture.py').read_bytes())})
    package_pair(a.baseline,a.candidate)
    require(original=={p.name:sha(p.read_bytes()) for p in (a.runtime_root/'BMP/BACKGRND.BMP').glob('*.png')},'original runtime inputs unchanged')
    save(a.output/'result.json',{'status':'PASS','positive_package_before_after':'PASS','controls':controls,
      'method':'New disposable runtime copies, fresh Python interpreter per control. Same-canvas wrong frame and valid changed ground with self-consistent report hash. Approved inputs untouched.',
      'harness_sha256':sha(Path(__file__).read_bytes()),'selected_report_sha256':sha((a.runtime_root/'export-report.json').read_bytes()),'candidate_sha256':sha(a.candidate.read_bytes())})
    print('PASS preparation positive, two executed binding controls, restored positive')
if __name__=='__main__':main()
