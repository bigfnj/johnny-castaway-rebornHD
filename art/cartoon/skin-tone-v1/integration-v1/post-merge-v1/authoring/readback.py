"""Fresh merged-checkout byte/source/evidence readback. Writes ignored audit JSON only."""
from pathlib import Path
import ast
import hashlib
import io
import json
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
COMMIT = '9ea8293f8efbd45a25717b4f8dd3bc5139586259'
BUNDLES = ['art/cartoon/skin-tone-v1', 'art/cartoon/standing018-proportions-v1',
           'art/cartoon/walk-pilot/connecting-poses-v1']
sha = lambda raw: hashlib.sha256(raw).hexdigest()
load = lambda path: json.loads(path.read_bytes())


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True).stdout


def main():
    assert git('rev-parse', 'HEAD').decode().strip() == COMMIT
    objects = []
    for value in git('ls-tree', '-r', '-z', COMMIT, '--', *BUNDLES).split(b'\0'):
        if value:
            meta, path = value.split(b'\t', 1)
            mode, kind, oid = meta.decode().split()
            assert kind == 'blob'
            objects.append((path.decode(), oid))
    payload = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
        input=('\n'.join(oid for _, oid in objects)+'\n').encode(), check=True, capture_output=True).stdout
    stream = io.BytesIO(payload)
    byte_rows, changed_docs = {}, []
    allowed_doc = 'art/cartoon/standing018-proportions-v1/README.md'
    for path, oid in objects:
        header = stream.readline().decode().split()
        assert header[:2] == [oid, 'blob']
        raw = stream.read(int(header[2]))
        assert stream.read(1) == b'\n'
        current = (ROOT/path).read_bytes()
        if raw != current:
            assert path == allowed_doc, 'Frozen checkout bytes differ:'+path
            changed_docs.append(path)
        byte_rows[path] = {'git_blob': oid, 'commit_sha256': sha(raw), 'bytes': len(raw),
                          'worktree_sha256': sha(current), 'exact': raw == current}
    (OUT/'checkout-files.json').write_text(json.dumps(byte_rows, indent=2)+'\n', encoding='utf-8', newline='\n')
    evidence_rows = []
    for bundle in BUNDLES:
        for path in (ROOT/bundle).rglob('evidence.json'):
            doc = load(path)
            rows = dict(doc.get('files_sha256', {}))
            files = doc.get('files')
            if isinstance(files, list):
                rows.update({r['path']: r['sha256'] for r in files if isinstance(r, dict) and 'path' in r and 'sha256' in r})
            elif isinstance(files, dict):
                rows.update({k: v['sha256'] if isinstance(v, dict) else v for k, v in files.items()})
            for name, digest in rows.items():
                assert sha((path.parent/name).read_bytes()) == digest, path.as_posix()+':'+name
            links = {}
            for key in ('bound_files_sha256', 'linked_evidence_sha256'):
                links.update(doc.get(key, {}))
            for name, digest in links.items():
                assert sha((ROOT/name).read_bytes()) == digest, name
            if rows:
                evidence_rows.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes()),
                                      'retained_checks': len(rows), 'linked_checks': len(links)})
    (OUT/'evidence-readback.json').write_text(json.dumps(evidence_rows, indent=2)+'\n', encoding='utf-8', newline='\n')
    source_rows = {}
    for folder in BUNDLES:
        for p in (ROOT/folder).rglob('*.py'):
            parts = p.relative_to(ROOT).parts
            if any(part.startswith(('evidence', 'trials-')) or part == 'review-evidence' for part in parts):
                continue
            raw = p.read_bytes()
            ast.parse(raw, filename=p.relative_to(ROOT).as_posix())
            source_rows[p.relative_to(ROOT).as_posix()] = sha(raw)
    for p in list((ROOT/'tools').glob('art_*.py')) + list((ROOT/'tests').glob('*art*.py')):
        raw = p.read_bytes()
        ast.parse(raw, filename=p.relative_to(ROOT).as_posix())
        source_rows[p.relative_to(ROOT).as_posix()] = sha(raw)
    for name in ['docs/art-style-learnings.md', 'docs/art-style-learnings-arrival.md',
                 'docs/art-style-learnings-connecting-poses.md',
                 'art/cartoon/skin-tone-v1/integration-v1/REPRODUCE.md']:
        source_rows[name] = sha((ROOT/name).read_bytes())
    (OUT/'source-hashes.json').write_text(json.dumps(source_rows, indent=2)+'\n', encoding='utf-8', newline='\n')
    ledger = load(ROOT/'art/cartoon/pack.json')
    accepted = load(ROOT/ledger['acceptance_record'])
    def origins(doc, name, stack=()):
        assert name not in stack and doc['accepted'] is True
        rows = {r['path']: r for r in doc['accepted_assets']}
        if 'inherited_acceptances' not in doc:
            return {p: name for p in rows}
        inherited = {}
        for child in doc['inherited_acceptances']:
            raw = (ROOT/child['path']).read_bytes()
            assert sha(raw) == child['sha256']
            child_doc = json.loads(raw)
            child_rows = {r['path']: r for r in child_doc['accepted_assets']}
            resolved = origins(child_doc, child['path'], (*stack, name))
            for p in child['asset_paths']:
                assert p not in inherited and rows[p] == child_rows[p]
                inherited[p] = resolved[p]
        new = set(doc['newly_accepted_assets'])
        assert not new & set(inherited) and new | set(inherited) == set(rows)
        return {**inherited, **{p: name for p in new}}
    resolved = origins(accepted, ledger['acceptance_record'])
    approved = {r['path']: r for r in accepted['accepted_assets']}
    packed = {r['path']: r for r in ledger['assets']}
    assert len(approved) == len(packed) == 43 and set(approved) == set(packed)
    with zipfile.ZipFile(ROOT/'assets/scrantic_data.zip') as z:
        assert len(z.namelist()) == len(set(z.namelist())) == 2594
        for p, row in packed.items():
            recipe = load(ROOT/row['recipe'])
            rs = {r['path']: r for r in recipe.get('frames', recipe.get('assets', []))}
            assert row['review'] == resolved[p] and row['recipe'] == approved[p]['recipe']
            assert row['sha256'] == approved[p]['sha256'] == rs[p]['candidate_png_sha256'] == sha(z.read('data/styles/cartoon/'+p))
            assert row['source_sha256'] == sha(z.read('data/hd/'+p))
    inputs = load(ROOT/'art/cartoon/skin-tone-v1/integration-v1/inputs.json')
    for name, digest in inputs['protected_files_sha256'].items():
        assert sha((ROOT/name).read_bytes()) == digest, name
    unchanged = git('diff', '--name-only', '3af0242', COMMIT, '--', 'src', 'platform', 'third_party', 'tools', 'tests', 'CMakeLists.txt', '.github').decode().splitlines()
    assert not unchanged
    checks = load(OUT/'checks.json')
    assert checks['status'] == 'PASS'
    closure = load(OUT/'restored-evidence-v2.json')
    assert closure['status'] == 'PASS'
    report = {'status': 'PASS_AFTER_RESTORATION_STAGED', 'commit': COMMIT, 'runner_sha256': sha(Path(__file__).read_bytes()),
              'checks_sha256': sha((OUT/'checks.json').read_bytes()), 'checkout_files': len(byte_rows),
              'checkout_bytes': sum(r['bytes'] for r in byte_rows.values()), 'frozen_checkout_mismatches': [],
              'authorized_unbound_current_doc_edits_during_audit': changed_docs,
              'durable_binders': closure['binder_count'], 'durable_reference_checks': closure['reference_checks'],
              'unique_referenced_paths_worktree_and_index': closure['unique_referenced_paths'],
              'restored_evidence_readback_sha256': sha((OUT/'restored-evidence-v2.json').read_bytes()),
              'initial_failure_report_sha256': sha((OUT/'missing-evidence-v1.json').read_bytes()),
              'source_fingerprints': len(source_rows), 'approval_recipe_source_member_bindings': 43,
              'production_archive_sha256': sha((ROOT/'assets/scrantic_data.zip').read_bytes()),
              'protected_integration_inputs': len(inputs['protected_files_sha256']),
              'runtime_platform_maintained_tool_test_build_ci_changes_from_baseline': unchanged,
              'findings': [{'status':'RESTORED_AND_STAGED_BY_PARENT',
                  'issue':'Three copied browser execution evidence records were absent from merged commit because their nested build directory was ignored.',
                  'runtime_impact':'None. Artwork, production ZIP, original evidence binder bytes and tests are unchanged.',
                  'affected_binder':'art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1/evidence.json',
                  'affected_paths':[r['path'] for r in closure['restored_after_merge']],
                  'resolution':'Parent copied original feature-worktree bytes and force-staged explicit files. All expected, feature-source, working and staged hashes match. Follow-up commit is pending.',
                  'backlog':'Add a copied-evidence completeness check against the Git index: recursively resolve durable binder destination members and require each staged blob to exist with its expected SHA256. Distinguish documented external/local-only inputs. A negative control must omit an ignored nested build member and name that missing path.'}],
              'review_scope': ['Fresh reading of maintained pack/catalog/pilot-history paths and test fixtures.',
                  'Fresh reading of selected v5 color adapter, combined integration helper, mutation witness path and replay instructions.',
                  'New-helper AST parsing and exact source fingerprints; not a claim that every duplicated historical helper was manually audited.',
                  'Image learnings retain original-first pose/placement, material calibration, mask/classification limits and separate human approval history.'],
              'limits': ['No new image generation, native capture, original-executable parity claim, or long raw-source replay.',
                  'Existing source mutation matrices were not repeated; regression suites include their normal negative-input cases.',
                  'Two inventory Windows symlink-privilege cases were explicitly skipped; hardlink cases ran.',
                  'Historical native review replay intentionally requires isolated pinned baseline inputs; published checkpoint writers must not be rerun.']}
    (OUT/'audit.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
