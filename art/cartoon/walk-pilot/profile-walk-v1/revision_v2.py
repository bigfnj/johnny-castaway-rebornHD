"""Preserve and publish the user-requested small downward003 foot revision."""
import argparse
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from urllib.request import urlopen

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = HERE / "review-evidence/pose-check-v2"
CACHE = Path(r"C:\Users\Admin\.codex\generated_images\01a0a1f0-5ca9-70b3-88cd-a31f4f736e75\exec-a8002660-35d9-4c04-af2e-510cf40066eb.png")
URL = "http://127.0.0.1:8932/profile-walk-key-v2/review.html"
DEST = Path(r"D:\.ai-work\worktrees\johnny-art-metadata\build\art-review\profile-walk-key-v2")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def build():
    export = ROOT / "build/profile-walk/export003-v2"
    canonical = HERE / "exports/003-v2"
    recipe = (canonical / "recipe.json").read_bytes()
    runtime = (export / "BMP/JOHNWALK.BMP/003.png").read_bytes()
    report = json.loads((canonical / "export-report.json").read_bytes())
    if recipe != (export / "recipe.json").read_bytes() or sha(runtime) != report["outputs_sha256"]["BMP/JOHNWALK.BMP/003.png"]:
        raise ValueError("revision-export003-identity")
    prior_path = HERE / "review-evidence/pose-check-v1/review.html"
    prior = prior_path.read_text(encoding="utf-8")
    prior_record = json.loads((HERE / "review-evidence/pose-check-v1/review-record.json").read_bytes())
    if sha(prior_path.read_bytes()) != prior_record["review_html_sha256"]:
        raise ValueError("prior-review-identity")
    pattern = r'(<script id="review-data" type="application/json">)(.*?)(</script>)'
    match = re.search(pattern, prior, re.S)
    data = json.loads(match[2])
    previous003 = data["frames"]["003"]["candidate"]
    data["frames"]["003"]["candidate"] = "data:image/png;base64," + base64.b64encode(runtime).decode("ascii")
    data["frames"]["003"]["version"] = "v2"
    html = prior[:match.start(2)] + json.dumps(data) + prior[match.end(2):]
    changes = {
        "Profile walk: first pose check": "Profile walk: lowered tucked foot",
        "Cartoon draft ·003 v1": "Cartoon draft ·003 v2",
        "Check the lifted foot and supporting leg in003, then the heel and toe angles in001. These are two still poses; the complete walk comes after this check.":
            "003 now has a slightly lower tucked foot. Check the clearance behind the planted calf. Pose001 remains available unchanged; this is still a pose review.",
        "Look for one flat supporting foot and a distinct tucked foot behind the calf.":
            "The tucked foot is slightly lower in this revision. It should still read as lifted, with a natural shin connection behind the supporting calf.",
    }
    for old, new in changes.items():
        expected_count = 2 if old == "Profile walk: first pose check" else 1
        if html.count(old) != expected_count:
            raise ValueError("review-text-contract:" + old)
        html = html.replace(old, new)
    payload = html.encode("utf-8")
    raw = (HERE / "003-profile-v2.png").read_bytes()
    call_bytes = (HERE / "003-call-v2.json").read_bytes()
    call = json.loads(call_bytes)
    ancestor = (HERE / "003-profile-v1.png").read_bytes()
    if sha(raw) != json.loads(recipe)["frames"][0]["source_sha256"]:
        raise ValueError("revision-raw-identity")
    with Image.open(HERE / "003-profile-v2.png") as image:
        alpha = image.getchannel("A")
        measurements = {"canvas": list(image.size), "mode": image.mode, "alpha_range": list(alpha.getextrema()),
                        "bounds_exclusive_by_alpha_threshold": {str(t): list(alpha.point(lambda a: 255 if a >= t else 0).getbbox()) for t in [1, 8, 128]}}
    # The persistent output is usable without the external image-generation cache.
    cache_identical = CACHE.read_bytes() == raw if CACHE.exists() else None
    if cache_identical is False:
        raise ValueError("revision-cache-copy")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "review.html").write_bytes(payload)
    save(OUT / "review-record.json", {"schema_version": 1, "scope": "Static003 foot correction; pose/motion approval pending.",
         "user_feedback": "can you slightly lower the tucked foot please ?", "prior_html_sha256": sha(prior_path.read_bytes()),
         "review_html_sha256": sha(payload), "runtime003_sha256": sha(runtime), "recipe003_sha256": sha(recipe),
         "previous003_runtime_sha256": sha(base64.b64decode(previous003.split(",")[1])), "001_and_originals_unchanged": True})
    save(HERE / "provenance003-v2.json", {"schema_version": 1, "tool": "built-in image_gen.imagegen",
         "model_identifier": "not exposed by tool", "generation_seed": "not exposed by tool",
         "raw": "003-profile-v2.png", "raw_sha256": sha(raw), "tool_output_path": str(CACHE), "cache_bytes_identical": cache_identical,
         "call": "003-call-v2.json", "call_sha256": sha(call_bytes), "prompt_utf8_sha256": sha(call["prompt"].encode("utf-8")),
         "actual_reference_order": [{"actual_path": call["referenced_image_paths"][0], "preserved_path": "003-profile-v1.png", "sha256": sha(ancestor)}],
         "user_feedback": "can you slightly lower the tucked foot please ?", "requested_displacement_raw_px": 45,
         "displacement_limit": "Prompt target only; no exact45-pixel or byte-identical unchanged-body claim.",
         "measurements": measurements, "cap_raw": json.loads(recipe)["frames"][0]["cap_raw"],
         "status": "Revised draft; human review pending. Original003-v1 and001-v2 review records remain historical."})
    save(HERE / "review-request-v2.json", {"status": "pending-human-review", "scope": "Revised tucked-foot003 only; no approval inferred for001 or motion.",
         "question": "In the revised profile-walk preview, does 003's slightly lower tucked foot look right now?", "review_url": URL, "review_html_sha256": sha(payload),
         "selected003_raw": "003-profile-v2.png", "selected003_raw_sha256": sha(raw), "runtime003_sha256": sha(runtime)})
    print(json.dumps({"status": "PASS", "html_sha256": sha(payload), "cache_bytes_identical": cache_identical}))


def check(phase):
    spec = importlib.util.spec_from_file_location("profile_viewer_check", HERE / "check_review.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OUT = OUT
    sys.argv = [str(HERE / "check_review.py"), "--phase", phase]
    module.main()


def publish():
    payload = (OUT / "review.html").read_bytes()
    DEST.mkdir(parents=True, exist_ok=True)
    target = DEST / "review.html"
    if target.exists() and target.read_bytes() != payload:
        raise ValueError("existing-published-review-differs")
    target.write_bytes(payload)
    with urlopen(URL, timeout=10) as response:
        if response.read() != payload:
            raise ValueError("served-review-differs")
    save(OUT / "publication.json", {"url": URL, "destination": str(target), "html_sha256": sha(payload), "served_bytes_identical": True})
    print(URL)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["build", "smoke", "regression", "publish"])
    action = parser.parse_args().action
    {"build": build, "smoke": lambda: check("smoke"), "regression": lambda: check("regression"), "publish": publish}[action]()
