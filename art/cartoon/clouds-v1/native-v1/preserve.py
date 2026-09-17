"""One-time exact-copy freeze of the bounded native cloud review."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'CMakeLists.txt').is_file())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_bytes((json.dumps(value, indent=2) + '\n').encode())


def require(ok, label):
    if not ok:
        raise ValueError('cloud preservation: ' + label)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--review', type=Path, required=True)
    parser.add_argument('--browser-checks', type=Path)
    args = parser.parse_args()
    run, review = args.run.resolve(), args.review.resolve()
    captures = run / 'captures'
    summary = json.loads((captures / 'summary.json').read_bytes())
    inputs = json.loads((captures / 'inputs.json').read_bytes())
    launch = json.loads((run / 'launch.json').read_bytes())
    page = json.loads((review / 'build.json').read_bytes())
    manifest = json.loads((review / 'manifest.json').read_bytes())
    require(summary['status'] == page['status'] == 'PASS', 'native/review completed')
    require(launch['exit_code'] == 0 and launch['no_surviving_task_container'], 'launch.json clean completion')
    require(digest(captures / 'inputs.json') == summary['inputs_sha256'], 'native inputs.json identity')
    require(digest(captures / 'build.json') == summary['build_sha256'], 'native build.json identity')
    require(digest(captures / 'summary.json') == manifest['native_summary']['sha256'], 'native summary.json identity')
    require(digest(review / 'review.html') == page['html_sha256'], 'review.html identity')
    require(digest(review / 'manifest.json') == page['manifest_sha256'], 'manifest.json identity')
    for n, h in manifest['atlases'].items():
        require(digest(review / n) == h, n + ' atlas identity')
    for p, h in manifest['reports_sha256'].items():
        require(digest(ROOT / p) == h, p + ' report identity')
    source_pins = {**inputs['protected_sha256'], **inputs['helpers_sha256']}
    source_pins.update({p.relative_to(ROOT).as_posix(): digest(p) for p in HERE.iterdir() if p.is_file()})
    for p, h in source_pins.items():
        require(digest(ROOT / p) == h, p + ' source identity')
    output = HERE / 'evidence-v1'
    require(not output.exists(), 'existing evidence is immutable')
    planned = {}
    for name in ('launch.json', 'launch.log'):
        planned['run/' + name] = run / name
    for name in ('inputs.json', 'build.json', 'build.stdout.txt', 'build.stderr.txt', 'summary.json', 'smoke.json', 'negative-controls.json'):
        planned['native/' + name] = captures / name
    concern_lines = []
    for case in summary['cases']:
        require(summary['cases'][case]['smoke'] == summary['cases'][case]['fresh_repeat'] == 'PASS', case + ' smoke/repeat')
        for side in ('baseline', 'candidate'):
            for phase in ('smoke', 'repeat'):
                folder = captures / case / side / phase
                report = json.loads((folder / 'report.json').read_bytes())
                require(digest(folder / 'capture.log') == report['log_sha256'], str(folder / 'capture.log') + ' identity')
                for name in ('report.json', 'capture.log'):
                    planned['native/' + folder.relative_to(captures).as_posix() + '/' + name] = folder / name
                concern_lines += [{'path': (folder / 'capture.log').relative_to(ROOT).as_posix(), 'line': line}
                                  for line in (folder / 'capture.log').read_text().splitlines()
                                  if re.search(r'warning|error|failed|ALSA|segmentation', line, re.I)]
    for p in review.iterdir():
        if p.is_file() and (p.suffix in ('.json', '.html') or p.name in manifest['atlases']):
            planned['review/' + p.name] = p
    if args.browser_checks:
        planned['review/' + args.browser_checks.name] = args.browser_checks.resolve()
    preservation_control = ROOT / 'build/clouds-v1/preservation-control.json'
    if preservation_control.is_file():
        planned['preservation-control.json'] = preservation_control
        planned['check_preservation.py'] = ROOT / 'build/clouds-v1/check_preservation.py'
    output.mkdir()
    files = {}
    for name, source in sorted(planned.items()):
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        require(digest(source) == digest(target), name + ' copied identity')
        files[name] = {'sha256': digest(target), 'bytes': target.stat().st_size, 'source': source.relative_to(ROOT).as_posix()}
    evidence = {'schema_version': 1, 'status': 'PASS', 'source_commit': launch['source_commit'],
        'baseline_sha256': summary['baseline_sha256'], 'candidate_sha256': summary['candidate_sha256'],
        'native_summary_sha256': digest(captures / 'summary.json'), 'files': files, 'source_pins': source_pins,
        'compiler_stderr_bytes': (captures / 'build.stderr.txt').stat().st_size, 'runtime_concern_lines': concern_lines,
        'excluded': 'Bulk native PPM/PNG sequences, executables and private archives remain scratch. Reports bind their pixels/archive/executable hashes; review atlases retain all three displayed clips losslessly.',
        'limits': 'Explicit native cloud fixtures, submitted pre-clip blit bounds and requested logical timing. No original executable, natural story selection, full traversal/wrap or performance claim.'}
    save(output / 'evidence.json', evidence)
    for p, row in files.items():
        require(digest(output / p) == row['sha256'] and digest(ROOT / row['source']) == row['sha256'], p + ' readback identity')
    save(output / 'readback.json', {'status': 'PASS', 'evidence_sha256': digest(output / 'evidence.json'),
        'exact_copies': len(files), 'source_pins_checked': len(source_pins),
        'retained_bytes': sum(row['bytes'] for row in files.values())})
    print(json.dumps({'evidence': str(output / 'evidence.json'), 'sha256': digest(output / 'evidence.json'), 'files': len(files)}, indent=2))


if __name__ == '__main__':
    main()
