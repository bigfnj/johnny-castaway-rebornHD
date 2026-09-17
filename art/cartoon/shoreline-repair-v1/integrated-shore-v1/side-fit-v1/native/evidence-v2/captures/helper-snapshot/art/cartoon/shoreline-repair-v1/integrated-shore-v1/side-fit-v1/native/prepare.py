"""Private six-side draft; exact selected ground, centers and all holidays retained."""
import argparse
import json
from pathlib import Path
import struct
import zipfile

from capture import ROOT, HERE, FRAMES, SIDES, BASE_SHA, REPORT_SHA, RECIPE_SHA, member, package_pair, require, save, selected_rows, sha


def prepare(baseline, runtime, output):
    output = output.resolve()
    output.relative_to(ROOT / 'build/shoreline-repair-v1')
    require(not output.exists(), 'fresh private preparation output')
    require(sha(baseline.read_bytes()) == BASE_SHA, 'selected offshore baseline identity')
    require(sha((runtime / 'export-report.json').read_bytes()) == REPORT_SHA, 'runtime export report identity')
    bindings, replacements = {}, {}
    for row in selected_rows():
        path = runtime / row['path']
        raw = path.read_bytes()
        require(sha(raw) == row['sha256'], f"{row['frame']:03} runtime/report identity")
        require(raw[:8] == b'\x89PNG\r\n\x1a\n' and list(struct.unpack('>II', raw[16:24])) == row['canvas'], f"{row['frame']:03} runtime/report canvas")
        bindings[path.resolve().relative_to(ROOT).as_posix()] = sha(raw)
        if row['frame'] in SIDES:
            replacements[member(row['frame'])] = raw
    for phase in ('smoke', 'regression'):
        source = HERE.parent / f'verification-{phase}.json'
        report = json.loads(source.read_bytes())
        require(report['status'] == 'PASS' and report['recipe_sha256'] == RECIPE_SHA and report['export_report_sha256'] == REPORT_SHA,
                phase+' selected export verification')
        bindings[source.relative_to(ROOT).as_posix()] = sha(source.read_bytes())
    output.mkdir(parents=True)
    target = output / 'candidate.zip'
    with zipfile.ZipFile(baseline) as original, zipfile.ZipFile(target, 'w') as candidate:
        for info in original.infolist():
            candidate.writestr(info, replacements.get(info.filename, original.read(info.filename)))
    pair = package_pair(baseline, target)
    record = {'schema_version': 1, 'accepted': False,
              'baseline': baseline.resolve().relative_to(ROOT).as_posix(),
              'candidate': target.relative_to(ROOT).as_posix(), 'package_pair': pair,
              'runtime_inputs_sha256': bindings,
              'selected_export_report': {'path': (runtime / 'export-report.json').resolve().relative_to(ROOT).as_posix(), 'sha256': REPORT_SHA},
              'prepare_sha256': sha(Path(__file__).read_bytes()),
              'capture_sha256': sha((HERE / 'capture.py').read_bytes()),
              'scope': 'Tentative six-side-only comparison; no center shading edit, production promotion or human approval.'}
    save(output / 'preparation.json', record)
    return record


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--runtime-root', type=Path, default=HERE.parent / 'candidates/v1')
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    result = prepare(a.baseline.resolve(), a.runtime_root.resolve(), a.output)
    print('PASS side native prepare ' + result['package_pair']['candidate_sha256'])
