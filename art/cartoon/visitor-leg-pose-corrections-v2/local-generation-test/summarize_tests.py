"""Summarize the observed local trials, without turning image output into art approval."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
rows = []
for name in ['006-direct-v1', '006-joint-path-v1', '009-from-008-v1', '004-hip-v1', '004-original-pose-v1']:
    folder = HERE / name
    record = json.loads((folder / 'record.json').read_text(encoding='utf-8'))
    qa = json.loads((folder / 'visual-review.json').read_text(encoding='utf-8'))
    output = Path(record['output']['path'])
    actual = hashlib.sha256(output.read_bytes()).hexdigest()
    assert actual == record['output']['sha256'], name
    rows.append({'run': name, 'execution': record['status'], 'visual_result': qa['status'],
                 'assessment': qa['assessment'], 'output_sha256': actual,
                 'inference_seconds': record['inference_seconds'],
                 'process_seconds_excluding_imports': record['process_seconds'],
                 'peak_torch_allocated_gib': record['peak_allocated_gib'],
                 'peak_torch_reserved_gib': record['peak_reserved_gib'],
                 'output_mode': record['output']['mode']})
gpu = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.used,memory.free', '--format=csv'],
                     capture_output=True, text=True, check=True, timeout=15).stdout.strip()
summary = {'schema_version': 1, 'model': 'black-forest-labs/FLUX.2-klein-4B',
           'tests_completed': len(rows), 'runs': rows,
           'method': 'One sequential local inference per saved prompt, each in a separate process, 1024px maximum edge, 4 steps, BF16, model CPU offload, seed7. Timings describe these trials only, not a performance comparison.',
           'conclusion': 'The isolated local environment executes reference edits. Both 006 trials failed the knee-position requirement; 009 removed the bottle but its pose changes were subtle. Both 004 trials failed the hip-integration requirement. The six approved built-in drawings remain selected; no current004 replacement is selected.',
           'all_inference_processes_completed': True,
           'gpu_observation_after_final_process_exit': gpu,
           'appearance_approval': None, 'production_integrated': False}
(HERE / 'test-summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'tests': len(rows), 'gpu': gpu, 'results': [row['visual_result'] for row in rows]}))
