"""Preserve measurements and actual image-generation ancestry for pose drafts."""
import hashlib
import json
from pathlib import Path

import PIL
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUTPUTS = {
    (1, 1): r"C:\Users\Admin\.codex\generated_images\01a0a1f0-5ca9-70b3-88cd-a31f4f736e75\exec-b84995a1-a357-41d6-84fb-2a48746ca66e.png",
    (3, 1): r"C:\Users\Admin\.codex\generated_images\01a0a1f0-5ca9-70b3-88cd-a31f4f736e75\exec-82b8b034-4ced-44f6-822b-829c9b4e4100.png",
    (1, 2): r"C:\Users\Admin\.codex\generated_images\01a0a1f0-5ca9-70b3-88cd-a31f4f736e75\exec-d7597a2b-574f-4bc9-80fe-eb300e2fd536.png",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    attempts = []
    for (frame, version), cache_path in OUTPUTS.items():
        raw = HERE / f"{frame:03}-profile-v{version}.png"
        data = raw.read_bytes()
        assert data == Path(cache_path).read_bytes(), f"cache-copy:{raw.name}"
        call_path = HERE / f"{frame:03}-call-v{version}.json"
        call = json.loads(call_path.read_bytes())
        original = (HERE / "reference" / f"{frame:03}-original-nearest8.png")
        appearance = ROOT / "art/cartoon/walk-pilot/front-arrival-v1/remaining-waits-v1/000-profile-v1.png"
        refs = []
        preserved_refs = [original, appearance] if version == 1 else [HERE / "001-profile-v1.png", original]
        for actual, preserved in zip(call["referenced_image_paths"], preserved_refs):
            content = preserved.read_bytes()
            assert content == Path(actual).read_bytes(), f"reference-copy:{preserved.name}"
            refs.append({"actual_path": actual, "preserved_path": preserved.relative_to(ROOT).as_posix(), "sha256": sha(content)})
        with Image.open(raw) as image:
            alpha = image.getchannel("A")
            bounds = {str(t): list(alpha.point(lambda a: 255 if a >= t else 0).getbbox()) for t in [1, 8, 128]}
            y = bounds["128"][1]
            xs = [x for x in range(image.width) if alpha.getpixel((x, y)) >= 128]
            cap = [(min(xs) + max(xs) + 1) / 2, y]
            measurement = {"canvas": list(image.size), "mode": image.mode, "alpha_range": list(alpha.getextrema()), "bounds_exclusive_by_alpha_threshold": bounds, "cap_raw": cap}
        status = "Draft only; human pose, motion and runtime acceptance pending."
        if frame == 1 and version == 1:
            status = "Rejected for runtime fit:2.75HD screen-right overhang. Preserved as the used ancestor for targeted toe editv2."
        attempts.append({"frame": frame, "version": version, "raw_output": raw.name, "raw_sha256": sha(data), "tool_output_path": cache_path,
                         "cache_bytes_identical": True, "call": call_path.name, "call_sha256": sha(call_path.read_bytes()),
                         "prompt_utf8_sha256": sha(call["prompt"].encode("utf-8")), "actual_reference_order": refs,
                         "measurements": measurement, "status": status})
    record = {"schema_version": 1, "tool": "built-in image_gen.imagegen", "model_identifier": "not exposed by tool",
              "generation_seed": "not exposed by tool", "measurement_pillow_version": PIL.__version__, "attempts": attempts,
              "appearance_approval": "art/cartoon/walk-pilot/front-arrival-v1/remaining-waits-v1/approval-v1.json",
              "reference_rule": "Supplied-original pose and occlusion; approved000 appearance. Diagnostic colors and ground shadows are not palette or sole landmarks.",
              "scope": "Generation provenance only. These drafts do not change the32-asset production pack."}
    (HERE / "provenance-v1.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "PASS", "attempts": [{"frame": a["frame"], "measurements": a["measurements"]} for a in attempts]}, indent=2))


if __name__ == "__main__":
    main()
