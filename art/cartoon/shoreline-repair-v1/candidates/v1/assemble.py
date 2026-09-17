"""Freeze the three selected diagnostic exports after smoke then fresh replay."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from PIL import Image

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parents[1]
HELPER = BUNDLE / 'export.py'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
recipe_path = BUNDLE / 'recipe-v1.json'
report_path = HERE / 'export-report.json'
assert not recipe_path.exists() and not report_path.exists()
rows, runs = [], []


def execute(frame, output, check):
    command = [sys.executable, '-B', str(HELPER), '--recipe', str(HERE/f'{frame:03}/recipe.json'), '--output', str(output)]
    if check:
        command.append('--check')
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', timeout=60)
    assert result.returncode == 0 and not result.stderr, (frame, result.stdout, result.stderr)
    assert 'WITNESS shore-export '+sha(HELPER) in result.stdout and 'DIAGNOSTIC ' in result.stdout
    runs.append({'frame': frame, 'phase': 'smoke' if check else 'fresh_replay',
                 'stdout': result.stdout, 'stderr': result.stderr, 'status': 'PASS'})


for frame in (3,7,9):
    execute(frame, HERE/f'{frame:03}', True)
with tempfile.TemporaryDirectory(prefix='assembly-replay-', dir=HERE) as temporary:
    work = Path(temporary).resolve()
    assert work.is_relative_to(HERE.resolve())
    for frame in (3,7,9):
        saved = HERE/f'{frame:03}'
        recipe = json.loads((saved/'recipe.json').read_bytes())
        report = json.loads((saved/'export-report.json').read_bytes())
        output = work/f'{frame:03}'
        execute(frame, output, False)
        for name in [*report['outputs_sha256'], 'export-report.json']:
            assert (saved/name).read_bytes() == (output/name).read_bytes()
        alpha = Image.open(saved/'full-guide-padded.png').getchannel('A')
        pad = recipe['padding_hd']
        scale = recipe['affine_forward'][0]
        x,y = [int(n*scale)+pad for n in recipe['guide_offset_xy']]
        w,h = recipe['runtime_canvas']
        regions = {'top': (0,0,alpha.width,y), 'bottom': (0,y+h,alpha.width,alpha.height),
                   'left': (0,y,x,y+h), 'right': (x+w,y,alpha.width,y+h)}
        edges = {}
        for name, rect in regions.items():
            hist = alpha.crop(rect).histogram()
            edges[name] = {'nonzero_pixels': sum(hist[1:]), 'alpha8_pixels': sum(hist[8:]),
                           'maximum_alpha': max(i for i,n in enumerate(hist) if n)}
        assert sum(v['alpha8_pixels'] for v in edges.values()) == report['filtered_alpha_outside_runtime']['alpha8_pixels']
        rows.append({'frame': frame, 'source': recipe['source'], 'source_sha256': recipe['source_sha256'],
                     'recipe': (saved/'recipe.json').relative_to(BUNDLE).as_posix(), 'recipe_sha256': sha(saved/'recipe.json'),
                     'export_report': (saved/'export-report.json').relative_to(BUNDLE).as_posix(), 'export_report_sha256': sha(saved/'export-report.json'),
                     'runtime_path': (saved/recipe['runtime_path']).relative_to(BUNDLE).as_posix(),
                     'runtime_sha256': sha(saved/recipe['runtime_path']), 'runtime_canvas': recipe['runtime_canvas'],
                     'affine_forward': recipe['affine_forward'], 'cropped_filtered_edges': edges})
aggregate = {'schema_version': 1, 'accepted': False, 'scope': 'First static diagnostic prototype.007 bottomfoam crop remains pending; topjoin crops are distinguished. No fitted geometry or visual acceptance.',
             'exporter_sha256': sha(HELPER), 'filter_sha256': recipe['filter_sha256'],
             'reference_sha256': recipe['reference_sha256'], 'frames': rows}
recipe_path.write_text(json.dumps(aggregate, indent=2)+'\n', encoding='utf-8', newline='\n')
verification = {'status': 'DIAGNOSTIC_REPRODUCTION_PASS', 'accepted': False,
                'aggregate_recipe_sha256': sha(recipe_path), 'helper_sha256': sha(Path(__file__)),
                'frame_count': len(rows), 'runs': runs,
                'guard_evidence': {'path': '007/verification.json', 'sha256': sha(HERE/'007/verification.json')},
                'limits': 'Image/source identity and fixed transform only. Edge counts are geometric, not material segmentation. Native scene/tide contact remains to be reviewed.'}
report_path.write_text(json.dumps(verification, indent=2)+'\n', encoding='utf-8', newline='\n')
print(json.dumps({'recipe_sha256': sha(recipe_path), 'report_sha256': sha(report_path),
                  'edge_counts': {r['frame']:r['cropped_filtered_edges'] for r in rows}}))
