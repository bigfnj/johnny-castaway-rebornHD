"""One-time preservation of the first coherent-master native still comparison."""
import json
from pathlib import Path
import shutil

from capture import CANVASES, HERE, ROOT, member, require, save, sha


def main():
    destination = HERE / 'evidence-v1'
    require(not destination.exists(), 'historical coherent-master evidence exists')
    run = ROOT / 'build/shoreline-repair-v1/native-master-v1'
    prepared = ROOT / 'build/shoreline-repair-v1/selected-master-v1/preparation.json'
    summary = json.loads((run / 'captures/summary.json').read_text())
    preparation = json.loads(prepared.read_text())
    launch = json.loads((run / 'launch.json').read_text())
    require(summary['status'] == 'PASS' and launch['exit_code'] == 0 and launch['no_surviving_task_container'], 'completed native run and cleanup')
    require(preparation['comparison'] == summary['packages'], 'capture/preparation package binding')
    export_root = ROOT / 'art/cartoon/shoreline-repair-v1/shared-master/candidates/v1'
    export_report = json.loads((export_root / 'export-report.json').read_text())
    require([row['frame'] for row in export_report['frames']] == list(CANVASES), 'ordered ten authoring frames')
    for row in export_report['frames']:
        source = export_root / row['path']
        digest = sha(source.read_bytes())
        require(digest == row['sha256'] == preparation['runtime_inputs_sha256'][source.relative_to(ROOT).as_posix()] ==
                summary['packages']['changed_members'][member(row['frame'])]['after'], 'authoring/runtime/native identity:' + row['path'])
    files = [(prepared, 'preparation.json')]
    files += [(path, 'native/' + path.relative_to(run).as_posix()) for path in sorted(run.rglob('*'))
              if path.is_file() and path.suffix in ('.json', '.txt', '.log')]
    for path in sorted((ROOT / 'build/shoreline-repair-v1/native-v2-toolchecks').glob('*.json')):
        require(json.loads(path.read_text())['status'] == 'PASS', 'completed helper checks')
        files.append((path, 'toolchecks/' + path.name))
    pins = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in HERE.iterdir() if p.is_file()}
    prior = HERE.parent / 'native/evidence-v1/evidence.json'
    older = json.loads(prior.read_text())
    for name, row in older['files'].items():
        require(sha((prior.parent / name).read_bytes()) == row['sha256'], 'prior evidence immutable:' + name)
    for name, digest in older['source_sha256'].items():
        require(sha((ROOT / name).read_bytes()) == digest, 'prior source immutable:' + name)
    pins[prior.relative_to(ROOT).as_posix()] = sha(prior.read_bytes())
    extra = [HERE.parent / 'native/capture.py', HERE.parent / 'native/driver.c',
             ROOT / 'art/cartoon/seasonal-v1/native/capture.py']
    extra += [HERE.parent / ('shared-master/' + name) for name in ('export.py', 'recipe-v1.json', 'verification-smoke.json', 'verification-regression.json', 'candidates/v1/export-report.json')]
    for path in extra:
        pins[path.relative_to(ROOT).as_posix()] = sha(path.read_bytes())
    inputs = json.loads((run / 'captures/inputs.json').read_text())
    for mapping in (inputs['protected_sha256'], inputs['dependencies_sha256'], preparation['runtime_inputs_sha256']):
        for name, digest in mapping.items():
            require(sha((ROOT / name).read_bytes()) == digest, 'source binding:' + name)
            pins[name] = digest
    omitted = {path.relative_to(ROOT).as_posix(): sha(path.read_bytes()) for path in sorted(run.rglob('*'))
               if path.is_file() and (path.suffix in ('.png', '.ppm', '.zip') or path.name == 'seasonal_probe')}
    candidate = prepared.parent / 'candidate.zip'
    omitted[candidate.relative_to(ROOT).as_posix()] = sha(candidate.read_bytes())
    destination.mkdir()
    manifest = {}
    for source, name in files:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        require(target.read_bytes() == source.read_bytes(), 'exact evidence copy:' + name)
        manifest[name] = {'sha256': sha(target.read_bytes()), 'source': source.relative_to(ROOT).as_posix()}
    save(destination / 'evidence.json', {'schema_version': 1, 'status': 'PASS', 'accepted': False,
        'scope': 'Four native stills with ten package replacements, only000/003/007/009 drawn. No all-phase motion or visual approval claim.',
        'files': manifest, 'source_sha256': pins, 'excluded_large_artifacts_sha256': omitted,
        'results': {'helper_smoke': 2, 'helper_regression': 8, 'helper_named_refusals': 6,
                    'native_smoke': 8, 'native_fresh_repeat': 8, 'native_named_refusals': 3,
                    'prior_frozen_files_read_back': len(older['files']), 'prior_frozen_source_bindings_read_back': len(older['source_sha256'])},
        'authoring_limits': {name: export_report[name] for name in ('filtered_alpha_outside_master_crop', 'master_alpha_outside_original_canvas_union', 'baked_foam_observation')},
        'replay': 'Use README commands with fresh scratch. Skip this historical one-time writer.'})
    binder = json.loads((destination / 'evidence.json').read_text())
    require(all(sha((destination / name).read_bytes()) == row['sha256'] for name, row in binder['files'].items()), 'copied evidence readback')
    require(all(sha((ROOT / name).read_bytes()) == digest for name, digest in binder['source_sha256'].items()), 'source index readback')
    print(f"PASS preserved {len(manifest)} exact records and {len(pins)} source bindings; evidence {sha((destination / 'evidence.json').read_bytes())}")


if __name__ == '__main__':
    main()
