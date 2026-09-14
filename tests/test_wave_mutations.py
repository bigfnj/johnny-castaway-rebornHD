"""Rebuild and execute four single-defect wave renderer controls, then restore.

Use a dedicated CMake build directory. Do not run other source builds concurrently.
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
    parser.add_argument('--exe', required=True, type=Path)
    parser.add_argument('--archive', required=True, type=Path)
    parser.add_argument('--work', required=True, type=Path)
    options = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source = root / 'src/engine/island.c'
    original = source.read_bytes()
    options.work.mkdir(parents=True, exist_ok=True)
    mutations = [
        ('half-alpha', 'restore',
         b'waveBase + (size_t)y * rowBytes, rowBytes);',
         b'waveBase + (size_t)y * rowBytes, 0);'),
        ('overlap', 'neighbors',
         b'for (int i = 0; i < waveOrderCount; i++) {',
         b'for (int i = waveOrderCount - 1; i < waveOrderCount; i++) {'),
        ('hd-legacy', 'hd-guard',
         b'if (style->legacyColorKey) return;',
         b'if (0 && style->legacyColorKey) return;'),
        ('inactive-tide', 'active-tide-guard',
         b'if (!hasReplacement) return;',
         b'if (0 && !hasReplacement) return;'),
    ]
    evidence = []

    def build(label):
        before = options.exe.stat().st_mtime_ns
        result = subprocess.run(['cmake', '--build', str(options.build), '--config', 'Release',
                                 '--target', 'jc_reborn', '--parallel', '4'], capture_output=True, timeout=180)
        text = result.stdout.decode('utf-8', 'replace') + result.stderr.decode('utf-8', 'replace')
        (options.work / f'{label}-build.log').write_text(text, encoding='utf-8')
        assert result.returncode == 0, text[-2500:]
        after = options.exe.stat().st_mtime_ns
        assert after > before, f'{label}: executable timestamp did not advance'
        return {'exe_mtime_before_ns': before, 'exe_mtime_after_ns': after,
                'exe_sha256': hashlib.sha256(options.exe.read_bytes()).hexdigest()}

    try:
        for assertion, name, old, new in mutations:
            assert original.count(old) == 1, f'{name}: ambiguous mutation site'
            source.write_bytes(original.replace(old, new))
            detail = build(name)
            result = subprocess.run([sys.executable, str(root / 'tests/test_wave_renderer.py'),
                                     '--exe', str(options.exe), '--archive', str(options.archive),
                                     '--only', assertion, '--work', str(options.work / name)],
                                    capture_output=True, timeout=120)
            text = result.stdout.decode('utf-8', 'replace') + result.stderr.decode('utf-8', 'replace')
            (options.work / f'{name}-test.log').write_text(text, encoding='utf-8')
            assert f'WITNESS wave assertion executed: {assertion}' in text, text
            failures = [line for line in text.splitlines() if line.startswith('FAIL ')]
            assert result.returncode == 1 and len(failures) == 1 and failures[0].startswith('FAIL tests/test_wave_renderer.py:'), text
            evidence.append({'mutation': name, 'assertion': assertion, 'failure': failures[0], **detail})
            print(f'FIRED {name}: one named failure, rebuilt executable and execution witness verified', flush=True)
            source.write_bytes(original)
    finally:
        source.write_bytes(original)
        build('restored')
        assert source.read_bytes() == original
    assert len(evidence) == len(mutations), 'Incomplete mutation run'
    (options.work / 'report.json').write_text(json.dumps(evidence, indent=2)+'\n', encoding='utf-8')
    print(f'Wave mutations: {len(evidence)}/{len(mutations)} FIRED; exact source restored and rebuilt')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
