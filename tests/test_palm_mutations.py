"""Rebuild single-defect palm controls and prove each assertion executed.

Do not run other source builds concurrently. Sources are restored in finally.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', required=True, type=Path)
    parser.add_argument('--driver', required=True, type=Path)
    parser.add_argument('--archive', required=True, type=Path)
    parser.add_argument('--work', required=True, type=Path)
    options = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    graphics, walk = root / 'src/engine/graphics.c', root / 'src/engine/walk.c'
    originals = {path: path.read_bytes() for path in (graphics, walk)}
    options.work.mkdir(parents=True, exist_ok=True)
    mutations = [
        ('outside-alpha', 'disable-atop', walk, b'if (palmUsesAtop) {', b'if (0 && palmUsesAtop) {'),
        ('overlap', 'remove-tree-color', graphics, b's[channel] * d[3] + d[channel]', b'0 * s[channel] * d[3] + d[channel]'),
        ('clipping', 'ignore-clip', graphics, b'platformGetClipRect(sfc, &clip);',
         b'platformGetClipRect(sfc, &clip); clip = (PlatformRect){0,0,platformGetSurfaceWidth(sfc),platformGetSurfaceHeight(sfc)};'),
        ('hd-legacy', 'disable-hd-guard', walk, b'if (!style->legacyColorKey) {', b'if (1) {'),
        ('partial-fallback', 'disable-presence-guard', walk, b'if (zipvfs_exists(path)) palmUsesAtop = 1;', b'palmUsesAtop = 1;'),
    ]
    evidence = []

    def build(label):
        before = options.driver.stat().st_mtime_ns
        result = subprocess.run(['cmake', '--build', str(options.build), '--config', 'Release',
            '--target', 'jc_palm_test'], capture_output=True, timeout=120)
        text = result.stdout.decode('utf-8', 'replace') + result.stderr.decode('utf-8', 'replace')
        (options.work / f'{label}-build.log').write_text(text, encoding='utf-8')
        assert result.returncode == 0, text[-2000:]
        after = options.driver.stat().st_mtime_ns
        assert after > before, f'{label}: driver timestamp did not advance'
        return {'mtime_before_ns': before, 'mtime_after_ns': after,
                'driver_sha256': hashlib.sha256(options.driver.read_bytes()).hexdigest()}

    try:
        for assertion, label, path, old, new in mutations:
            original = originals[path]
            assert original.count(old) == 1, f'{path}: mutation site is not unique'
            path.write_bytes(original.replace(old, new))
            detail = build(label)
            result = subprocess.run([sys.executable, '-B', str(root / 'tests/test_palm_renderer.py'),
                '--driver', str(options.driver), '--archive', str(options.archive), '--only', assertion,
                '--work', str(options.work / label)], capture_output=True, timeout=120)
            output = result.stdout.decode('utf-8', 'replace') + result.stderr.decode('utf-8', 'replace')
            (options.work / f'{label}-test.log').write_text(output, encoding='utf-8')
            assert f'WITNESS palm assertion executed: {assertion}' in output, output
            failures = [line for line in output.splitlines() if line.startswith('FAIL ')]
            assert result.returncode == 1 and len(failures) == 1 and failures[0].startswith('FAIL tests/test_palm_renderer.py:'), output
            evidence.append({'mutation': label, 'assertion': assertion, 'source': str(path), 'failure': failures[0], **detail})
            print(f'FIRED {label}: rebuilt driver, executed witness, one named assertion failure', flush=True)
            path.write_bytes(original)
    finally:
        for path, original in originals.items():
            path.write_bytes(original)
        build('restored')
    assert all(path.read_bytes() == original for path, original in originals.items())
    (options.work / 'report.json').write_text(json.dumps(evidence, indent=2)+'\n', encoding='utf-8')
    print(f'Palm mutations: {len(evidence)}/{len(mutations)} FIRED; exact source restored and rebuilt')


if __name__ == '__main__':
    main()
