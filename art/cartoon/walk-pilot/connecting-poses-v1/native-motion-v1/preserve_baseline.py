"""Freeze baseline reports and executed guards without bulk images or binaries."""
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
    negative = config.load_json(source / 'negative-controls/baseline/report.json')
    assert summary['status'] == negative['status'] == 'PASS', 'completed native baseline and guard checks'
    assert core.protected() == build['protected_sha256'], 'baseline protected inputs still exact'
    names = ['preparation.json', 'route_driver.c', 'trace_driver.c']
    names += ['baseline-v1/' + name for name in ('build.json', 'build.stdout.txt', 'build.stderr.txt', 'trace-build.stdout.txt', 'trace-build.stderr.txt', 'independent-trace.json', 'route-contract.json', 'summary.json')]
    names += [f'baseline-v1/{clip}/{phase}/{name}' for clip in config.CLIPS for phase in ('smoke', 'full', 'repeat') for name in ('capture.log', 'report.json')]
    names += ['negative-controls/baseline/' + name for name in ('report.json', 'execution.log', 'execution.json', 'wrong-waypoint-prediction/trace-build.stdout.txt', 'wrong-waypoint-prediction/trace-build.stderr.txt', 'wrong-selected-waypoint-path/capture.log', 'wrong-terminal-role/capture.log')]
    preserved = {}
    for name in names:
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, path)
        assert path.read_bytes() == (source / name).read_bytes(), 'exact retained baseline bytes:' + name
        preserved[name] = config.sha(path.read_bytes())
    helper_hashes = dict(build['helper_sha256'])
    for name, expected in negative['executed_helper_sha256'].items():
        assert name not in helper_hashes or helper_hashes[name] == expected, 'same capture helpers through negative controls:' + name
        helper_hashes[name] = expected
    for name, expected in helper_hashes.items():
        original = config.HERE / name
        assert config.sha(original.read_bytes()) == expected, 'executed helper still exact:' + name
        path = destination / 'helpers' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, path)
        preserved['helpers/' + name] = config.sha(path.read_bytes())
    for original, name in ((config.ROOT / 'build/connecting-analysis/run_baseline_negatives.py', 'host-run_baseline_negatives.py'), (config.HERE / 'BASELINE.md', 'BASELINE.md'), (Path(__file__), 'preserve_baseline.py')):
        path = destination / 'helpers' / name
        shutil.copyfile(original, path)
        preserved['helpers/' + name] = config.sha(path.read_bytes())
    record = {'schema_version': 1, 'status': 'PASS baseline; candidate motion review is a separate checkpoint',
              'source_commit': build['source_commit'], 'production_archive_sha256': config.PRODUCTION_SHA,
              'evidence_root': destination.relative_to(config.ROOT).as_posix(), 'files_sha256': preserved,
              'clips': {name: {'displays': row['display_count'], 'duration_ms': row['duration_ms']} for name, row in summary['clips'].items()},
              'completed': ['Independent compiled C trace of all twelve prime/travel contracts', 'Fresh unchanged-source native observer', 'All six smoke clips before six full and exact fresh-process repeats', 'Nine executed baseline input negatives with restored positive control', 'Protected production source/archive identity'],
              'not_validated_by_this_checkpoint': ['Candidate capture/comparison', 'Browser review', 'Publication', 'Human motion approval'],
              'helper_snapshot_scope': 'Files hash-bound at native build and baseline negative execution. Only the named execution reports establish coverage; copied unrelated helper files do not imply execution.',
              'omitted': 'All PPM/PNG captures, private ZIP copies, native executables and profile settings remain local scratch; display image hashes are retained in reports.',
              'preserver_sha256': config.sha(Path(__file__).read_bytes())}
    binder.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    assert all(config.sha((destination / name).read_bytes()) == digest for name, digest in preserved.items()), 'final retained-file readback'
    print(f'PASS retained {len(preserved)} exact baseline files; binder SHA256={config.sha(binder.read_bytes())}')


if __name__ == '__main__':
    main()
