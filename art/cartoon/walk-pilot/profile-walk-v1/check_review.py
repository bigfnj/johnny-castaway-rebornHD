"""Headless smoke then pixel/interaction regression for the two-pose viewer."""
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import re

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / "review-evidence/pose-check-v1"


def require(ok, label):
    if not ok:
        raise ValueError(label)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["smoke", "regression"], required=True)
    args = parser.parse_args()
    html = OUT / "review.html"
    source = html.read_text(encoding="utf-8")
    # Expectations come from the unmodified durable page, including in the mutation run.
    data = json.loads(re.search(r'<script id="review-data" type="application/json">(.*?)</script>', source, re.S)[1])
    cases = []
    errors = []
    print("WITNESS check_review.py SHA256=" + hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), flush=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 1100}, device_scale_factor=1)
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(html.as_uri())
        page.wait_for_function("window.reviewReady === true")
        require(not errors, "page-errors")
        require(page.locator("#status").inner_text().startswith("Pose 003"), "initial-pose")
        require(page.locator("#identity").evaluate("img => img.complete && img.naturalWidth === 80"), "standing-reference")
        if args.phase == "regression":
            smoke = json.loads((OUT / "browser-smoke.json").read_bytes())
            require(smoke["status"] == "PASS" and smoke["html_sha256"] == hashlib.sha256(html.read_bytes()).hexdigest(), "prior-smoke")
            for frame in ["003", "001"]:
                page.select_option("#pose", frame)
                for feet in [False, True]:
                    if page.locator("#feet").get_attribute("aria-pressed") != str(feet).lower():
                        page.click("#feet")
                    for mirrored in [False, True]:
                        if page.locator("#mirror").get_attribute("aria-pressed") != str(mirrored).lower():
                            page.click("#mirror")
                        for which in ["original", "candidate"]:
                            verify_pixels(page, data, frame, feet, mirrored, which)
                        cases.append({"frame": frame, "feet": feet, "mirrored": mirrored, "both_canvas_pixels": "PASS"})
            page.select_option("#pose", "003")
            page.click("#feet")
            page.click("#mirror")
            page.screenshot(path=str(OUT / "whole-body003.png"), full_page=True)
            page.select_option("#pose", "001")
            page.screenshot(path=str(OUT / "whole-body001.png"), full_page=True)
            # Deliberately substitute standing000 for candidate003, while preserving the expected003 bytes.
            page.select_option("#pose", "003")
            page.evaluate("images['003-candidate'] = document.getElementById('identity'); render();")
            failure = None
            try:
                verify_pixels(page, data, "003", False, False, "candidate")
            except ValueError as error:
                failure = str(error)
            require(failure == "canvas-candidate-003", "negative-control-wrong-pose")
            cases.append({"mutation": "substitute-standing000-for-candidate003", "failure": failure, "status": "FIRED"})
        require(not errors, "page-errors")
        browser.close()
    report = {"status": "PASS", "phase": args.phase, "html_sha256": hashlib.sha256(html.read_bytes()).hexdigest(),
              "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "cases": cases,
              "scope": "Headless static viewer and pixels. No native engine or artistic acceptance.", "console_errors": errors}
    (OUT / f"browser-{args.phase}.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report))


def verify_pixels(page, data, frame, feet, mirrored, which):
    actual = page.locator("#" + which).evaluate("c => c.toDataURL('image/png').split(',')[1]")
    actual = Image.open(io.BytesIO(base64.b64decode(actual))).convert("RGB")
    original = Image.open(io.BytesIO(base64.b64decode(data["frames"][frame][which].split(",")[1]))).convert("RGBA")
    zoom = 5 if feet else 4
    width, height = [n * zoom for n in data["frames"][frame]["canvas"]]
    sprite = original.resize((width, height), Image.Resampling.NEAREST)
    if mirrored:
        sprite = sprite.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    x, y = (512 - width) // 2, -80 * zoom + 38 if feet else 16
    expected = Image.new("RGBA", (512, 640), (188, 200, 206, 255))
    expected.alpha_composite(sprite, (x, y))
    box = (x + 1, max(y + 1, 0), x + width - 1, min(y + height - 1, 640))
    diff = ImageChops.difference(actual.crop(box), expected.convert("RGB").crop(box))
    # Browser/Pillow premultiplication rounding can differ by one channel level.
    require(max(channel[1] for channel in diff.getextrema()) <= 2, f"canvas-{which}-{frame}")


if __name__ == "__main__":
    main()
