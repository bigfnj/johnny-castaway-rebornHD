"""Validate the served round-four review and preserved full archive."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from playwright.async_api import Browser, Page, async_playwright


HERE = Path(__file__).resolve().parent
FOCUSED_URL = "http://127.0.0.1:8941/mermaid-departures-and-dates-batch-v1/review.html"
FULL_URL = "http://127.0.0.1:8941/mermaid-departures-and-dates-batch-v1/review-full.html"
FOCUSED_KEYS = ["SLEVEJM2.BMP-009", "SLEVEJM3.BMP-004"]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_report(name: str, report: dict[str, Any]) -> None:
    (HERE / name).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


async def validate_page(
    browser: Browser,
    url: str,
    expected_cards: int,
    expected_panels: int,
    expected_keys: list[str] | None = None,
    check_artifact_links: bool = False,
    screenshot_name: str | None = None,
) -> dict[str, Any]:
    page_errors: list[str] = []
    request_failures: list[str] = []
    http_errors: list[dict[str, Any]] = []
    console_errors: list[str] = []
    page = await browser.new_page(viewport={"width": 1800, "height": 1100})
    page.on("pageerror", lambda error: page_errors.append(str(error)))
    page.on(
        "requestfailed",
        lambda request: request_failures.append(
            f"{request.method} {request.url}: {request.failure or 'unknown failure'}"
        ),
    )
    page.on(
        "response",
        lambda response: http_errors.append({"url": response.url, "status": response.status})
        if response.status >= 400
        else None,
    )
    page.on(
        "console",
        lambda message: console_errors.append(message.text)
        if message.type == "error"
        else None,
    )

    report: dict[str, Any] = {
        "checked_at_utc": now_utc(),
        "url": url,
        "expected_cards": expected_cards,
        "expected_panels": expected_panels,
    }
    if expected_keys is not None:
        report["expected_keys"] = expected_keys

    try:
        await page.goto(url, wait_until="networkidle", timeout=30_000)
        await page.wait_for_function(
            "expected => document.querySelectorAll('canvas[data-loaded]').length === expected",
            arg=expected_panels,
            timeout=30_000,
        )
        loading_text = (await page.locator("#loading").inner_text()).strip()
        card_keys = await page.eval_on_selector_all(
            "figure[id]", "nodes => nodes.map(node => node.id)"
        )
        canvas_state = await page.eval_on_selector_all(
            "canvas",
            """canvases => canvases.map((canvas, index) => {
                const pixels = canvas.getContext('2d').getImageData(
                    0, 0, canvas.width, canvas.height
                ).data;
                let nonblank = false;
                for (let offset = 3; offset < pixels.length; offset += 4) {
                    if (pixels[offset] !== 0) {
                        nonblank = true;
                        break;
                    }
                }
                return {
                    index,
                    kind: canvas.dataset.kind || null,
                    loaded: canvas.dataset.loaded || null,
                    nonblank
                };
            })""",
        )
        artifact_links: list[dict[str, Any]] = []
        if check_artifact_links:
            links = await page.eval_on_selector_all(
                "a",
                """nodes => nodes
                    .map(node => ({label: node.textContent.trim(), url: node.href}))
                    .filter(item => item.label === 'Exact saved request' ||
                                    item.label === 'Generation record')""",
            )
            for link in links:
                response = await page.request.get(link["url"])
                artifact_links.append(
                    {"label": link["label"], "url": link["url"], "status": response.status}
                )

        report.update(
            {
                "page_errors": page_errors,
                "request_failures": request_failures,
                "http_errors": http_errors,
                "console_errors": console_errors,
                "appearance_approval": None,
                "production_integrated": False,
                "native_motion_checked": False,
                "loading_text": loading_text,
                "card_count": len(card_keys),
                "card_keys": card_keys,
                "canvas_count": len(canvas_state),
                "loaded_panels": sum(item["loaded"] == "true" for item in canvas_state),
                "failed_panels": sum(item["loaded"] == "false" for item in canvas_state),
                "load_error_count": await page.locator(".load-error").count(),
                "original_count": sum(item["kind"] == "original" for item in canvas_state),
                "nonblank_canvas_count": sum(item["nonblank"] for item in canvas_state),
                "blank_canvas_indices": [
                    item["index"] for item in canvas_state if not item["nonblank"]
                ],
            }
        )
        if check_artifact_links:
            report["artifact_links"] = artifact_links

        failure = ""
        if report["card_count"] != expected_cards:
            failure = f"expected {expected_cards} cards, got {report['card_count']}"
        elif expected_keys is not None and card_keys != expected_keys:
            failure = f"card keys differ: expected {expected_keys}, got {card_keys}"
        elif report["canvas_count"] != expected_panels:
            failure = f"expected {expected_panels} canvases, got {report['canvas_count']}"
        elif report["loaded_panels"] != expected_panels:
            failure = f"expected {expected_panels} loaded panels, got {report['loaded_panels']}"
        elif report["nonblank_canvas_count"] != expected_panels:
            failure = (
                f"expected {expected_panels} nonblank canvases, "
                f"got {report['nonblank_canvas_count']}"
            )
        elif report["original_count"] != expected_cards:
            failure = (
                f"expected {expected_cards} original canvases, "
                f"got {report['original_count']}"
            )
        elif any((page_errors, request_failures, http_errors, console_errors)):
            failure = "browser errors were recorded"
        elif report["load_error_count"] or report["failed_panels"]:
            failure = "one or more image panels failed to load"
        elif check_artifact_links and len(artifact_links) != expected_cards * 2:
            failure = (
                f"expected {expected_cards * 2} artifact links, got {len(artifact_links)}"
            )
        elif check_artifact_links and any(link["status"] != 200 for link in artifact_links):
            failure = "one or more artifact links did not return HTTP 200"

        report["status"] = "failed" if failure else "passed"
        if failure:
            report["failure"] = failure
        if screenshot_name is not None:
            await page.screenshot(path=str(HERE / screenshot_name), full_page=True)
            report["screenshot"] = screenshot_name
        report["completed_at_utc"] = now_utc()
        return report
    finally:
        await page.close()


async def main() -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        try:
            negative = await validate_page(
                browser,
                FOCUSED_URL,
                expected_cards=3,
                expected_panels=4,
                expected_keys=FOCUSED_KEYS,
                check_artifact_links=True,
            )
            write_report("browser-review-round4-focused-negative-control.json", negative)
            expected_failure = "expected 3 cards, got 2"
            if negative.get("status") != "failed" or negative.get("failure") != expected_failure:
                raise RuntimeError(
                    "focused negative control did not fail on the intended card-count guard"
                )

            focused = await validate_page(
                browser,
                FOCUSED_URL,
                expected_cards=2,
                expected_panels=4,
                expected_keys=FOCUSED_KEYS,
                check_artifact_links=True,
                screenshot_name="browser-review-round4-focused.png",
            )
            write_report("browser-review-round4-focused.json", focused)
            if focused.get("status") != "passed":
                raise RuntimeError(f"focused review failed: {focused.get('failure')}")

            full = await validate_page(
                browser,
                FULL_URL,
                expected_cards=72,
                expected_panels=144,
            )
            write_report("browser-review-round4-full-archive.json", full)
            if full.get("status") != "passed":
                raise RuntimeError(f"full archive failed: {full.get('failure')}")
        finally:
            await browser.close()

    print(
        json.dumps(
            {
                "focused_status": focused["status"],
                "focused_cards": focused["card_count"],
                "focused_nonblank_canvases": focused["nonblank_canvas_count"],
                "negative_control_failure": negative["failure"],
                "full_status": full["status"],
                "full_cards": full["card_count"],
                "full_nonblank_canvases": full["nonblank_canvas_count"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
