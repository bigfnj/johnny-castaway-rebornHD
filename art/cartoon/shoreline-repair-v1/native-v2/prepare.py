"""Package a coherent-ground export beside the exact earlier V5-prop baseline."""
import argparse
from pathlib import Path
import zipfile

from capture import ROOT, CANVASES, PROP_HASHES, member, native, package_pair, require, save, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--runtime-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.relative_to(ROOT / 'build/shoreline-repair-v1')
    require(not output.exists(), 'fresh preparation directory required')
    baseline = args.baseline.resolve()
    baseline.relative_to(ROOT)
    # A replay may change ZIP timestamps; retained payloads and the four props
    # are authoritative. Record the actual envelope hash with this new run.
    baseline_metadata = native.selected_archive(baseline)
    require(set(baseline_metadata['new_cartoon_members']) == set(PROP_HASHES) and
            baseline_metadata['holiday_members_sha256'] == PROP_HASHES, 'exact V5 prop payloads')
    replacements, inputs = {}, {}
    for frame in CANVASES:
        path = (args.runtime_root / f'BMP/BACKGRND.BMP/{frame:03}.png').resolve()
        raw = path.read_bytes()
        replacements[member(frame)] = raw
        inputs[path.relative_to(ROOT).as_posix()] = sha(raw)
    output.mkdir(parents=True)
    candidate = output / 'candidate.zip'
    with zipfile.ZipFile(baseline) as source, zipfile.ZipFile(candidate, 'w') as target:
        for info in source.infolist():
            target.writestr(info, replacements.get(info.filename, source.read(info.filename)))
    _, _, comparison = package_pair(baseline, candidate)
    save(output / 'preparation.json', {'accepted': False, 'comparison': comparison,
         'baseline': baseline.relative_to(ROOT).as_posix(), 'runtime_inputs_sha256': inputs,
         'helper_sha256': sha(Path(__file__).read_bytes()),
         'scope': 'Diagnostic candidate only. Exact native canvases and retained payloads; no claim of visual approval or full wave-cycle behavior.'})
    print('PASS coherent-ground diagnostic package: ' + str(candidate))


if __name__ == '__main__':
    main()
