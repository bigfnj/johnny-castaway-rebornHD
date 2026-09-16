"""Capture actual raw image ancestry and decisions for the first full-cycle drafts."""
import hashlib
import json
from pathlib import Path

from PIL import Image
import PIL

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CACHE = Path(r"C:\Users\Admin\.codex\generated_images\01a0a1f0-5ca9-70b3-88cd-a31f4f736e75")
ATTEMPTS = [
    (2, 1, "484afa80-0ee5-4b86-a8b7-13b2b96353c1", "Technical candidate; forward far-arm continuity review pending."),
    (4, 1, "2914e0c6-b1b7-49e5-b4f1-d3aa9dc1f810", "Rejected:8.8HD right overhang and forward toes angled up instead of down-right; ancestor forv2."),
    (5, 1, "47874f99-840b-40b2-9e0c-cf9767674c8d", "Rejected:7.75HD right overhang; ancestor for forward shin/foot repositioning."),
    (4, 2, "46cfbd39-1658-4afc-ad54-433053a724b5", "Technical candidate; rear far-arm continuity review pending."),
    (5, 2, "3f7f6c9f-5422-490d-8692-c45640b2f4bc", "Rejected:returned dark/glowing background had material alpha outside the figure, corrupting cap detection; ancestor for extractionv3."),
    (6, 1, "9e6c5c16-549d-41ca-a2c4-d62c96b66b5c", "Technical candidate; user explicitly preferred retaining its background arm. No whole-gait approval inferred."),
    (5, 3, "ab491d13-1b1a-48ec-8263-0a10fe2f6458", "Technical candidate after image-tool transparency extraction; rear far-arm review pending."),
    (6, 2, "7c5d3a2e-c01e-41f0-aa03-3353b97db2c4", "Unselected hidden-arm experiment. User said the background arm fits, so006-v1 is retained."),
    (7, 1, "4d1d1087-3818-418a-a669-8250ba6c8d72", "Technical candidate; passing-pose far-arm occlusion will be assessed in motion."),
    (8, 1, "ad8851bc-c080-47b9-a6a8-235714bcff3b", "Rejected:8.2HD right overhang; ancestor for forward shin/foot repositioning."),
    (8, 2, "3b380946-f13f-43bc-826f-26c34614bca2", "Technically fitting foot correction; superseded for arm-direction review byv3. No final pose approval."),
    (8, 3, "f89bae5d-2742-437a-9192-48939804a6cd", "User-requested forward far-arm study. Human arm review pending;0.65HD right-foot overhang prevents runtime export."),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    attempts = []
    for frame, version, tool_id, status in ATTEMPTS:
        stem = f"{frame:03}"
        raw_path = HERE / f"{stem}-profile-v{version}.png"
        raw = raw_path.read_bytes()
        call_path = HERE / f"{stem}-call-v{version}.json"
        call_bytes = call_path.read_bytes()
        call = json.loads(call_bytes)
        cache = CACHE / f"exec-{tool_id}.png"
        assert cache.read_bytes() == raw, f"cache-copy:{raw_path.name}"
        refs = []
        for actual in call["referenced_image_paths"]:
            path = Path(actual)
            preserved = path.relative_to(ROOT).as_posix()
            refs.append({"actual_path": actual, "preserved_path": preserved, "sha256": sha(path.read_bytes())})
        with Image.open(raw_path) as image:
            alpha = image.getchannel("A")
            bounds = {str(t): list(alpha.point(lambda a: 255 if a >= t else 0).getbbox()) for t in [1, 8, 128]}
            y = bounds["128"][1]
            xs = [x for x in range(image.width) if alpha.getpixel((x, y)) >= 128]
            measurement = {"canvas": list(image.size), "mode": image.mode, "alpha_range": list(alpha.getextrema()),
                           "bounds_exclusive_by_alpha_threshold": bounds, "first_alpha128_row_midpoint": [(min(xs) + max(xs) + 1) / 2, y],
                           "corner_alpha_tl_tr_bl_br": [alpha.getpixel(xy) for xy in [(0, 0), (image.width - 1, 0), (0, image.height - 1), (image.width - 1, image.height - 1)]]}
        attempts.append({"frame": frame, "version": version, "raw_output": raw_path.name, "raw_sha256": sha(raw),
                         "tool_output_path": str(cache), "cache_bytes_identical": True, "call": call_path.name,
                         "call_sha256": sha(call_bytes), "prompt_utf8_sha256": sha(call["prompt"].encode("utf-8")),
                         "actual_reference_order": refs, "measurements": measurement, "status": status})
    feedback = HERE / "arm-feedback-20260916.png"
    record = {"schema_version": 1, "tool": "built-in image_gen.imagegen", "model_identifier": "not exposed by tool",
              "generation_seed": "not exposed by tool", "measurement_pillow_version": PIL.__version__, "attempts": attempts,
              "earlier_generation_records": ["provenance-v1.json", "provenance003-v2.json"],
              "user_steering": ["much better proceed", "the background arm there fits",
                                "and on this pose, it feels like with the stride there should be a background arm  as well",
                                "maybe we need to revisit the arm on these walking poses"],
              "feedback_image": {"preserved_path": feedback.name, "sha256": sha(feedback.read_bytes()), "role": "User arm-direction feedback; not an input to the actual image-tool calls."},
              "scope": "Full profile family drafts, paused at008 arm-direction checkpoint. No complete gait, native candidate or production approval.",
              "reference_rule": "Original geometry controls pose; approved appearance guides identity. User far-arm direction supersedes prior blanket occlusion prompts.",
              "limits": ["Prompt invariants are requests, not evidence of byte-identical unchanged regions.",
                         "Alpha and cap observations are remeasured after every image call.005-v2's top row is contamination, not a valid cap.",
                         "No per-frame body resizing, anatomical warp, manual repainting or alpha hardening was used."]}
    (HERE / "cycle-provenance-v1.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "PASS", "attempts": len(attempts), "exact_raw_cache_copies": len(attempts), "generation_calls_and_reference_hashes_preserved": True}))


if __name__ == "__main__":
    main()
