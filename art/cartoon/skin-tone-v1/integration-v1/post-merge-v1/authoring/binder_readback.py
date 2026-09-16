"""Read copied durable binder closure against working bytes and the Git index."""
from pathlib import Path
import hashlib
import io
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
FEATURE = Path('D:/.ai-work/worktrees/johnny-cartoon-connecting-poses')
BUNDLES = ['art/cartoon/skin-tone-v1', 'art/cartoon/standing018-proportions-v1',
           'art/cartoon/walk-pilot/connecting-poses-v1']
COMMIT = '9ea8293f8efbd45a25717b4f8dd3bc5139586259'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def git(*args, data=None):
    return subprocess.run(['git', *args], cwd=ROOT, input=data, check=True, capture_output=True).stdout

def main():
    index = {}
    for item in git('ls-files', '--stage', '-z').split(b'\0'):
        if item:
            meta, name = item.split(b'\t', 1)
            mode, oid, stage = meta.decode().split()
            assert stage == '0'
            index[name.decode()] = oid
    commit_paths = {p.decode() for p in git('ls-tree', '-r', '--name-only', '-z', COMMIT).split(b'\0') if p}
    binder_paths = [p for p in index if any(p.startswith(b+'/') for b in BUNDLES)
                    and Path(p).name in ('evidence.json', 'manifest.json', 'baseline-checkpoint.json')]
    checks = []
    binders = []
    def add(binder, path, digest, relation):
        assert len(digest) == 64
        key = path.relative_to(ROOT).as_posix()
        checks.append({'binder':binder, 'path':key, 'expected_sha256':digest, 'relation':relation})
    for name in sorted(binder_paths):
        p = ROOT/name
        d = json.loads(p.read_bytes())
        base = ROOT/d['evidence_root'] if 'evidence_root' in d else p.parent
        before = len(checks)
        for key, digest in d.get('files_sha256', {}).items():
            add(name, base/key, digest, 'copied-member')
        files = d.get('files', {})
        if isinstance(files, list):
            for row in files:
                path = row['path']
                target = ROOT/path if path.startswith('art/') else base/path
                add(name, target, row['sha256'], 'durable-member')
        else:
            for path, row in files.items():
                add(name, base/path, row['sha256'] if isinstance(row, dict) else row, 'copied-member')
        for field in ('bound_files_sha256', 'linked_evidence_sha256', 'external_inputs_sha256', 'helpers_sha256', 'raw_sources_sha256', 'helper_source_sha256'):
            links = d.get(field, {})
            if not isinstance(links, dict):
                continue
            for path, digest in links.items():
                if path.startswith(('art/', 'tools/', 'src/', 'tests/')) and isinstance(digest, str) and len(digest)==64:
                    add(name, ROOT/path, digest, 'repo-source-link')
        links = d.get('linked_evidence', {})
        for key, value in links.items():
            if isinstance(value, dict):
                add(name, ROOT/value['path'], value['sha256'], 'linked-evidence')
            else:
                add(name, ROOT/key, value, 'linked-evidence')
        for field in ('native_evidence', 'native_evidence_readback', 'unchanged_helpers_and_executed_guard_evidence'):
            if field in d:
                add(name, ROOT/d[field]['path'], d[field]['sha256'], 'linked-evidence')
        binders.append({'path':name, 'sha256':sha(p.read_bytes()), 'reference_checks':len(checks)-before})
    wanted = sorted({c['path'] for c in checks})
    requests = [(p, index[p]) for p in wanted if p in index]
    raw = git('cat-file', '--batch', data=('\n'.join(oid for _,oid in requests)+'\n').encode())
    stream = io.BytesIO(raw)
    staged = {}
    for path, oid in requests:
        header = stream.readline().decode().split()
        assert header[:2] == [oid, 'blob']
        value = stream.read(int(header[2]))
        assert stream.read(1)==b'\n'
        staged[path] = sha(value)
    failures, restored = [], {}
    for c in checks:
        p = ROOT/c['path']
        c['worktree_sha256'] = sha(p.read_bytes()) if p.is_file() else None
        c['index_sha256'] = staged.get(c['path'])
        c['present_in_audited_commit'] = c['path'] in commit_paths
        c['status'] = 'PASS' if c['worktree_sha256']==c['index_sha256']==c['expected_sha256'] else 'FAIL'
        if c['status']=='FAIL':
            failures.append(c)
        if not c['present_in_audited_commit']:
            source = FEATURE/c['path']
            restored[c['path']] = {k:v for k,v in c.items() if k!='binder'}
            restored[c['path']]['feature_source_sha256'] = sha(source.read_bytes()) if source.is_file() else None
            assert restored[c['path']]['feature_source_sha256'] == c['expected_sha256']
    report = {'status':'PASS' if not failures else 'FAIL', 'audited_commit':COMMIT,
        'runner_sha256':sha(Path(__file__).read_bytes()), 'binders':binders,
        'binder_count':len(binders), 'reference_checks':len(checks), 'unique_referenced_paths':len(wanted),
        'failures':failures, 'restored_after_merge':list(restored.values()), 'checks':checks,
        'excluded_reference_classes':[
            'Review-record image inventories describe explicitly omitted regenerated/local preview bulk assets; they are not copied-member binders.',
            'Native source-pins identify compilation inputs, separately covered by commit/source fingerprints; no claim every source-pins entry is a copied evidence member.',
            'executed_source, copy_sources, copy_records source sides and runtime_pngs_retained_in_ignored_build describe ancestry or intentionally local inputs. Destination file members are checked.',
            'External original resources, raw image generation cache, binaries and bulk capture PNGs are documented reproduction prerequisites, not claimed durable copies.']}
    target = OUT/'restored-evidence-v2.json'
    target.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('checks','binders')}, indent=2))
    assert not failures
    return report

if __name__=='__main__':
    main()
