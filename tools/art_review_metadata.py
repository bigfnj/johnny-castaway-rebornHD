#!/usr/bin/env python3
"""Generate an original-first, offline review catalog for the approved pilot.

This reports evidence and differences; it never scores artistic correctness or
changes artwork. Existing art_common and inventory_scenes readers own ZIP/PNG
and RESOURCE framing. All paths in the generated document are repository-relative.
"""
import argparse
import json
import math
import re
import sys
import zipfile
from pathlib import Path

from art_common import ArtError, digest, inspect_png, read_json, safe_member, source_catalog
from inventory_scenes import resource_catalog, metadata, u16

PACK = "art/cartoon/pack.json"
WALK = "art/cartoon/walk-pilot/calm-focus-runtime-v1"
ACCEPTANCE = WALK + "/production-acceptance.json"
HISTORICAL_WALK = "art/cartoon/walk-pilot/directional-cycle-v1"
ROUTE_ACCEPTANCE = HISTORICAL_WALK + "/acceptance.json"
ISLAND = "art/cartoon/island-pilot-v1"
TIMING = ISLAND + "/review-evidence/capture-files-and-timing.json"
OUTPUT = "docs/knowledge-base/cartoon-art-metadata"
ORIGINAL = "docs/knowledge-base/cartoon-original-reference.json"
ORIGINAL_IDENTITY = "docs/knowledge-base/original-extractor-reference.json"
RECIPES = [WALK + "/recipe.json"] + [ISLAND + "/" + x + "/recipe.json" for x in (
    "palm-sand-cloud", "ocean-shadow-center-waves", "side-waves")]
HISTORICAL_REVIEW_REQUESTS = {
    "date": "2026-09-15", "basis": "user-visual-review-of-supplied-original-comparison",
    "preview": "local original-vs-cartoon-walk.html; original indices with port dump palette and index0 transparency",
    "not_automatically_verified": True,
    "observations": [
        {"id": "walk-024-trailing-right-foot", "frame": 24, "status": "correction-requested",
         "original_reference_observation": "The trailing anatomical right foot turns inward along the walking trajectory.",
         "variant_judgment": "The current Cartoon trailing right foot needs a more inward angle.",
         "correction_target": "Adjust that foot angle while preserving the original limb identity and trajectory."},
        {"id": "walk-028-leg-order", "frame": 28, "status": "correction-requested",
         "original_reference_observation": "Anatomical left foot is forward and right foot is back.",
         "variant_judgment": "The Cartoon pose reverses that leg order.",
         "correction_target": "Restore anatomical left-forward/right-back limb order."},
        {"id": "walk-029-leg-order", "frame": 29, "status": "correction-requested",
         "original_reference_observation": "Anatomical left foot is forward and right foot is back.",
         "variant_judgment": "The Cartoon pose reverses that leg order.",
         "correction_target": "Restore anatomical left-forward/right-back limb order."}],
    "awaiting_human_decision": [{"frames": [26, 27], "question": "Whether to reduce the higher rear-foot lift."}],
    "historical_approval_policy": "Earlier acceptance records remain unchanged. They do not close these new correction requests."}


def require(condition, label, reason):
    if not condition:
        raise ArtError(f"{label}: {reason}")


def text_fingerprint(data):
    """Same strict UTF-8/LF policy as the maintained scene inventory.

    Preserve BOM, other characters and whitespace; normalize CRLF and lone CR.
    """
    return digest(data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))


def keyed(rows, key, label):
    result = {row[key]: row for row in rows}
    require(len(result) == len(rows), label, "duplicate identity")
    return result


def family(path):
    if path.startswith("BMP/JOHNWALK.BMP/"):
        return "walk-e-to-a"
    if path.startswith("SCR/"):
        return "ocean-day"
    index = int(Path(path).stem)
    if 3 <= index <= 11:
        return ("shore-high-left", "shore-high-center", "shore-high-right")[(index - 3) // 3]
    return {0: "sand", 12: "palm", 13: "palm", 14: "shadow", 15: "cloud"}[index]


def original_canvas(resource, index):
    """Read original dimensions, not a variant's canvas or alpha bounds."""
    metadata(resource)
    if index is None:
        return resource["dimensions"]
    count = resource["image_count"]
    require(0 <= index < count, resource["name"], "original frame index out of range")
    data = resource["_payload"]
    return [u16(data, 18 + 2 * index), u16(data, 18 + 2 * count + 2 * index)]


def xpm_facts(data, label, sprite):
    """Read the production dump's limited XPM format, not arbitrary XPM syntax.

    Normalization is semantic: BMP palette index zero is transparent, regardless
    of its RGB; SCR has no transparent index. Palette colors stay unmodified.
    """
    strings = re.findall(r'^"([^"\\]*)"(?:,|\};?)?\r?$', data.decode("ascii"), re.M)
    require(bool(strings), label, "missing XPM strings")
    width, height, colors, chars = map(int, strings[0].split())
    require(chars == 1 and colors == 16 and width > 0 and height > 0, label, "unsupported dump header")
    require(len(strings) == 1 + colors + height, label, "XPM row count differs")
    palette = {}
    for line in strings[1:17]:
        match = re.fullmatch(r"(.) c #([0-9a-fA-F]{6})", line)
        require(match is not None and match[1] in "0123456789abcdef" and match[1] not in palette, label, "invalid XPM palette")
        palette[match[1]] = bytes.fromhex(match[2])
    rows = strings[17:]
    require(all(len(row) == width and set(row) <= set(palette) for row in rows), label, "invalid XPM pixel rows")
    rgba = bytearray()
    points = []
    for y, row in enumerate(rows):
        for x, code in enumerate(row):
            transparent = sprite and code == "0"
            rgba.extend(b"\0\0\0\0" if transparent else palette[code] + b"\xff")
            if not transparent:
                points.append((x, y))
    bounds = ([min(x for x, y in points), min(y for x, y in points),
               max(x for x, y in points) + 1, max(y for x, y in points) + 1] if points else None)
    return {"canvas": [width, height], "xpm_sha256": digest(data),
            "index_plane_sha256": digest(bytes(int(code, 16) for row in rows for code in row)),
            "rgba_sha256": digest(bytes(rgba)), "visible_bounds_exclusive": bounds,
            "transparent_index": 0 if sprite else None}


def validate_original_identity(inputs, engine, reference, label):
    expected = {row["name"]: row["original_sha256"] for row in reference["source_resources"]}
    require(inputs == expected, label, "resource identity is not the supplied original distribution")
    require(isinstance(engine, str) and re.fullmatch(r"[0-9a-f]{64}", engine) is not None,
            label, "decoder identity is not a SHA-256")


def import_original(root, dump):
    report_path = dump.parent / "report.json"
    report = read_json(report_path.read_bytes(), "original dump report")
    require(report["exit_code"] == 0, "original dump report", "dump did not succeed")
    reference = read_json((root / ORIGINAL_IDENTITY).read_bytes(), ORIGINAL_IDENTITY)
    validate_original_identity(report["input_sha256"], report["engine_sha256"], reference, "original dump report")
    pack = read_json((root / PACK).read_bytes(), PACK)
    assets = {}
    for path in pack["required_assets"]:
        parts = path.split("/")
        name = (f"BMP/{parts[1]}.{Path(parts[2]).stem}.xpm" if parts[0] == "BMP"
                else f"SCR/{Path(parts[1]).stem}.xpm")
        data = (dump / name).read_bytes()
        require(digest(data) == report["dump_sha256"][name], name, "original dump hash differs")
        assets[path] = {"dump_member": name, **xpm_facts(data, name, parts[0] == "BMP")}
    return {"schema_version": 1, "basis": "supplied-original-resources-decoded-by-production-engine",
            "input_sha256": report["input_sha256"], "decoder_executable_sha256": report["engine_sha256"],
            "dump_report_sha256": digest(report_path.read_bytes()),
            "normalization": "Index-plane hash uses one byte per pixel (0..15), row-major. BMP index0 becomes transparent RGBA0; SCR all indices opaque; all visible RGB unchanged. RGBA hash uses row-major bytes. Bounds are exclusive native pixels, not anatomical anchors.",
            "original_executable_render_parity": False, "assets": assets}


def registration(row, recipe, label):
    scale_spec = row.get("scale_exact", recipe.get("scale_exact"))
    scale = scale_spec["numerator"] / scale_spec["denominator"]
    canvas = row["runtime_canvas"]
    if row.get("transform_kind") == "opaque_resize":
        source = row["generated_canvas"]
        require(all(math.isclose(source[i] * scale, canvas[i], abs_tol=1e-9)
                    for i in (0, 1)), label, "nonuniform full-canvas resize")
        return {"kind": "full-canvas-resize", "scale": scale, "landmark": None,
                "landmark_residual_hd": None, "basis": "recorded-export-transform"}
    matrix = row["affine_forward"]
    require(matrix[0] == matrix[4] == scale and matrix[1] == matrix[3] == 0,
            label, "transform is not the declared uniform scale and translation")
    raw = row.get("cap_raw", row.get("landmark_raw"))
    target = row.get("cap_target_hd", row.get("landmark_target_local_hd"))
    actual = [matrix[0] * raw[0] + matrix[2], matrix[4] * raw[1] + matrix[5]]
    residual = [round(actual[i] - target[i], 10) for i in (0, 1)]
    require(all(abs(x) <= 1e-9 for x in residual), label, "recorded landmark does not map to target")
    return {"kind": "uniform-affine", "scale": scale, "affine_forward": matrix,
            "landmark": row.get("semantic_landmark", "visually retained cap feature"),
            "raw_xy": raw, "target_local_hd_xy": target, "landmark_residual_hd": residual,
            "basis": "recorded-measured-authoring-registration",
            "engine_anchor": False,
            "limitation": "Residual checks recipe arithmetic, not independent feature detection or pose fidelity."}


def walk_sequence(source, timing, acceptance):
    # Parse the named original-derived route, ending at its zero row. Do not
    # infer a repeating six-frame cycle: the last two entries are 025 then 027.
    lines = source.splitlines()
    start = next(i for i, line in enumerate(lines) if "// E to A" in line)
    route = []
    for line in lines[start:]:
        match = re.search(r"\{\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\s*\}", line)
        require(match is not None, "src/data/walk_data.h", "unrecognized E-to-A row")
        flip, x, y, frame = map(int, match.groups())
        if x == 0:
            break
        route.append({"position": len(route), "frame": frame, "flip_x": bool(flip),
                      "draw_logical_xy": [x - 1, y]})
    scope = acceptance["motion_scope"]
    require(len(route) == scope["positions"], "src/data/walk_data.h", "reviewed route length differs")
    pose_ms = scope["native_pose_ms"]
    require(set(timing["frames"]) == {"hd", "cartoon"}, TIMING, "both HD and Cartoon timelines are required")
    require(timing["status"] == "PASS", TIMING, "capture evidence is not successful")
    expected_end = len(route) * pose_ms + scope["endpoint_hold_added_ms"]
    require(timing["duration_ms"] == expected_end, TIMING, "review duration differs from poses plus endpoint hold")
    # The reviewed diagnostic has a hold-start display at 23*120 ms in addition
    # to pose starts and 160 ms background updates. This is not a universal VM
    # frame schedule or a claim about the original executable.
    display_times = sorted(set(range(0, len(route) * pose_ms + 1, pose_ms)) |
                           set(range(160, expected_end, 160)))
    for style, records in timing["frames"].items():
        require(len(records) == timing["frames_per_style"], TIMING, "display count differs")
        require(sum(r["duration_ms"] for r in records) == timing["duration_ms"], TIMING,
                "display durations do not cover review")
        first = {}
        end = 0
        for record in records:
            require(record["duration_ms"] > 0, TIMING, "display duration must be positive")
            require(record["logical_time_ms"] == end, TIMING, "display timeline is not contiguous")
            end += record["duration_ms"]
            position = record["pose_index_zero_based"]
            require(0 <= position < len(route), TIMING, "unknown route position")
            expected = route[position]["draw_logical_xy"] + [route[position]["frame"], 5]
            require(record["original_draw_xy_frame_slot"] == expected, TIMING, "capture draw differs from original route")
            require(position == min(record["logical_time_ms"] // pose_ms, len(route) - 1), TIMING,
                    "intervening display has the wrong pose")
            require(position == len(route) - 1 or end <= (position + 1) * pose_ms, TIMING,
                    "display interval crosses a pose boundary")
            first.setdefault(position, record["logical_time_ms"])
        require(first == {i: i * pose_ms for i in range(len(route))}, TIMING, "capture pose cadence differs")
        require([r["logical_time_ms"] for r in records] == display_times, TIMING, "reviewed background display schedule differs")
    for row in route:
        row["start_ms"] = row["position"] * pose_ms
    return {"id": "walk-e-to-a", "resource": "JOHNWALK.BMP", "basis": "original-derived-route-and-native-capture-record",
            "route_source": "src/data/walk_data.h", "draw_convention_source": "src/engine/walk.c:walkAnimate",
            "historical_route_acceptance": ROUTE_ACCEPTANCE, "historical_capture_evidence": TIMING,
            "capture_artwork_scope": "Historical directional-cycle-v1 pixels; these records establish route and cadence, not captures of the current Calm focus artwork.",
            "route": route, "pose_ms": pose_ms,
            "diagnostic_endpoint_hold_ms": scope["endpoint_hold_added_ms"],
            "captured_review_ms": timing["duration_ms"],
            "review_displays_per_style": timing["frames_per_style"],
            "travel_logical_xy": [route[-1]["draw_logical_xy"][i] - route[0]["draw_logical_xy"][i] for i in (0, 1)],
            "original_executable_timing_verified": False,
            "limitation": "120 ms is the port's reviewed native cadence; no original-executable timing calibration. The extra endpoint hold is diagnostic."}


def build(root):
    evidence = {}

    def load(path):
        data = (root / path).read_bytes()
        # Art records preserve exact bytes; maintained docs normalize checkout
        # newlines so Windows and Unix identify the same text.
        preserved = path.startswith(("art/cartoon/walk-pilot/", "art/cartoon/island-pilot-v1/"))
        evidence[path] = {"sha256": digest(data) if preserved else text_fingerprint(data), "hash_basis": "file-bytes" if preserved else "utf8-normalized-newlines"}
        return read_json(data, path)

    def source(path):
        data = (root / path).read_bytes()
        text = data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
        evidence[path] = {"sha256": text_fingerprint(data), "hash_basis": "utf8-normalized-newlines"}
        return text

    pack = load(PACK)
    accepted = load(ACCEPTANCE)
    require(pack.get("acceptance_record") == ACCEPTANCE, PACK, "active acceptance pointer differs")
    require(accepted.get("accepted") is True, ACCEPTANCE, "production acceptance is pending")
    current_review = accepted["current_human_review"]
    walk_acceptance = load(ROUTE_ACCEPTANCE)
    load(HISTORICAL_WALK + "/recipe.json")
    timing = load(TIMING)
    supplied_original = load(ORIGINAL)
    validate_original_identity(supplied_original["input_sha256"], supplied_original["decoder_executable_sha256"],
                               load(ORIGINAL_IDENTITY), ORIGINAL)
    recipes = {path: load(path) for path in RECIPES}
    source("docs/art-style-learnings.md")
    source("art/cartoon/motion-review.md")
    source("src/engine/island.c")
    source("src/engine/walk.c")
    route = walk_sequence(source("src/data/walk_data.h"), timing, walk_acceptance)
    packed = keyed(pack["assets"], "path", PACK)
    approved = keyed(accepted["accepted_assets"], "path", ACCEPTANCE)
    require(set(packed) == set(approved) == set(pack["required_assets"]), PACK, "accepted coverage differs")
    require(pack["runtime"]["scale"] == 2, PACK, "pilot scale differs")
    recipe_rows = {}
    for path, recipe in recipes.items():
        rows = keyed(recipe.get("frames", recipe.get("assets")), "path", path)
        require(set(rows) == set(recipe["required_assets"]), path, "recipe coverage differs")
        require(not set(rows).intersection(recipe_rows), path, "duplicate recipe coverage")
        for asset, row in rows.items():
            recipe_rows[asset] = (path, recipe, row)
        # Verify the complete raw source bundle once, then selected member bytes.
        bundle = recipe["source_bundle"]
        bundle_path = str(Path(path).parent / bundle["file"]).replace("\\", "/")
        require(digest((root / bundle_path).read_bytes()) == bundle["sha256"], bundle_path, "source bundle hash differs")
        evidence[bundle_path] = {"sha256": bundle["sha256"], "hash_basis": "file-bytes"}
        with zipfile.ZipFile(root / bundle_path) as z:
            for asset, row in rows.items():
                data = z.read(str(safe_member(row["generated_image"])))
                require(digest(data) == row["source_sha256"], asset, "selected raw hash differs")
                inspect_png(data, asset + " raw", expected=tuple(row["generated_canvas"]), decode=False)
        provenance = str(Path(path).with_name("provenance.json")).replace("\\", "/")
        load(provenance)
    require(set(recipe_rows) == set(packed), PACK, "recipe coverage differs from pilot")
    assets = []
    archive_path = "assets/scrantic_data.zip"
    with zipfile.ZipFile(root / archive_path) as archive:
        hd = source_catalog(archive)
        _, resources = resource_catalog(archive.read("data/RESOURCE.MAP"), archive.read("data/RESOURCE.001"))
        for member in ("data/RESOURCE.MAP", "data/RESOURCE.001", "data/hd/manifest.json"):
            evidence[archive_path + "!" + member] = {"sha256": digest(archive.read(member)), "hash_basis": "zip-member-bytes"}
        for asset, item in sorted(packed.items()):
            safe_member(asset)
            path, recipe, row = recipe_rows[asset]
            original = hd[asset]
            index = original.get("index")
            resource = resources[original["resource"]]
            logical = original_canvas(resource, index)
            native = supplied_original["assets"][asset]
            require(native["canvas"] == logical, asset, "supplied original canvas differs from bundled resource")
            require(logical == [original["logical_width"], original["logical_height"]], asset, "HD manifest differs from original dimensions")
            canvas = [n * pack["runtime"]["scale"] for n in logical]
            require(row["runtime_canvas"] == canvas, asset, "recipe canvas differs from original")
            require(item["source_sha256"] == original["source_sha256"], asset, "HD reference hash differs")
            require(item.get("recipe") == approved[asset].get("recipe") == path, asset, "active recipe pointer differs")
            require(item.get("review") == ACCEPTANCE, asset, "active review pointer differs")
            require(approved[asset]["sha256"] == item["sha256"] == row["candidate_png_sha256"], asset, "acceptance hash differs")
            member = "data/styles/cartoon/" + asset
            data = archive.read(member)
            require(digest(data) == item["sha256"], member, "production PNG hash differs")
            inspect_png(data, member, expected=tuple(canvas), decode=False)
            reg = registration(row, recipe, asset)
            deviations = {}
            for key in ("white_foam_extent_delta_hd", "shoreline_extent_delta_hd_vs_original"):
                if key in row:
                    deviations[key] = row[key]
            if index in (26, 27) and original["resource"] == "JOHNWALK.BMP":
                deviations["rear_foot_clearance_hd"] = {
                    "hd_proxy_approx": 4, "variant_approx": 11.6 if index == 26 else 11,
                    "basis": "historical-hd-proxy-comparison", "precision": "approximate; no automatic threshold",
                    "source": HISTORICAL_WALK + "/recipe.json#known_geometry_limitations",
                    "measured_variant_recipe": HISTORICAL_WALK + "/recipe.json",
                    "current_variant_independently_remeasured": False,
                    "current_disposition": "Displayed foot lift accepted in the reviewed motion; no claim of anatomical parity."}
            assets.append({"id": asset.removesuffix(".png"), "family": family(asset),
                "original": {"resource": original["resource"], "frame_index": index,
                    "logical_canvas": native["canvas"], "basis": "supplied-original-decoded-pixels",
                    "native_reference": {"evidence": ORIGINAL, **native},
                    "bundled_resource": {"payload_sha256": resource["payload_sha256"],
                        "volume_offset": resource["offset"], "canvas_matches_supplied_original": True},
                    "hd_proxy": {"member": original["source_member"], "sha256": original["source_sha256"],
                                 "canvas": [original["source_width"], original["source_height"]]},
                    "pose_landmarks": None, "per_frame_anatomy_verified": False},
                "variant": {"style": "cartoon", "member": member, "sha256": item["sha256"],
                    "canvas": canvas, "recipe": path, "raw_member": row["generated_image"],
                    "raw_sha256": row["source_sha256"], "registration": reg,
                    "reviewed_scene_origin_hd": row.get("scene_origin_hd"),
                    "placement_basis": "first-reference-cloud-position" if asset.endswith("BACKGRND.BMP/015.png") else "zero-offset-scene-recipe" if "scene_origin_hd" in row else "route-dependent",
                    "acceptance": ACCEPTANCE, "historically_human_accepted": True},
                "comparison": {"canvas_matches_original_at_scale": True,
                    "recorded_deviations": deviations, "artistic_fidelity": "unverified-by-this-tool",
                    "current_user_review_ids": [note["id"] for note in current_review["observations"]
                        if original["resource"] == "JOHNWALK.BMP" and note["frame"] == index]}})
    walk_assets = [x for x in assets if x["family"] == "walk-e-to-a"]
    require({x["original"]["frame_index"] for x in walk_assets} == {r["frame"] for r in route["route"]}, PACK, "route assets differ from accepted walking family")
    require(len({x["variant"]["registration"]["scale"] for x in walk_assets}) == 1, PACK, "walking family scale differs")
    return {"schema_version": 1, "purpose": "authoring-review-only", "style": "cartoon", "coverage": "partial",
        "reference_policy": "Supplied original decoded pixels establish reference canvases and bounds; bundled RESOURCE headers are compared separately. Original-derived draw records establish route. HD PNGs are upscaled proxies, not assumed pixel-identical to the supplied original. Cartoon acceptance never establishes original anatomy.",
        "coordinates": {"logical": "original 640x480 scene coordinates", "hd": "logical multiplied by 2", "raw": "generated source canvas pixels", "landmarks": "manual authoring observations, not engine anchors"},
        "summary": {"assets": len(assets), "walking_assets": len(walk_assets), "island_assets": len(assets) - len(walk_assets)},
        "current_human_review": current_review,
        "current_acceptance_record": ACCEPTANCE,
        "historical_human_correction_requests": HISTORICAL_REVIEW_REQUESTS,
        "original_observations": [{"assets": ["BMP/JOHNWALK.BMP/024"], "basis": "historical-hd-proxy-inspection",
            "source": "art/cartoon/motion-review.md",
            "statement": "024 foreground leg descends from the screen-right shorts opening; far leg begins at the screen-left opening with the small foot mostly behind and screen-left of the planted ankle.",
            "independently_remeasured_in_this_catalog": False},
            {"family": "walk-e-to-a", "basis": "historical-hd-proxy-inspection", "source": "docs/art-style-learnings.md",
             "statement": "Six HD proxy poses share the upper 38 HD reference rows after their recorded horizontal offsets. Precise anatomical left/right labels for every pose remain unverified."}],
        "motion": route,
        "island_motion": {"basis": "port-code-and-native-capture-record", "source": "src/engine/island.c:islandAnimate",
            "evidence": ISLAND + "/review-evidence/wave-phase-validation.json",
            "high_tide_families": {"left": [3, 4, 5], "center": [6, 7, 8], "right": [9, 10, 11]},
            "background_step_ms": 160, "family_updates": "one family per step; latest updated family is on top; phase counters persist across island reinitialization",
            "not_a_synchronized_three_frame_animation": True,
            "scope": "Fresh-process reviewed day/OCEAN02, high tide, zero offset, no raft/holiday. Cloud origin is a reference capture position, not fixed placement."},
        "assets": assets, "evidence": evidence,
        "limits": ["Original XPM evidence is decoded by the port, not a capture of the original executable. No new anatomical annotation is performed.",
                   "Numeric registration residuals test transform consistency, not original-versus-variant landmark coincidence.",
                   "Historical raised-foot observations are retained with their older variant identity. Current displayed foot lift and known leg differences were accepted, not proven anatomically equivalent.",
                   "No pixel-equality or invented aesthetic threshold is applied across styles. Other poses/states remain outside this pilot."]}


def markdown(report):
    lines = ["# Cartoon pilot: original-first review metadata", "",
        "Generated by `python tools/art_review_metadata.py`. Use `--check` to verify reproduction.", "",
        "[JSON catalog](cartoon-art-metadata.json) keeps original facts, variant mapping and acceptance separate.",
        "It maps the current 21 production replacements: six Calm focus walk poses and 15 unchanged island assets.", "",
        "[Supplied original XPM evidence](cartoon-original-reference.json) establishes native canvases and visible bounds.",
        "Bundled RESOURCE headers are checked separately. Existing HD PNGs are labeled upscaled proxies, not assumed",
        "pixel-identical to the original installation. The E-to-A sequence is read from the original-derived walk table",
        "and checked against historical HD and Cartoon capture records. This is port timing, not measured original EXE timing.", "",
        "## Comparison findings", "",
        "All canvases match original dimensions at scale 2, all production bytes match the final acceptance ledger,",
        "and all recorded affine landmarks map to their declared targets. These are technical checks, not artistic approval.",
        "The cap landmarks are manually selected registration features, not engine anchors or newly detected pixel features.", "",
        "The earlier directional-cycle-v1 review recorded rear-foot clearance near 11.6 HD pixels in 026 and 11 in 027,",
        "versus about 4 in the packaged HD proxies. It also recorded elevated clearance in 029 without a reliable number.",
        "Those approximate measurements belong to the older drawings; this catalog has not remeasured the current feet.", "",
        "## Human review and retained differences", "",
        "The user approved the displayed Calm focus walk, then its revised toes in the actual Linux island preview.",
        "The decision accepts the displayed foot lift in 026/027 and known leg differences; it does not establish",
        "anatomical agreement with the original. The JSON retains the earlier correction requests as historical observations",
        "and links the current dispositions to the separate production acceptance. Earlier art records remain byte-identical.", "",
        "The original-reference observations remain separate: the earlier user comparison requested an inward angle for",
        "Cartoon 024's trailing right foot and identified original 028/029 as anatomical left-forward/right-back.",
        "Artistic acceptance does not change those observations or the stored supplied-original pixel facts.", "",
        "The JSON separately retains an older 024 foreground-leg description from HD proxies; that historical description",
        "is not a new original-pixel annotation. Per-frame anatomy remains unverified by this tool. The JSON also retains",
        "the recorded shoreline/foam extent deltas where available. Nonzero differences have no automatic pass/fail threshold.", "",
        "## Asset map", "", "| Original identity | Logical canvas | Cartoon canvas | Family | Registration scale |", "|---|---|---|---|---|"]
    for asset in report["assets"]:
        o, v = asset["original"], asset["variant"]
        shape = lambda value: " x ".join(map(str, value))
        lines.append(f"| `{asset['id']}` | {shape(o['logical_canvas'])} | {shape(v['canvas'])} | {asset['family']} | {v['registration']['scale']} |")
    lines += ["", "## Reviewed motion", "",
        "The 23-position route travels (-94,+30) logical pixels without a horizontal flip. Each pose starts 120 ms apart.",
        "The final 025-to-027 transition is retained; this route is not an invented repeating six-frame loop.",
        "The historical route review lasts 3760 ms including a separate 1000 ms endpoint hold. Its 42 display records include intervening",
        "160 ms background updates, so display duration and pose duration are distinct fields.", "",
        "Those historical captures show the older directional-cycle-v1 artwork. Current Calm focus scene captures and",
        "their Linux platform/seed/archive identities are linked by the current acceptance record; they are separate evidence.", "",
        "High-tide wave groups 003-005, 006-008 and 009-011 advance independently. Latest-update draw order matters",
        "where center/right foam overlaps. The cloud's recorded origin is only its first reference position.", "",
        "## Evidence and scope", "",
        "The JSON links immutable recipes, selected raw hashes, production ZIP members, original resource payloads,",
        "human acceptance and native capture records. Hashes identify inputs; they do not turn a human observation",
        "into an engine fact. Raw landmark residuals verify arithmetic only. Original-resolution anatomical measurement",
        "and a complete limb-order annotation of every pose remain work for a future review.", "",
        "For another pack, preserve original identities and evidence classifications, then add its own mapping and",
        "acceptance. Do not copy Cartoon judgments into the original reference layer.", "",
        "Run smoke before regression: `python tests/test_art_review_metadata.py --phase smoke`, then",
        "`python tests/test_art_review_metadata.py --phase regression --mutation-check`.", "",
        "Normal regeneration uses stored original-XPM facts and says that the external original inputs were not reread.",
        "To refresh them, run `python tools/art_review_metadata.py --import-original-dump PATH_TO_DUMP`, then regenerate.",
        "The dump's parent must contain its successful `report.json`; all 21 XPM byte hashes are checked before writing.",
        "The reference record identifies the exact original RESOURCE hashes and decoder executable. It does not claim",
        "original-executable rendering parity. Text fingerprints use strict UTF-8, normalize CRLF and lone CR to LF,",
        "and preserve BOMs, other characters, whitespace and trailing blank lines. Immutable recipe/acceptance JSON",
        "hashes use exact preserved bytes; the maintained pack ledger uses the text policy.", "",
        "See [art guidance](../cartoon-art.md), [learnings](../art-style-learnings.md),",
        "[motion review](../../art/cartoon/motion-review.md) and",
        f"[current production acceptance](../../{report['current_acceptance_record']}).", ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--import-original-dump", type=Path, help="refresh compact original XPM evidence from a successful dump/report pair")
    args = parser.parse_args(argv)
    print("WITNESS art_review_metadata " + digest(Path(__file__).read_bytes()))
    try:
        if args.import_original_dump:
            require(not args.check, ORIGINAL, "cannot import during a read-only check")
            original = import_original(args.root, args.import_original_dump)
            (args.root / ORIGINAL).write_text(json.dumps(original, indent=2) + "\n", encoding="utf-8", newline="\n")
            print("PASS original-reference-import " + str(len(original["assets"])))
            return 0
        report = build(args.root)
        print("REFERENCE stored original-dump evidence; external original inputs were not reread in this run")
        outputs = {OUTPUT + ".json": json.dumps(report, indent=2) + "\n", OUTPUT + ".md": markdown(report)}
        for path, text in outputs.items():
            if args.check:
                require((args.root / path).read_text(encoding="utf-8") == text, path, "generated metadata differs")
        if not args.check:
            for path, text in outputs.items():
                (args.root / path).parent.mkdir(parents=True, exist_ok=True)
                (args.root / path).write_text(text, encoding="utf-8", newline="\n")
        print("PASS art-review-metadata " + json.dumps(report["summary"], sort_keys=True))
        return 0
    except (ArtError, ValueError, KeyError, OSError, zipfile.BadZipFile) as exc:
        print("ERROR " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
