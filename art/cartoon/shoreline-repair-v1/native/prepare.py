"""Create private diagnostic ZIPs only; original-scale props stay identical."""
import argparse
import json
from pathlib import Path
import zipfile

from capture import ROOT, native, package_pair, require, save, sha

PROPS = ROOT / 'art/cartoon/seasonal-v1/candidates/v5'
RECIPE = ROOT / 'art/cartoon/seasonal-v1/recipe-v5.json'
RECIPE_SHA = '5e60af35fd517663b4c0f3c4c26da97d61f81ccad807fadc5bb858c6ed3c848f'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wave003', type=Path)
    parser.add_argument('--wave007', type=Path)
    parser.add_argument('--wave009', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    waves = {frame: getattr(args, f'wave{frame:03}') for frame in (3, 7, 9)}
    require(all(waves.values()) or not any(waves.values()), 'all three wave inputs or none')
    output = args.output.resolve()
    output.relative_to(ROOT / 'build/shoreline-repair-v1')
    require(not output.exists(), 'fresh preparation directory required')
    production = ROOT / 'assets/scrantic_data.zip'
    require(sha(production.read_bytes()) == native.PRODUCTION_SHA, 'pinned production baseline')
    require(sha(RECIPE.read_bytes()) == RECIPE_SHA, 'fixed restored-props recipe')
    report_path = PROPS / 'export-report.json'
    report = json.loads(report_path.read_text())
    require(report['recipe_sha256'] == RECIPE_SHA, 'restored props export recipe binding')
    require([row['frame'] for row in report['frames']] == [0, 1, 2, 3], 'four ordered props frames')
    additions = {}
    inputs = {RECIPE.relative_to(ROOT).as_posix(): RECIPE_SHA,
              report_path.relative_to(ROOT).as_posix(): sha(report_path.read_bytes())}
    for row in report['frames']:
        expected = f"BMP/HOLIDAY.BMP/{row['frame']:03}.png"
        require(row['path'] == expected, 'restored props frame/path binding')
        path = PROPS / expected
        raw = path.read_bytes()
        require(sha(raw) == row['candidate_png_sha256'] == report['outputs_sha256'][expected], 'restored props PNG identity:' + expected)
        additions['data/styles/cartoon/' + expected] = raw
        inputs[path.relative_to(ROOT).as_posix()] = sha(raw)
    replacements = {}
    for frame, path in waves.items():
        if path:
            path = path.resolve()
            raw = path.read_bytes()
            replacements[f'data/styles/cartoon/BMP/BACKGRND.BMP/{frame:03}.png'] = raw
            inputs[path.relative_to(ROOT).as_posix()] = sha(raw)
    output.mkdir(parents=True)
    baseline = output / 'baseline.zip'
    with zipfile.ZipFile(production) as source, zipfile.ZipFile(baseline, 'w') as target:
        require(len(source.namelist()) == len(set(source.namelist())), 'production duplicate members')
        for info in source.infolist():
            target.writestr(info, source.read(info.filename))
        for name, raw in additions.items():
            target.writestr(name, raw, compress_type=zipfile.ZIP_DEFLATED)
    metadata = native.selected_archive(baseline)
    result = {'accepted': False, 'baseline': metadata, 'source_inputs_sha256': inputs,
              'production_archive_sha256': native.PRODUCTION_SHA, 'prepare_sha256': sha(Path(__file__).read_bytes()),
              'scope': 'Private still-preview inputs. Does not approve art, assert wave fit, or modify production.'}
    if replacements:
        candidate = output / 'candidate.zip'
        with zipfile.ZipFile(baseline) as source, zipfile.ZipFile(candidate, 'w') as target:
            for info in source.infolist():
                target.writestr(info, replacements.get(info.filename, source.read(info.filename)))
        _, _, result['comparison'] = package_pair(baseline, candidate)
    require(sha(production.read_bytes()) == native.PRODUCTION_SHA, 'production unchanged')
    save(output / 'preparation.json', result)
    print('PASS private diagnostic package: ' + str(output))


if __name__ == '__main__':
    main()
