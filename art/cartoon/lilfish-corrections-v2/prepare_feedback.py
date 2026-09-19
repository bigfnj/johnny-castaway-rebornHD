"""Retain the exact user screenshots and source bindings for five fish fixes."""
import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR = ROOT / "art/cartoon/gulls-fish-batch-v1"

def pin(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

shots = {
    "000": "f568f753-c274-491c-83eb-f68076752b0b",
    "001": "0dde8f22-f372-4e41-86cd-ed49251de57b",
    "006": "66746e72-eb72-486d-b479-714403e945ba",
    "008": "be4c5a84-f46a-4146-85be-ac27775743f9",
}
notes = {
    "000": "The fish is reversed relative to the original eye and appears to have two mouths. Correct anatomical orientation and give it one mouth.",
    "001": "The fish is backward. It should look as though it jumped up and is beginning to fall backward onto its back.",
    "006": "The right fish wears sunglasses in the original.",
    "007": "The middle fish wears sunglasses in the original.",
    "008": "Four fish, one wearing sunglasses. Remove the duplicated-body anatomy so each fish has one coherent body and tail.",
}
(HERE / "reference/user-feedback").mkdir(parents=True, exist_ok=True)
rows = []
for frame, note in notes.items():
    v = 2 if frame == "008" else 1
    row = {"resource": "LILFISH.BMP", "frame": frame, "user_note": note,
           "original": pin(PRIOR / f"reference/original/LILFISH.BMP/{frame}.png"),
           "nearest8": pin(PRIOR / f"reference/nearest8/LILFISH.BMP/{frame}.png"),
           "prior_raw": pin(PRIOR / f"generation/LILFISH.BMP/{frame}-generated-v{v}.png")}
    if frame in shots:
        source = Path("C:/Users/Admin/AppData/Local/Temp") / f"codex-clipboard-{shots[frame]}.png"
        target = HERE / "reference/user-feedback" / f"{frame}.png"
        shutil.copyfile(source, target)
        assert target.read_bytes() == source.read_bytes()
        row["user_screenshot"] = pin(target)
    rows.append(row)
record = {
    "schema_version": 1, "status": "targeted_corrections_in_progress", "date": "2026-09-18",
    "user_text": '000 you got it reversed, look at the eye, the fish is reversed, you also seemed to give it "two" mouths, you should correct for that as well. 001 you got it backwards again, look at the eye, in this instance the fish looks like it jumped up and is just starting to fall backwards onto its back. 006 the right fish is wearing sunglasses. 007 the middle fish is wearing sunglasses. 008 is odd, you have 4 fish, one should be wearing the sunglasses, but you gave one of the fishes "two" bodies, which is odd.',
    "source_review": pin(PRIOR / "review-record.json"),
    "source_record": pin(PRIOR / "reference/source.json"),
    "frames": rows, "approval": None,
    "scope": "Only these five corrections. Unmentioned drawings gain no approval from this feedback.",
    "native_testing": "Deferred to bulk integration"
}
(HERE / "feedback.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print("Retained four user screenshots and five exact source/prior bindings")
