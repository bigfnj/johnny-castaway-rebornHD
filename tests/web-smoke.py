"""Headless browser smoke test for the Emscripten build.

WHY A REAL BROWSER. "it compiled" was the only bar the web target had ever had to
clear, and it was clearing it while being silent (platformOpenAudio was a stub
whose handler body was a comment) and while able to freeze the tab (the single
yield point sat inside a conditional busy-wait). Neither is visible to a linker.

WHAT IT ASSERTS, and each one exists because it failed at some point:

  1. The page loads and the Emscripten runtime initialises at all.
  2. The canvas actually PAINTS something other than a blank rectangle. A build
     that starts and renders nothing passes every other check.
  3. The engine RUNS, and the tab stays responsive while it does. This is the
     freeze check: the page must answer JavaScript while the engine is looping.
  4. A bounded run (`frames N`) reaches its own clean exit, which also proves
     Module.arguments is wired - without it no option could reach the engine in
     a browser at all.
  5. No "Fatal error" reached the log.

Audio cannot be asserted end to end without a user gesture, which headless
Chromium will not fake. What IS asserted is that the engine created an
AudioContext and scheduled buffers onto it, which is the part that was missing.

Usage:  python tests/web-smoke.py <dir-containing-jc_reborn.js>
"""
import http.server
import functools
import socketserver
import sys
import threading
import os

from playwright.sync_api import sync_playwright


def serve(directory):
    """A throwaway localhost server. file:// will not do: the Emscripten glue
    fetches jc_reborn.wasm and jc_reborn.data, and both are blocked by CORS on a
    file URL, which fails in a way that looks like a broken build."""
    handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                                directory=directory)
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


def main():
    if len(sys.argv) < 2:
        print("usage: web-smoke.py <build dir>")
        return 1
    build = os.path.abspath(sys.argv[1])
    for required in ("jc_reborn.js", "jc_reborn.wasm", "jc_reborn.data", "index.html"):
        if not os.path.isfile(os.path.join(build, required)):
            print("FAIL missing %s in %s" % (required, build))
            return 1

    httpd, port = serve(build)
    failures = []

    def check(name, ok, detail=""):
        if ok:
            print("  ok   %s" % name)
        else:
            print("  FAIL %s%s" % (name, (" - " + detail) if detail else ""))
            failures.append(name)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
            page = browser.new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))

            # A LONG run, deliberately, and this matters more than it looks.
            #
            # An earlier revision used `frames 120`, which at max speed finishes
            # in well under a second - so by the time the probes below ran, the
            # engine had already exited and torn down its audio. The page was
            # then trivially responsive and the freeze check could not fail. A
            # mutation that removed the yield entirely still "passed" it.
            #
            # The frame budget here is large enough that the engine is certainly
            # still looping throughout, and bounded only so a broken build cannot
            # spin forever in CI. The clean-exit case gets its own page load
            # below, where finishing IS the thing being asserted.
            #
            # nosound is NOT passed: the audio path is under test.
            url = ("http://127.0.0.1:%d/index.html"
                   "?args=window+maxspeed+hotkeys+seed+9+frames+2000000" % port)
            page.goto(url, wait_until="load", timeout=60000)

            print("\n== the runtime starts ==")
            # A build with no yield freezes so early that jcReady - set in
            # onRuntimeInitialized, one statement before main() takes the thread
            # for good - is never OBSERVABLE, even though it was assigned. So
            # this wait is itself a freeze check, and it must report as one
            # rather than escaping as a traceback: measured, the mutant reaches
            # exactly here and no further.
            started = True
            try:
                page.wait_for_function("window.jcReady === true", timeout=120000)
            except Exception:  # noqa: BLE001
                started = False
            check("Emscripten runtime initialises and the page can answer", started,
                  "no response in 120s - the main thread never yielded")
            if not started:
                browser.close()
                print("")
                print("%d check(s) failed" % len(failures))
                return 1

            check("Module.arguments reached the engine",
                  page.evaluate("Module.arguments.length") > 0)

            print("\n== the tab stays responsive while the engine runs ==")
            # THE FREEZE CHECK, and it must be wait_for_function rather than
            # evaluate.
            #
            # An earlier revision probed with page.evaluate() under
            # page.set_default_timeout(5000). That bound never reaches evaluate:
            # it takes no timeout argument and the driver simply waits for the
            # CDP reply, however long that is. Measured against a page whose main
            # thread was blocked for 120s: wait_for_function(timeout=5000) raised
            # TimeoutError in 5.0s, while evaluate returned after 114.1s - it sat
            # out the entire freeze and then reported success. So the check could
            # not fail on the very condition it exists to catch; it could only
            # hang, which is what the yield mutation did to it for 20 minutes.
            #
            # wait_for_function enforces its deadline driver-side, so a page that
            # cannot answer produces a bounded failure. Repeated, because a
            # single lucky gap between frames would prove nothing.
            responsive = True
            for i in range(5):
                try:
                    # A real round trip: the predicate is only true if the page
                    # executed it, and the value is derived from the argument so
                    # a constant cannot satisfy it.
                    page.wait_for_function("(n) => n + 1 === %d" % (i + 1),
                                           arg=i, timeout=5000)
                except Exception as exc:  # noqa: BLE001
                    responsive = False
                    errors.append("unresponsive after %d probe(s): %s"
                                  % (i, type(exc).__name__))
                    break
                page.wait_for_timeout(300)
            check("page answers JavaScript while the engine is looping", responsive)

            # Every probe below reads state out of the page, so none of them can
            # answer if the page is frozen - they would hang exactly as the old
            # freeze check did. Fail them explicitly instead of skipping in
            # silence, so a frozen run reports what it could not measure.
            if not responsive:
                for blocked in ("canvas has painted a real frame",
                                "engine created an AudioContext",
                                "engine scheduled audio buffers onto it",
                                "no fatal error while running"):
                    check(blocked, False, "not measurable: the page is frozen")
                check("no uncaught page errors", not errors, "; ".join(errors[:2]))
                browser.close()
                print("")
                print("%d check(s) failed" % len(failures))
                return 1

            print("\n== it renders ==")
            painted = page.evaluate(
                """() => {
                    const c = document.getElementById('canvas');
                    const ctx = c.getContext('2d');
                    const d = ctx.getImageData(0, 0, c.width, c.height).data;
                    let nonBlack = 0;
                    for (let i = 0; i < d.length; i += 4) {
                        if (d[i] || d[i+1] || d[i+2]) { nonBlack++; }
                    }
                    return { w: c.width, h: c.height, nonBlack: nonBlack };
                }"""
            )
            print("     canvas %dx%d, %d non-black pixels"
                  % (painted["w"], painted["h"], painted["nonBlack"]))
            check("canvas has painted a real frame", painted["nonBlack"] > 1000)

            print("\n== audio was wired, not stubbed ==")
            audio = page.evaluate(
                "() => ({ ctx: typeof window.audioContext, "
                "state: window.audioContext ? window.audioContext.state : null, "
                "scheduled: window.jcAudioNext || 0 })"
            )
            print("     audioContext=%s state=%s scheduledAhead=%.3fs"
                  % (audio["ctx"], audio["state"], audio["scheduled"]))
            check("engine created an AudioContext", audio["ctx"] == "object")
            # jcAudioNext only advances when webAudioPump actually scheduled a
            # buffer, which requires the engine's mixer callback to have run. The
            # old stub could never move it.
            check("engine scheduled audio buffers onto it", audio["scheduled"] > 0,
                  "state=%s (a suspended context schedules nothing)" % audio["state"])

            log = page.evaluate("window.jcLog ? window.jcLog.join('\\n') : ''")
            check("no fatal error while running", not page.evaluate("window.jcHadFatalError === true") and "Fatal error" not in log,
                  log[-200:] if log else "")
            check("no uncaught page errors", not errors, "; ".join(errors[:2]))

            print("\n== a bounded run reaches its own clean exit ==")
            # A SECOND page load. Here finishing is the assertion, so the frame
            # budget is small. This is also the only proof that `frames N`
            # terminates the engine under Emscripten, where exit() unwinds an
            # asyncify-rewound stack rather than returning normally.
            page2 = browser.new_page()
            errors2 = []
            page2.on("pageerror", lambda e: errors2.append(str(e)))
            page2.goto("http://127.0.0.1:%d/index.html"
                       "?args=window+nosound+maxspeed+hotkeys+seed+9+frames+60" % port,
                       wait_until="load", timeout=60000)
            page2.wait_for_function("window.jcReady === true", timeout=120000)
            try:
                # The ENGINE announces it, which is the only reliable signal here.
                # Module.onExit is not called under -sNO_EXIT_RUNTIME and
                # calledRun reports only that startup finished, so neither
                # distinguishes "running" from "finished". stdout reaches
                # Module.print, which index.html collects into window.jcLog.
                page2.wait_for_function(
                    "window.jcLog && window.jcLog.some("
                    "  s => s.indexOf('stopping after') !== -1)",
                    timeout=90000)
                finished = True
            except Exception as exc:  # noqa: BLE001
                finished = False
                errors2.append(str(exc))
            check("bounded run reached its own frame limit and stopped", finished)
            log2 = page2.evaluate("window.jcLog ? window.jcLog.join('\\n') : ''")
            check("bounded run reported no fatal error", not page2.evaluate("window.jcHadFatalError === true") and "Fatal error" not in log2,
                  log2[-200:] if log2 else "")

            browser.close()
    finally:
        httpd.shutdown()

    print("")
    if failures:
        print("%d check(s) failed" % len(failures))
        return 1
    print("web smoke passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
