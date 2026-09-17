"""Fresh seven-member private package plus exact007 source-difference witness."""
import argparse
import json
from pathlib import Path
import zipfile
import combined as c


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    output = a.output.resolve()
    output.relative_to(c.ROOT/'build/shoreline-repair-v1')
    c.require(not output.exists(), 'fresh combined package output')
    c.require(c.sha(a.baseline.read_bytes()) == c.old.BASE_SHA, 'selected offshore baseline identity')
    rows, bindings = c.selection()
    replacements = {c.member(r['frame']): (c.ROOT/r['source_path']).read_bytes() for r in rows if r['frame'] in c.CHANGED}
    output.mkdir(parents=True)
    candidate = output/'candidate.zip'
    with zipfile.ZipFile(a.baseline) as z, zipfile.ZipFile(candidate, 'w') as out:
        for info in z.infolist():
            out.writestr(info, replacements.get(info.filename,z.read(info.filename)))
    pair = c.package_pair(a.baseline, candidate)
    support = c.center_support(a.baseline, candidate)
    c.save(output/'center007-support.json', support)
    c.save(output/'export-report.json', {'schema_version': 1, 'accepted': False, 'frames': rows, 'source_bindings_sha256': bindings})
    record = {'schema_version': 2, 'accepted': False, 'package_pair': pair,
              'center_support': {'path': (output/'center007-support.json').relative_to(c.ROOT).as_posix(), 'sha256': c.sha((output/'center007-support.json').read_bytes())},
              'selection': {'path': (output/'export-report.json').relative_to(c.ROOT).as_posix(), 'sha256': c.sha((output/'export-report.json').read_bytes())},
              'helpers_sha256': {q.relative_to(c.ROOT).as_posix(): c.sha(q.read_bytes()) for q in (Path(__file__), c.HERE/'combined.py')},
              'scope': 'Tentative six side placements plus cleaned007. Ground,006,008,all four holidays and2591 other payloads retained; human review pending.'}
    c.save(output/'preparation.json',record)
    print(json.dumps({'status':'PASS','candidate_sha256':pair['candidate_sha256'],'support_pixels':support['pixels']}))


if __name__ == '__main__':
    main()
