"""Replay the three frozen low-tide exporters in an isolated baseline snapshot."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LOW = 'art/cartoon/low-tide-v1'
COMMIT = '9e2f061d07095e69faf6119a97d26c9be2620b8d'
sha = lambda data: hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.exists(), 'use fresh scratch'
    a.output.mkdir(parents=True)
    source = a.output.resolve() / 'source'
    wave = json.loads((ROOT / LOW / 'wave-reuse-v1/recipe-v1.json').read_bytes())
    files = set(wave['source_bindings'])
    files.update(['tools/art_common.py', 'tools/art_pack.py', LOW+'/export_draft.py',
                  LOW+'/shore-raw-v3.png', LOW+'/rock-raw-v2.png',
                  LOW+'/wave-reuse-v1/export.py', LOW+'/wave-reuse-v1/recipe-v1.json',
                  LOW+'/rock-waves-v1/export.py'])
    for f in range(39,42):
        record = LOW + f'/rock-waves-v1/generation-{f:03}-v1.json'
        files.update([record, LOW+f'/rock-waves-v1/{f:03}-raw-v1.png'])
        files.update(json.loads((ROOT/record).read_bytes())['referenced_image_paths'])
    snapshot = subprocess.check_output(['git','-C',str(ROOT),'archive','--format=zip',COMMIT,*sorted(files)])
    identities = {}
    with zipfile.ZipFile(io.BytesIO(snapshot)) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            target = (source/info.filename).resolve()
            assert target.is_relative_to(source), info.filename
            data = z.read(info.filename)
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(data)
            identities[info.filename] = sha(data)
            assert data == (ROOT/info.filename).read_bytes(), info.filename
    assert set(identities) == files, 'source snapshot inventory'
    baseline = subprocess.check_output(['git','-C',str(ROOT),'show',COMMIT+':assets/scrantic_data.zip'])
    assert sha(baseline) == wave['archive_sha256'], 'baseline archive'
    (source/'assets').mkdir()
    (source/'assets/scrantic_data.zip').write_bytes(baseline)
    jobs = [
        ('static-smoke', LOW+'/export_draft.py', ['--output',str(a.output.resolve()/'static'), '--candidate',str(a.output.resolve()/'static.zip')], 'static', [1,2]),
        ('island-regression', LOW+'/wave-reuse-v1/export.py', ['--recipe',str(source/LOW/'wave-reuse-v1/recipe-v1.json'),'--output',str(a.output.resolve()/'island')], 'island', list(range(30,39))),
        ('rock-regression', LOW+'/rock-waves-v1/export.py', ['--output',str(a.output.resolve()/'rock')], 'rock', list(range(39,42))),
    ]
    selected = {r['frame']:r for r in json.loads((HERE/'runtime-recipe.json').read_bytes())['frames']}
    records = []
    for label, helper, arguments, folder, frames in jobs:
        cmd = [sys.executable,'-B',str(source/helper),*arguments]
        result = subprocess.run(cmd,cwd=source,capture_output=True,text=True,timeout=300)
        (a.output/(label+'.stdout.txt')).write_text(result.stdout,encoding='utf-8')
        (a.output/(label+'.stderr.txt')).write_text(result.stderr,encoding='utf-8')
        assert result.returncode == 0, label+': '+result.stderr
        outputs = {}
        for frame in frames:
            row = selected[frame]
            raw = (a.output/folder/row['path']).read_bytes()
            assert sha(raw) == row['candidate_png_sha256'], row['path']
            outputs[row['path']] = sha(raw)
        records.append({'label':label,'exit_code':result.returncode,'exporter':helper,
                        'exporter_sha256':identities[helper],'exact_outputs':outputs})
        print('PASS '+label+': '+str(len(outputs))+' exact approved PNGs',flush=True)
    report = {'status':'PASS','source_commit':COMMIT,'baseline_sha256':sha(baseline),
              'snapshot_files_sha256':identities,'commands_in_order':records,'reproduced_pngs':14,
              'helper_sha256':sha(Path(__file__).read_bytes()),
              'scope':'Frozen source exporter replay. All14 selected PNG bytes match production recipe. Live production is never modified.'}
    (a.output/'replay.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())


if __name__ == '__main__':
    main()
