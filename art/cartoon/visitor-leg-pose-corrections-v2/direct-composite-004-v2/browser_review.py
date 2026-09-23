"""Exercise the served 004 composite review and save browser evidence."""
import hashlib
import json
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright


HERE = Path(__file__).resolve().parent
BASE = "http://127.0.0.1:8941/"
ANIMATION_URL = BASE + "visitor-leg-pose-corrections-v2/color-sequence-review.html"
STILL_URL = BASE + "mermaid-expression-corrections-v1/review.html#frame-SSUZY1.BMP-004"
EXPECTED_004 = "2d6a7257197339e2d000cc6ed1862d190ba2186434e329c725b4c0c9d59d6bfd"
EXPECTED_005 = "beeebb3388ba6ab44fc52fbd824aac464158570f6bb0e4d71e0e675b1199b5de"


def main():
    page_errors, console_errors, http_errors, launch_errors = [], [], [], []
    with sync_playwright() as playwright:
        browser = None
        for channel in ("chrome", "msedge", None):
            try:
                browser = playwright.chromium.launch(headless=True, **({"channel": channel} if channel else {}))
                browser_channel = channel or "bundled chromium"
                break
            except Exception as error:
                launch_errors.append({"channel": channel, "error": str(error)})
        if browser is None:
            raise RuntimeError(json.dumps(launch_errors))
        context = browser.new_context(viewport={"width": 1440, "height": 1120}, device_scale_factor=1)

        def observe(page):
            page.on("pageerror", lambda error: page_errors.append(str(error)))
            page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
            page.on("response", lambda response: http_errors.append({"url": response.url, "status": response.status}) if response.status >= 400 else None)

        page = context.new_page()
        observe(page)
        page.goto(ANIMATION_URL, wait_until="domcontentloaded")
        page.wait_for_function("!document.getElementById('play').disabled", timeout=30000)
        sequence = page.evaluate("data")
        assert len(sequence["steps"]) == 26 and sequence["nominal_excerpt_ms"] == 5840
        assert sequence["sprites"]["4"]["candidate"]["sha256"] == EXPECTED_004
        assert sequence["sprites"]["5"]["candidate"]["sha256"] == EXPECTED_005
        assert "ground_bottle" not in sequence
        assert page.locator("#frameLabel").inner_text() == "SSUZY1.BMP 004"
        assert "Direct composite" in page.locator("#framePending").inner_text()
        candidate_href = page.locator("#cartoonMeta a").get_attribute("href")
        assert candidate_href == sequence["sprites"]["4"]["candidate"]["url"]
        response = context.request.get(urljoin(ANIMATION_URL, candidate_href))
        assert response.status == 200 and hashlib.sha256(response.body()).hexdigest() == EXPECTED_004
        page.screenshot(path=str(HERE / "animation-review-004.png"))

        page.locator("#drawingMode").select_option("selected")
        selected_href = page.locator("#cartoonMeta a").get_attribute("href")
        assert selected_href == sequence["sprites"]["4"]["cartoon"]["url"]
        assert "imported-004-v1/004-transparent-v1.png" in selected_href
        assert page.locator("#framePending").inner_text() == "Approved imported selection"
        page.locator("#drawingMode").select_option("candidate")
        assert page.locator("#cartoonMeta a").get_attribute("href") == candidate_href

        page.locator("#jump5").click()
        assert page.locator("#frameLabel").inner_text() == "SSUZY1.BMP 005"
        frame_005_href = page.locator("#cartoonMeta a").get_attribute("href")
        assert frame_005_href == sequence["sprites"]["5"]["candidate"]["url"]
        assert "Regenerated color candidate" in page.locator("#framePending").inner_text()
        response = context.request.get(urljoin(ANIMATION_URL, frame_005_href))
        assert response.status == 200 and hashlib.sha256(response.body()).hexdigest() == EXPECTED_005
        page.locator("#prev").click()
        assert page.locator("#frameLabel").inner_text() == "SSUZY1.BMP 004"
        page.locator("#next").click()
        assert page.locator("#frameLabel").inner_text() == "SSUZY1.BMP 005"
        page.locator("#jump4").click()
        page.locator("#play").click()
        page.wait_for_function("cursor >= 6", timeout=5000)
        page.locator("#play").click()
        assert page.locator("#play").inner_text() == "Play"
        playback_cursor = page.evaluate("cursor")
        page.locator("#jump4").click()
        assert page.locator("#error").inner_text() == ""

        still = context.new_page()
        observe(still)
        still.goto(STILL_URL, wait_until="domcontentloaded")
        still.wait_for_function("document.getElementById('loading').dataset.complete === 'true'", timeout=30000)
        loading_status = still.locator("#loading").inner_text()
        assert loading_status == "263 image panels loaded, no load errors."
        row = still.evaluate("data.assets.find(row => row.key === 'SSUZY1.BMP-004')")
        assert row["candidate_kind"] == "direct-png-composite"
        assert row["images"]["revised"]["sha256"] == EXPECTED_004
        assert row["appearance_approval"] is None
        assert row["production_integrated"] is False and row["native_motion_checked"] is False
        assert row["generation_record"] is None
        assert row["candidate_record"]["path"].endswith("direct-composite-004-v2/record.json")
        card = still.locator("#frame-SSUZY1\\.BMP-004")
        assert "Direct composite v2: awaiting appearance review" in card.locator(".state").inner_text()
        assert card.locator('canvas[data-kind="revised"]').get_attribute("data-loaded") == "true"
        card.screenshot(path=str(HERE / "still-review-004.png"))

        report = {
            "animation_url": ANIMATION_URL, "still_url": STILL_URL,
            "browser_channel": browser_channel, "browser_version": browser.version,
            "candidate_004_url": urljoin(ANIMATION_URL, candidate_href), "candidate_004_sha256": EXPECTED_004,
            "selected_004_url": urljoin(ANIMATION_URL, selected_href), "selected_toggle_checked": True,
            "candidate_005_url": urljoin(ANIMATION_URL, frame_005_href), "candidate_005_sha256": EXPECTED_005,
            "frame_005_unchanged": True, "previous_next_checked": True, "playback_reached_cursor": playback_cursor,
            "steps": 26, "duration_ms": 5840, "ground_bottle_added": False,
            "still_loading_status": loading_status, "still_candidate_kind": row["candidate_kind"],
            "appearance_approval": None, "production_integrated": False, "native_motion_checked": False,
            "page_errors": page_errors, "console_errors": console_errors, "http_errors": http_errors,
            "launch_errors": launch_errors,
            "screenshots": ["animation-review-004.png", "still-review-004.png"],
        }
        (HERE / "browser-review.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        assert not page_errors, page_errors
        assert not http_errors, http_errors
        print(json.dumps(report))
        browser.close()


if __name__ == "__main__":
    main()
