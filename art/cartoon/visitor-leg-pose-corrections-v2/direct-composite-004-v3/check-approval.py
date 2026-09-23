"""Verify only the served scoped 004 approval."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
EXPECTED = "d53304f654f59676097bbbb15add2d54e8f503cd173511e59475c5cf5d2c957d"
errors = []
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page()
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto("http://127.0.0.1:8941/visitor-leg-pose-corrections-v2/color-sequence-review.html")
    page.wait_for_function("!document.getElementById('play').disabled", timeout=15000)
    label = page.locator("#framePending").inner_text()
    assert label == "Direct composite v3: appearance approved by user"
    data = page.evaluate("data")
    assert data["sprites"]["4"]["cartoon"]["sha256"] == EXPECTED
    assert data["sprites"]["4"]["candidate"]["appearance_approval"]["output"]["sha256"] == EXPECTED
    assert data["sprites"]["5"]["candidate"]["appearance_approval"] is None
    page.locator("#drawingMode").select_option("selected")
    assert "direct-composite-004-v3/004-composite-v3.png" in page.locator("#cartoonMeta a").get_attribute("href")
    page.goto("http://127.0.0.1:8941/mermaid-expression-corrections-v1/review.html#frame-SSUZY1.BMP-004")
    row = page.evaluate("data.assets.find(row=>row.key==='SSUZY1.BMP-004')")
    assert row["status"] == "approved_by_user" and row["appearance_approval"]["output"]["sha256"] == EXPECTED
    assert row["production_integrated"] is False and row["native_motion_checked"] is False
    assert page.evaluate("data.assets.find(row=>row.key==='SSUZY1.BMP-005').appearance_approval") is None
    still_label = page.locator("[id='frame-SSUZY1.BMP-004'] .state").inner_text()
    assert still_label == "Direct composite v3: appearance approved by user"
    assert not errors, errors
    report = {"animation_label": label, "still_label": still_label, "approved_sha256": EXPECTED,
              "selected_mode_uses_approved_004": True, "005_candidate_unapproved": True,
              "production_integrated": False, "native_motion_checked": False, "page_errors": errors}
    (HERE / "approval-browser-review.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    browser.close()
