"""Publish only the pending direct-composite 004 into the existing review pages.

Run after record.json, request.json and the final composite PNG are ready.
The unfinished color-sequence builder is deliberately not invoked.
"""
import argparse
import copy
import importlib.util
import json
import os
from pathlib import Path


HERE = Path(__file__).resolve().parent
VISITOR = HERE.parent
ART = VISITOR.parent
ROOT = ART.parents[1]
MERMAID = ART / "mermaid-expression-corrections-v1"
KEY = "SSUZY1.BMP-004"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sequence_pin(info):
    return {"path": info["path"], "sha256": info["sha256"],
            "url": os.path.relpath(ROOT / info["path"], VISITOR).replace(os.sep, "/")}


def main(check_only=False):
    spec = importlib.util.spec_from_file_location("composite_review_builder", MERMAID / "build_review.py")
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    composite = builder.load_direct_composite_004(HERE / "record.json")
    before = read_json(VISITOR / "color-sequence.json")
    before_still = read_json(MERMAID / "review-data.json")
    selected_path = VISITOR / "selected-versions.json"
    selected_bytes = selected_path.read_bytes()

    # Work from the deployed schema-2 viewer, preserving its sequence and other art.
    assert before["schema_version"] == 2, "Expected the deployed schema-2 sequence"
    assert len(before["steps"]) == 26 and before["nominal_excerpt_ms"] == 5840
    assert "ground_bottle" not in before
    assert {key for key, sprite in before["sprites"].items() if sprite.get("candidate")} == {"4", "5"}
    after = copy.deepcopy(before)
    output = composite["output"]
    after["sprites"]["4"]["candidate"] = {
        **sequence_pin(output), "canvas": output["canvas"], "bounds": output["alpha8_bounds"],
        "record": sequence_pin(composite["record"]),
        "request": sequence_pin(composite["request"]),
        "version": composite["version"], "artifact_kind": "direct-png-composite",
        "appearance_approval": None, "review_status": "awaiting_review",
        "review_label": f'Direct composite v{composite["version"]}: leg placement awaiting review',
    }
    after["color_correction_status"] = (
        "004 direct composite leg-placement candidate and 005 regenerated color candidate await review. "
        "Approved imported selections remain unchanged.")
    after["display_notes"][0] = (
        "Candidate mode uses the direct composite leg-placement correction for 004 and the regenerated "
        "color candidate for 005, both awaiting review. Every other frame uses its unchanged selected "
        "drawing. Approved selection mode uses the imported 004 and 005 PNGs.")
    after["display_notes"][1] = (
        "This viewer does not alter PNG pixels, approval records, selectors or runtime assets. "
        "Links open the exact displayed PNGs and the saved composite or generation requests.")

    expected_rows = [builder.build_row(source, composite) for source in builder.make_sources()]
    before_rows = {row["key"]: row for row in before_still["assets"]}
    assert len(expected_rows) == len(before_rows) == 103
    for row in expected_rows:
        if row["key"] != KEY:
            assert row == before_rows[row["key"]], f'Unrelated still-review change: {row["key"]}'
    for frame, sprite in after["sprites"].items():
        assert sprite["cartoon"] == before["sprites"][frame]["cartoon"]
        if frame != "4":
            assert sprite == before["sprites"][frame]
    assert after["steps"] == before["steps"] and after["clips"] == before["clips"]

    template = (VISITOR / "color-sequence-template.html").read_text(encoding="utf-8")
    assert template.count("__SEQUENCE_DATA__") == 1
    embedded = json.dumps(after).replace("</", "<\\/")
    page = template.replace("__SEQUENCE_DATA__", embedded)
    if not check_only:
        (VISITOR / "color-sequence.json").write_text(json.dumps(after, indent=2) + "\n", encoding="utf-8")
        (VISITOR / "color-sequence-review.html").write_text(page, encoding="utf-8")
        builder.main(HERE / "record.json")
        assert selected_path.read_bytes() == selected_bytes

    print(json.dumps({
        "mode": "check-only" if check_only else "published",
        "candidate": output["path"], "candidate_sha256": output["sha256"],
        "status": "direct composite awaiting appearance review",
        "selected_pins_unchanged": True, "frame_005_unchanged": True,
        "other_still_rows_unchanged": 102, "steps": 26, "duration_ms": 5840,
        "ground_bottle_added": False,
    }))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="Prepare and verify without writing review pages")
    main(parser.parse_args().check_only)
