"""Freeze the completed baseline without bulk images, private ZIPs or binaries."""
import json
from pathlib import Path
import shutil
import config
import native_core as core


def main():
    source = config.OUT
    destination = config.HERE / 'evidence/baseline-v1'
    binder = config.HERE / 'baseline-checkpoint.json'
    assert not destination.exists() and not binder.exists(), 'preserve previous baseline checkpoint'
    summary = config.load_json(source / 'baseline-v1/summary.json')
    build = config.load_json(source / 'baseline-v1/build.json')
    assert summary['status'] == 'PASS', 'completed native baseline checks'
    assert core.protected() == build['protected_sha256'], 'baseline protected inputs still exact'
    assert not (source / 'candidate-v1').exists(), 'candidate remains unprepared pending arm review'
    names = ['preparation.json', 'route_driver.c', 'trace_driver.c']
    names += ['baseline-v1/' + name for name in ('build.json', 'build.stdout.txt', 'build.stderr.txt', 'trace-build.stdout.txt', 'trace-build.stderr.txt', 'independent-trace.json', 'route-contract.json', 'summary.json')]
    names += [f'baseline-v1/{clip}/{phase}/{name}' for clip in config.CLIPS for phase in ('smoke', 'full', 'repeat') for name in ('capture.log', 'report.json')]
    preserved = {}
    for name in names:
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, path)
        assert path.read_bytes() == (source / name).read_bytes(), 'exact retained baseline bytes:' + name
        preserved[name] = config.sha(path.read_bytes())
    for name, expected in build['helper_sha256'].items():
        original = config.HERE / name
        assert config.sha(original.read_bytes()) == expected, 'helper present at native build still exact:' + name
        path = destination / 'helpers' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, path)
        preserved['helpers/' + name] = config.sha(path.read_bytes())
    record = {'schema_version': 1, 'status': 'baseline complete; candidate on hold for human arm-design review',
              'source_commit': build['source_commit'], 'production_archive_sha256': config.PRODUCTION_SHA,
              'evidence_root': destination.relative_to(config.ROOT).as_posix(), 'files_sha256': preserved,
              'clips': {name: {'displays': row['display_count'], 'duration_ms': row['duration_ms']} for name, row in summary['clips'].items()},
              'completed': ['Independent compiled C trace of all four route contracts', 'Fresh unchanged-source native observer', 'Each route smoke then full then exact fresh-process repeat', 'Protected production source/archive identity'],
              'not_run': ['Candidate packaging', 'Candidate native capture/comparison', 'Browser smoke/regression', 'Native/browser negative controls', 'Publication', 'Human motion approval'],
              'helper_snapshot_scope': 'Files present and hash-bound at native build; execution evidence is in the named reports. Future candidate/review helpers are not validated by this baseline.',
              'omitted': 'All PPM/PNG captures, private ZIP copies, native executables and profile settings remain local scratch; display image hashes are retained in reports.',
              'preserver_sha256': config.sha(Path(__file__).read_bytes())}
    binder.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    assert all(config.sha((destination / name).read_bytes()) == digest for name, digest in preserved.items()), 'final retained-file readback'
    print(f'PASS retained {len(preserved)} exact baseline files; binder SHA256={config.sha(binder.read_bytes())}')


if __name__ == '__main__':
    main()
