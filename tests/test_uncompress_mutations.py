"""Rebuild isolated decoder mutants and require exactly one named failure each."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', required=True, type=Path)
    parser.add_argument('--probe', required=True, type=Path)
    parser.add_argument('--engine', required=True, type=Path)
    parser.add_argument('--work', required=True, type=Path)
    options = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source = root / 'src/engine/uncompress.c'
    original = source.read_bytes()
    options.work.mkdir(parents=True, exist_ok=True)
    mutations = [
        ('rle-short-output', b'if (outOffset != outSize) {\n        fatalError("RLE',
         b'if (0 && outOffset != outSize) {\n        fatalError("RLE'),
        ('lzw-short-output', b'if (outOffset != outSize) {\n        fatalError("LZW',
         b'if (0 && outOffset != outSize) {\n        fatalError("LZW'),
        ('lzw-full-buffer-early', b'if (outOffset >= outSize)\r\n                    return outData;',
         b'if (outOffset >= outSize)\r\n                    fatalError("mutant rejects full-buffer return");'),
    ]
    # Source line endings may differ between checkout platforms.
    def replace_once(data, old, new):
        if old not in data:
            old, new = old.replace(b'\r\n', b'\n'), new.replace(b'\r\n', b'\n')
        if old not in data:
            old, new = old.replace(b'\n', b'\r\n'), new.replace(b'\n', b'\r\n')
        assert data.count(old) == 1, 'ambiguous mutation site'
        return data.replace(old, new)

    def build(label):
        before = {str(exe): exe.stat().st_mtime_ns for exe in [options.probe, options.engine]}
        run = subprocess.run(['cmake', '--build', str(options.build), '--config', 'Release',
                              '--target', 'jc_reborn', 'jc_uncompress_test', '--parallel', '4'],
                             capture_output=True, timeout=180)
        text = (run.stdout + run.stderr).decode('utf-8', 'replace')
        (options.work / f'{label}-build.log').write_text(text, encoding='utf-8')
        assert run.returncode == 0, text
        artifacts = []
        for exe in [options.probe, options.engine]:
            after = exe.stat().st_mtime_ns
            assert after > before[str(exe)], f'{label}: no rebuild: {exe}'
            artifacts.append({'name': exe.name, 'before_ns': before[str(exe)], 'after_ns': after,
                              'sha256': hashlib.sha256(exe.read_bytes()).hexdigest()})
        return artifacts

    evidence = []
    try:
        for name, old, new in mutations:
            source.write_bytes(replace_once(original, old, new))
            artifacts = build(name)
            run = subprocess.run([sys.executable, str(root / 'tests/test_uncompress.py'),
                                  '--probe', str(options.probe), '--engine', str(options.engine),
                                  '--only', name], capture_output=True, timeout=30)
            text = (run.stdout + run.stderr).decode('utf-8', 'replace')
            (options.work / f'{name}-test.log').write_text(text, encoding='utf-8')
            assert f'WITNESS decoder assertion executed: {name}' in text, text
            assert 'WITNESS production uncompress ' in text, text
            failures = [line for line in text.splitlines() if line.startswith('FAIL ')]
            assert run.returncode == 1 and len(failures) == 1, text
            assert failures[0].startswith(f'FAIL tests/test_uncompress.py:{name}:'), text
            evidence.append({'mutation': name, 'failure': failures[0], 'artifacts': artifacts})
            print(f'FIRED {name}: rebuilt artifacts, execution witness and one named failure', flush=True)
    finally:
        source.write_bytes(original)
        build('restored')
        assert source.read_bytes() == original
    assert len(evidence) == len(mutations)
    (options.work / 'report.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    print(f'Decoder mutations: {len(evidence)}/{len(mutations)} FIRED; exact source restored and rebuilt')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
