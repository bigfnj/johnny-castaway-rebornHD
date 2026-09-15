"""Exercise the shipped art selector against a real Emscripten build.

Usage: python tests/web-art-controls.py build_web [--mutation-check]
The mutation changes only the HTML response in one isolated browser context.
The WASM renderer remains real, and the test proves the changed HTML was served.
"""
import argparse
import functools
import hashlib
import http.server
import json
from pathlib import Path
import threading
from urllib.parse import parse_qs, urlencode, urlparse

from playwright.sync_api import sync_playwright


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


SHORT = "window nosound maxspeed seed 9 frames 4"
LONG = "window nosound maxspeed hotkeys seed 9 frames 2000000"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build", type=Path)
    parser.add_argument("--mutation-check", action="store_true")
    options = parser.parse_args()
    build = options.build.resolve()
    for name in ("index.html", "jc_reborn.js", "jc_reborn.wasm", "jc_reborn.data"):
        if not (build / name).is_file():
            print("FAIL missing %s" % (build / name))
            return 1
    html = (build / "index.html").read_bytes()
    handler = functools.partial(QuietHandler, directory=str(build))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = "http://127.0.0.1:%d/index.html" % server.server_address[1]
    failures = []

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()

            def opened(arguments=SHORT, saved=None, blocked=False, body=None, extra=None):
                context = browser.new_context()
                # Seeding once lets the real change/reload path prove persistence.
                if saved is not None:
                    context.add_init_script("""if (!sessionStorage.getItem('jc.testSeeded')) {
                        localStorage.setItem('jc.artStyle', %s);
                        sessionStorage.setItem('jc.testSeeded', 'yes');
                    }""" % json.dumps(saved))
                if blocked:
                    context.add_init_script("""Object.defineProperty(window, 'localStorage', {
                        get: function () { throw new DOMException('blocked', 'SecurityError'); }
                    });""")
                # Count the renderer's actual paint calls, not an independent timer.
                context.add_init_script("""window.jcTestPaints = 0;
                    var originalPaint = CanvasRenderingContext2D.prototype.putImageData;
                    CanvasRenderingContext2D.prototype.putImageData = function () {
                        window.jcTestPaints++;
                        return originalPaint.apply(this, arguments);
                    };""")
                page = context.new_page()
                page.set_default_timeout(10000)
                if body is not None:
                    page.route("**/index.html*", lambda route: route.fulfill(
                        body=body, content_type="text/html"))
                params = dict(extra or {})
                params["args"] = arguments
                try:
                    response = page.goto(origin + "?" + urlencode(params) + "#island",
                                         wait_until="load", timeout=60000)
                    expected = body if body is not None else html
                    if response is None or response.body() != expected:
                        raise AssertionError("the expected index.html was not served")
                    page.wait_for_function("window.jcReady === true", timeout=60000)
                    return context, page
                except Exception:
                    context.close()
                    raise

            def run(name, action):
                try:
                    action()
                    print("  ok   " + name)
                except Exception as exc:
                    failures.append(name)
                    print("  FAIL %s - %s" % (name, exc))

            def assert_args(page, expected):
                # Emscripten prepends argv[0] to Module.arguments. The selector's
                # own array must remain separate, or each reload adds that name.
                actual = page.evaluate("Module.arguments.slice(1)")
                assert actual == expected, "arguments: %r; expected %r" % (actual, expected)
                assert page.evaluate("jcArgs") == expected, "engine mutated the selector's user arguments"

            def args_case(arguments, saved, expected, picker):
                context, page = opened(arguments, saved)
                try:
                    assert_args(page, expected)
                    assert page.locator("#art-style").input_value() == picker
                finally:
                    context.close()

            run("URL style overrides browser preference", lambda: args_case(
                SHORT + " style hd", "cartoon", (SHORT + " style hd").split(), "hd"))
            run("saved browser style reaches engine arguments", lambda: args_case(
                SHORT, "cartoon", (SHORT + " style cartoon").split(), "cartoon"))
            run("invalid saved preference leaves the HD default", lambda: args_case(
                SHORT, "unknown", SHORT.split(), "hd"))
            run("last explicit style wins without rewriting arguments", lambda: args_case(
                SHORT + " style hd style cartoon", "hd",
                (SHORT + " style hd style cartoon").split(), "cartoon"))
            run("a capture filename named style remains an operand", lambda: args_case(
                SHORT + " capture style", "cartoon",
                (SHORT + " capture style style cartoon").split(), "cartoon"))

            def reload_case(blocked=False):
                initial = SHORT + " capture style style cartoon style hd"
                context, page = opened(initial, blocked=blocked, extra={"keep": "hello world"})
                try:
                    before = page.url
                    with page.expect_navigation(wait_until="load", timeout=60000):
                        page.locator("#art-style").select_option("cartoon")
                    page.wait_for_function("window.jcReady === true", timeout=60000)
                    expected = (SHORT + " capture style style cartoon").split()
                    assert page.url != before
                    assert_args(page, expected)
                    assert page.locator("#art-style").input_value() == "cartoon"
                    query = parse_qs(urlparse(page.url).query)
                    assert query["args"][0].split() == expected
                    assert query["keep"] == ["hello world"]
                    assert urlparse(page.url).fragment == "island"
                    if not blocked:
                        assert page.evaluate("localStorage.getItem('jc.artStyle')") == "cartoon"
                        page.goto(origin + "?" + urlencode({"args": SHORT}), wait_until="load")
                        page.wait_for_function("window.jcReady === true", timeout=60000)
                        assert_args(page, (SHORT + " style cartoon").split())
                finally:
                    context.close()

            run("selection reload preserves operands/query/hash and persists", reload_case)
            run("selection and reload work with blocked localStorage", lambda: reload_case(True))

            def keyboard_case(body=None):
                context, page = opened(LONG + " style hd", body=body)
                try:
                    page.wait_for_function("window.jcTestPaints >= 3", timeout=15000)
                    page.evaluate("""window.jcTestKeys = [];
                        ['keydown', 'keyup'].forEach(function (kind) {
                            window.addEventListener(kind, function (event) {
                                window.jcTestKeys.push(event.type);
                            }, true);
                        });""")
                    page.locator("#art-style").focus()
                    page.keyboard.press("Escape")
                    paints = page.evaluate("window.jcTestPaints")
                    try:
                        page.wait_for_function("(n) => window.jcTestPaints >= n + 3",
                                               arg=paints, timeout=5000)
                        advancing = True
                    except Exception:
                        advancing = False
                    assert advancing and page.evaluate("window.jcTestKeys.length") == 0, (
                        "index.html: toolbar Escape reached a later window capture listener "
                        "or stopped the real renderer")
                finally:
                    context.close()

            run("toolbar keydown/keyup leave the real renderer painting", keyboard_case)

            def outside_key_case():
                context, page = opened(LONG + " style hd")
                try:
                    page.wait_for_function("window.jcTestPaints >= 3", timeout=15000)
                    page.locator("#canvas").dispatch_event("keydown", {"key": "Escape"})
                    page.wait_for_timeout(400)
                    paints = page.evaluate("window.jcTestPaints")
                    page.wait_for_timeout(400)
                    assert page.evaluate("window.jcTestPaints") == paints, (
                        "Escape outside the toolbar failed to reach the engine")
                finally:
                    context.close()

            run("canvas Escape still reaches and stops the renderer", outside_key_case)

            def native_select_case():
                context, page = opened(SHORT + " style hd")
                try:
                    page.locator("#art-style").focus()
                    with page.expect_navigation(wait_until="load", timeout=60000):
                        page.keyboard.press("End")
                    page.wait_for_function("window.jcReady === true", timeout=60000)
                    assert page.locator("#art-style").input_value() == "cartoon"
                    assert_args(page, (SHORT + " style cartoon").split())
                finally:
                    context.close()

            run("native select keyboard navigation still changes style", native_select_case)

            if options.mutation_check:
                needle = b"event.stopImmediatePropagation();"
                assert html.count(needle) == 1, "mutation must target exactly one guard in index.html"
                mutant = html.replace(needle, b"void event; /* keyboard guard disabled */", 1)
                print("  witness index.html served SHA256 " + hashlib.sha256(mutant).hexdigest())
                try:
                    keyboard_case(mutant)
                except AssertionError as exc:
                    print("  FIRED 1/1 index.html keyboard guard mutation: " + str(exc))
                else:
                    failures.append("index.html keyboard guard mutation survived")
                    print("  FAIL index.html keyboard guard mutation survived")
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print("web art controls: %d failed" % len(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
