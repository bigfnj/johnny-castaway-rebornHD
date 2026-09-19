"""Retain the two user-directed shape changes and their exact input artwork."""
import hashlib
import json
import shutil
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR = ROOT / "art/cartoon/lilfish-corrections-v2"
def pin(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
(HERE / "reference/user-feedback").mkdir(parents=True, exist_ok=True)
specs = [("000", "5ffb0d35-09a5-40ae-8bc9-dfd4c79efa16", 2), ("007", "14126a58-c48b-4c35-9f49-6e56cec53db5", 1)]
rows = []
for frame, clipboard, version in specs:
    source = Path("C:/Users/Admin/AppData/Local/Temp") / f"codex-clipboard-{clipboard}.png"
    target = HERE / f"reference/user-feedback/{frame}.png"
    shutil.copyfile(source, target)
    assert source.read_bytes() == target.read_bytes()
    rows.append({"frame": frame, "screenshot": pin(target),
                 "prior_raw": pin(PRIOR / f"generation/LILFISH.BMP/{frame}-generated-v{version}.png"),
                 "original": pin(ROOT / f"art/cartoon/gulls-fish-batch-v1/reference/original/LILFISH.BMP/{frame}.png")})
data = {"schema_version": 1, "date": "2026-09-19",
        "exact_user_text": 'the top right fish has to much of an elongated body, maybe just make it a 4th fish. in 000 that bump i circled in green looks like a 2nd mouth, smooth it out',
        "frames": rows, "prior_review": pin(PRIOR / "review-record.json"),
        "interpretation": {"000": "Smooth only the two-lobed crown above the eye into a rounded contour. Retain the actual left mouth and corrected body orientation.",
                           "007": "Screenshot identifies selected007. Split its overlong arched fish into two compact individual fish, giving four visible fish as suggested by the user."},
        "007_count_note": "Explicit art-direction alternative: four generated fish versus three in original007. Keep original source and native catch attribution unchanged; no runtime count acceptance is implied.",
        "approval": None, "native_testing": "Deferred to bulk integration"}
(HERE / "feedback.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
print("Saved two exact screenshots and input bindings")
