"""Adapt the preserved checked-publication helper for the new017 review slug."""
from pathlib import Path
import hashlib
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PRIOR = ROOT / 'art/cartoon/walk-pilot/front-refresh-v1/review-evidence/native-publication-v1/publish.py'


def main():
    target = OUT / 'publish.py'
    if target.exists():
        raise ValueError('preserve existing publication helper')
    text = PRIOR.read_text(encoding='utf-8')
    replacements = [
        ('ROOT = HERE.parents[5]', 'ROOT = HERE.parents[2]'),
        ("SOURCE = ROOT / 'build/front-native-review/island-review-v1'", "SOURCE = HERE / 'island-review-v1'"),
        ("FROZEN = HERE.parent / 'native-island-v1'", 'FROZEN = SOURCE'),
        ('front-refresh-island-v1', 'front-arrival017-v1'),
    ]
    for old, new in replacements:
        count = 2 if old == 'front-refresh-island-v1' else 1
        if text.count(old) != count:
            raise ValueError('unique publication adaptation anchor:' + old)
        text = text.replace(old, new)
    anchor = "    expected = {'review.html': record['html_sha256'], **record['image_files']}"
    additional = """    validation = json.loads((SOURCE / 'browser-validation.json').read_bytes())
    assert validation['html_sha256'] == record['html_sha256'], 'browser-tested-html-identity'
    assert validation['test_sha256'] == sha((HERE / 'check_review.py').read_bytes()), 'browser-checker-identity'
    assert validation['smoke_passed'] == 2 and len(validation['regressions']) == 4 and len(validation['mutations']) == 3, 'required-local-browser-validation'
    assert all(row['result'] == 'FIRED' and row['failure_count'] == 1 for row in validation['mutations']), 'executed-browser-mutations'
""" + anchor
    if text.count(anchor) != 1:
        raise ValueError('unique publication validation insertion')
    text = text.replace(anchor, additional)
    anchor = "        checks.append('fixed close-up preserves exact arrival pixels')"
    additional = """        page.locator('#arrival').click()
        state = page.evaluate('nativeReviewState')
        assert state['frame'] == 17 and state['position'] == 2760 and not state['playing'] and state['view'] == 'walk', 'published-show-arrival'
        page.locator('#prev').click()
        assert page.evaluate('nativeReviewState.frame') == 27, 'published-previous-last-step'
        page.locator('#next').click()
        assert page.evaluate('nativeReviewState.frame') == 17, 'published-next-arrival'
        page.locator('#replay').click()
        assert page.evaluate('nativeReviewState.index') == 0 and page.evaluate('nativeReviewState.playing'), 'published-replay'
        page.locator('#speed').select_option('0.5')
        page.evaluate('reviewCallback(0);reviewCallback(240)')
        assert page.evaluate('nativeReviewState.position') == 120, 'published-slow-speed'
        page.locator('#speed').select_option('1')
""" + anchor
    if text.count(anchor) != 1:
        raise ValueError('unique publication controls insertion')
    text = text.replace(anchor, additional)
    text = text.replace('r.left>=0&&r.right<=innerWidth&&Math.abs(r.width/c.width-r.height/c.height)<0.001', 'r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight&&Math.abs(r.width/c.width-r.height/c.height)<0.001')
    text = text.replace("'scope': 'Publication of previously captured native route; no additional human acceptance.'", "'scope': 'Publication of native current Cartoon walk and proposed017 comparison. Human approval pending; production archive unchanged.'")
    target.write_text(text, encoding='utf-8', newline='\n')
    record = {'source': PRIOR.relative_to(ROOT).as_posix(), 'source_sha256': hashlib.sha256(PRIOR.read_bytes()).hexdigest(),
              'output_sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'slug': 'front-arrival017-v1'}
    (OUT / 'publication-adaptation.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print('PASS publication helper prepared; nothing published yet')


if __name__ == '__main__':
    main()
