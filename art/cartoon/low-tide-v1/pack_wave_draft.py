"""Build a private low-tide motion candidate from approved static and draft waves."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from art_common import inspect_png
from art_pack import build_archive

sha = lambda raw:hashlib.sha256(raw).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--island-waves',type=Path,required=True)
    p.add_argument('--rock-waves',type=Path,required=True)
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--report',type=Path,required=True)
    a=p.parse_args()
    source=ROOT/'assets/scrantic_data.zip'
    replacements={}
    rows=[]
    for frame in [1,2,*range(30,42)]:
        folder=HERE/'static-v2' if frame<3 else a.island_waves if frame<39 else a.rock_waves
        member=f'BMP/BACKGRND.BMP/{frame:03}.png'
        path=folder/member
        size=(768,138) if frame==1 else (128,60) if frame==2 else (256,96) if frame==31 else (240,96) if frame<33 else (352,56) if frame<36 else (176,96) if frame<39 else (208,58)
        raw=path.read_bytes()
        inspect_png(raw,member,size)
        replacements[member]=raw
        rows.append({'path':member,'sha256':sha(raw),'size':size,
                     'source':path.resolve().relative_to(ROOT).as_posix(),
                     'approval':'static shape only' if frame<3 else 'motion review pending'})
    with zipfile.ZipFile(source) as z:
        before={n:sha(z.read(n)) for n in z.namelist()}
        existing={n.removeprefix('data/styles/cartoon/'):z.read(n) for n in z.namelist()
                  if n.startswith('data/styles/cartoon/') and n.endswith('.png')}
        manifest=json.loads(z.read('data/styles/cartoon/manifest.json'))
    existing.update(replacements)
    build_archive(source,a.candidate,manifest,existing)
    with zipfile.ZipFile(a.candidate) as z:
        after={n:sha(z.read(n)) for n in z.namelist()}
    result={'production_sha256':sha(source.read_bytes()),'candidate_sha256':sha(a.candidate.read_bytes()),
            'accepted':False,'scope':'Private motion review of14 low-tide additions. Existing production payloads preserved.',
            'frames':rows,'source_member_count':len(before),'candidate_member_count':len(after),
            'changed_existing_members':[n for n in before if before[n]!=after.get(n)],
            'added_members':sorted(set(after)-set(before)),
            'packer_sha256':sha(Path(__file__).read_bytes())}
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(json.dumps({k:result[k] for k in ['candidate_sha256','source_member_count','candidate_member_count','changed_existing_members']}))


if __name__=='__main__':
    main()
