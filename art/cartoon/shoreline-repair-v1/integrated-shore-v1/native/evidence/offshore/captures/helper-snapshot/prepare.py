"""Make a private candidate, preserving every non-shoreline ZIP payload."""
import argparse
import json
from pathlib import Path
import zipfile
from capture import ROOT,FRAMES,member,package_pair,require,save,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--runtime-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    output=a.output.resolve();output.relative_to(ROOT/'build/shoreline-repair-v1')
    require(not output.exists(),'fresh private package directory')
    report_path=(a.runtime_root/'export-report.json').resolve()
    report=json.loads(report_path.read_bytes());rows=report['frames']
    require([row['frame'] for row in rows]==list(FRAMES),'ordered explicit runtime selection')
    replacements={};bindings={}
    for frame,row in zip(FRAMES,rows):
        source=(a.runtime_root/f'BMP/BACKGRND.BMP/{frame:03}.png').resolve()
        raw=source.read_bytes()
        require(row['path']==f'BMP/BACKGRND.BMP/{frame:03}.png' and row['sha256']==sha(raw),'runtime frame/report binding:'+str(frame))
        require(list(__import__('struct').unpack('>II',raw[16:24]))==row['canvas'],'runtime canvas/report binding:'+str(frame))
        replacements[member(frame)]=raw;bindings[source.relative_to(ROOT).as_posix()]=sha(raw)
    output.mkdir(parents=True);target=output/'candidate.zip'
    with zipfile.ZipFile(a.baseline) as old,zipfile.ZipFile(target,'w') as new:
        for info in old.infolist():new.writestr(info,replacements.get(info.filename,old.read(info.filename)))
    pair=package_pair(a.baseline,target)
    save(output/'preparation.json',{'accepted':False,'baseline':a.baseline.resolve().relative_to(ROOT).as_posix(),
      'candidate':target.relative_to(ROOT).as_posix(),'package_pair':pair,'runtime_inputs_sha256':bindings,
      'selected_export_report':{'path':report_path.relative_to(ROOT).as_posix(),'sha256':sha(report_path.read_bytes())},
      'prepare_sha256':sha(Path(__file__).read_bytes()),'capture_sha256':sha((Path(__file__).parent/'capture.py').read_bytes()),
      'scope':'Exact supplied runtime bytes packaged as diagnostic. Artwork approval is separate; no production writes.'})
    print('PASS private package: '+str(target))
if __name__=='__main__':main()
