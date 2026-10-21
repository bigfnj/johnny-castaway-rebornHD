"""Build the focused eight-frame review for the third feedback pass."""

from __future__ import annotations

import copy
import hashlib
import html
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT_DIR = HERE
TARGET_KEYS = [
    "SLEVEJM2.BMP-009",
    "SLEVEJM3.BMP-004",
    "SMDATE1.BMP-002",
    "SMDATE6.BMP-006",
    "SMDATE6.BMP-018",
    "SMDATE6.BMP-019",
    "SMDATE6.BMP-020",
    "SMDATE6.BMP-021",
]
EXPECTED_VERSIONS = {
    "SLEVEJM2.BMP-009": 6,
    "SLEVEJM3.BMP-004": 5,
    "SMDATE1.BMP-002": 5,
    "SMDATE6.BMP-006": 11,
    "SMDATE6.BMP-018": 3,
    "SMDATE6.BMP-019": 3,
    "SMDATE6.BMP-020": 3,
    "SMDATE6.BMP-021": 4,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pin(path: Path) -> dict[str, str]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha256(path),
    }


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def href_from_pin(value: dict[str, Any]) -> str:
    source = ROOT / value["path"]
    return os.path.relpath(source, OUTPUT_DIR).replace("\\", "/")


def assert_exact_targets(keys: Any, label: str) -> None:
    if not isinstance(keys, (list, dict, set, frozenset, tuple)):
        raise ValueError(f"{label} does not contain a key collection")
    actual = set(keys)
    expected = set(TARGET_KEYS)
    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        raise ValueError(
            f"{label} does not match the eight focused targets; "
            f"missing={missing}, unexpected={unexpected}"
        )


def run_target_negative_control() -> dict[str, Any]:
    mutated = TARGET_KEYS + ["SMDATE6.BMP-999"]
    fired = False
    message = ""
    try:
        assert_exact_targets(mutated, "negative-control targets")
    except ValueError as error:
        fired = True
        message = str(error)
    if not fired or "SMDATE6.BMP-999" not in message:
        raise ValueError("Focused-target negative control was not caught by the real guard")
    return {
        "mutation": "Added SMDATE6.BMP-999 to an in-memory copy of the focused key list.",
        "guard_fired": True,
        "failure_message": message,
        "source_files_modified": False,
    }


def card(row: dict[str, Any]) -> str:
    key = row["key"]
    resource = row["resource"]
    frame = row["frame"]
    label = f"{resource.removesuffix('.BMP')} {frame}"
    request_href = href_from_pin(row["request"])
    record_href = href_from_pin(row["generation_record"])
    note = html.escape(row["review_note"])
    cartoon_href = html.escape(row["url"], quote=True)
    original_href = html.escape(row["original_url"], quote=True)
    return (
        f'<figure id="{html.escape(key, quote=True)}" '
        f'data-filter="{html.escape(key + " " + resource + " generated", quote=True)}">'
        f'<figcaption>{html.escape(label)}<span>{html.escape(resource.removesuffix(".BMP"))}</span></figcaption>'
        '<p class="state generated">Ready for appearance review</p>'
        f'<p class="review-note">{note}</p>'
        f'<a class="art" href="{cartoon_href}" target="_blank" rel="noopener" '
        f'aria-label="Open cartoon {html.escape(key, quote=True)}">'
        f'<canvas width="720" height="440" data-key="{html.escape(key, quote=True)}" '
        f'data-kind="cartoon" aria-label="Cartoon {html.escape(key, quote=True)}"></canvas></a>'
        '<p class="links">'
        f'<a href="{html.escape(request_href, quote=True)}" target="_blank" rel="noopener">Exact saved request</a>'
        ' &middot; '
        f'<a href="{html.escape(record_href, quote=True)}" target="_blank" rel="noopener">Generation record</a>'
        '</p>'
        f'<details open><summary>Original {html.escape(key)}</summary>'
        f'<a class="original" href="{original_href}" target="_blank" rel="noopener">'
        f'<canvas width="720" height="250" data-key="{html.escape(key, quote=True)}" '
        f'data-kind="original" aria-label="Original {html.escape(key, quote=True)}"></canvas>'
        '</a></details></figure>'
    )


def main() -> None:
    source_path = HERE / "review-data-before-feedback-round4.json"
    feedback_path = HERE / "feedback-2026-09-24-round3.json"
    selection_record_path = HERE / "feedback-round3-selection-record.json"
    template_path = HERE / "review-template.html"
    source = load_object(source_path)
    feedback = load_object(feedback_path)
    selection_record = load_object(selection_record_path)

    feedback_assets = feedback.get("assets")
    assert_exact_targets(feedback_assets, "round-three feedback")
    assert_exact_targets(
        selection_record.get("exact_changed_keys"),
        "round-three selection proof",
    )
    negative_control = run_target_negative_control()
    assets = source.get("assets")
    if not isinstance(assets, list):
        raise ValueError("Main review data has no asset list")
    by_key = {row["key"]: row for row in assets}
    if len(by_key) != len(assets):
        raise ValueError("Main review data contains duplicate keys")

    rows = []
    for key in TARGET_KEYS:
        if key not in by_key:
            raise ValueError(f"Focused target is missing from the main review: {key}")
        row = copy.deepcopy(by_key[key])
        if row.get("status") != "generated":
            raise ValueError(f"Focused target is not ready: {key}")
        if row.get("version") != EXPECTED_VERSIONS[key]:
            raise ValueError(
                f"Focused target {key} has version {row.get('version')}, "
                f"expected {EXPECTED_VERSIONS[key]}"
            )
        for field in ("selected_raw", "original_reference", "request", "generation_record"):
            if not isinstance(row.get(field), dict):
                raise ValueError(f"Focused target lacks {field}: {key}")
        if not isinstance(row.get("review_note"), str) or not row["review_note"]:
            raise ValueError(f"Focused target lacks a review note: {key}")
        proof = selection_record.get("corrected_frames", {}).get(key)
        if not isinstance(proof, dict):
            raise ValueError(f"Selection proof lacks focused target: {key}")
        bindings = (
            ("selected_raw", "selected_output"),
            ("request", "request"),
            ("generation_record", "record"),
        )
        for row_field, proof_field in bindings:
            if row[row_field].get("path") != proof.get(proof_field, {}).get("path"):
                raise ValueError(f"Focused target {key} has a {row_field} path mismatch")
            if row[row_field].get("sha256") != proof.get(proof_field, {}).get("sha256"):
                raise ValueError(f"Focused target {key} has a {row_field} hash mismatch")
        row["url"] = href_from_pin(row["selected_raw"])
        row["original_url"] = href_from_pin(row["original_reference"])
        rows.append(row)

    counts = dict(Counter(row["status"] for row in rows))
    summary = "8 updated drawings; 0 pending; 0 failed. 8 original comparisons."
    data = {"assets": rows, "counts": counts, "summary": summary}

    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["resource"], []).append(row)
    nav = []
    for resource, group_rows in grouped.items():
        title = resource.removesuffix(".BMP")
        nav.append(
            f'<a href="#{html.escape(group_rows[0]["key"], quote=True)}">'
            f'{html.escape(title)} ({len(group_rows)})</a>'
        )
    sections = [
        '<section><h2 id="updates">Updated requests</h2><div class="grid">'
        + "\n".join(card(row) for row in rows)
        + "</div></section>"
    ]

    template = template_path.read_text(encoding="utf-8")
    template = template.replace(
        "<title>72 mermaid departure and date drawings</title>",
        "<title>8 round-three drawing updates</title>",
    ).replace(
        "<h1>72 mermaid departure and date drawings</h1>",
        "<h1>8 round-three drawing updates</h1>",
    ).replace(
        "Each cartoon is paired with its exact original. Compare pose, facing direction, eye visibility, overlapping limbs and prop placement. The group links and frame filter jump to individual drawings.",
        "Only the drawings changed by the latest feedback pass are shown here. Each final candidate is paired with its exact original.",
    ).replace(
        'The departure animal is the established gray shark. Open the <a href="../shark-identity-corrections-v1/review.html">27 shark corrections with previous drawings beside them</a> for the focused comparison.',
        'Open the <a href="review-full.html">full 72-drawing archival gallery</a> or the <a href="feedback-2026-09-24-round3.json">exact saved feedback</a>.',
    ).replace(
        "<body>",
        '<body data-review-data="review-data-round3.json">',
    )
    page = (
        template.replace("{{NAV}}", "".join(nav))
        .replace("{{SECTIONS}}", "\n".join(sections))
        .replace("{{SUMMARY}}", html.escape(summary))
    )

    data_path = OUTPUT_DIR / "review-data-round3.json"
    page_path = OUTPUT_DIR / "review-round3.html"
    record_path = OUTPUT_DIR / "review-round3-record.json"
    data_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    page_path.write_text(page, encoding="utf-8")
    record = {
        "schema_version": 1,
        "status": "awaiting_appearance_review",
        "selected_frame_count": len(rows),
        "exact_keys": TARGET_KEYS,
        "page": pin(page_path),
        "data": pin(data_path),
        "feedback": pin(feedback_path),
        "selection_proof": pin(selection_record_path),
        "builder": pin(Path(__file__).resolve()),
        "target_negative_control": negative_control,
        "selected_assets": [
            {
                "key": row["key"],
                "version": row["version"],
                "output": row["selected_raw"],
                "request": row["request"],
                "generation_record": row["generation_record"],
            }
            for row in rows
        ],
        "appearance_approval": None,
        "production_integrated": False,
        "native_motion_checked": False,
    }
    optional_evidence = {
        "browser_validation": HERE / "browser-review-round3-focused.json",
        "browser_negative_control": HERE / "browser-review-round3-focused-negative-control.json",
        "browser_screenshot": HERE / "browser-review-round3-focused.png",
        "full_archive_browser_validation": HERE / "browser-review-round3-full-archive.json",
    }
    for field, path in optional_evidence.items():
        if path.is_file():
            record[field] = pin(path)
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"Built focused round-three review with {len(rows)} cards and {len(rows) * 2} image panels.")


if __name__ == "__main__":
    main()
