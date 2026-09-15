"""Bind the complete unpublished native review without rewriting prior evidence."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    names = ['prepare.py', 'capture.py', 'route_driver.c', 'preparation.json', 'finish.py', 'evidence.json',
             'prepare_candidate.py', 'capture_candidate.py', 'check_candidate_guards.py', 'build_review.py',
             'check_review.py', 'README.md', 'baseline-v1/build.json', 'baseline-v1/route-contract.json',
             'baseline-v1/summary.json', 'candidate-v1/preparation.json', 'candidate-v1/recipe.json',
             'candidate-v1/export-report.json', 'candidate-v1/summary.json',
             'candidate-v1/mask-guard-verification.json', 'island-review-v1/review.html',
             'island-review-v1/review-record.json', 'island-review-v1/browser-validation.json']
    names += [f'baseline-v1/{phase}/report.json' for phase in ('smoke', 'full', 'repeat')]
    names += [f'candidate-v1/{phase}/report.json' for phase in ('smoke', 'full')]
    report = {'status': 'technical review passed; unpublished; awaiting separate human review',
              'files_sha256': {name: sha((OUT / name).read_bytes()) for name in names},
              'scope': 'No production changes or human approval assigned. Detailed byte and runtime identities are in bound reports.'}
    target = OUT / 'native-review-evidence.json'
    if target.exists():
        raise ValueError('preserve previous completed review evidence')
    target.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'PASS', 'files_bound': len(names), 'manifest_sha256': sha(target.read_bytes())}))


if __name__ == '__main__':
    main()
