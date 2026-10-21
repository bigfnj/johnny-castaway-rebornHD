"""Build the focused six-card review for the fifth feedback pass."""

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
SELECTED_KEY = "SLEVEJM2.BMP-009"
CANDIDATE_SOURCE_KEY = "SLEVEJM3.BMP-004"
CANDIDATE_VARIANTS = (
    ("eye-a", "Eye A", 7, "Soft diagonal almond with rounded tips."),
    ("eye-b", "Eye B", 8, "Lopsided bean/egg with a fuller lower curve."),
    ("eye-c", "Eye C", 9, "Asymmetric slanted oval tapering toward the snout."),
    ("eye-d", "Eye D", 10, "Soft tilted teardrop with a rounded outer corner."),
    ("eye-e", "Eye E", 11, "Curved almond/wedge closest to the pixel original."),
)
CARD_KEYS = [SELECTED_KEY] + [
    f"{CANDIDATE_SOURCE_KEY}-{suffix}" for suffix, _label, _version, _note in CANDIDATE_VARIANTS
]
FEEDBACK_KEYS = {SELECTED_KEY, CANDIDATE_SOURCE_KEY}


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


def assert_exact_card_keys(keys: Any, label: str) -> None:
    if not isinstance(keys, (list, tuple)):
        raise ValueError(f"{label} does not contain an ordered card-key collection")
    actual_list = list(keys)
    actual = set(actual_list)
    expected = set(CARD_KEYS)
    if len(actual_list) != len(actual):
        raise ValueError(f"{label} contains duplicate card keys")
    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        raise ValueError(
            f"{label} does not match the six focused card keys; "
            f"missing={missing}, unexpected={unexpected}"
        )


def run_card_key_negative_control() -> dict[str, Any]:
    mutated = CARD_KEYS + ["SMDATE6.BMP-999"]
    fired = False
    message = ""
    try:
        assert_exact_card_keys(mutated, "negative-control cards")
    except ValueError as error:
        fired = True
        message = str(error)
    if not fired or "SMDATE6.BMP-999" not in message:
        raise ValueError("Focused-card negative control was not caught by the real guard")
    return {
        "mutation": "Added SMDATE6.BMP-999 to an in-memory copy of the focused card-key list.",
        "guard_fired": True,
        "failure_message": message,
        "source_files_modified": False,
    }


def require_pin(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} is not a pinned artifact")
    path_value = value.get("path")
    expected_sha = value.get("sha256")
    if not isinstance(path_value, str) or not isinstance(expected_sha, str):
        raise ValueError(f"{label} has incomplete path/hash metadata")
    path = ROOT / path_value
    if not path.is_file():
        raise ValueError(f"{label} is missing: {path_value}")
    actual_sha = sha256(path)
    if actual_sha != expected_sha:
        raise ValueError(
            f"{label} hash mismatch: expected {expected_sha}, got {actual_sha}"
        )
    return copy.deepcopy(value)


def card(row: dict[str, Any]) -> str:
    key = row["key"]
    resource = row["resource"]
    label = row["display_label"]
    request_href = href_from_pin(row["request"])
    record_href = href_from_pin(row["generation_record"])
    note = html.escape(row["review_note"])
    cartoon_href = html.escape(row["url"], quote=True)
    original_href = html.escape(row["original_url"], quote=True)
    state_class = "selected" if row["review_state"] == "selected-correction" else "alternative"
    state_text = (
        "Selected correction, ready for appearance review"
        if row["review_state"] == "selected-correction"
        else "Unselected eye alternative, ready for your choice"
    )
    if row.get("appearance_approval"):
        state_class = "approved"
        state_text = "Appearance approved by user on September 25, 2026"
    elif row.get("choice_completed"):
        state_text = "Unselected alternative"
    return (
        f'<figure id="{html.escape(key, quote=True)}" '
        f'data-filter="{html.escape(key + " " + resource + " " + label + " generated", quote=True)}">'
        f'<figcaption>{html.escape(label)}<span>{html.escape(resource.removesuffix(".BMP"))}</span></figcaption>'
        f'<p class="state generated {state_class}">{html.escape(state_text)}</p>'
        f'<p class="review-note">{note}</p>'
        f'<a class="art" href="{cartoon_href}" target="_blank" rel="noopener" '
        f'aria-label="Open cartoon {html.escape(label, quote=True)}">'
        f'<canvas width="720" height="440" data-key="{html.escape(key, quote=True)}" '
        f'data-kind="cartoon" aria-label="Cartoon {html.escape(label, quote=True)}"></canvas></a>'
        '<p class="links">'
        f'<a href="{html.escape(request_href, quote=True)}" target="_blank" rel="noopener">Exact saved request</a>'
        ' &middot; '
        f'<a href="{html.escape(record_href, quote=True)}" target="_blank" rel="noopener">Generation record</a>'
        '</p>'
        f'<details open><summary>Original {html.escape(row["original_label"])}</summary>'
        f'<a class="original" href="{original_href}" target="_blank" rel="noopener">'
        f'<canvas width="720" height="250" data-key="{html.escape(key, quote=True)}" '
        f'data-kind="original" aria-label="Original {html.escape(row["original_label"], quote=True)}"></canvas>'
        '</a></details></figure>'
    )


def main() -> None:
    source_path = HERE / "review-data.json"
    feedback_path = HERE / "feedback-2026-09-24-round5.json"
    selection_record_path = HERE / "feedback-round5-selection-record.json"
    template_path = HERE / "review-template.html"
    source = load_object(source_path)
    feedback = load_object(feedback_path)
    selection_record = load_object(selection_record_path)
    approval_path = HERE / "acceptance/appearance-round5-2026-09-25.json"
    approvals = load_object(approval_path)["approved_assets"] if approval_path.is_file() else {}

    def approved_row(row: dict[str, Any], source_key: str) -> bool:
        approved = approvals.get(source_key, {})
        return (
            approved.get("version") == row.get("version")
            and approved.get("output", {}).get("path") == row["selected_raw"]["path"]
            and approved.get("output", {}).get("sha256") == row["selected_raw"]["sha256"]
        )

    feedback_assets = feedback.get("assets")
    if not isinstance(feedback_assets, dict) or set(feedback_assets) != FEEDBACK_KEYS:
        raise ValueError("Round-five feedback does not match the two requested source frames")
    if feedback.get("requested_candidate_versions") != {
        CANDIDATE_SOURCE_KEY: [version for _suffix, _label, version, _note in CANDIDATE_VARIANTS]
    }:
        raise ValueError("Round-five feedback does not request the expected five eye versions")
    if selection_record.get("status") != "round5_selection_and_candidates_verified":
        raise ValueError("Round-five selection proof has not passed")
    if selection_record.get("exact_changed_keys") != [SELECTED_KEY]:
        raise ValueError("Round-five selection proof does not isolate the selected correction")

    negative_control = run_card_key_negative_control()
    assets = source.get("assets")
    if not isinstance(assets, list):
        raise ValueError("Main review data has no asset list")
    by_key = {row["key"]: row for row in assets}
    if len(by_key) != len(assets):
        raise ValueError("Main review data contains duplicate keys")
    for source_key in FEEDBACK_KEYS:
        if source_key not in by_key:
            raise ValueError(f"Focused source is missing from the main review: {source_key}")

    selected_source = by_key[SELECTED_KEY]
    if selected_source.get("status") != "generated" or selected_source.get("version") != 8:
        raise ValueError("SLEVEJM2.BMP-009 v8 is not the current selected correction")
    selected_proof = selection_record.get("corrected_frames", {}).get(SELECTED_KEY)
    if not isinstance(selected_proof, dict):
        raise ValueError("Round-five selection proof lacks SLEVEJM2.BMP-009")
    for row_field, proof_field in (
        ("selected_raw", "selected_output"),
        ("request", "request"),
        ("generation_record", "record"),
    ):
        row_pin = require_pin(selected_source.get(row_field), f"{SELECTED_KEY} {row_field}")
        proof_pin = require_pin(selected_proof.get(proof_field), f"{SELECTED_KEY} proof {proof_field}")
        if row_pin.get("path") != proof_pin.get("path") or row_pin.get("sha256") != proof_pin.get("sha256"):
            raise ValueError(f"{SELECTED_KEY} {row_field} does not match the selection proof")

    selected_row = copy.deepcopy(selected_source)
    selected_row.update(
        {
            "display_label": "SLEVEJM2 009",
            "original_label": "SLEVEJM2.BMP-009",
            "review_state": "selected-correction",
            "selected_for_main_review": True,
            "url": href_from_pin(selected_row["selected_raw"]),
            "original_url": href_from_pin(selected_row["original_reference"]),
        }
    )
    if approved_row(selected_row, SELECTED_KEY):
        selected_row["appearance_approval"] = pin(approval_path)
    rows = [selected_row]

    candidate_source = by_key[CANDIDATE_SOURCE_KEY]
    choice_completed = approved_row(candidate_source, CANDIDATE_SOURCE_KEY)
    if not choice_completed and candidate_source.get("version") != 6:
        raise ValueError("SLEVEJM3.BMP-004 selection needs an approval matching its exact output")
    original_reference = require_pin(
        candidate_source.get("original_reference"), f"{CANDIDATE_SOURCE_KEY} original"
    )
    candidate_proofs = selection_record.get("unselected_candidate_variations", {}).get(
        CANDIDATE_SOURCE_KEY
    )
    if not isinstance(candidate_proofs, dict):
        raise ValueError("Round-five selection proof lacks the eye alternatives")

    for suffix, eye_label, version, description in CANDIDATE_VARIANTS:
        proof = candidate_proofs.get(f"v{version}")
        if not isinstance(proof, dict) or proof.get("version") != version:
            raise ValueError(f"Round-five selection proof lacks {CANDIDATE_SOURCE_KEY} v{version}")
        output_pin = require_pin(proof.get("output"), f"{CANDIDATE_SOURCE_KEY} v{version} output")
        request_pin = require_pin(proof.get("request"), f"{CANDIDATE_SOURCE_KEY} v{version} request")
        record_pin = require_pin(proof.get("record"), f"{CANDIDATE_SOURCE_KEY} v{version} record")
        synthetic_key = f"{CANDIDATE_SOURCE_KEY}-{suffix}"
        rows.append(
            {
                "key": synthetic_key,
                "source_key": CANDIDATE_SOURCE_KEY,
                "resource": "SLEVEJM3.BMP",
                "frame": "004",
                "version": version,
                "status": "generated",
                "display_label": f"SLEVEJM3 004, {eye_label}",
                "original_label": "SLEVEJM3.BMP-004",
                "review_state": "unselected-alternative",
                "selected_for_main_review": False,
                "review_note": f"{eye_label}, v{version}. {description} This is an unselected alternative; SLEVEJM3 004 remains selected at v6 until you choose.",
                "selected_raw": output_pin,
                "request": request_pin,
                "generation_record": record_pin,
                "original_reference": original_reference,
                "url": href_from_pin(output_pin),
                "original_url": href_from_pin(original_reference),
            }
        )
        row = rows[-1]
        if choice_completed:
            row["choice_completed"] = True
            row["review_note"] = f"{eye_label}, v{version}. {description} Unselected alternative. Eye A v7 is approved and selected."
        if approved_row(row, CANDIDATE_SOURCE_KEY) and choice_completed:
            row["review_state"] = "approved-selected-eye"
            row["selected_for_main_review"] = True
            row["appearance_approval"] = pin(approval_path)
            row["review_note"] = f"{eye_label}, v{version}. {description} Approved and selected on September 25, 2026."

    assert_exact_card_keys([row["key"] for row in rows], "focused review rows")
    selected_count = sum(row["selected_for_main_review"] is True for row in rows)
    unselected_count = sum(row["review_state"] == "unselected-alternative" for row in rows)
    approved_count = sum(bool(row.get("appearance_approval")) for row in rows)
    if selected_count != (2 if choice_completed else 1):
        raise ValueError("Focused selected count does not match the recorded eye choice")
    if unselected_count != (4 if choice_completed else 5):
        raise ValueError("Focused alternative count does not match the recorded eye choice")

    counts = dict(Counter(row["status"] for row in rows))
    summary = "6 candidates; 0 pending; 0 failed. 6 original comparisons."
    if choice_completed:
        summary = f"{approved_count} approved selections; {unselected_count} unselected eye alternatives. 6 original comparisons."
    data = {
        "assets": rows,
        "counts": counts,
        "summary": summary,
        "selected_correction_count": selected_count,
        "unselected_alternative_count": unselected_count,
        "appearance_approved_count": approved_count,
    }

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
        '<section><h2 id="updates">Round-five correction and eye choices</h2><div class="grid">'
        + "\n".join(card(row) for row in rows)
        + "</div></section>"
    ]

    template = template_path.read_text(encoding="utf-8")
    template = template.replace(
        "<title>72 mermaid departure and date drawings</title>",
        "<title>6 round-five review candidates</title>",
    ).replace(
        "<h1>72 mermaid departure and date drawings</h1>",
        "<h1>6 round-five review candidates</h1>",
    ).replace(
        "Each cartoon is paired with its exact original. Compare pose, facing direction, eye visibility, overlapping limbs and prop placement. The group links and frame filter jump to individual drawings.",
        "The selected SLEVEJM2 009 correction appears first. The five SLEVEJM3 004 cards are unselected eye alternatives, each paired with the same exact original for comparison.",
    ).replace(
        'The departure animal is the established gray shark. Open the <a href="../shark-identity-corrections-v1/review.html">27 shark corrections with previous drawings beside them</a> for the focused comparison.',
        'Open the <a href="review-round4.html">previous two-frame review</a>, the <a href="review-full.html">full 72-drawing archival gallery</a>, or the <a href="feedback-2026-09-24-round5.json">exact saved feedback</a>. SLEVEJM3 004 remains selected at v6 until an eye alternative is chosen.',
    ).replace(
        "<body>",
        '<body data-review-data="review-data-round5.json">',
    )
    page = (
        template.replace("{{NAV}}", "".join(nav))
        .replace("{{SECTIONS}}", "\n".join(sections))
        .replace("{{SUMMARY}}", html.escape(summary))
    )
    if choice_completed:
        page = page.replace(
            "The selected SLEVEJM2 009 correction appears first. The five SLEVEJM3 004 cards are unselected eye alternatives, each paired with the same exact original for comparison.",
            "SLEVEJM2 009 v8 and SLEVEJM3 004 Eye A v7 are approved and selected. The four remaining eye alternatives are retained below for reference.",
        ).replace(
            "SLEVEJM3 004 remains selected at v6 until an eye alternative is chosen.",
            'SLEVEJM3 004 Eye A v7 is selected. <a href="acceptance/appearance-round5-2026-09-25.json">Saved appearance approval</a>.',
        ).replace("6 round-five review candidates", "Round-five approved selections and alternatives")

    data_path = OUTPUT_DIR / "review-data-round5.json"
    page_path = OUTPUT_DIR / "review.html"
    record_path = OUTPUT_DIR / "review-round5-record.json"
    data_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    page_path.write_text(page, encoding="utf-8")
    record = {
        "schema_version": 1,
        "status": "two_appearance_approved_selections" if approved_count == 2 else "awaiting_eye_choice_and_appearance_review",
        "card_count": len(rows),
        "selected_correction_count": selected_count,
        "unselected_variation_count": unselected_count,
        "exact_card_keys": CARD_KEYS,
        "page": pin(page_path),
        "data": pin(data_path),
        "feedback": pin(feedback_path),
        "selection_proof": pin(selection_record_path),
        "builder": pin(Path(__file__).resolve()),
        "card_key_negative_control": negative_control,
        "selected_correction": {
            "key": selected_row["key"],
            "version": selected_row["version"],
            "output": selected_row["selected_raw"],
            "request": selected_row["request"],
            "generation_record": selected_row["generation_record"],
        },
        "unselected_variations": [
            {
                "card_key": row["key"],
                "source_key": row["source_key"],
                "version": row["version"],
                "output": row["selected_raw"],
                "request": row["request"],
                "generation_record": row["generation_record"],
            }
            for row in rows[1:] if not row["selected_for_main_review"]
        ],
        "appearance_approval": pin(approval_path) if approved_count else None,
        "approved_selections": [
            {"key": row.get("source_key", row["key"]), "version": row["version"], "output": row["selected_raw"]}
            for row in rows if row.get("appearance_approval")
        ],
        "production_integrated": False,
        "native_motion_checked": False,
        "limits": (
            "The five SLEVEJM3.BMP-004 variations are unselected alternatives. This record "
            "does not select an eye, claim appearance approval, prove native motion, or prove "
            "production integration."
        ),
    }
    if approved_count:
        record["limits"] = "Appearance approval applies only to the two exact saved selections. Production integration and native motion remain unchecked."
    optional_evidence = {
        "browser_validation": HERE / "browser-review-round5-focused.json",
        "browser_negative_control": HERE / "browser-review-round5-focused-negative-control.json",
        "browser_screenshot": HERE / "browser-review-round5-focused.png",
        "full_archive_browser_validation": HERE / "browser-review-round5-full-archive.json",
    }
    if approved_count:
        optional_evidence = {
            "browser_validation": HERE / "browser-review-round5-approved.json",
            "browser_screenshot": HERE / "browser-review-round5-approved.png",
        }
    for field, path in optional_evidence.items():
        if path.is_file():
            record[field] = pin(path)
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(
        "Built focused round-five review with "
        f"{len(rows)} cards, {len(rows) * 2} image panels, "
        f"{selected_count} selected corrections, {approved_count} approved, and {unselected_count} unselected eye alternatives."
    )


if __name__ == "__main__":
    main()
