"""Check only the served v3 004 candidate and save its animation and still views."""
import hashlib
import json
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright


HERE = Path(__file__).resolve().parent
ANIMATION_URL = "http://127.0.0.1:8941/visitor-leg-pose-corrections-v2/color-sequence-review.html"
STILL_URL = "http://127.0.0.1:8941/mermaid-expression-corrections-v1/review.html#frame-SSUZY1.BMP-004"


def main():
    record = json.loads((HERE / "record.json").read_text(encoding="utf-8-sig"))
    expected = record["output"]["sha256"]
    page_errors, console_errors = [], []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1120}, device_scale_factor=1)

        def observe(page):
            page.on("pageerror", lambda error: page_errors.append(str(error)))
            page.on("console", lambda message: console_errors.append({"text": message.text, "location": message.location}) if message.type == "error" else None)

        page = context.new_page()
        observe(page)
        page.goto(ANIMATION_URL, wait_until="domcontentloaded")
        page.wait_for_function("!document.getElementById('play').disabled", timeout=30000)
        candidate = page.evaluate("data.sprites['4'].candidate")
        assert candidate["version"] == 3 and candidate["sha256"] == expected
        assert candidate["path"] == record["output"]["path"]
        assert page.locator("#frameLabel").inner_text() == "SSUZY1.BMP 004"
        assert page.locator("#framePending").inner_text() == "Direct composite v3: belly contour awaiting review"
        href = page.locator("#cartoonMeta a").get_attribute("href")
        assert href == candidate["url"]
        response = context.request.get(urljoin(ANIMATION_URL, href))
        assert response.status == 200 and hashlib.sha256(response.body()).hexdigest() == expected
        page.screenshot(path=str(HERE / "animation-review-004.png"))

        still = context.new_page()
        observe(still)
        still.goto(STILL_URL, wait_until="domcontentloaded")
        card = still.locator("[id='frame-SSUZY1.BMP-004']")
        card.locator('canvas[data-kind="revised"][data-loaded="true"]').wait_for(timeout=30000)
        row = still.evaluate("data.assets.find(row => row.key === 'SSUZY1.BMP-004')")
        assert row["candidate_version"] == 3 and row["images"]["revised"]["sha256"] == expected
        assert row["correction"] == record["requested_change"]
        assert row["appearance_approval"] is None and row["production_integrated"] is False
        card.screenshot(path=str(HERE / "still-review-004.png"))
        report = {
            "animation_url": ANIMATION_URL, "still_url": STILL_URL,
            "candidate_004_url": urljoin(ANIMATION_URL, href), "candidate_004_sha256": expected,
            "candidate_version": 3, "review_status": "belly contour awaiting review",
            "still_correction": row["correction"], "appearance_approval": None,
            "production_integrated": False, "page_errors": page_errors, "console_errors": console_errors,
            "screenshots": ["animation-review-004.png", "still-review-004.png"],
        }
        (HERE / "browser-review.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        assert not page_errors, page_errors
        print(json.dumps(report))
        browser.close()


if __name__ == "__main__":
    main()
