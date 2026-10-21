"""Verify the fourth two-frame feedback pass against its frozen baseline."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASELINE_PATH = HERE / "review-data-before-feedback-round4.json"
CURRENT_PATH = HERE / "review-data.json"
FEEDBACK_PATH = HERE / "feedback-2026-09-24-round4.json"
OUTPUT_PATH = HERE / "feedback-round4-selection-record.json"

TARGET_KEYS = frozenset(
    {
        "SLEVEJM2.BMP-009",
        "SLEVEJM3.BMP-004",
    }
)
EXPECTED_ASSET_COUNT = 72


class VerificationError(AssertionError):
    """Raised when the selection record does not prove the intended change."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise VerificationError(f"required file is missing: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise VerificationError(f"expected a JSON object: {path}")
    return value


def asset_map(document: dict[str, Any], source: Path) -> dict[str, dict[str, Any]]:
    assets = document.get("assets")
    if not isinstance(assets, list):
        raise VerificationError(f"assets must be a list: {source}")
    result: dict[str, dict[str, Any]] = {}
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            raise VerificationError(f"asset {index} must be an object: {source}")
        key = asset.get("key")
        if not isinstance(key, str) or not key:
            raise VerificationError(f"asset {index} has no valid key: {source}")
        if key in result:
            raise VerificationError(f"duplicate asset key {key}: {source}")
        result[key] = asset
    return result


def selection_identity(asset: dict[str, Any], key: str) -> tuple[int, str]:
    version = asset.get("version")
    selected_raw = asset.get("selected_raw")
    if not isinstance(version, int) or version < 1:
        raise VerificationError(f"{key}: version must be a positive integer")
    if not isinstance(selected_raw, dict):
        raise VerificationError(f"{key}: selected_raw must be an object")
    digest = selected_raw.get("sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        raise VerificationError(f"{key}: selected_raw.sha256 is invalid")
    return version, digest


def unchanged_mismatches(
    baseline: dict[str, dict[str, Any]],
    current: dict[str, dict[str, Any]],
    unchanged_keys: set[str],
) -> list[dict[str, Any]]:
    mismatches: list[dict[str, Any]] = []
    for key in sorted(unchanged_keys):
        before_version, before_sha = selection_identity(baseline[key], key)
        after_version, after_sha = selection_identity(current[key], key)
        if after_version != before_version:
            mismatches.append(
                {
                    "key": key,
                    "field": "version",
                    "expected": before_version,
                    "actual": after_version,
                }
            )
        if after_sha != before_sha:
            mismatches.append(
                {
                    "key": key,
                    "field": "selected_raw.sha256",
                    "expected": before_sha,
                    "actual": after_sha,
                }
            )
    return mismatches


def assert_unchanged(
    baseline: dict[str, dict[str, Any]],
    current: dict[str, dict[str, Any]],
    unchanged_keys: set[str],
) -> None:
    failures = unchanged_mismatches(baseline, current, unchanged_keys)
    if failures:
        labels = ", ".join(f"{item['key']}:{item['field']}" for item in failures)
        raise VerificationError(
            f"unchanged-frame guard found {len(failures)} mismatch(es): {labels}"
        )


def run_negative_control(
    baseline: dict[str, dict[str, Any]],
    current: dict[str, dict[str, Any]],
    unchanged_keys: set[str],
) -> dict[str, Any]:
    witness_key = sorted(unchanged_keys)[0]
    mutated = copy.deepcopy(current)
    original_sha = mutated[witness_key]["selected_raw"]["sha256"]
    replacement_sha = "0" * 64 if original_sha != "0" * 64 else "f" * 64
    mutated[witness_key]["selected_raw"]["sha256"] = replacement_sha

    failures = unchanged_mismatches(baseline, mutated, unchanged_keys)
    expected_label = f"{witness_key}:selected_raw.sha256"
    if len(failures) != 1:
        raise VerificationError(
            "negative control did not produce exactly one unchanged-frame failure"
        )
    if failures[0]["key"] != witness_key or failures[0]["field"] != "selected_raw.sha256":
        raise VerificationError(
            f"negative control named the wrong binding: {failures[0]}"
        )

    guard_fired = False
    failure_message = ""
    try:
        assert_unchanged(baseline, mutated, unchanged_keys)
    except VerificationError as error:
        guard_fired = True
        failure_message = str(error)
    if not guard_fired or expected_label not in failure_message:
        raise VerificationError("negative control was not caught by the real guard")

    return {
        "mutation": (
            f"Changed {witness_key} selected_raw.sha256 in memory, then restored it "
            "by discarding the copied data."
        ),
        "guard_fired": True,
        "failure_count": 1,
        "detected_binding": expected_label,
        "failure_message": failure_message,
        "source_files_modified": False,
    }


def repo_file(relative_path: str, label: str) -> Path:
    if not isinstance(relative_path, str) or not relative_path:
        raise VerificationError(f"{label}: path is missing")
    candidate = (ROOT / relative_path).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError as error:
        raise VerificationError(f"{label}: path escapes the repository: {relative_path}") from error
    if not candidate.is_file():
        raise VerificationError(f"{label}: file is missing: {relative_path}")
    return candidate


def require_hash(path: Path, expected: Any, label: str) -> str:
    if not isinstance(expected, str) or len(expected) != 64:
        raise VerificationError(f"{label}: expected SHA-256 is invalid")
    actual = sha256(path)
    if actual != expected:
        raise VerificationError(
            f"{label}: SHA-256 mismatch, expected {expected}, got {actual}"
        )
    return actual


def assert_builtin_imagegen(document: dict[str, Any], name: str, key: str) -> None:
    if document.get("tool") != "image_gen.imagegen":
        raise VerificationError(f"{key}: {name} is not an imagegen artifact")
    mode = document.get("mode")
    if name == "request":
        if mode not in (None, "built-in"):
            raise VerificationError(f"{key}: request claims non-built-in mode {mode!r}")
    elif mode != "built-in":
        raise VerificationError(f"{key}: record is not a built-in imagegen artifact")


def run_provenance_negative_control(current: dict[str, dict[str, Any]]) -> dict[str, Any]:
    witness_key = sorted(TARGET_KEYS)[0]
    resource, frame = witness_key.rsplit("-", 1)
    version, _ = selection_identity(current[witness_key], witness_key)
    record_path = repo_file(
        f"art/cartoon/mermaid-departures-and-dates-batch-v1/generation/"
        f"{resource}/{frame}-record-v{version}.json",
        f"{witness_key} provenance negative control",
    )
    mutated = copy.deepcopy(load_object(record_path))
    mutated["mode"] = "external"

    guard_fired = False
    failure_message = ""
    try:
        assert_builtin_imagegen(mutated, "record", witness_key)
    except VerificationError as error:
        guard_fired = True
        failure_message = str(error)
    expected_message = f"{witness_key}: record is not a built-in imagegen artifact"
    if not guard_fired or failure_message != expected_message:
        raise VerificationError("provenance negative control was not caught by the real guard")

    return {
        "mutation": (
            f"Changed {witness_key} generation-record mode to external in memory, then "
            "restored it by discarding the copied data."
        ),
        "guard_fired": True,
        "failure_message": failure_message,
        "source_files_modified": False,
    }


def verify_target(
    key: str,
    baseline: dict[str, Any],
    current: dict[str, Any],
) -> dict[str, Any]:
    resource, frame = key.rsplit("-", 1)
    version, output_sha = selection_identity(current, key)
    baseline_version, baseline_sha = selection_identity(baseline, key)
    if version <= baseline_version:
        raise VerificationError(
            f"{key}: selected version {version} must be newer than baseline {baseline_version}"
        )
    if output_sha == baseline_sha:
        raise VerificationError(f"{key}: selected output SHA-256 did not change")
    if current.get("resource") != resource or current.get("frame") != frame:
        raise VerificationError(f"{key}: review-data resource/frame identity mismatch")
    if current.get("status") != "generated":
        raise VerificationError(f"{key}: selected status must be generated")

    prefix = "art/cartoon/mermaid-departures-and-dates-batch-v1/generation"
    expected_output = f"{prefix}/{resource}/{frame}-generated-v{version}.png"
    expected_request = f"{prefix}/{resource}/{frame}-v{version}-request.json"
    expected_record = f"{prefix}/{resource}/{frame}-record-v{version}.json"

    selected_raw = current.get("selected_raw")
    request_ref = current.get("request")
    record_ref = current.get("generation_record")
    if not all(isinstance(item, dict) for item in (selected_raw, request_ref, record_ref)):
        raise VerificationError(f"{key}: selected output/request/record metadata is incomplete")
    if selected_raw.get("path") != expected_output:
        raise VerificationError(f"{key}: selected output path is not bound to version {version}")
    if request_ref.get("path") != expected_request:
        raise VerificationError(f"{key}: request path is not bound to version {version}")
    if record_ref.get("path") != expected_record:
        raise VerificationError(f"{key}: record path is not bound to version {version}")
    expected_url = f"generation/{resource}/{frame}-generated-v{version}.png"
    if current.get("url") != expected_url:
        raise VerificationError(f"{key}: review URL is not bound to the selected output")

    output_path = repo_file(expected_output, f"{key} output")
    request_path = repo_file(expected_request, f"{key} request")
    record_path = repo_file(expected_record, f"{key} record")
    require_hash(output_path, selected_raw.get("sha256"), f"{key} output")
    request_sha = require_hash(request_path, request_ref.get("sha256"), f"{key} request")
    record_sha = require_hash(record_path, record_ref.get("sha256"), f"{key} record")

    request = load_object(request_path)
    record = load_object(record_path)
    expected_identity = {"resource": resource, "frame": frame, "version": version}
    for name, document in (("request", request), ("record", record)):
        actual_identity = {field: document.get(field) for field in expected_identity}
        if actual_identity != expected_identity:
            raise VerificationError(
                f"{key}: {name} identity mismatch, expected {expected_identity}, "
                f"got {actual_identity}"
            )
        assert_builtin_imagegen(document, name, key)

    record_output = record.get("output")
    record_request = record.get("request")
    if not isinstance(record_output, dict) or not isinstance(record_request, dict):
        raise VerificationError(f"{key}: record output/request binding is incomplete")
    if record_output.get("path") != expected_output or record_output.get("sha256") != output_sha:
        raise VerificationError(f"{key}: record does not bind the selected output")
    if record_request.get("path") != expected_request or record_request.get("sha256") != request_sha:
        raise VerificationError(f"{key}: record does not bind the selected request")

    record_image = record.get("image")
    if not isinstance(record_image, dict):
        raise VerificationError(f"{key}: record image metadata is missing")
    for field in ("canvas", "mode", "alpha_range", "alpha8_bounds"):
        if record_image.get(field) != selected_raw.get(field):
            raise VerificationError(f"{key}: record image.{field} does not match review data")
    if record.get("appearance_approval") is not None:
        raise VerificationError(f"{key}: generation record must not claim appearance approval")
    if record.get("production_integrated") is not False:
        raise VerificationError(f"{key}: generation record must not claim production integration")
    if record.get("native_motion_checked") is not False:
        raise VerificationError(f"{key}: generation record must not claim native-motion review")

    return {
        "baseline_version": baseline_version,
        "selected_version": version,
        "baseline_output_sha256": baseline_sha,
        "selected_output": {"path": expected_output, "sha256": output_sha},
        "request": {"path": expected_request, "sha256": request_sha},
        "record": {"path": expected_record, "sha256": record_sha},
    }


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> None:
    baseline_document = load_object(BASELINE_PATH)
    current_document = load_object(CURRENT_PATH)
    feedback = load_object(FEEDBACK_PATH)
    baseline = asset_map(baseline_document, BASELINE_PATH)
    current = asset_map(current_document, CURRENT_PATH)

    if len(TARGET_KEYS) != 2:
        raise VerificationError(f"target list has {len(TARGET_KEYS)} keys instead of 2")
    feedback_keys = feedback.get("assets")
    if not isinstance(feedback_keys, dict) or set(feedback_keys) != TARGET_KEYS:
        raise VerificationError("feedback file keys do not exactly match the 2 verifier targets")
    if len(baseline) != EXPECTED_ASSET_COUNT or len(current) != EXPECTED_ASSET_COUNT:
        raise VerificationError(
            f"expected {EXPECTED_ASSET_COUNT} baseline and current assets, "
            f"got {len(baseline)} and {len(current)}"
        )
    if set(baseline) != set(current):
        missing = sorted(set(baseline) - set(current))
        added = sorted(set(current) - set(baseline))
        raise VerificationError(f"asset keyset changed; missing={missing}, added={added}")
    if not TARGET_KEYS <= set(current):
        raise VerificationError(f"target keys are absent: {sorted(TARGET_KEYS - set(current))}")

    unchanged_keys = set(current) - TARGET_KEYS
    if len(unchanged_keys) != 70:
        raise VerificationError(f"expected 70 unchanged keys, got {len(unchanged_keys)}")

    negative_control = run_negative_control(baseline, current, unchanged_keys)
    print(f"negative control passed: {negative_control['failure_message']}")
    assert_unchanged(baseline, current, unchanged_keys)

    provenance_negative_control = run_provenance_negative_control(current)
    print(
        "provenance negative control passed: "
        f"{provenance_negative_control['failure_message']}"
    )

    full_entry_changes = {key for key in current if current[key] != baseline[key]}
    if full_entry_changes != TARGET_KEYS:
        missing = sorted(TARGET_KEYS - full_entry_changes)
        unexpected = sorted(full_entry_changes - TARGET_KEYS)
        raise VerificationError(
            f"full review entries did not change at exactly the 2 targets; "
            f"missing={missing}, unexpected={unexpected}"
        )

    selection_changes = {
        key
        for key in current
        if selection_identity(current[key], key) != selection_identity(baseline[key], key)
    }
    if selection_changes != TARGET_KEYS:
        missing = sorted(TARGET_KEYS - selection_changes)
        unexpected = sorted(selection_changes - TARGET_KEYS)
        raise VerificationError(
            f"selected version/output did not change at exactly the 2 targets; "
            f"missing={missing}, unexpected={unexpected}"
        )

    corrected = {
        key: verify_target(key, baseline[key], current[key]) for key in sorted(TARGET_KEYS)
    }
    report = {
        "schema_version": 1,
        "status": "round4_selection_verified",
        "baseline_asset_count": len(baseline),
        "current_asset_count": len(current),
        "corrected_frame_count": len(corrected),
        "unchanged_frame_count": len(unchanged_keys),
        "exact_changed_keys": sorted(full_entry_changes),
        "selection_changed_keys": sorted(selection_changes),
        "corrected_frames": corrected,
        "unchanged_guard": {
            "fields": ["version", "selected_raw.sha256"],
            "verified_frame_count": len(unchanged_keys),
            "mismatches": [],
        },
        "negative_control": negative_control,
        "provenance_negative_control": provenance_negative_control,
        "inputs": {
            relative(path): sha256(path)
            for path in (BASELINE_PATH, CURRENT_PATH, FEEDBACK_PATH, Path(__file__).resolve())
        },
        "appearance_approval": None,
        "production_integrated": False,
        "native_motion_checked": False,
        "limits": (
            "This record proves selection scope and artifact bindings. It does not prove "
            "appearance acceptance, native motion, or production integration."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "corrected_frame_count": report["corrected_frame_count"],
                "unchanged_frame_count": report["unchanged_frame_count"],
                "negative_control_guard_fired": negative_control["guard_fired"],
                "output": relative(OUTPUT_PATH),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except VerificationError as error:
        print(f"round-four verification failed: {error}")
        raise SystemExit(1) from error
