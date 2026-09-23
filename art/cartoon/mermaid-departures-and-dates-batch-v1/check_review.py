"""One-off verification of this 72-drawing review artifact, not a repository gate."""
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
URL = "http://127.0.0.1:8941/mermaid-departures-and-dates-batch-v1/review.html"
EXPECTED_CARDS = 72
EXPECTED_PANELS = 144


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    report = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "url": URL,
              "status": "running", "appearance_approval": None,
              "native_motion_checked": False, "page_errors": [], "request_failures": [],
              "http_errors": [], "console_errors": [], "selected_assets": [],
              "edge_alpha_observations": [], "screenshots": []}
    try:
        data_path = HERE / "review-data.json"
        data = json.loads(data_path.read_text(encoding="utf-8"))
        rows = data["assets"]
        require(len(rows) == EXPECTED_CARDS, f"Expected72 assets, got {len(rows)}")
        require(len({row['key'] for row in rows}) == EXPECTED_CARDS, "Duplicate asset keys")
        for row in rows:
            key = row["key"]
            require(row["status"] == "generated", f"Unready card: {key}: {row['status']}")
            output = verify_pin(row["selected_raw"], f"{key} selected PNG")
            request = verify_pin(row["request"], f"{key} exact request")
            record_path = verify_pin(row["generation_record"], f"{key} generation record")
            verify_pin(row["original_reference"], f"{key} original reference")
            record = json.loads(record_path.read_text(encoding="utf-8"))
            require(record['resource'] == row['resource'] and int(record['frame']) == int(row['frame'])
                    and record['version'] == row['version'], f"Record identity mismatch: {key}")
            require(record['output']['path'] == row['selected_raw']['path'], f"Record path mismatch: {key}")
            require(record["output"]["sha256"] == digest(output), f"Record output mismatch: {key}")
            require(record["request"]["sha256"] == digest(request), f"Record request mismatch: {key}")
            require(record["request"]["path"] == row["request"]["path"], f"Wrong request selected: {key}")
            spec = json.loads(request.read_text(encoding='utf-8'))
            reference_paths = [verify_pin(ref, f"{key} reference") for ref in record['references']]
            require([p.resolve() for p in reference_paths] == [Path(p).resolve() for p in spec['arguments']['referenced_image_paths']],
                    f"Request reference list mismatch: {key}")
            raw_path = Path(record['raw_tool_output'])
            require(raw_path.is_file() and digest(raw_path) == digest(output), f"Raw output byte-copy mismatch: {key}")
            with Image.open(output) as im:
                require(im.mode == "RGBA", f"Non-RGBA selected image: {key}: {im.mode}")
                alpha = im.getchannel("A")
                extrema = list(alpha.getextrema())
                bounds = alpha.point(lambda v: 255 if v >= 8 else 0).getbbox()
                require(extrema[0] == 0, f"No fully transparent background pixels: {key}: {extrema}")
                require(bounds is not None and bounds[2] > bounds[0] and bounds[3] > bounds[1],
                        f"Empty alpha bounds: {key}")
                require(list(bounds) == row["selected_raw"]["alpha8_bounds"], f"Bounds mismatch: {key}")
                require(list(im.size) == row["selected_raw"]["canvas"], f"Canvas mismatch: {key}")
                edge_max = max(alpha.crop(box).getextrema()[1] for box in
                               [(0, 0, im.width, 1), (0, im.height - 1, im.width, im.height),
                                (0, 0, 1, im.height), (im.width - 1, 0, im.width, im.height)])
                item = {"key": key, "version": row["version"], "sha256": digest(output),
                        "request_sha256": digest(request), "canvas": list(im.size), "mode": im.mode,
                        "alpha_range": extrema, "alpha8_bounds": list(bounds), "edge_alpha_max": edge_max}
            report["selected_assets"].append(item)
            if edge_max:
                report["edge_alpha_observations"].append({"key": key, "edge_alpha_max": edge_max,
                    "note": "Visible-opacity content touches canvas boundary; inspect for clipping."
                            if edge_max >= 8 else "Only faint alpha below8 reaches boundary; no alpha8 content touches edge."})
        report["local_hash_records_checked"] = len(rows)
        expected_resources = Counter(row["resource"] for row in rows)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel="chrome", headless=True)
            page = browser.new_page(viewport={"width": 1800, "height": 1250}, device_scale_factor=1)
            page.on("pageerror", lambda error: report["page_errors"].append(str(error)))
            page.on("requestfailed", lambda request: report["request_failures"].append(
                {"url": request.url, "failure": request.failure}))
            page.on("response", lambda response: report["http_errors"].append(
                {"url": response.url, "status": response.status}) if response.status >= 400 else None)
            page.on("console", lambda message: report["console_errors"].append({"text": message.text, "location": message.location})
                    if message.type == "error" else None)
            page.goto(URL, wait_until="networkidle")
            page.wait_for_function("document.getElementById('loading').textContent.includes('image panels loaded.')", timeout=30000)
            report["loading_text"] = page.locator("#loading").inner_text()
            report["card_count"] = page.locator("figure[data-filter]").count()
            report["canvas_count"] = page.locator("canvas").count()
            report["loaded_panels"] = page.locator('canvas[data-loaded="true"]').count()
            report["failed_panels"] = page.locator('canvas[data-loaded="false"]').count()
            require(report["card_count"] == EXPECTED_CARDS, f"Wrong card count: {report['card_count']}")
            require(report["canvas_count"] == EXPECTED_PANELS, f"Wrong canvas count: {report['canvas_count']}")
            require(report["loaded_panels"] == EXPECTED_PANELS, f"Incomplete image loading: {report['loading_text']}")
            require(report["failed_panels"] == 0 and page.locator(".load-error").count() == 0, "Image panel load errors")
            served_data = page.request.get(urljoin(URL, "review-data.json"))
            require(served_data.status == 200, "Review data did not return200")
            require(hashlib.sha256(served_data.body()).hexdigest() == digest(data_path), "Served review data differs from disk")
            links = page.locator(".links a").evaluate_all(
                "els => els.filter(e => ['Exact saved request','Generation record'].includes(e.textContent)).map(e => ({text:e.textContent,url:e.href}))")
            labels = Counter(link["text"] for link in links)
            require(labels == {"Exact saved request": EXPECTED_CARDS, "Generation record": EXPECTED_CARDS},
                    f"Missing request/record links: {dict(labels)}")
            report["request_record_links"] = []
            for link in links:
                response = page.request.get(link["url"])
                report["request_record_links"].append({**link, "status": response.status})
                require(response.status == 200, f"Broken artifact link: {link['url']}: {response.status}")
            report["resource_filters"] = []
            for resource, count in expected_resources.items():
                page.locator("#filter").fill(resource)
                ids = page.locator("figure:visible").evaluate_all("els => els.map(e => e.id)")
                require(len(ids) == count and all(key.startswith(resource + "-") for key in ids),
                        f"Resource filter mismatch: {resource}: {ids}")
                report["resource_filters"].append({"resource": resource, "visible_cards": len(ids)})
            page.locator("#filter").fill("no-such-resource-qa")
            require(page.locator("figure:visible").count() == 0, "Filter does not hide unmatched cards")
            page.locator("#clear-filter").click()
            require(page.locator("figure:visible").count() == EXPECTED_CARDS, "Clear filter failed")
            page.locator("#originals").click()
            require(page.locator("details[open]").count() == 0, "Hide originals failed")
            page.locator("#originals").click()
            require(page.locator("details[open]").count() == EXPECTED_CARDS, "Show originals failed")
            report["original_visibility_toggle_checked"] = True
            page.locator("#filter").fill("SLEVEJM3.BMP")
            page.evaluate("window.scrollTo(0,0)")
            light_background = page.locator(".art:visible").first.evaluate("e => getComputedStyle(e).backgroundColor")
            require(page.locator("#background").get_attribute("aria-pressed") == "false", "Initial background state incorrect")
            page.screenshot(path=str(HERE / "browser-review-light.png"))
            page.locator("#background").click()
            dark_background = page.locator(".art:visible").first.evaluate("e => getComputedStyle(e).backgroundColor")
            require(page.locator("body").evaluate("e => e.classList.contains('dark')"), "Dark class not set")
            require(page.locator("#background").get_attribute("aria-pressed") == "true", "Dark toggle state incorrect")
            require(light_background != dark_background, "Checkerboard color did not change")
            page.screenshot(path=str(HERE / "browser-review-dark.png"))
            page.locator("#filter").fill("SLEVEJM2.BMP-005")
            page.locator("figure:visible").screenshot(path=str(HERE / "browser-slevejm2-005-dark.png"))
            page.locator("#filter").fill("SMDATE1.BMP-012")
            page.locator("figure:visible").screenshot(path=str(HERE / "browser-smdate1-012-dark.png"))
            page.locator("#background").click()
            require(page.locator("#background").get_attribute("aria-pressed") == "false", "Light toggle did not restore")
            page.locator("#filter").fill("SLEVEJM2.BMP-005")
            page.locator("figure:visible").screenshot(path=str(HERE / "browser-slevejm2-005-light.png"))
            page.locator("#clear-filter").click()
            report["light_dark_toggle_checked"] = True
            report["screenshots"] = ["browser-review-light.png", "browser-review-dark.png",
                                     "browser-slevejm2-005-dark.png", "browser-slevejm2-005-light.png",
                                     "browser-smdate1-012-dark.png"]
            require(not report["page_errors"], f"Page errors: {report['page_errors']}")
            require(not report["request_failures"], f"Failed requests: {report['request_failures']}")
            require(not report["http_errors"], f"HTTP errors: {report['http_errors']}")
            require(not report["console_errors"], f"Console errors: {report['console_errors']}")
            browser.close()
        report["status"] = "passed"
    except Exception as error:
        report["status"] = "failed"
        report["failure"] = str(error)
        raise
    finally:
        report["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        (HERE / "browser-review.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({key: value for key, value in report.items()
                          if key not in {"selected_assets", "request_record_links"}}, indent=2))


if __name__ == "__main__":
    main()
