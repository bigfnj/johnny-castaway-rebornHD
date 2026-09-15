"""Create a private two-member replacement ZIP from hash-bound technical exports."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import struct
import zipfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
EXPECTED = {28: '5b645ae3003c54dc65946118999f0f3906ca0f7fa47a10fa61c60ba10b46e3f4',
            29: '8a33597aaba9206ff8ff98bad24bd12a52142eac0bdd56c92cbf4b7de798017a'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, label):
    if not ok:
        raise ValueError('prepare_candidate.py: ' + label)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exports', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=OUT / 'candidate-v1')
    args = parser.parse_args()
    folder = args.output.resolve()
    require(not folder.exists(), 'preserve existing candidate')
    source = ROOT / 'assets/scrantic_data.zip'
    baseline = json.loads((OUT / 'baseline-v1/summary.json').read_bytes())
    require(sha(source.read_bytes()) == baseline['archive_sha256'], 'baseline archive identity')
    recipe = json.loads((args.exports / 'recipe.json').read_bytes())
    report = json.loads((args.exports / 'export-report.json').read_bytes())
    require(recipe['preview_only'] is False and report['preview_only'] is False
            and report['runtime_sprites_written'] is True and report['runtime_fit_all_source_centers'] is True,
            'runtime-ready technical export')
    replacements, records = {}, []
    with zipfile.ZipFile(source) as archive:
        source_members = {name: sha(archive.read(name)) for name in archive.namelist()}
        require(len(source_members) == len(archive.namelist()), 'unique source members')
        for frame in range(24, 30):
            relative = f'BMP/JOHNWALK.BMP/{frame:03}.png'
            name = 'data/styles/cartoon/' + relative
            raw = (args.exports / relative).read_bytes()
            exported = next(row for row in report['frames'] if row['frame'] == frame)
            require(sha(raw) == exported['runtime_png_sha256'], 'exported PNG binding:' + name)
            if frame not in EXPECTED:
                require(raw == archive.read(name) and exported['retained_runtime_bytes_identical'] is True,
                        'retained runtime bytes:' + name)
                continue
            require(sha(raw) == EXPECTED[frame], 'selected candidate identity:' + name)
            require(raw[:8] == b'\x89PNG\r\n\x1a\n', 'PNG signature:' + name)
            size = list(struct.unpack('>II', raw[16:24]))
            require(size == exported['runtime_canvas'], 'runtime canvas:' + name)
            replacements[name] = raw
            records.append({'frame': frame, 'member': name, 'old_sha256': source_members[name],
                            'new_sha256': sha(raw), 'canvas': size})
        folder.mkdir()
        target = folder / 'scrantic_data.zip'
        with zipfile.ZipFile(target, 'x') as candidate:
            candidate.comment = archive.comment
            for info in archive.infolist():
                candidate.writestr(copy.copy(info), replacements.get(info.filename, archive.read(info.filename)))
    with zipfile.ZipFile(target) as candidate:
        require(candidate.namelist() == list(source_members), 'all member names/order preserved')
        changed = []
        for name, before in source_members.items():
            actual = sha(candidate.read(name))
            require(actual == (sha(replacements[name]) if name in replacements else before),
                    'member bytes:' + name)
            if actual != before:
                changed.append(name)
        require(set(changed) == set(replacements), 'exactly selected028/029 changed')
    for name in ('recipe.json', 'export-report.json'):
        shutil.copyfile(args.exports / name, folder / name)
    evidence = {'scope': 'Private native-review candidate; no human approval or production promotion.',
                'archive_sha256': sha(target.read_bytes()), 'base_archive_sha256': baseline['archive_sha256'],
                'baseline_executable_sha256': baseline['executable_sha256'],
                'replaced_members': records, 'unchanged_members': len(source_members) - len(replacements),
                'total_members': len(source_members), 'recipe_sha256': sha((folder / 'recipe.json').read_bytes()),
                'export_report_sha256': sha((folder / 'export-report.json').read_bytes()),
                'prepare_helper_sha256': sha(Path(__file__).read_bytes())}
    (folder / 'preparation.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    require(sha(source.read_bytes()) == baseline['archive_sha256'], 'production ZIP unchanged')
    print(json.dumps(evidence))


if __name__ == '__main__':
    main()
