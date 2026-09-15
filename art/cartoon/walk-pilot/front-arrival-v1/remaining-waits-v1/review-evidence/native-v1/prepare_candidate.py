"""Add exactly the two explicit000015 handoff PNGs above the approved baseline."""
import copy
import hashlib
import json
from pathlib import Path
import struct
import zipfile

import config

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    target = OUT / 'candidate-v1'
    assert not target.exists(), 'preserve candidate artifacts'
    binding = json.loads((OUT / 'baseline-v1/build.json').read_bytes())
    baseline = OUT / 'baseline-pack.zip'
    assert sha(baseline.read_bytes()) == binding['baseline_pack_sha256'], 'approved baseline ZIP identity'
    assert sha((ROOT / 'assets/scrantic_data.zip').read_bytes()) == config.PRODUCTION_SHA, 'production unchanged'
    selection = json.loads((OUT / 'candidate-selection.json').read_bytes())
    assert sorted(row['frame'] for row in selection['frames']) == list(config.CANDIDATE_FRAMES), 'only configured new frames'
    records, additions = [], {}
    with zipfile.ZipFile(baseline) as archive:
        names = archive.namelist()
        assert len(names) == len(set(names)), 'unique baseline members'
        before = {name: sha(archive.read(name)) for name in names}
        for selected in selection['frames']:
            frame = selected['frame']
            member = f'data/styles/cartoon/BMP/JOHNWALK.BMP/{frame:03}.png'
            assert member not in names, 'candidate frame absent from prior approved baseline'
            raw = (ROOT / selected['path']).read_bytes()
            assert sha(raw) == selected['sha256'], 'explicit runtime identity:' + member
            assert sha((ROOT / selected['recipe_path']).read_bytes()) == selected['recipe_sha256'], 'explicit recipe identity:' + member
            assert len(raw) >= 33 and raw[:16] == b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR' and raw[24:29] == bytes([8, 6, 0, 0, 0]), 'RGBA PNG contract'
            size = list(struct.unpack('>II', raw[16:24]))
            assert size == list(struct.unpack('>II', archive.read(f'data/hd/BMP/JOHNWALK.BMP/{frame:03}.png')[16:24])), 'original doubled runtime canvas'
            additions[member] = raw
            records.append({'frame': frame, 'member': member, 'new_sha256': sha(raw), 'canvas': size, 'recipe_sha256': selected['recipe_sha256']})
        target.mkdir()
        with zipfile.ZipFile(target / 'scrantic_data.zip', 'x') as output:
            output.comment = archive.comment
            for info in archive.infolist():
                output.writestr(copy.copy(info), archive.read(info.filename))
            for member, raw in additions.items():
                info = copy.copy(archive.getinfo('data/hd/BMP/JOHNWALK.BMP/' + member.rsplit('/', 1)[1]))
                info.filename = info.orig_filename = member
                output.writestr(info, raw)
    with zipfile.ZipFile(target / 'scrantic_data.zip') as packed:
        assert packed.namelist() == names + list(additions), 'exactly000015 added'
        assert all(sha(packed.read(name)) == digest for name, digest in before.items()), 'every previously approved and production member exact'
        assert all(packed.read(name) == raw for name, raw in additions.items()), 'exact handoff PNG bytes'
    record = {'archive_sha256': sha((target / 'scrantic_data.zip').read_bytes()),
              'base_archive_sha256': binding['baseline_pack_sha256'], 'baseline_executable_sha256': binding['executable_sha256'],
              'added_members': records, 'unchanged_members': len(names), 'total_members': len(names) + len(additions),
              'selection_sha256': sha((OUT / 'candidate-selection.json').read_bytes()),
              'prepare_helper_sha256': sha(Path(__file__).read_bytes()), 'scope': 'Private000015 technical candidate only; all approved artwork and production remain unchanged.'}
    (target / 'preparation.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
