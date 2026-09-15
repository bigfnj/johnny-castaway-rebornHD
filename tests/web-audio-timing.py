"""Trace real AudioContext scheduling through shipped GJHOT.TTM's long frame wait.

This checks scheduled PCM and continuity in Chromium, not physical speaker output.
The controlled-clock C probe supplies the deterministic timing negative control.
"""
import argparse
import functools
import hashlib
import http.server
import json
from pathlib import Path
import struct
import threading
from urllib.parse import urlencode
import zipfile

from playwright.sync_api import sync_playwright


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


TRACE = """(() => {
    window.jcTimingAudio = [];
    window.jcTimingPaints = [];
    const makeSource = AudioContext.prototype.createBufferSource;
    AudioContext.prototype.createBufferSource = function () {
        const context = this;
        const source = makeSource.apply(this, arguments);
        const start = source.start;
        source.start = function (when) {
            window.jcTimingAudio.push({now: context.currentTime, when: when,
                duration: source.buffer.duration, state: context.state,
                bytes: Array.from(source.buffer.getChannelData(0), value => Math.round(value * 128 + 128))});
            return start.apply(this, arguments);
        };
        return source;
    };
    const paint = CanvasRenderingContext2D.prototype.putImageData;
    CanvasRenderingContext2D.prototype.putImageData = function () {
        if (window.audioContext) window.jcTimingPaints.push(window.audioContext.currentTime);
        return paint.apply(this, arguments);
    };
})();"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build", type=Path)
    parser.add_argument("--archive", type=Path, default=Path(__file__).resolve().parents[1] / "assets/scrantic_data.zip")
    parser.add_argument("--report", type=Path)
    options = parser.parse_args()
    build = options.build.resolve()
    with zipfile.ZipFile(options.archive) as archive:
        wav = archive.read("data/sound24.wav")
    length = struct.unpack_from("<I", wav, 40)[0]
    rate = struct.unpack_from("<I", wav, 24)[0]
    expected = wav[44:44 + length]
    assert rate == 11025 and length == 9672, "sound24 fixture changed; review timing oracle"
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(build)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
            context = browser.new_context()
            context.add_init_script(TRACE)
            page = context.new_page()
            errors, witnesses = [], []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("console", lambda message: witnesses.append(message.text)
                    if "PLAY_SAMPLE 24" in message.text or "stopping after" in message.text else None)
            url = f"http://127.0.0.1:{server.server_address[1]}/index.html?" + urlencode({
                "args": "window hotkeys debug style hd ttm GJHOT.TTM frames 20"})
            response = page.goto(url, wait_until="load", timeout=60000)
            assert response and response.body() == (build / "index.html").read_bytes(), "index.html response differs from build"
            page.wait_for_function("window.jcReady === true && window.jcLog.some(s => s.includes('stopping after'))", timeout=30000)
            state = page.evaluate("({audio: window.jcTimingAudio, paints: window.jcTimingPaints, fatal: window.jcHadFatalError})")
            assert not errors and not state["fatal"], "GJHOT browser runtime failed"
            assert any("PLAY_SAMPLE 24" in line for line in witnesses), "GJHOT did not execute PLAY_SAMPLE 24"
            assert any("stopping after 20 frame(s)" in line for line in witnesses), "GJHOT did not reach bounded exit"
            print("WITNESS platform_web.c GJHOT PLAY_SAMPLE 24 and bounded exit", flush=True)
            audio = state["audio"]
            pcm = b"".join(bytes(record["bytes"]) for record in audio)
            offset = pcm.find(expected)
            assert offset >= 0 and pcm.find(expected, offset + 1) == -1, "GJHOT sound24 PCM is missing, reordered or repeated"
            selected, cursor = [], 0
            for record in audio:
                end = cursor + len(record["bytes"])
                if cursor < offset + length and end > offset:
                    selected.append(record)
                cursor = end
            assert len(selected) >= 10, "GJHOT sample did not cross enough scheduled buffers"
            gaps = [right["when"] - left["when"] - left["duration"] for left, right in zip(selected, selected[1:])]
            assert all(abs(gap) < 1 / rate for gap in gaps), "GJHOT sound24 has a scheduling gap or overlap"
            assert all(record["state"] == "running" and record["when"] + record["duration"] - record["now"] <= 0.25 + 1024 / rate + 0.005
                       for record in selected), "GJHOT audio exceeded its existing lookahead bound"
            waits = [(a, b) for a, b in zip(state["paints"], state["paints"][1:]) if b - a >= 0.9]
            assert any(any(a + 0.35 < record["now"] < b - 0.05 for record in selected) for a, b in waits), "GJHOT did not replenish sound24 during the long display wait"
            report = {"result": "PASS", "physical_audio_measured": False, "sample": "data/sound24.wav",
                      "sample_bytes": length, "sample_sha256": hashlib.sha256(expected).hexdigest(),
                      "sample_buffers": len(selected), "max_abs_schedule_gap_seconds": max(map(abs, gaps)),
                      "long_display_intervals_seconds": [b - a for a, b in waits],
                      "paint_count": len(state["paints"]), "witnesses": witnesses,
                      "wasm_sha256": hashlib.sha256((build / "jc_reborn.wasm").read_bytes()).hexdigest()}
            print(f"PASS platform_web.c GJHOT sound24: {length} exact PCM bytes across {len(selected)} contiguous buffers", flush=True)
            if options.report:
                options.report.parent.mkdir(parents=True, exist_ok=True)
                options.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
