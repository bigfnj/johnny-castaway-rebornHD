"""Prepare a two-panel017 reviewer by adapting preserved native review helpers."""
from pathlib import Path
import hashlib
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PRIOR = ROOT / 'art/cartoon/walk-pilot/front-refresh-v1/review-evidence/native-island-v1/helpers'


def change(text, old, new, count=1):
    if text.count(old) != count:
        raise ValueError('unique review adaptation anchor:' + old)
    return text.replace(old, new)


def main():
    for name in ('build_review.py', 'check_review.py', 'review-adaptation.json'):
        if (OUT / name).exists():
            raise ValueError('preserve existing reviewer:' + name)
    text = (PRIOR / 'build_review.py').read_text(encoding='utf-8')
    text = change(text, 'ROOT = OUT.parents[1]', 'ROOT = OUT.parents[2]')
    text = change(text, "assert left['executable_sha256'] == right['executable_sha256'] and right['status'] == 'PASS'", "assert left['executable_sha256'] == right['executable_sha256'] and right['status'] == 'PASS' and right['control'] is False")
    text = change(text, 'Johnny\'s front walk refresh', 'Johnny\'s front arrival pose')
    text = change(text, 'Watch the current Cartoon front walk beside the proposed refresh. The new footwork is on the right.', 'Watch the approved Cartoon walk settle into the new standing pose on the right. Use Show arrival for a closer look.')
    text = change(text, "('Current arrival', 'Current Cartoon', 1)", "('Current arrival', 'Current Cartoon walk + HD standing017', 1)")
    text = change(text, "('New Cartoon arrival', 'Provisional front walk', 1)", "('New Cartoon arrival', 'Same walk + new Cartoon017', 1)")
    text = change(text, 'Only walking frames 028 and 029 are revised. Watch the whole gait at Normal speed, then use the pose controls to inspect individual steps. The standing arrival is unchanged HD artwork.', 'Only standing017 is new. All walking artwork is unchanged. Watch at Normal speed, then use Previous pose and Next pose to judge the last step into the arrival.')
    text = change(text, "row.frame===data.arrival_frame?'Arrival pose (existing HD)':`Walking pose ${row.pose_index+1} / ${data.travel_pose_count}`", "row.frame===data.arrival_frame?'Arrival pose · JOHNWALK.BMP 017':`Walking pose ${row.pose_index+1} / ${data.travel_pose_count} · JOHNWALK.BMP ${String(row.frame).padStart(3,'0')}`")
    text = change(text, 'Both panels use the approved Cartoon island and the same actual E-to-A route. The private candidate replaces only frames 028 and 029; frames 024-027 remain byte-identical. The last walking frame 027 is drawn at (300,242), then the existing mirrored HD017 arrival at (293,243) holds for 1.6 seconds. All timing, draw positions and background updates come from the same native Linux observer. This is port rendering and logical timing, not an original-executable or physical wall-clock comparison.', 'Both panels use the approved Cartoon island and all six approved front-walk frames on the same actual E-to-A route. Only the right standing017 is new. The private candidate adds one Cartoon017 sprite while preserving all 2579 production members. The last walking frame027 is drawn at (300,242), then the mirrored017 arrival at (293,243) holds for 1.6 seconds. All timing, draw positions and background updates come from the same native Linux observer. This is port rendering and logical timing, not an original-executable or physical wall-clock comparison. No turn has been appended.')
    anchor = "    page = page.replace('__DATA__', json.dumps(data, separators=(',', ':')))"
    addition = """    page = page.replace('<button id="next">Next pose</button>', '<button id="next">Next pose</button><button id="arrival">Show arrival</button><button id="replay">Replay walk</button>')
    page = page.replace("$('play').onclick=()=>play(!playing);", "$('arrival').onclick=()=>{play(false);$('view').value='walk';select(data.frames.findIndex(row=>row.frame===data.arrival_frame));};$('replay').onclick=()=>{select(0);play(true);};$('play').onclick=()=>play(!playing);")
""" + anchor
    text = change(text, anchor, addition)
    start = text.index("    checker = (PRIOR / 'check_review.py')")
    end = text.index("    print(f'PASS unpublished front native review:", start)
    text = text[:start] + text[end:]
    (OUT / 'build_review.py').write_text(text, encoding='utf-8', newline='\n')

    checker = (PRIOR / 'check_review.py').read_text(encoding='utf-8')
    checker = change(checker, "row['frame'] == 28", "row['frame'] == 17")
    anchor = "        checks.append('close-up/full-island controls, last-walk-to-arrival stepping and recorded-route repeat')"
    addition = """        page.locator('#arrival').click()
        state = page.evaluate('nativeReviewState')
        assert state['frame'] == 17 and state['position'] == 2760 and not state['playing'] and state['view'] == 'walk', 'show-arrival-target-and-pause'
        assert page.locator('#candidate').evaluate('c=>[c.width,c.height]') == [400, 280]
        page.locator('#replay').click()
        assert page.evaluate('nativeReviewState.index') == 0 and page.evaluate('nativeReviewState.playing'), 'replay-resets-walk'
        page.locator('#speed').select_option('0.5')
        page.evaluate('reviewCallback(0);reviewCallback(240)')
        assert page.evaluate('nativeReviewState.index') == 1 and page.evaluate('nativeReviewState.position') == 120, 'slow-speed-exact-cadence'
        page.locator('#speed').select_option('1')
        page.locator('#replay').click()
        page.evaluate('reviewCallback(0);reviewCallback(120)')
        assert page.evaluate('nativeReviewState.index') == 1 and page.evaluate('nativeReviewState.position') == 120, 'normal-speed-exact-cadence'
        page.evaluate('play(false)')
        page.locator('#view').select_option('island')
""" + anchor
    checker = change(checker, anchor, addition)
    checker = change(checker, "page.set_viewport_size({'width': width, 'height': 1100})", "page.set_viewport_size({'width': width, 'height': 900})")
    checker = change(checker, "r.left>=0&&r.right<=innerWidth&&Math.abs(r.width/c.width-r.height/c.height)<0.001", "r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight&&Math.abs(r.width/c.width-r.height/c.height)<0.001")
    anchor = "        browser.close()"
    addition = """        text = raw.decode()
        old = 'select(data.frames.findIndex(row=>row.frame===data.arrival_frame))'
        assert text.count(old) == 1
        changed = text.replace(old, 'select(0)')
        mutant = args.review / 'arrival-control-mutant.html'
        mutant.write_text(changed, encoding='utf-8', newline='\\n')
        page = browser.new_page()
        response = page.goto(base_url + mutant.name)
        assert response.body() == mutant.read_bytes(), 'served-arrival-mutant-byte-identity'
        script = re.findall(r'<script>(.*?)</script>', changed, re.S)[-1]
        assert sha(page.locator('script').last.text_content().encode()) == sha(script.encode()), 'loaded-arrival-mutant-script-identity'
        page.wait_for_function('window.nativeReviewState&&nativeReviewState.ready')
        page.locator('#arrival').click()
        assert page.evaluate('nativeReviewState.frame') != 17, 'show-arrival mutant survived'
        mutations.append({'label': 'review.html:show-arrival-target', 'result': 'FIRED', 'failure_count': 1,
                          'html_sha256': sha(mutant.read_bytes()), 'witness': 'Exact served bytes and loaded script executed; Show arrival selected walking028 and failed the017 target oracle.'})
        page.close()
""" + anchor
    checker = change(checker, anchor, addition)
    (OUT / 'check_review.py').write_text(checker, encoding='utf-8', newline='\n')
    manifest = {'scope': 'Native017 viewer helper adaptations; no candidate artwork or human approval.',
                'source_helper_sha256': {name: hashlib.sha256((PRIOR / name).read_bytes()).hexdigest() for name in ('build_review.py', 'check_review.py')},
                'output_helper_sha256': {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in ('build_review.py', 'check_review.py')}}
    (OUT / 'review-adaptation.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print('PASS two-panel017 native viewer and controls checker prepared')


if __name__ == '__main__':
    main()
