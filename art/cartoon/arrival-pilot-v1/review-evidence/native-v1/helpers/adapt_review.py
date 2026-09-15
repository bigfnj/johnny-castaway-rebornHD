"""Derive an arrival-only viewer from the preserved, previously checked native viewer."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
OLD = ROOT / 'art/cartoon/walk-expansion-v1/review-evidence/island-v1/helpers'


def replace_once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def main():
    viewer = (OLD / 'build_review.py').read_text(encoding='utf-8')
    viewer = viewer.replace('from run_baseline import', 'from capture_format import')
    viewer = replace_once(viewer, "HERE / 'baseline-v2/full'", "HERE / 'baseline/full'")
    viewer = viewer.replace("Johnny's new walk on the island", "Johnny's new arrival pose")
    viewer = replace_once(viewer, 'Current HD walk on the left, Cartoon candidate on the right. Watch the steps and the arrival.',
                          'Watch the same Cartoon walk settle into the arrival pose. The new standing artwork is on the right.')
    viewer = replace_once(viewer, '<h2>Current HD walk</h2>', '<h2>Current arrival</h2>')
    viewer = replace_once(viewer, '<h2>Cartoon candidate</h2>', '<h2>New Cartoon arrival</h2>')
    viewer = replace_once(viewer, '<p>The final standing pose still uses the existing HD artwork in both views.</p>',
                          '<p>Only the standing pose is new. Use Previous pose and Next pose to check the last step into the arrival.</p>')
    viewer = replace_once(viewer,
        'Both views use the current Cartoon island. The baseline uses the packaged HD walking sprites, not original-executable captures or the decoded supplied-original sprites. These are paired native Linux captures from the same saved executable and the same unmodified B-to-A route. The candidate archive adds six sprites; every prior archive member remains unchanged. The recorded timing includes background updates and the 1.6-second arrival hold. It does not establish original executable rendering or wall-clock speed.',
        'Both views use the approved Cartoon island and rear walk. The left arrival uses packaged HD frame 018; only the right arrival uses new Cartoon frame 018. These are paired native Linux captures from the same saved executable and unmodified B-to-A route. The private candidate adds one sprite and preserves every production member. The script moves the sprite origin from (302,244) on the last walking pose to (298,240) on arrival; the review preserves that shift. Recorded timing includes background updates and the 1.6-second arrival hold. This does not establish original executable rendering or physical wall-clock speed. No turn has been appended.')
    viewer = replace_once(viewer, 'row.draw_xy[0]*2-100,row.draw_xy[1]*2-40,400,280', '580,440,400,280')
    target = OUT / 'build_review.py'
    assert not target.exists(), 'preserve-existing-viewer-source'
    target.write_text(viewer, encoding='utf-8', newline='\n')
    test = (OLD / 'check_review.py').read_text(encoding='utf-8')
    # The first 23 walking poses must now match, so the wrong-side pixel mutation
    # must execute a real arrival state where the two recorded images differ.
    test = replace_once(test,
        "failed = page.evaluate(HASH_CANVAS, 'candidate') != expected[data['frames'][0]['candidate']]",
        "arrival = next(i for i, row in enumerate(data['frames']) if row['frame'] == 18)\n                page.evaluate('i=>select(i)', arrival)\n                failed = page.evaluate(HASH_CANVAS, 'candidate') != expected[data['frames'][arrival]['candidate']]")
    test = replace_once(test, "checks.append('close-up/full-island controls and recorded-route repeat')",
        "page.evaluate('select(0);play(false)')\n        for _ in range(22): page.locator('#next').click()\n        assert page.evaluate('nativeReviewState.frame') == 22\n        page.locator('#next').click()\n        assert page.evaluate('nativeReviewState.frame') == 18\n        page.locator('#prev').click()\n        assert page.evaluate('nativeReviewState.frame') == 22\n        checks.append('close-up/full-island controls, last-walk-to-arrival stepping and recorded-route repeat')")
    test = replace_once(test, "x, y = row['draw_xy'][0] * 2 - 100, row['draw_xy'][1] * 2 - 40", 'x, y = 580, 440')
    target = OUT / 'check_review.py'
    assert not target.exists(), 'preserve-existing-viewer-test'
    target.write_text(test, encoding='utf-8', newline='\n')
    print('Prepared versioned arrival viewer and focused browser checks')


if __name__ == '__main__':
    main()
