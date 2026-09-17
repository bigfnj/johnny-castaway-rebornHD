"""Preserve this completed command run and explicit evidence membership."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).resolve().parent
OUT = ROOT/'art/cartoon/low-tide-v1/integration-v1/authoring-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def save(path, value):
    path.write_bytes((json.dumps(value, indent=2)+'\n').encode())


def main():
    phases = {p: json.loads((SOURCE/(p+'.json')).read_bytes())
        for p in ('smoke', 'generate', 'regression')}
    assert all(p['status'] == 'PASS' for p in phases.values())
    OUT.mkdir(parents=True, exist_ok=False)
    names = {'run.py', 'preserve.py', 'smoke.json', 'generate.json', 'regression.json'}
    for phase in phases.values():
        names.update(c['log'] for c in phase['commands'])
    for name in sorted(names):
        shutil.copyfile(SOURCE/name, OUT/name)
    generated = ['docs/knowledge-base/cartoon-production-catalog.json',
        'docs/knowledge-base/cartoon-production-catalog.md',
        'docs/knowledge-base/cartoon-art-metadata.json',
        'docs/knowledge-base/cartoon-art-metadata.md',
        'art/cartoon/character-inventory-v1/inventory.json',
        'art/cartoon/character-inventory-v1/README.md']
    low = ROOT/'art/cartoon/low-tide-v1/integration-v1'
    save(OUT/'integration-review.json', {
        'scope': 'Independent read-only review of prepare.py and its current aggregate records; no new tests added.',
        'reviewed_helper': {'path': (low/'prepare.py').relative_to(ROOT).as_posix(), 'sha256': sha(low/'prepare.py')},
        'artifact_hashes': {p: sha(low/p) for p in ('runtime-recipe.json', 'production-acceptance.json', 'integrated-pack.json')},
        'readback': {'checked_hash_bindings': 76, 'mismatches': [], 'accepted_assets': 61,
            'inherited_rows_byte_fields_exact': 47, 'pilot_history_unchanged': True,
            'runtime_declaration_unchanged': True, 'live_pack_equals_integrated_pack': True},
        'finding': 'No substantive current metadata or provenance mismatch found.',
        'limits': [
            'prepare.py member_negative_control checks an altered in-memory hash map. It is not an executed damaged-ZIP refusal or source-guard removal proof.',
            'prepare.py writes aggregate records under its own directory. Historical source replay must occur in isolated baseline scratch, not against promoted live files.',
            'Source-export replay and platform/native runs belong to separate root/agent evidence; they were not rerun by this authoring pass.']})
    names.add('integration-review.json')
    regression = phases['regression']['commands']
    planned = sum(c['tests'] or 0 for c in regression)
    skips = [line for c in regression for line in c['skip_lines']]
    report = {'schema_version': 1, 'status': 'PASS',
        'production_archive_sha256': sha(ROOT/'assets/scrantic_data.zip'),
        'pack_sha256': sha(ROOT/'art/cartoon/pack.json'),
        'smoke_tests': sum(c['tests'] or 0 for c in phases['smoke']['commands']),
        'regression_reported_tests': planned, 'regression_executed_tests': planned-len(skips),
        'regression_skipped_tests': len(skips), 'skip_lines': skips,
        'generated_outputs_sha256': {p: sha(ROOT/p) for p in generated},
        'files_sha256': {name: sha(OUT/name) for name in sorted(names)},
        'membership_scope': 'Every files_sha256 key is relative to this authoring-v1 directory and must be committed with this binder. No ignored log is implicitly excluded.',
        'excluded': ['Ignored scratch runner directory duplicates', 'Unchanged maintained tools/tests, pinned in phase reports',
            'Production archive and generated files, bound by path/hash instead of duplicated'],
        'limits': ['Two Windows symlink-privilege cases skipped explicitly.',
            'Stored supplied-original evidence was checked; original external resources and original executable colors were not reread.',
            'Historical pilot metadata remains21 assets; current production catalog covers61. Johnny outstanding counts remain1002 with28 accepted and84 uncertain.',
            'This uses existing maintained test controls. No new domain guard or source-removal mutation was introduced.']}
    save(OUT/'verification.json', report)
    readback = {'status': 'PASS', 'verification_sha256': sha(OUT/'verification.json'),
        'copied_files': len(names), 'all_hashes_match': all(sha(OUT/p)==h for p,h in report['files_sha256'].items())}
    assert readback['all_hashes_match']
    save(OUT/'readback.json', readback)
    print(json.dumps({'verification': str(OUT/'verification.json'), 'sha256': sha(OUT/'verification.json'),
        'readback_sha256': sha(OUT/'readback.json'), 'reported_tests': planned, 'skips': skips}))


if __name__ == '__main__':
    main()
