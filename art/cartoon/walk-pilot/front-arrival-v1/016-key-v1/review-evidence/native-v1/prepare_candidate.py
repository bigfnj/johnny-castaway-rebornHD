"""Prepare an isolated future016 candidate; all existing ZIP members remain exact."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import struct
import zipfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
MEMBER = 'data/styles/cartoon/BMP/JOHNWALK.BMP/016.png'
HD_MEMBER = 'data/hd/BMP/JOHNWALK.BMP/016.png'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, label):
    if not ok:
        raise ValueError('prepare_candidate.py: ' + label)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--png', type=Path, required=True)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--output', type=Path, default=OUT / 'candidate-v1')
    args = parser.parse_args()
    folder = args.output.resolve()
    require(not folder.exists(), 'preserve existing candidate evidence')
    baseline = json.loads((OUT / 'baseline-v1/summary.json').read_bytes())
    source = OUT / 'baseline-pack.zip'
    require(sha(source.read_bytes()) == baseline['baseline_pack_sha256'], 'current baseline archive identity')
    raw = args.png.read_bytes()
    require(sha(raw) == args.expected_sha256, 'explicit candidate016 identity')
    require(len(raw) >= 33 and raw[:16] == b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR', 'candidate PNG header')
    require(raw[24:29] == bytes([8, 6, 0, 0, 0]), 'candidate 8-bit non-interlaced RGBA')
    size = list(struct.unpack('>II', raw[16:24]))
    with zipfile.ZipFile(source) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), 'unique baseline ZIP members')
        require(MEMBER not in names, 'baseline has no Cartoon016')
        require(size == list(struct.unpack('>II', archive.read(HD_MEMBER)[16:24])), 'unchanged016 runtime canvas')
        before = {name: sha(archive.read(name)) for name in names}
        folder.mkdir()
        target = folder / 'scrantic_data.zip'
        with zipfile.ZipFile(target, 'x') as candidate:
            candidate.comment = archive.comment
            for info in archive.infolist():
                candidate.writestr(copy.copy(info), archive.read(info.filename))
            info = copy.copy(archive.getinfo(HD_MEMBER))
            info.filename = MEMBER
            info.orig_filename = MEMBER
            candidate.writestr(info, raw)
    with zipfile.ZipFile(target) as candidate:
        require(candidate.namelist() == names + [MEMBER], 'exactly one new Cartoon016 member')
        require(all(sha(candidate.read(name)) == digest for name, digest in before.items()), 'every existing member unchanged, including024-029')
        require(candidate.read(MEMBER) == raw, 'new016 exact bytes')
    (folder / '016.png').write_bytes(raw)
    report = {
        'scope': 'Private technical comparison only; no production edit or approval of016. PNG fit/provenance remain authoring responsibilities.',
        'archive_sha256': sha(target.read_bytes()), 'base_archive_sha256': baseline['baseline_pack_sha256'],
        'baseline_executable_sha256': baseline['executable_sha256'],
        'added_members': [{'frame': 16, 'member': MEMBER, 'new_sha256': sha(raw), 'canvas': size}],
        'unchanged_members': len(names), 'total_members': len(names) + 1,
        'prepare_helper_sha256': sha(Path(__file__).read_bytes())
    }
    (folder / 'preparation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    require(sha(source.read_bytes()) == baseline['baseline_pack_sha256'], 'approved017 baseline archive unchanged')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
