"""Refresh the main batch's shark overrides from the focused review.

The default mode is a read-only dry run. Pass ``--write`` only after
``build_review.py`` has rebuilt the focused review from the current selections.
This script deliberately does not run either main-batch builder and does not
modify the main batch's selected versions or review notes.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BATCH = HERE.parent / "mermaid-departures-and-dates-batch-v1"
FOCUSED_PATH = HERE / "review-data.json"
PLAN_PATH = HERE / "correction-plan.json"
SELECTIONS_PATH = HERE / "selected-corrections.json"
TARGET_PATH = BATCH / "shark-correction-overrides.json"


class RefreshError(RuntimeError):
    """Focused data is incomplete, stale, or inconsistent."""


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_file(pin: dict[str, Any], label: str) -> Path:
    if not isinstance(pin, dict):
        raise RefreshError(f"{label}: expected a pinned-file object")
    relative = pin.get("path")
    expected_hash = pin.get("sha256")
    if not isinstance(relative, str) or not relative:
        raise RefreshError(f"{label}: missing path")
    if not isinstance(expected_hash, str) or len(expected_hash) != 64:
        raise RefreshError(f"{label}: missing SHA-256")
    path = (ROOT / relative).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as error:
        raise RefreshError(f"{label}: path escapes repository: {relative}") from error
    if not path.is_file():
        raise RefreshError(f"{label}: file does not exist: {relative}")
    actual_hash = sha256(path)
    if actual_hash != expected_hash:
        raise RefreshError(
            f"{label}: hash mismatch for {relative}: {actual_hash} != {expected_hash}"
        )
    return path


def expected_versions(plan: dict[str, Any], selections: dict[str, Any]) -> dict[str, int]:
    entries = plan.get("entries")
    if plan.get("schema_version") != 1 or not isinstance(entries, list):
        raise RefreshError("correction-plan.json must be schema 1 with an entries list")
    result: dict[str, int] = {}
    for entry in entries:
        key = entry.get("key")
        if not isinstance(key, str) or key in result:
            raise RefreshError(f"correction plan has an invalid or duplicate key: {key!r}")
        version = selections.get(key, entry.get("version"))
        if not isinstance(version, int) or isinstance(version, bool) or version < 1:
            raise RefreshError(f"{key}: selected version must be a positive integer")
        result[key] = version
    if len(result) != 27:
        raise RefreshError(f"correction plan must contain 27 entries, found {len(result)}")
    unexpected = set(selections) - set(result)
    if unexpected:
        raise RefreshError(f"selected-corrections.json has unknown keys: {sorted(unexpected)}")
    return result


def collect_assets(
    focused: dict[str, Any], expected: dict[str, int]
) -> dict[str, dict[str, Any]]:
    entries = focused.get("entries")
    if focused.get("schema_version") != 1 or not isinstance(entries, list):
        raise RefreshError("review-data.json must be schema 1 with an entries list")
    rows: dict[str, dict[str, Any]] = {}
    for row in entries:
        key = row.get("key")
        if not isinstance(key, str) or key in rows:
            raise RefreshError(f"focused review has an invalid or duplicate key: {key!r}")
        rows[key] = row
    if set(rows) != set(expected):
        raise RefreshError(
            "focused review keys do not exactly match the 27 correction-plan keys"
        )

    assets: dict[str, dict[str, Any]] = {}
    for key in expected:
        row = rows[key]
        resource = row.get("resource")
        frame = row.get("frame")
        if key != f"{resource}-{frame}":
            raise RefreshError(f"{key}: resource/frame identity mismatch")
        if row.get("version") != expected[key]:
            raise RefreshError(
                f"{key}: focused review is stale; expected selected version "
                f"{expected[key]}, found {row.get('version')!r}. Run build_review.py first."
            )
        if row.get("status") not in {"awaiting_review", "appearance_approved"}:
            raise RefreshError(f"{key}: correction is not ready for review")
        review_note = row.get("visual_review")
        if not isinstance(review_note, str) or not review_note.strip():
            raise RefreshError(f"{key}: visual_review is empty")

        output = row.get("output")
        record = row.get("record")
        repo_file(output, f"{key} output")
        record_path = repo_file(record, f"{key} record")
        record_document = read_json(record_path)
        if (
            record_document.get("resource") != resource
            or str(record_document.get("frame")).zfill(3) != str(frame)
            or record_document.get("version") != row.get("version")
        ):
            raise RefreshError(f"{key}: generation record identity/version mismatch")
        record_output = record_document.get("output")
        if not isinstance(record_output, dict) or (
            record_output.get("path") != output.get("path")
            or record_output.get("sha256") != output.get("sha256")
        ):
            raise RefreshError(f"{key}: generation record does not bind the selected output")

        assets[key] = {
            "version": row["version"],
            "review_note": review_note,
            "output": output,
            "record": record,
        }
    return assets


def build_payload(
    focused: dict[str, Any],
    plan: dict[str, Any],
    selections: dict[str, Any],
    existing: dict[str, Any],
) -> dict[str, Any]:
    if existing.get("schema_version") != 1 or not isinstance(existing.get("assets"), dict):
        raise RefreshError("existing shark-correction-overrides.json must be schema 1")
    expected = expected_versions(plan, selections)
    assets = collect_assets(focused, expected)
    existing_keys = set(existing["assets"])
    if existing_keys != set(assets):
        raise RefreshError(
            "refusing to add or drop focused override entries; existing and focused key sets differ"
        )
    payload = copy.deepcopy(existing)
    payload["assets"] = assets
    return payload


def changed_keys(existing: dict[str, Any], payload: dict[str, Any]) -> list[str]:
    return [
        key
        for key, value in payload["assets"].items()
        if existing["assets"].get(key) != value
    ]


def self_test(
    focused: dict[str, Any],
    plan: dict[str, Any],
    selections: dict[str, Any],
    existing: dict[str, Any],
) -> None:
    build_payload(focused, plan, selections, existing)
    mutated = copy.deepcopy(focused)
    mutated["entries"][0]["version"] += 1
    try:
        build_payload(mutated, plan, selections, existing)
    except RefreshError as error:
        if "focused review is stale" not in str(error):
            raise RefreshError(f"self-test failed with the wrong guard: {error}") from error
    else:
        raise RefreshError("self-test failed: stale focused data was accepted")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="atomically replace the main shark override file after validation",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="also prove that a stale-version mutation is rejected",
    )
    args = parser.parse_args()

    focused = read_json(FOCUSED_PATH)
    plan = read_json(PLAN_PATH)
    selections = read_json(SELECTIONS_PATH)
    existing_bytes = TARGET_PATH.read_bytes()
    existing = json.loads(existing_bytes.decode("utf-8-sig"))
    payload = build_payload(focused, plan, selections, existing)
    changes = changed_keys(existing, payload)

    if args.self_test:
        self_test(focused, plan, selections, existing)

    if args.write:
        if TARGET_PATH.read_bytes() != existing_bytes:
            raise RefreshError("override file changed during validation; refusing to overwrite it")
        encoded = (json.dumps(payload, indent=2) + "\n").encode("utf-8")
        temporary = TARGET_PATH.with_suffix(TARGET_PATH.suffix + ".tmp")
        try:
            temporary.write_bytes(encoded)
            temporary.replace(TARGET_PATH)
        finally:
            temporary.unlink(missing_ok=True)
        mode = "wrote"
    else:
        mode = "dry run; would update"

    suffix = " self-test passed." if args.self_test else ""
    print(
        f"Validated all {len(payload['assets'])} focused shark overrides; "
        f"{mode} {len(changes)} entries: {', '.join(changes) if changes else '(none)'}.{suffix}"
    )


if __name__ == "__main__":
    main()
