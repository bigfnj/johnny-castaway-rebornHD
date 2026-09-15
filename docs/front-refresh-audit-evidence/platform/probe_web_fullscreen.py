"""Bounded, headless observation of fullscreen state; does not modify source."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=str(ROOT / "build_web")))
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    report = {"scope": "Headless Chromium fullscreen hotkey observation using existing Web build; no native windows.", "steps": [], "build_sha256": {name: hashlib.sha256((ROOT / "build_web" / name).read_bytes()).hexdigest() for name in ("index.html", "jc_reborn.js", "jc_reborn.wasm", "jc_reborn.data")}}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.goto(f"http://127.0.0.1:{server.server_port}/index.html?args=window+nosound+maxspeed+hotkeys+seed+9+frames+2000000", timeout=60000)
                page.wait_for_function("window.jcReady === true", timeout=30000)
                def record(label):
                    page.wait_for_timeout(300)
                    report["steps"].append({"label": label, **page.evaluate("({fullscreen:!!document.fullscreenElement, exited: window.jcExitCode ?? null, errors:window.jcErrors})")})
                record("initial windowed control")
                page.keyboard.press("Alt+Enter")
                record("first Alt+Enter")
                page.evaluate("document.exitFullscreen()")
                record("browser exits fullscreen independently")
                page.keyboard.press("Alt+Enter")
                record("next Alt+Enter")
                page.keyboard.press("Alt+Enter")
                record("following Alt+Enter")
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)
        (OUT / "web-fullscreen-observation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))

if __name__ == "__main__":
    main()
