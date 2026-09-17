"""Stage only the exported New Year banner over the selected offshore package.

Preparation scaffold: execute and validate after the new runtime handoff exists.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'CMakeLists.txt').is_file())
BASE_SHA='ab5c8094b461307b87d68d2bb148eae5b9ce56d93cb6b93805c27c7fbd8e24ac'
MEMBER='data/styles/cartoon/BMP/HOLIDAY.BMP/003.png'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def prepare(baseline,runtime,expected,output):
    assert not output.exists(), 'banner preparation: existing output'
    assert sha(baseline.read_bytes())==BASE_SHA, 'banner preparation: selected offshore baseline identity'
    png=runtime.read_bytes()
    assert sha(png)==expected, 'banner preparation: runtime 003.png identity'
    assert png[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',png[16:24])==(304,94), 'banner preparation: 003.png original runtime canvas304x94'
    assert png[25] in (4,6), 'banner preparation: 003.png explicit alpha'
    with zipfile.ZipFile(baseline) as old:
        names=old.namelist()
        assert len(names)==len(set(names)) and MEMBER in names, 'banner preparation: baseline member set'
        before={n:sha(old.read(n)) for n in names}
        assert before[MEMBER]!=expected, 'banner preparation: replacement is unchanged'
        output.mkdir(parents=True)
        candidate=output/'candidate.zip'
        with zipfile.ZipFile(candidate,'w') as new:
            for info in old.infolist():
                new.writestr(info,png if info.filename==MEMBER else old.read(info.filename))
    with zipfile.ZipFile(candidate) as new:
        after={n:sha(new.read(n)) for n in new.namelist()}
    assert before.keys()==after.keys() and [n for n in before if before[n]!=after[n]]==[MEMBER], 'banner preparation: only003 may change'
    record={'status':'PREPARED','baseline_sha256':BASE_SHA,'candidate_sha256':sha(candidate.read_bytes()),
            'changed_member':MEMBER,'before_png_sha256':before[MEMBER],'after_png_sha256':expected,
            'canvas':[304,94],'member_count':len(before),'unchanged_members':len(before)-1,
            'runtime_path':runtime.relative_to(ROOT).as_posix(),'prepare_sha256':sha(Path(__file__).read_bytes()),
            'scope':'Private banner-only candidate; all shoreline, wave and other decoration payloads unchanged. Native and human attachment checks remain pending.'}
    (output/'preparation.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--runtime',type=Path,required=True)
    p.add_argument('--runtime-sha256',required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();prepare(a.baseline.resolve(),a.runtime.resolve(),a.runtime_sha256,a.output.resolve())
