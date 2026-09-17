"""Focused reference readback, exact cell replication, and source-pin refusal."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
HELPER = HERE / 'prepare.py'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    manifest = json.loads((HERE / 'source.json').read_bytes())
    witness = 'WITNESS cloud-reference ' + sha(HELPER.read_bytes().replace(b'\r\n', b'\n'))
    cases = []
    for name, extra, expected in [('fresh_replay', [], 0),
                                   ('wrong_original_archive', ['--originals', str(ROOT / 'assets/scrantic_data.zip')], 1),
                                   ('restored_positive', [], 0)]:
        command = [sys.executable, '-B', str(HELPER), '--check'] + extra
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        assert result.returncode == expected and witness in result.stdout, name
        if expected:
            assert result.stdout.splitlines() == [witness, 'FAIL art/cartoon/character-inventory-v1/reference-originals.zip: source identity differs'], name
        else:
            assert 'PASS cloud-reference' in result.stdout, name
        cases.append({'name': name, 'arguments': ['--check'] + extra, 'exit_code': result.returncode,
                      'stdout': result.stdout, 'stderr': result.stderr})
    rows = []
    for row in manifest['frames']:
        label = row['resource'].split('.')[0].lower() + '-' + str(row['frame']).zfill(3)
        native = np.array(Image.open(HERE / (label + '-original.png')).convert('RGBA'))
        guide = np.array(Image.open(HERE / (label + '-guide.png')).convert('RGBA'))
        scale = row['guide']['integer_scale']
        x, y = row['guide']['offset']
        expected = np.zeros_like(guide)
        expected[y:y + native.shape[0] * scale, x:x + native.shape[1] * scale] = native.repeat(scale, 0).repeat(scale, 1)
        assert np.array_equal(guide, expected), label + ': pixel-cell replication'
        assert sorted(np.unique(native[:, :, 3]).tolist()) == [0, 255], label + ': source alpha'
        hd = np.array(Image.open(HERE / (label + '-hd.png')).convert('RGBA'))
        hd[np.all(hd == [168, 0, 168, 255], axis=2), 3] = 0
        doubled = native.repeat(2, 0).repeat(2, 1)
        visible = (hd[:, :, 3] > 0) & (doubled[:, :, 3] > 0)
        rows.append({'resource': row['resource'], 'frame': row['frame'], 'exact_guide_replication': True,
                     'source_alpha_values': [0, 255],
                     'hd_vs_original2x_alpha_different_pixels': int(np.count_nonzero(hd[:, :, 3] != doubled[:, :, 3])),
                     'hd_vs_original2x_visible_rgb_different_pixels': int(np.count_nonzero(np.any(hd[:, :, :3] != doubled[:, :, :3], axis=2) & visible))})
    for name, expected in manifest['files_sha256'].items():
        assert sha((HERE / name).read_bytes()) == expected, name
    result = {'status': 'PASS', 'scope': 'Six source references and21 PNG readbacks only; no creative export, engine run or broad suite.',
              'source_sha256': sha((HERE / 'source.json').read_bytes()),
              'prepare_lf_sha256': manifest['prepare_lf_sha256'],
              'verify_lf_sha256': sha(Path(__file__).read_bytes().replace(b'\r\n', b'\n')),
              'ordered_fresh_process_checks': cases, 'pixel_checks': rows,
              'limitation': 'The negative control substitutes an actual wrong archive and proves the source identity guard. No source-removal mutation or original decoder rerun is claimed.'}
    (HERE / 'verification.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('PASS cloud-reference-verification: three fresh processes, six exact pixel-cell checks,21 PNG hashes')


if __name__ == '__main__':
    main()
