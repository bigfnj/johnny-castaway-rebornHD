"""Check the requested review rows and their current-view links in Chrome."""
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE=Path(__file__).resolve().parent
BASE="http://127.0.0.1:8941/"
EXPECTED_004="a931a3974ea04b86665b9efbaf7f6104ce7271b1fd6b255d15600d7fd6058344"
APPROVED_004="d53304f654f59676097bbbb15add2d54e8f503cd173511e59475c5cf5d2c957d"
EXPECTED_005="ce4cd909762c0236e08f49b2c194e2891b3cfc538915a0682cc6dc3c28401597"

def main():
    errors=[]
    manifest=json.loads((HERE/"glimse/manifest.json").read_text(encoding="utf-8-sig"))
    retry=next(row for row in manifest["entries"] if row["frame"]=="013")
    raw_output=retry.get("output")
    retry_output=raw_output["path"] if isinstance(raw_output,dict) else raw_output
    expected_retry_hash=hashlib.sha256((HERE.parents[2]/retry_output).read_bytes()).hexdigest() if retry_output else None
    assert retry_output == "art/cartoon/review-corrections-2026-09-22/glimse/013-candidate-v5.png"
    assert expected_retry_hash == "93169db219cdc814b368a06b0693419e2ef71d962e3cc7bee99436fcedbfdaed"
    expected_counts={"approved_by_user":12,"selected_by_user":1}
    loaded_panels=39
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(channel="chrome",headless=True)
        page=browser.new_page(viewport={"width":1440,"height":1120})
        page.on("pageerror",lambda error:errors.append(str(error)))
        page.goto(BASE+"review-corrections-2026-09-22/review.html")
        page.wait_for_function("document.getElementById('loading').dataset.complete==='true'",timeout=30000)
        focused=page.evaluate("data")
        rows={row["key"]:row for row in focused["entries"]}
        assert focused["counts"]==expected_counts
        assert page.locator("article").count()==13
        assert page.locator('canvas[data-loaded="false"]').count()==0
        assert page.locator('canvas[data-loaded="true"]').count()==loaded_panels
        assert rows["SSUZY1.BMP-004"]["output"]["sha256"]==EXPECTED_004
        assert rows["SSUZY1.BMP-004"]["previous"]["sha256"]==APPROVED_004
        assert rows["SSUZY1.BMP-005"]["output"]["sha256"]==EXPECTED_005
        if retry_output:
            assert rows["SMGLIMSE.BMP-013"]["output"]["sha256"]==expected_retry_hash
        else:
            assert rows["SMGLIMSE.BMP-013"]["output"] is None
        assert rows["SMGLIMSE.BMP-014"]["status"]=="approved_by_user"
        assert page.locator("[id='frame-SMGLIMSE.BMP-014'] .state").inner_text()=="Appearance approved by you"
        assert all(row["appearance_approval"] for row in rows.values() if row["status"]=="approved_by_user")
        assert rows["SMGLIMSE.BMP-013"]["status"]=="approved_by_user"
        assert rows["SMGLIMSE.BMP-013"]["appearance_approval"]["output"]["sha256"]==expected_retry_hash
        assert rows["SMGLIMSE.BMP-014"]["appearance_approval"]["output"]["sha256"]=="4b6db9d40db5caf30289da8f5e2448f0b0fcb3fec7c8f87e0f1f7dca5e84b956"
        retry_record=retry["record"]["path"] if isinstance(retry["record"],dict) else retry["record"]
        assert rows["SMGLIMSE.BMP-013"]["record"]["path"]==retry_record
        assert rows["SMGLIMSE.BMP-014"]["latest_attempt_record"]["path"].endswith("014-v3-record.json")
        page.screenshot(path=str(HERE/"focused-review-top.png"))
        page.locator("[id='frame-SSUZY1.BMP-005']").screenshot(path=str(HERE/"selected-005-review.png"))
        page.locator("[id='frame-SMGLIMSE.BMP-014']").screenshot(path=str(HERE/"glimpse-014-review.png"))
        page.locator("#checker").click()
        assert "dark" in page.locator("body").get_attribute("class")
        page.locator("#resource").select_option("SSUZY1.BMP")
        assert page.locator("article:visible").count()==2

        page.goto(BASE+"visitor-leg-pose-corrections-v2/color-sequence-review.html")
        page.wait_for_function("!document.getElementById('play').disabled",timeout=15000)
        sequence=page.evaluate("data")
        assert sequence["sprites"]["4"]["candidate"]["sha256"]==EXPECTED_004
        assert sequence["sprites"]["4"]["candidate"]["appearance_approval"]["output"]["sha256"]==EXPECTED_004
        assert sequence["sprites"]["4"]["cartoon"]["sha256"]==EXPECTED_004
        assert sequence["sprites"]["5"]["candidate"]["sha256"]==EXPECTED_005
        assert sequence["sprites"]["5"]["cartoon"]["sha256"]==EXPECTED_005
        assert len(sequence["steps"])==26 and sequence["nominal_excerpt_ms"]==5840
        assert "appearance approved" in page.locator("#framePending").inner_text()
        page.locator("#drawingMode").select_option("selected")
        assert "004-upright-bottle-local-v1.png" in page.locator("#cartoonMeta a").get_attribute("href")
        page.locator("#jump5").click()
        assert "generation/SSUZY1.BMP/005-generated-v2.png" in page.locator("#cartoonMeta a").get_attribute("href")

        page.goto(BASE+"mermaid-expression-corrections-v1/review.html")
        existing=page.evaluate("data")
        current={row["key"]:row for row in existing["assets"]}
        assert current["SSUZY1.BMP-004"]["images"]["revised"]["sha256"]==EXPECTED_004
        assert current["SSUZY1.BMP-004"]["appearance_approval"]["output"]["sha256"]==EXPECTED_004
        assert current["SSUZY1.BMP-005"]["images"]["revised"]["sha256"]==EXPECTED_005
        assert current["SSUZY1.BMP-005"]["status"]=="approved_by_user"
        if retry_output:
            assert current["SMGLIMSE.BMP-013"]["images"]["revised"]["sha256"]==expected_retry_hash
        else:
            assert current["SMGLIMSE.BMP-013"]["images"]["revised"] is None
        assert current["SMGLIMSE.BMP-014"]["status"]=="approved_by_user"
        assert not errors,errors
        report={"focused_url":BASE+"review-corrections-2026-09-22/review.html","rows":13,
            "approved_corrections":12,"selected_005":1,"no_image_frames":[],"incomplete_drafts":[],
            "pending_candidates":[],"retry_013_record":retry_record,
            "loaded_image_panels":loaded_panels,"failed_image_panels":0,"page_errors":errors,
            "approved_004_sha256":EXPECTED_004,"previous_approved_004_body_sha256":APPROVED_004,
            "selected_005_sha256":EXPECTED_005,"005_old_color_candidate_shown":False,
            "current_views_synced":True,"sequence_steps":26,"sequence_duration_ms":5840,
            "light_dark_toggle_checked":True,"resource_filter_checked":True,
            "screenshots":["focused-review-top.png","selected-005-review.png","glimpse-014-review.png"]}
        (HERE/"browser-review.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(report))
        browser.close()

if __name__=="__main__":
    main()
