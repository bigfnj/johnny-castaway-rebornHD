"""Rebuild ownership mutants; require one executed, named allocation-test failure."""
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
    options.work.mkdir(parents=True, exist_ok=True)
    mutations = [
        ('inactive-scene-owner', 'scene-release', 'ads.c',
         '    int wasRunning = ttmThreads[sceneNo].isRunning != TTM_FREE;',
         '    if (!ttmThreads[sceneNo].isRunning) return;\n'
         '    int wasRunning = ttmThreads[sceneNo].isRunning != TTM_FREE;'),
        ('scene-pointer-clear', 'scene-release', 'ads.c',
         '    ttmThreads[sceneNo].ttmLayer = NULL;',
         '    /* mutant retains the released scene pointer */'),
        ('benchmark-last-two', 'benchmark-release', 'ads.c',
         '    for (int i=0; i < MAX_TTM_THREADS; i++)\n'
         '        adsStopScene(i);\n\n    ttmResetSlot(&ttmSlots[0]);',
         '    for (int i=0; i < MAX_TTM_THREADS - 2; i++)\n'
         '        adsStopScene(i);\n\n    ttmResetSlot(&ttmSlots[0]);'),
        ('standalone-saved-owner', 'standalone-saved-zone', 'ads.c',
         '    ttmResetSlot(&ttmSlots[0]);\n    grReleaseSavedLayer();',
         '    ttmResetSlot(&ttmSlots[0]);\n    /* mutant retains saved layer */'),
        ('reinit-scene-owner', 'reinitialize', 'ads.c',
         '    for (int i=0; i < MAX_TTM_THREADS; i++)\n'
         '        adsStopScene(i);\n    for (int i=0; i < MAX_TTM_SLOTS; i++)',
         '    /* mutant drops scene ownership without release */\n'
         '    for (int i=0; i < MAX_TTM_SLOTS; i++)'),
        ('inactive-cloud-owner', 'reinitialize', 'ads.c',
         '    ttmCloudsThread.isRunning = TTM_FREE;\n'
         '    grFreeLayer(ttmCloudsThread.ttmLayer);',
         '    if (ttmCloudsThread.isRunning) grFreeLayer(ttmCloudsThread.ttmLayer);\n'
         '    ttmCloudsThread.isRunning = TTM_FREE;'),
        ('borrowed-background', 'reinitialize', 'ads.c',
         '    ttmBackgroundThread.ttmLayer = NULL;',
         '    grFreeLayer(ttmBackgroundThread.ttmLayer);\n'
         '    ttmBackgroundThread.ttmLayer = NULL;'),
        ('zero-sprite-cache', 'reinitialize', 'ttm.c',
         '        grReleaseBmp(ttmSlot, (uint16)i);',
         '        if (ttmSlot->numSprites[i]) grReleaseBmp(ttmSlot, (uint16)i);'),
        ('graphics-background-owner', 'graphics-release', 'graphics.c',
         '    grReleaseScreen();\n    artStyleReportUsage();',
         '    /* mutant retains screen owner */\n    artStyleReportUsage();'),
        ('graphics-saved-owner', 'graphics-release', 'graphics.c',
         '    if (platform_window) grCaptureFrame();\n    grReleaseSavedLayer();',
         '    if (platform_window) grCaptureFrame();\n    /* mutant retains saved owner */'),
    ]
    sources = {root / 'src/engine' / item[2] for item in mutations}
    originals = {source: source.read_bytes() for source in sources}

    def replace_once(data, old, new):
        old, new = old.encode(), new.encode()
        if old not in data:
            old, new = old.replace(b'\n', b'\r\n'), new.replace(b'\n', b'\r\n')
        assert data.count(old) == 1, 'ambiguous mutation site'
        return data.replace(old, new)

    def build(label):
        before = {str(exe): exe.stat().st_mtime_ns for exe in [options.probe, options.engine]}
        run = subprocess.run(['cmake', '--build', str(options.build), '--config', 'Release',
                              '--target', 'jc_reborn', 'jc_lifecycle_test', '--parallel', '4'],
                             capture_output=True, timeout=180)
        output = (run.stdout + run.stderr).decode('utf-8', 'replace')
        (options.work / f'{label}-build.log').write_text(output, encoding='utf-8')
        assert run.returncode == 0, output
        artifacts = []
        for exe in [options.probe, options.engine]:
            after = exe.stat().st_mtime_ns
            assert after > before[str(exe)], f'{label}: no rebuild: {exe}'
            artifacts.append({'name': exe.name, 'before_ns': before[str(exe)], 'after_ns': after,
                              'sha256': hashlib.sha256(exe.read_bytes()).hexdigest()})
        return artifacts

    evidence = []
    try:
        for name, check, filename, old, new in mutations:
            # Restore each previous mutant before introducing the next one.
            for source, original in originals.items():
                if source.read_bytes() != original:
                    source.write_bytes(original)
            source = root / 'src/engine' / filename
            source.write_bytes(replace_once(originals[source], old, new))
            artifacts = build(name)
            run = subprocess.run([sys.executable, str(root / 'tests/test_lifecycle.py'),
                                  '--exe', str(options.probe), '--only', check],
                                 capture_output=True, timeout=45)
            output = (run.stdout + run.stderr).decode('utf-8', 'replace')
            (options.work / f'{name}-test.log').write_text(output, encoding='utf-8')
            assert f'WITNESS lifecycle assertion executed: {check}' in output, output
            assert f'WITNESS production lifecycle executed: {check}' in output, output
            failures = [line for line in output.splitlines() if line.startswith('FAIL ')]
            assert run.returncode == 1 and len(failures) == 1, output
            assert failures[0].startswith(f'FAIL tests/test_lifecycle.py:{check}:'), output
            diagnostics = [line for line in output.splitlines()
                           if line.startswith('CHECK ') or line.startswith('ALLOCATION TRACKER:')]
            assert len(diagnostics) == 1, output
            evidence.append({'mutation': name, 'check': check,
                             'diagnostic': diagnostics[0], 'artifacts': artifacts})
            print(f'FIRED {name}: rebuilt artifacts, execution witness and one named failure', flush=True)
    finally:
        for source, original in originals.items():
            source.write_bytes(original)
        build('restored')
        assert all(source.read_bytes() == original for source, original in originals.items())
    assert len(evidence) == len(mutations)
    (options.work / 'report.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    print(f'Lifecycle mutations: {len(evidence)}/{len(mutations)} FIRED; exact sources restored and rebuilt')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
