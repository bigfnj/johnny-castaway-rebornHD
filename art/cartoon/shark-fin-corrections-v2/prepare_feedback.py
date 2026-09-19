import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREVIOUS = HERE.parent / "sharks-batch-v1"

def pin(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

rows = []
for frame, name, version in [
    ("026", "codex-clipboard-c8cc371c-8140-4a88-974c-78dcfabbccdd.png", 1),
    ("035", "codex-clipboard-456a18e9-f811-4edf-8c61-4d97385f7a9a.png", 2),
]:
    source = Path("C:/Users/Admin/AppData/Local/Temp") / name
    screenshot = HERE / "reference/user-feedback" / f"{frame}.png"
    screenshot.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, screenshot)
    assert source.read_bytes() == screenshot.read_bytes()
    rows.append({"resource": "GJFFFOOD.BMP", "frame": frame, "user_screenshot": pin(screenshot),
                 "prior_raw": pin(PREVIOUS / f"generation/GJFFFOOD.BMP/{frame}-generated-v{version}.png"),
                 "original": pin(PREVIOUS / f"reference/original/GJFFFOOD.BMP/{frame}.png"),
                 "nearest8": pin(PREVIOUS / f"reference/nearest8/GJFFFOOD.BMP/{frame}.png")})
feedback = {"schema_version": 1, "date": "2026-09-19", "status": "corrections requested; no new appearance approval",
            "user_request": 'the "tongue" you made is actually a fin, its closer to the design of 027 & 028 make sense? 035, its hard to tell what is going on, its the sharks body mostly in the water with his "fin" sticking out, similar in design to 036.',
            "frames": rows, "prior_review": pin(PREVIOUS / "review-record.json"),
            "interpretation": {"026": "Gray fin beneath the snout, related to027/028; remove the mistaken pink tongue and gaping mouth treatment.",
                               "035": "Mostly submerged shark body with a clearly exposed fin, using036 as the adjacent anatomy reference; reduce the obscuring wave."},
            "unmentioned_frames": "No additional appearance approval inferred.", "production_package_changed": False}
(HERE / "feedback.json").write_text(json.dumps(feedback, indent=2) + "\n", encoding="utf-8")
print("Saved two exact feedback screenshots and prior selections")
