"""Bounded diagnostic retention in the served page, with isolated HTML mutations."""
import argparse
import functools
import hashlib
import http.server
import json
from pathlib import Path
import threading
from urllib.parse import urlencode

from playwright.sync_api import sync_playwright


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def verify(page, case, evidence):
    # Suppress only the artificial stress producer's console forwarding. The basic
    # case separately proves ordinary print/printErr still reach the browser console.
    if case == "basic":
        messages = []
        page.on("console", lambda message: messages.append((message.type, message.text)))
        state = page.evaluate("""() => {
            var reference = window.jcLog;
            Module.print('logging stdout witness');
            Module.printErr('logging stderr witness');
            return {same: reference === window.jcLog, tail: jcLog.slice(-2),
                error: jcErrors.slice(-1), fatal: window.jcHadFatalError};
        }""")
        assert state == {"same": True, "tail": ["logging stdout witness", "logging stderr witness"],
                         "error": ["logging stderr witness"], "fatal": False}, "index.html: basic log forwarding"
        assert ("log", "logging stdout witness") in messages and ("error", "logging stderr witness") in messages, "index.html: console forwarding"
        return
    if case == "backing-storage":
        # Measure the actual served logger in Chromium after the engine stops.
        # CDP collects JavaScript garbage; no forced-GC browser flags are needed.
        # Four distinct inputs defeat string reuse, and stdout/stderr exercise
        # both retained arrays. Console forwarding is excluded from this budget.
        session = page.context.new_cdp_session(page)
        try:
            session.send("HeapProfiler.collectGarbage")
            before = session.send("Runtime.getHeapUsage")["usedSize"]
            state = page.evaluate("""() => {
                var originalLog = console.log, originalError = console.error;
                console.log = console.error = function () {};
                try {
                    for (var i = 0; i < 4; i++) {
                        var text = String(i) + 'x'.repeat(32 * 1024 * 1024);
                        if (i % 2) Module.printErr(text); else Module.print(text);
                    }
                } finally { console.log = originalLog; console.error = originalError; }
                return {lengths: jcLog.slice(-4).map(item => item.length)};
            }""")
            session.send("HeapProfiler.collectGarbage")
            retained = session.send("Runtime.getHeapUsage")["usedSize"] - before
            # Reading characters can flatten V8 concatenations and detach their
            # slices, so inspect content only AFTER measuring retained storage.
            state.update(page.evaluate("""() => ({
                prefixes: jcLog.slice(-4).map(item => item[0]),
                errorPrefixes: jcErrors.slice(-2).map(item => item[0])})"""))
            page.evaluate("jcLog.length = 0; jcErrors.length = 0;")
            session.send("HeapProfiler.collectGarbage")
            cleared = session.send("Runtime.getHeapUsage")["usedSize"] - before
            evidence.update(input_utf16_units=4 * (32 * 1024 * 1024 + 1),
                            retained_heap_delta=retained, cleared_heap_delta=cleared)
            print(f"WITNESS index.html logging backing-storage heap {json.dumps(evidence, sort_keys=True)}", flush=True)
            assert state == {"lengths": [4096] * 4, "prefixes": list("0123"),
                             "errorPrefixes": ["1", "3"]}, "index.html: backing storage producer"
            # A generous 8 MiB ceiling distinguishes four bounded records from
            # the 128 MiB original backing strings, allowing browser bookkeeping.
            assert retained < 8 * 1024 * 1024, "index.html: bounded log backing storage"
        finally:
            session.detach()
        return
    state = page.evaluate("""(caseName) => {
        var reference = window.jcLog;
        var before = jcLog.slice();
        var originalLog = console.log;
        var originalError = console.error;
        console.log = console.error = function () {};
        try {
            if (caseName === 'retention') {
                for (var i = 0; i < 2000; i++) Module.print('line ' + i);
            } else if (caseName === 'stderr') {
                for (var i = 0; i < 40; i++) Module.printErr('error ' + i);
                for (var i = 0; i < 2000; i++) Module.print('line ' + i);
            } else if (caseName === 'length') {
                Module.print('a'.repeat(4096));
                Module.print('b'.repeat(12000));
                Module.printErr('c'.repeat(12000));
                Module.print('a'.repeat(4080) + '\\ud83d\\ude80' + 'z'.repeat(12000));
            } else if (caseName === 'fatal') {
                // The marker is beyond the retention limit, so detection must
                // consult the original input rather than the truncated record.
                Module.printErr('x'.repeat(6000) + ' Fatal error: logging witness');
                for (var i = 0; i < 40; i++) Module.printErr('later error ' + i);
                for (var i = 0; i < 2000; i++) Module.print('line ' + i);
            }
        } finally { console.log = originalLog; console.error = originalError; }
        return {before: before, same: reference === window.jcLog, log: jcLog,
            errors: jcErrors, fatal: window.jcHadFatalError, title: document.title,
            unicodeTail: caseName === 'length' ? jcLog[jcLog.length - 1].slice(4080)
                .split('').map(item => item.charCodeAt(0)) : []};
    }""", case)
    assert state["same"], "index.html: log array identity"
    if case == "retention":
        expected = state["before"] + [f"line {i}" for i in range(2000)]
        assert len(state["log"]) == 512, "index.html: log count limit"
        assert state["log"][:64] == expected[:64], "index.html: startup prefix retention"
        assert state["log"][64:] == expected[-448:], "index.html: recent log ordering"
    elif case == "stderr":
        assert state["errors"] == [f"error {i}" for i in range(24, 40)], "index.html: stderr retention limit"
    elif case == "length":
        exact, clipped, error, unicode_clipped = state["log"][-4:]
        assert exact == "a" * 4096, "index.html: under-limit message preservation"
        assert len(clipped) == len(error) == 4096 and clipped.endswith("... [truncated]") and error.endswith("... [truncated]"), "index.html: message length limit"
        assert state["errors"][-1] == error, "index.html: bounded stderr message"
        # Inspect code units in the page because CDP string transport can replace
        # an unpaired surrogate at this deliberately split character boundary.
        assert unicode_clipped[:4080] == "a" * 4080 and state["unicodeTail"] == [0xD83D] + list(map(ord, "... [truncated]")), "index.html: UTF-16 truncation preservation"
    elif case == "fatal":
        assert state["fatal"] is True, "index.html: sticky fatal status before truncation"
        assert state["title"] == "Johnny Castaway Reborn - error", "index.html: fatal error title"
        assert all("Fatal error" not in item for item in state["log"] + state["errors"]), "index.html: fatal eviction fixture"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build", type=Path)
    parser.add_argument("--phase", choices=["smoke", "regression", "all"], default="all")
    parser.add_argument("--mutations", action="store_true")
    parser.add_argument("--report", type=Path)
    options = parser.parse_args()
    build = options.build.resolve()
    for name in ("index.html", "jc_reborn.js", "jc_reborn.wasm", "jc_reborn.data"):
        assert (build / name).is_file(), f"missing {build / name}"
    html = (build / "index.html").read_bytes()
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(build)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_address[1]}/index.html?" + urlencode({"args": "window nosound maxspeed seed 9 frames 4"})
    records = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            browser_version = browser.version

            def run(case, body):
                context = browser.new_context()
                evidence = {}
                try:
                    # Observe the engine's console stop witness independently of
                    # the retention code, which some mutations intentionally break.
                    context.add_init_script("""window.jcLoggingTestStopped = false;
                        var originalLog = console.log;
                        console.log = function () {
                            for (var i = 0; i < arguments.length; i++) {
                                if (String(arguments[i]).includes('stopping after 4 frame(s)'))
                                    window.jcLoggingTestStopped = true;
                            }
                            return originalLog.apply(this, arguments);
                        };""")
                    page = context.new_page()
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.route("**/index.html*", lambda route: route.fulfill(body=body, content_type="text/html"))
                    response = page.goto(url, wait_until="load", timeout=60000)
                    assert response and response.body() == body, "index.html: expected response bytes were not served"
                    page.wait_for_function("window.jcReady === true && window.jcLoggingTestStopped", timeout=30000)
                    assert not errors, "index.html: page runtime failure"
                    print(f"WITNESS index.html logging {case} BEGIN sha256={hashlib.sha256(body).hexdigest()}", flush=True)
                    verify(page, case, evidence)
                    return evidence
                except AssertionError as error:
                    error.evidence = evidence
                    raise
                finally:
                    context.close()

            cases = ["basic"] if options.phase == "smoke" else ["retention", "stderr", "length", "fatal", "backing-storage"]
            if options.phase == "all": cases.insert(0, "basic")
            for case in cases:
                evidence = run(case, html)
                print(f"PASS index.html logging {case}", flush=True)
                records.append({"case": case, "result": "PASS", **evidence})
            if options.mutations:
                definitions = [
                    ("retention", b"if (jcLog.length > 512)", b"if (false && jcLog.length > 512)", "index.html: log count limit"),
                    ("retention", b"jcLog.splice(64,", b"jcLog.splice(0,", "index.html: startup prefix retention"),
                    ("stderr", b"if (jcErrors.length > 16)", b"if (false && jcErrors.length > 16)", "index.html: stderr retention limit"),
                    ("length", b"text.length > 4096 ?", b"false ?", "index.html: message length limit"),
                    ("fatal", b"window.jcHadFatalError = true;", b"/* mutation: discard fatal status */", "index.html: sticky fatal status before truncation"),
                    ("fatal", b"/Fatal error/i.test(text)", b"/Fatal error/i.test(text.slice(0, 4096))", "index.html: sticky fatal status before truncation"),
                    ("basic", b"retainLog(text, false);", b"/* mutation: drop stdout */", "index.html: basic log forwarding"),
                    ("backing-storage", b".split('').join('')", b"", "index.html: bounded log backing storage"),
                    ("length", b".split('').join('')", b".split('').join('').replace(/[\\uD800-\\uDBFF]$/, '')", "index.html: UTF-16 truncation preservation"),
                ]
                for case, old, new, expected in definitions:
                    assert html.count(old) == 1, (case, old)
                    mutant = html.replace(old, new)
                    try:
                        run(case, mutant)
                    except AssertionError as error:
                        assert str(error) == expected, f"wrong mutation failure: {error}"
                        records.append({"case": case, "result": "FIRED", "expected_failure": expected,
                                        "served_sha256": hashlib.sha256(mutant).hexdigest(), "runtime_witness": True,
                                        **error.evidence})
                        print(f"FIRED {expected} (served and executed)", flush=True)
                    else:
                        raise AssertionError(f"SURVIVED {expected}")
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    if options.report:
        options.report.parent.mkdir(parents=True, exist_ok=True)
        options.report.write_text(json.dumps({"html_sha256": hashlib.sha256(html).hexdigest(),
                                             "chromium_version": browser_version,
                                             "checks": records}, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
