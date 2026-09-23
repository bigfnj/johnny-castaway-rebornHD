"""Verify the served shark review and its immutable image provenance."""
import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
URL = "http://127.0.0.1:8941/shark-identity-corrections-v1/review.html"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def verify_pin(pin, label):
    require(isinstance(pin, dict), f"Missing {label}")
    path = ROOT / pin["path"]
    require(path.is_file(), f"Missing {label}: {path}")
    require(digest(path) == pin["sha256"], f"Hash mismatch for {label}: {path}")
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-pending", action="store_true", help="Verify a progress snapshot while drawings are still being generated.")
    args = parser.parse_args()
    report = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "url": URL,
              "status": "running", "allow_pending": args.allow_pending, "appearance_approval": None,
              "production_integrated": False, "native_motion_checked": False,
              "page_errors": [], "request_failures": [], "http_errors": [], "console_errors": [],
              "selected_assets": [], "screenshots": []}
    try:
        data = read(HERE / "review-data.json")
        rows = data["entries"]
        require(len(rows) == 27 and len({row["key"] for row in rows}) == 27, "Expected 27 unique correction cards")
        plan = {row["key"]: row for row in read(HERE / "correction-plan.json")["entries"]}
        require(set(plan) == {row["key"] for row in rows}, "Review scope differs from correction plan")
        report["pending_keys"] = [row["key"] for row in rows if not row["output"]]
        require(args.allow_pending or not report["pending_keys"], f"Corrections still pending: {report['pending_keys']}")
        for row in rows:
            key = row["key"]
            require(row["appearance_approval"] is None, f"Unapproved correction marked approved: {key}")
            for kind in ("original", "previous", "previous_record"):
                verify_pin(row[kind], f"{key} {kind}")
                require(row[kind]["sha256"] == plan[key][kind]["sha256"], f"Historical pin changed: {key} {kind}")
            if not row["output"]:
                continue
            require(row["status"] == "awaiting_review", f"Wrong correction status: {key}")
            output = verify_pin(row["output"], f"{key} corrected PNG")
            request = verify_pin(row["request"], f"{key} exact request")
            record = read(verify_pin(row["record"], f"{key} generation record"))
            require(record["resource"] == row["resource"] and int(record["frame"]) == int(row["frame"])
                    and record["version"] == row["version"], f"Record identity mismatch: {key}")
            require(record["output"]["path"] == row["output"]["path"] and record["output"]["sha256"] == digest(output), f"Wrong recorded output: {key}")
            require(record["request"]["path"] == row["request"]["path"] and record["request"]["sha256"] == digest(request), f"Wrong recorded request: {key}")
            ref_paths = [verify_pin(ref, f"{key} reference") for ref in record["references"]]
            require([p.resolve() for p in ref_paths] == [Path(p).resolve() for p in read(request)["arguments"]["referenced_image_paths"]], f"Reference list differs: {key}")
            raw = Path(record["raw_tool_output"])
            require(raw.is_file() and digest(raw) == digest(output), f"Raw output copy differs: {key}")
            with Image.open(output) as im:
                require(im.mode == "RGBA", f"Corrected PNG lacks alpha: {key}")
                alpha = im.getchannel("A")
                bounds = alpha.point(lambda a: 255 if a >= 8 else 0).getbbox()
                require(alpha.getextrema()[0] == 0 and bounds is not None, f"Invalid transparency: {key}")
                require(list(bounds) == row["output"]["bounds"] and list(im.size) == row["output"]["canvas"], f"Image dimensions/bounds mismatch: {key}")
                report["selected_assets"].append({"key": key, "version": row["version"], "sha256": digest(output), "canvas": list(im.size), "alpha_range": list(alpha.getextrema())})
        report["historical_assets_verified_unchanged"] = len(rows)
        report["corrected_assets_verified"] = len(report["selected_assets"])
        expected_panels = sum(bool(row[kind]) for row in rows for kind in ("original", "previous", "output"))
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel="chrome", headless=True)
            page = browser.new_page(viewport={"width": 1800, "height": 1250}, device_scale_factor=1)
            page.on("pageerror", lambda error: report["page_errors"].append(str(error)))
            page.on("requestfailed", lambda request: report["request_failures"].append({"url": request.url, "failure": request.failure}))
            page.on("response", lambda response: report["http_errors"].append({"url": response.url, "status": response.status}) if response.status >= 400 else None)
            page.on("console", lambda message: report["console_errors"].append(message.text) if message.type == "error" else None)
            page.goto(URL, wait_until="networkidle")
            page.wait_for_function("document.getElementById('loading').dataset.complete === 'true'", timeout=30000)
            report["card_count"] = page.locator("article").count()
            report["canvas_count"] = page.locator("canvas").count()
            report["loaded_panels"] = page.locator('canvas[data-loaded="true"]').count()
            report["loading_text"] = page.locator("#loading").inner_text()
            require(report["card_count"] == 27, "Wrong served card count")
            require(report["canvas_count"] == expected_panels and report["loaded_panels"] == expected_panels, "Incomplete image panel loading")
            require(page.locator('canvas[data-loaded="false"]').count() == 0, "Image loading failure")
            for filename in ("review.html", "review-data.json"):
                response = page.request.get(urljoin(URL, filename))
                require(response.status == 200 and hashlib.sha256(response.body()).hexdigest() == digest(HERE / filename), f"Served artifact differs: {filename}")
            links = page.locator(".links a").evaluate_all("els => els.filter(e => ['Exact request','Image record'].includes(e.textContent)).map(e => ({label:e.textContent,url:e.href}))")
            require(len(links) == sum(bool(row[kind]) for row in rows for kind in ("request", "record")), "Missing request/record links")
            report["request_record_links"] = []
            for link in links:
                response = page.request.get(link["url"])
                require(response.status == 200, f"Broken artifact link: {link['url']}")
                report["request_record_links"].append({**link, "status": response.status})
            report["navigation_links"] = []
            for link in page.locator("nav a").evaluate_all("els => els.map(e => ({label:e.textContent,url:e.href}))"):
                response = page.request.get(link["url"])
                require(response.status == 200, f"Broken navigation: {link['url']}")
                report["navigation_links"].append({**link, "status": response.status})
            report["resource_filters"] = []
            for resource, expected in Counter(row["resource"] for row in rows).items():
                page.locator("#resource").select_option(resource)
                visible = page.locator("article:visible").evaluate_all("els => els.map(e => e.dataset.resource)")
                require(len(visible) == expected and all(value == resource for value in visible), f"Resource filter failure: {resource}")
                report["resource_filters"].append({"resource": resource, "visible_cards": len(visible)})
            page.locator("#resource").select_option("")
            require(page.locator("article:visible").count() == 27, "All corrections filter failure")
            light = page.locator(".art").first.evaluate("e => getComputedStyle(e).backgroundColor")
            page.locator("#resource").select_option("SLEVEJM3.BMP")
            page.evaluate("window.scrollTo(0,0)")
            page.screenshot(path=str(HERE / "browser-review-light.png"))
            page.locator("#checker").click()
            dark = page.locator(".art").first.evaluate("e => getComputedStyle(e).backgroundColor")
            require(light != dark and page.locator("#checker").get_attribute("aria-pressed") == "true", "Dark checkerboard toggle failed")
            page.screenshot(path=str(HERE / "browser-review-dark.png"))
            page.locator("#checker").click()
            require(page.locator("#checker").get_attribute("aria-pressed") == "false", "Light checkerboard restoration failed")
            report["screenshots"] = ["browser-review-light.png", "browser-review-dark.png"]
            page.locator("#resource").select_option("")
            for key in ("SLEVEJM1.BMP-008", "SLEVEJM2.BMP-003", "SLEVEJM3.BMP-004"):
                filename = f"browser-{key}.png"
                page.locator(f"#frame-{key.replace('.', chr(92)+'.')}").screenshot(path=str(HERE / filename))
                report["screenshots"].append(filename)
            for field in ("page_errors", "request_failures", "http_errors", "console_errors"):
                require(not report[field], f"Browser errors: {field}: {report[field]}")
            browser.close()
        report["status"] = "passed_progress_snapshot" if report["pending_keys"] else "passed"
    except Exception as error:
        report["status"] = "failed"
        report["failure"] = str(error)
        raise
    finally:
        report["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        (HERE / "browser-review.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({key: value for key, value in report.items() if key not in {"selected_assets", "request_record_links"}}, indent=2))


if __name__ == "__main__":
    main()
