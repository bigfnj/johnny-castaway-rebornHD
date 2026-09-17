"""Preserve the static draft, prompt lineage and technical review inputs."""
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BUILD = ROOT / 'build/low-tide-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_bytes((json.dumps(value, indent=2) + '\n').encode())


def copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    assert source.read_bytes() == target.read_bytes(), target


def main():
    for name in ['originals.md', 'runtime.md']:
        copy(Path('D:/.ai-work/projects/johnny-castaway-rebornHD/build/low-tide-preflight') / name,
             HERE / 'preflight' / name)
    copy(BUILD / 'static-review.md', HERE / 'preflight/static-review.md')
    copy(BUILD / 'static-export-v1/static-closeup.png', HERE / 'reference/shore-v2-join-defect.png')
    copy(BUILD / 'static-export-v1/export.json', HERE / 'preflight/export-v1.json')
    exported = BUILD / 'static-export-v2'
    repeated = BUILD / 'static-export-v2-repeat'
    comparisons = []
    for path in sorted(exported.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(exported)
        assert path.read_bytes() == (repeated / rel).read_bytes(), rel
        copy(path, HERE / 'static-v2' / rel)
        comparisons.append({'path': rel.as_posix(), 'smoke_sha256': sha(path),
                            'fresh_repeat_sha256': sha(repeated / rel)})
    first = BUILD / 'static-candidate-v2.zip'
    second = BUILD / 'static-candidate-v2-repeat.zip'
    assert first.read_bytes() == second.read_bytes(), 'candidate fresh repeat'
    save(HERE / 'preflight/export-repeat.json', {
        'scope': 'Existing PNG validation and first export followed by a fresh export process; all output bytes compared.',
        'candidate_sha256': sha(first), 'repeat_candidate_sha256': sha(second),
        'files': comparisons, 'production_modified': False})
    generations = []
    for family, versions in [('shore', [1, 2, 3]), ('rock', [1, 2])]:
        for version in versions:
            prompt = HERE / f'generation-{family}-v{version}.json'
            raw = HERE / f'{family}-raw-v{version}.png'
            record = json.loads(prompt.read_bytes())
            references = []
            for original in record['referenced_image_paths']:
                preserved = 'reference/shore-v2-join-defect.png' if original.startswith('build/') else original
                reference = HERE / preserved
                references.append({'supplied_path': original, 'preserved_path': preserved,
                                   'sha256': sha(reference)})
            generations.append({'tool': 'built-in image_gen', 'prompt_record': prompt.name,
                                'prompt_record_sha256': sha(prompt), 'raw_output': raw.name,
                                'raw_output_sha256': sha(raw), 'references_in_supplied_order': references,
                                'selected_for_static_review': (family, version) in [('shore', 3), ('rock', 2)],
                                'human_approved': False})
    save(HERE / 'generation-index.json', {
        'scope': 'Unapproved static beach and rock studies. Earlier drafts retained as ancestors.',
        'generations': generations})
    sources = {
        'earlier-static.png': HERE / 'native-v1/images/prewave-current.png',
        'draft-static.png': HERE / 'native-v1/images/prewave-candidate.png',
        'original-shape.png': HERE / 'reference/original-static-world.png',
        'earlier-waves.png': HERE / 'native-v1/images/current-none.png',
        'draft-waves.png': HERE / 'native-v1/images/candidate-none.png',
        'earlier-clovers.png': HERE / 'native-v1/images/current-clover.png',
        'draft-clovers.png': HERE / 'native-v1/images/candidate-clover.png',
        'beach.png': HERE / 'static-v2/BMP/BACKGRND.BMP/001.png',
        'rock.png': HERE / 'static-v2/BMP/BACKGRND.BMP/002.png',
    }
    rows = []
    for name, path in sources.items():
        copy(path, HERE / 'review' / name)
        rows.append({'file': name, 'source': str(path.relative_to(ROOT)).replace('\\', '/'), 'sha256': sha(path)})
    save(HERE / 'review/images.json', {'images': rows,
         'static_native_scope': 'Actual grBackgroundSfc after BACKGRND002 and before initial waves, clouds, Johnny and holidays.',
         'original_shape_scope': 'Source-only decoded original geometry composite in diagnostic colors; not a DOSBox screenshot.',
         'full_scene_scope': 'Native final captures. Both sides still use unchanged fallback low-tide waves.'})
    print('Preserved five generations, both static exports, exact repeat results and nine review images.')


if __name__ == '__main__':
    main()
