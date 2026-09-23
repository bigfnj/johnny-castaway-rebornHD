"""Run the authorized local Qwen evaluation and stop its isolated server afterward."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import traceback
import urllib.error
import urllib.request

from PIL import Image

HERE = Path(__file__).resolve().parent
COMFY = Path('D:/.ai-work/ops/comfyui-qwen21')
PYTHON = Path('D:/.ai-work/venvs/johnny-qwen21/Scripts/python.exe')
MODELS = Path('D:/.ai-work/models/Qwen-Image-2.1')
URL = 'http://127.0.0.1:8191'


def api(path, data=None, timeout=20):
    body = None if data is None else json.dumps(data).encode('utf-8')
    req = urllib.request.Request(URL + path, data=body,
                                 headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f'HTTP {exc.code}: {exc.read().decode("utf-8", "replace")}') from exc


def gpu():
    proc = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.free,utilization.gpu',
                           '--format=csv,noheader,nounits'], capture_output=True, text=True,
                           timeout=15, check=True)
    values = [int(x.strip()) for x in proc.stdout.strip().split(',')]
    return dict(zip(['used_mib', 'free_mib', 'utilization_percent'], values))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--validate-only', action='store_true', help='Start ComfyUI on CPU, validate model availability, then stop without submitting a prompt.')
    args = parser.parse_args()
    if not args.run_id or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in args.run_id):
        parser.error('run-id must contain lowercase letters, numbers, hyphens or underscores')
    run_dir = HERE / 'runs' / args.run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    record = {'status': 'starting', 'model': 'Qwen-Image-2.1', 'run_id': args.run_id,
              'appearance_approval': None, 'production_integrated': False,
              'memory_measurement': 'Sampled nvidia-smi total GPU usage includes Windows and other processes.'}

    def save():
        content = json.dumps(record, indent=2) + '\n'
        (run_dir / 'record.json').write_text(content, encoding='utf-8')
        (HERE / 'record.json').write_text(content, encoding='utf-8')

    server = None
    started = time.monotonic()
    success = False
    output_dir = run_dir / 'comfy-output'
    output_dir.mkdir()
    try:
        downloaded = json.loads((MODELS / 'download-record.json').read_text(encoding='utf-8'))
        if len(downloaded['files']) != 3:
            raise RuntimeError('All three verified model components must be downloaded first')
        record['download_provenance'] = downloaded
        request = json.loads((HERE / 'request.json').read_text(encoding='utf-8'))
        record['settings'] = request['settings']
        for ref in request['references']:
            if hashlib.sha256(Path(ref['file']).read_bytes()).hexdigest() != ref['sha256']:
                raise RuntimeError('Reference changed after preparation: ' + ref['file'])
        try:
            api('/system_stats', timeout=2)
        except (urllib.error.URLError, TimeoutError):
            pass
        else:
            raise RuntimeError('Port8191 already serves an app; refusing to reuse or stop it')
        record['gpu_before'] = gpu()
        if not args.validate_only and record['gpu_before']['free_mib'] < 19000:
            raise RuntimeError('Less than19GB VRAM free; leaving other GPU work untouched')
        record['comfy_commit'] = subprocess.check_output(
            ['git', '-C', str(COMFY), 'rev-parse', 'HEAD'], text=True).strip()
        command = [str(PYTHON), '-u', str(COMFY / 'main.py'),
                   '--listen', '127.0.0.1', '--port', '8191', '--disable-auto-launch',
                   '--disable-all-custom-nodes', '--disable-api-nodes',
                   '--use-pytorch-cross-attention', '--reserve-vram', '4', '--cache-none',
                   '--models-directory', str(MODELS), '--input-directory', str(HERE / 'inputs'),
                   '--output-directory', str(output_dir)]
        if args.validate_only:
            command.append('--cpu')
        record['server_command'] = command
        env = os.environ.copy()
        env.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1')
        with (run_dir / 'server.log').open('w', encoding='utf-8') as log:
            server = subprocess.Popen(command, cwd=COMFY, stdout=log, stderr=subprocess.STDOUT,
                                      env=env, creationflags=subprocess.CREATE_NO_WINDOW)
        record['server_pid'] = server.pid
        save()
        startup_deadline = time.monotonic() + 300
        while time.monotonic() < startup_deadline:
            if server.poll() is not None:
                raise RuntimeError('ComfyUI startup failed; see server.log')
            try:
                stats = api('/system_stats', timeout=2)
                break
            except (urllib.error.URLError, TimeoutError):
                time.sleep(2)
        else:
            raise TimeoutError('ComfyUI startup exceeded five minutes')
        record['system_stats'] = stats
        info = api('/object_info', timeout=60)
        workflow = json.loads((HERE / 'workflow-api.json').read_text(encoding='utf-8'))
        # The request is the source of truth on reruns; never reuse stale prompt text.
        workflow['8']['inputs']['prompt'] = request['prompt']
        workflow['8']['inputs']['resolution'] = request['settings']['resolution']
        workflow['10']['inputs'].update({
            'seed': request['settings']['seed'], 'steps': request['settings']['steps'],
            'cfg': request['settings']['cfg'], 'sampler_name': request['settings']['sampler'],
            'scheduler': request['settings']['scheduler'],
        })
        missing = sorted({n['class_type'] for n in workflow.values()} - set(info))
        if missing:
            raise RuntimeError('Required nodes unavailable: ' + ', '.join(missing))
        for node_id, field in [('5', 'unet_name'), ('6', 'clip_name'), ('7', 'vae_name')]:
            node = workflow[node_id]
            available = info[node['class_type']]['input']['required'][field][0]
            if node['inputs'][field] not in available:
                raise RuntimeError('Requested model is not available to ComfyUI: ' + node['inputs'][field])
        if args.validate_only:
            record['status'] = 'workflow_available_without_inference'
            record['note'] = 'All12 native nodes and all3 model components are available. CPU startup only; no prompt submitted or image generated.'
            success = True
            return 0
        (run_dir / 'workflow-api.json').write_text(json.dumps(workflow, indent=2), encoding='utf-8')
        submitted = api('/prompt', {'prompt': workflow, 'client_id': 'johnny-qwen21-' + args.run_id}, timeout=60)
        record['submission'] = submitted
        if submitted.get('node_errors') or 'prompt_id' not in submitted:
            raise RuntimeError('Workflow validation failed: ' + json.dumps(submitted))
        prompt_id = submitted['prompt_id']
        record['status'] = 'running'
        record['startup_seconds'] = round(time.monotonic() - started, 2)
        record['gpu_samples'] = []
        save()
        inference_start = time.monotonic()
        next_report = 0
        while time.monotonic() - inference_start < 1800:
            if server.poll() is not None:
                raise RuntimeError('ComfyUI exited during generation; see server.log')
            elapsed = round(time.monotonic() - inference_start, 2)
            sample = {'seconds': elapsed, **gpu()}
            record['gpu_samples'].append(sample)
            if elapsed >= next_report:
                print(json.dumps({'status': 'running', **sample}), flush=True)
                next_report = elapsed + 30
                save()
            history = api('/history/' + prompt_id)
            if prompt_id in history:
                result = history[prompt_id]
                (run_dir / 'history.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
                if not result['status'].get('completed') or result['status'].get('status_str') == 'error':
                    raise RuntimeError('Generation failed: ' + json.dumps(result['status']))
                images = result.get('outputs', {}).get('12', {}).get('images', [])
                if not images:
                    raise RuntimeError('Completed history contains no saved image')
                item = images[0]
                produced = (output_dir / item.get('subfolder', '') / item['filename']).resolve()
                if not produced.is_relative_to(output_dir.resolve()):
                    raise RuntimeError('Output path falls outside the isolated run')
                final = run_dir / 'output-raw.png'
                shutil.copyfile(produced, final)
                shutil.copyfile(final, HERE / 'output-raw.png')
                with Image.open(final) as im:
                    im.load()
                    record['output'] = {'path': str(final), 'mode': im.mode, 'size': list(im.size),
                                        'sha256': hashlib.sha256(final.read_bytes()).hexdigest(),
                                        'alpha_extrema': list(im.getchannel('A').getextrema()) if 'A' in im.getbands() else None}
                record['inference_seconds'] = round(time.monotonic() - inference_start, 2)
                record['status'] = 'image_returned_needs_visual_review'
                success = True
                break
            time.sleep(5)
        else:
            raise TimeoutError('Generation exceeded30minutes')
    except Exception:
        record['status'] = 'failed'
        record['error'] = traceback.format_exc()
        print(record['error'], flush=True)
    finally:
        if server is not None and server.poll() is None:
            try:
                api('/interrupt', {}, timeout=5)
            except Exception:
                pass
            # Windows venv python.exe launches another Python process. Stop this
            # owned tree, not just the launcher, so CUDA allocations are released.
            subprocess.run(['taskkill', '/PID', str(server.pid), '/T', '/F'],
                           capture_output=True, text=True, timeout=20, check=False)
            try:
                server.wait(timeout=20)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=10)
        record['process_seconds'] = round(time.monotonic() - started, 2)
        record['gpu_after'] = gpu()
        samples = record.get('gpu_samples', [])
        record['peak_total_gpu_used_mib'] = max([s['used_mib'] for s in samples], default=None)
        record['server_stopped'] = server is None or server.poll() is not None
        save()
        print(json.dumps({k: record[k] for k in ['status', 'process_seconds', 'peak_total_gpu_used_mib', 'server_stopped']}), flush=True)
    return 0 if success else 1


if __name__ == '__main__':
    raise SystemExit(main())
