"""One-off immutable publication and served-page verification for motion-v1."""
import hashlib
import json
from pathlib import Path
import urllib.request

from playwright.sync_api import sync_playwright

SOURCE = Path("art/cartoon/walk-pilot/front-refresh-v1/review-evidence/motion-v1").resolve()
DEST = Path("D:/.ai-work/worktrees/johnny-art-metadata/build/art-review/front-refresh-motion-v1")
URL = "http://127.0.0.1:8932/front-refresh-motion-v1/"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    evidence = json.loads((SOURCE / "review-record.json").read_bytes())
    assert not DEST.exists(), "preserve-prior-published-review"
    files = {name: (SOURCE / name).read_bytes() for name in evidence["files"]}
    assert all(sha(raw) == evidence["files"][name] for name, raw in files.items()), "source-review-identities"
    DEST.mkdir()
    for name, raw in files.items():
        target = DEST / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    served = {}
    for name, raw in files.items():
        with urllib.request.urlopen(URL + name, timeout=10) as response:
            actual = response.read()
        assert actual == raw, "served-byte-identity:" + name
        served[name] = sha(actual)
    print("PASS served-byte smoke: 20 exact HTML/data/image files", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.add_init_script("window.__frames=[];window.requestAnimationFrame=cb=>window.__frames.push(cb);window.__step=t=>{const q=window.__frames.splice(0);q.forEach(cb=>cb(t));};")
            page.goto(URL + "review.html")
            page.wait_for_function("window.frontReviewState && frontReviewState.ready")
            assert page.evaluate("frontReviewState.frame") == 28
            assert not errors
            print("PASS served browser smoke: ready at original route's028", flush=True)
            page.locator("#play").click()
            states = []
            for index in range(24):
                state = page.evaluate("frontReviewState")
                assert state["index"] == index
                changed = page.evaluate("""()=>{const read=id=>{const c=document.getElementById(id);return c.getContext('2d').getImageData(0,0,c.width,c.height).data;};const a=read('current'),b=read('revised');let n=0;for(let i=0;i<a.length;i++)if(a[i]!==b[i])n++;return n;}""")
                assert (changed == 0) == (state["frame"] not in (28, 29)), "intended-frame-differences"
                states.append({"index": index, "frame": state["frame"], "hold": state["hold"], "changed_rgba_channels": changed})
                if index < 23:
                    page.locator("#next").click()
            assert "Diagnostic endpoint hold" in page.locator("#status").inner_text()
            page.locator("#next").click()
            page.locator("#play").click()
            page.evaluate("window.__step(0);window.__step(121)")
            assert page.evaluate("frontReviewState.index") == 1, "normal-cadence"
            page.locator("#play").click()
            page.evaluate("window.__step(500);window.__step(1000)")
            assert page.evaluate("frontReviewState.index") == 1, "pause"
            page.locator("#previous").click()
            assert page.evaluate("frontReviewState.index") == 0, "previous"
            page.locator("#speed").select_option("0.5")
            page.locator("#play").click()
            page.evaluate("window.__step(2000);window.__step(2180)")
            assert page.evaluate("frontReviewState.index") == 0, "slow-first-half"
            page.evaluate("window.__step(2250)")
            assert page.evaluate("frontReviewState.index") == 1, "slow-advance"
            page.locator("#repeat").uncheck()
            page.evaluate("window.__step(20000)")
            assert page.evaluate("frontReviewState.hold && !frontReviewState.playing"), "stop-at-hold"
            page.locator("#repeat").check()
            page.locator("#next").click()
            page.locator("#speed").select_option("1")
            page.locator("#play").click()
            page.evaluate("window.__step(30000);window.__step(33761)")
            assert page.evaluate("frontReviewState.index===0 && frontReviewState.playing && Math.abs(frontReviewState.position-1)<0.01"), "repeat-wrap"
            panels = page.locator(".panels canvas").evaluate_all("cs=>cs.map(c=>{const r=c.getBoundingClientRect();return {width:r.width,height:r.height,right:r.right,bottom:r.bottom};})")
            assert all(row["right"] <= 1280 and row["bottom"] <= 900 for row in panels), "1280x900-layout"
            assert not errors
        finally:
            browser.close()
    report = {"status": "PASS", "url": URL + "review.html", "smoke_before_regression": True,
              "served_files_sha256": served, "browser_states": states,
              "controls": ["normal-120ms", "pause", "previous-next", "slow-half-speed", "diagnostic-hold", "repeat-off-stop", "repeat-on-wrap"],
              "viewport": [1280, 900], "panels": panels, "javascript_errors": errors,
              "source_script_sha256": sha(Path(__file__).read_bytes()),
              "scope": "Published standalone composition only; no production pack mutation, human approval, or native capture."}
    (SOURCE / "served-review-verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("PASS served regressions: 24 states, intended pixel changes, timing/controls/repeat/layout; " + URL + "review.html", flush=True)


if __name__ == "__main__":
    main()
