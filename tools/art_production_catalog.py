#!/usr/bin/env python3
"""Inventory every production art slot without generating or promoting artwork.

This catalog derives coverage from the bundled RESOURCE headers and HD manifest.
HD duplicates/blank facts describe proxies, not supplied-original pixel truth.
Acceptance requires matching ledger, recipe and actual production PNG bytes.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path, PurePosixPath
import re
import struct
import sys
import zipfile
import zlib

from art_common import ArtError, cartoon_footprint, digest, inspect_png, read_json, safe_member, source_catalog
from inventory_scenes import resource_catalog, metadata, u16

PLAN = "art/cartoon/production-plan.json"
PACK = "art/cartoon/pack.json"
ARCHIVE = "assets/scrantic_data.zip"
ORIGINAL = "docs/knowledge-base/cartoon-original-reference.json"
OUTPUT = "docs/knowledge-base/cartoon-production-catalog"
PREFIX = "data/styles/cartoon/"


def require(condition, label, reason):
    if not condition:
        raise ArtError(f"{label}: {reason}")


def keyed(rows, label):
    require(isinstance(rows, list) and all(isinstance(row, dict) and isinstance(row.get("path"), str)
            for row in rows), label, "expected asset rows with paths")
    result = {row["path"]: row for row in rows}
    require(len(result) == len(rows), label, "duplicate asset path")
    return result


def text_hash(data):
    return digest(data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))


def proxy_blank(data, label, sprite):
    """Find visible HD pixels under the runtime's legacy key rule.

    Structural PNG validation and complete inflated length precede this scan.
    Stop reconstructing rows after the first visible pixel; this is a blankness
    fact, not a replacement for the pack validator's full PNG decode checks.
    """
    info = inspect_png(data, label, decode=False)
    width, height, color = info["width"], info["height"], info["color_type"]
    bpp = {2: 3, 4: 2, 6: 4}[color]
    stride = width * bpp
    pos, blocks = 8, []
    while pos < len(data):
        length = struct.unpack_from(">I", data, pos)[0]
        if data[pos + 4:pos + 8] == b"IDAT":
            blocks.append(data[pos + 8:pos + 8 + length])
        pos += length + 12
    expected = (stride + 1) * height
    decoder = zlib.decompressobj()
    try:
        raw = decoder.decompress(b"".join(blocks), expected + 1)
    except zlib.error as exc:
        raise ArtError(f"{label}: invalid compressed proxy PNG") from exc
    require(len(raw) == expected and decoder.eof and not decoder.unused_data,
            label, "proxy PNG scanline length differs")
    require(all(raw[y * (stride + 1)] <= 4 for y in range(height)), label, "invalid proxy PNG filter")
    previous = bytearray(stride)
    for y in range(height):
        start = y * (stride + 1)
        filtering = raw[start]
        row = bytearray(raw[start + 1:start + 1 + stride])
        if filtering:
            for i in range(stride):
                left = row[i - bpp] if i >= bpp else 0
                above = previous[i]
                corner = previous[i - bpp] if i >= bpp else 0
                if filtering == 1:
                    predictor = left
                elif filtering == 2:
                    predictor = above
                elif filtering == 3:
                    predictor = (left + above) // 2
                else:
                    p = left + above - corner
                    distances = (abs(p - left), abs(p - above), abs(p - corner))
                    predictor = (left, above, corner)[distances.index(min(distances))]
                row[i] = (row[i] + predictor) & 255
        for x in range(width):
            offset = x * bpp
            alpha = row[offset + bpp - 1] if color in (4, 6) else 255
            keyed_out = sprite and color in (2, 6) and alpha == 255 and row[offset:offset + 3] == b"\xa8\x00\xa8"
            if alpha != 0 and not keyed_out:
                return False
        previous = row
    return True


def bundled_canvases(archive):
    _, resources = resource_catalog(archive.read("data/RESOURCE.MAP"), archive.read("data/RESOURCE.001"))
    result = {}
    for name, resource in resources.items():
        if resource["type"] not in ("BMP", "SCR"):
            continue
        metadata(resource)
        if resource["type"] == "SCR":
            result[f"SCR/{name}.png"] = resource["dimensions"]
        else:
            count, payload = resource["image_count"], resource["_payload"]
            for index in range(count):
                result[f"BMP/{name}/{index:03}.png"] = [u16(payload, 18 + index * 2), u16(payload, 18 + count * 2 + index * 2)]
    return result


def reference_assets(original, plan, record):
    """Link stored facts only; do not import or decode an external distribution."""
    result = {path: dict(row, record=ORIGINAL, record_format="asset-map")
              for path, row in original["assets"].items()}
    paths = plan.get("additional_original_frame_records", [])
    require(isinstance(paths, list) and all(isinstance(path, str) for path in paths)
            and len(paths) == len(set(paths)), PLAN, "invalid or duplicate original frame record")
    for path in paths:
        metadata = record(path)
        frames = metadata.get("frames")
        require(isinstance(frames, list) and metadata.get("frame_count") == len(frames)
                and all(isinstance(row, dict) and isinstance(row.get("resource"), str)
                        and row["resource"].endswith(".BMP") and type(row.get("frame")) is int
                        and row["frame"] >= 0 for row in frames), path, "invalid original frame identities or count")
        source_name = metadata.get("source")
        require(isinstance(source_name, str), path, "missing original frame source")
        source_path = str(PurePosixPath(path).parent / source_name)
        source = record(source_path)
        require(source.get("resource_sha256") == original["input_sha256"], source_path, "supplied-original distribution differs")
        seen = set()
        for row in frames:
            slot = f"BMP/{row['resource']}/{row['frame']:03}.png"
            require(slot not in seen, path, "duplicate original frame identity")
            seen.add(slot)
            require(isinstance(row.get("canvas"), list) and len(row["canvas"]) == 2
                    and all(type(n) is int and n > 0 for n in row["canvas"])
                    and row.get("transparent_index") == 0
                    and all(isinstance(row.get(key), str) and re.fullmatch(r"[0-9a-f]{64}", row[key])
                            for key in ("xpm_sha256", "index_plane_sha256", "rgba_sha256")),
                    path, "invalid stored original pixel facts")
            require(isinstance(source.get("xpm_sha256"), dict)
                    and source["xpm_sha256"].get(f"{row['frame']:03}") == row["xpm_sha256"],
                    path, f"original frame XPM hash differs from source record:{row['frame']:03}")
            previous = result.get(slot)
            require(previous is None or all(previous.get(key) == row.get(key) for key in
                    ("canvas", "xpm_sha256", "index_plane_sha256", "rgba_sha256", "transparent_index")),
                    path, "overlapping original frame facts differ")
            result[slot] = dict(row, record=path, record_format="bmp-frame-list")
    return result


def approval_origins(accepted, approved, acceptance_path, record, record_hash):
    """Bind aggregate approval rows to explicitly inherited human reviews.

    Legacy records approve their own complete asset list. An aggregate may
    inherit selected earlier assets, preserving their row review pointers,
    while explicitly identifying the newly approved complement. Each earlier
    record's complete inheritance chain is still checked.
    """
    root_path, resolved = acceptance_path, {}
    # Explicit stack avoids a recursion-depth limit as approval history grows.
    pending = [(accepted, approved, acceptance_path, (), None)]
    while pending:
        accepted, approved, acceptance_path, ancestors, children = pending.pop()
        if acceptance_path in resolved:
            continue
        origins = {path: acceptance_path for path in approved}
        if children is not None:
            for previous_path, paths in children:
                for path in paths:
                    origins[path] = resolved[previous_path][path]
            resolved[acceptance_path] = origins
            continue
        if "inherited_acceptances" not in accepted and "newly_accepted_assets" not in accepted:
            resolved[acceptance_path] = origins
            continue
        inherited = accepted.get("inherited_acceptances")
        newly = accepted.get("newly_accepted_assets")
        require(isinstance(inherited, list) and all(isinstance(item, dict) for item in inherited),
                acceptance_path, "invalid inherited acceptance list")
        require(isinstance(newly, list) and all(isinstance(path, str) for path in newly)
                and len(newly) == len(set(newly)), acceptance_path, "invalid newly accepted asset list")
        inherited_paths, seen_records = set(), set()
        children, requests = [], []
        for item in inherited:
            previous_path = item.get("path")
            require(isinstance(previous_path, str) and previous_path not in (*ancestors, acceptance_path)
                    and previous_path not in seen_records, acceptance_path, "invalid or duplicate inherited acceptance path")
            seen_records.add(previous_path)
            paths = item.get("asset_paths")
            require(isinstance(paths, list) and all(isinstance(path, str) for path in paths)
                    and len(paths) == len(set(paths)), previous_path, "invalid inherited asset list")
            require(set(paths) <= set(approved) and not (set(paths) & inherited_paths),
                    previous_path, "inherited assets are unknown or overlap")
            previous = record(previous_path)
            checksum = item.get("sha256")
            require(isinstance(checksum, str) and re.fullmatch(r"[0-9a-f]{64}", checksum)
                    and record_hash is not None and record_hash(previous_path) == checksum,
                    previous_path, "inherited acceptance file hash differs")
            require(previous.get("accepted") is True, previous_path, "inherited acceptance is pending")
            previous_rows = keyed(previous.get("accepted_assets"), previous_path)
            require(set(paths) <= set(previous_rows), previous_path, "selected asset is missing from inherited acceptance")
            for path in paths:
                require(all(previous_rows[path].get(key) == approved[path].get(key) for key in ("sha256", "recipe")),
                        path, "inherited approval differs from aggregate")
            inherited_paths.update(paths)
            children.append((previous_path, paths))
            requests.append((previous, previous_rows, previous_path, (*ancestors, acceptance_path), None))
        require(set(newly) == set(approved) - inherited_paths, acceptance_path, "new approval coverage differs from inherited complement")
        pending.append((accepted, approved, acceptance_path, ancestors, children))
        pending.extend(reversed(requests))
    return resolved[root_path]


def assemble(archive, plan, pack, original, record, canvases, record_hash=None):
    catalog = source_catalog(archive)
    require(isinstance(plan, dict) and plan.get("schema_version") == 1 and plan.get("style") == "cartoon",
            PLAN, "expected schema_version 1 and style cartoon")
    priorities = plan.get("priority_resources")
    resources = {row["resource"] for row in catalog.values()}
    require(isinstance(priorities, list) and all(isinstance(name, str) and name in resources for name in priorities)
            and len(priorities) == len(set(priorities)), PLAN, "unknown or duplicate priority resource")
    require(set(catalog) == set(canvases), "data/hd/manifest.json", "HD inventory differs from bundled RESOURCE slots")
    runtime = pack.get("runtime", {})
    require(pack.get("schema_version") == 1 and runtime.get("id") == "cartoon" and type(runtime.get("scale")) is int and runtime["scale"] == 2
            and runtime.get("alpha") == "straight" and runtime.get("coverage") in ("partial", "complete"), PACK, "invalid Cartoon runtime contract")
    packed = keyed(pack.get("assets"), PACK)
    required = pack.get("required_assets")
    require(isinstance(required, list) and all(isinstance(path, str) for path in required)
            and len(required) == len(set(required)), PACK, "invalid or duplicate required asset")
    require(set(packed) == set(pack.get("required_assets", [])) and set(packed) <= set(catalog), PACK, "pack coverage differs from required source slots")
    require(runtime["coverage"] != "complete" or set(packed) == set(catalog), PACK, "complete pack is missing source slots")
    archive_assets = {name[len(PREFIX):] for name in archive.namelist() if name.startswith(PREFIX) and name != PREFIX + "manifest.json"}
    require(archive_assets == set(packed), PACK, "production archive coverage differs from ledger")
    manifest = read_json(archive.read(PREFIX + "manifest.json"), PREFIX + "manifest.json")
    require(manifest == runtime, PREFIX + "manifest.json", "runtime manifest differs from ledger")
    acceptance_path = pack.get("acceptance_record")
    require(isinstance(acceptance_path, str), PACK, "missing active acceptance record")
    accepted = record(acceptance_path)
    require(accepted.get("accepted") is True, acceptance_path, "active production acceptance is pending")
    approved = keyed(accepted.get("accepted_assets"), acceptance_path)
    require(set(approved) == set(packed), acceptance_path, "acceptance coverage differs from production")
    approval_paths = approval_origins(accepted, approved, acceptance_path, record, record_hash)
    recipes, recipe_rows = {}, {}
    for item in packed.values():
        path = item.get("recipe")
        require(isinstance(path, str), item["path"], "missing recipe reference")
        if path not in recipes:
            recipes[path] = record(path)
            recipe_rows[path] = keyed(recipes[path].get("frames", recipes[path].get("assets")), path)
    original_assets = reference_assets(original, plan, record)
    require(set(original_assets) <= set(catalog), PLAN, "original reference names an unknown runtime slot")
    blank_facts, groups, assets = {}, defaultdict(list), []
    for path, source in catalog.items():
        logical = [source["logical_width"], source["logical_height"]]
        footprint = cartoon_footprint(path, logical, runtime["scale"], packed.get(path, {}).get("footprint"))
        require(logical == canvases[path], path, "HD logical canvas differs from bundled RESOURCE")
        proxy_hash = source["source_sha256"]
        groups[proxy_hash].append(path)
        # Blankness differs between a keyed sprite and opaque screen even when
        # their encoded PNG bytes are identical. Cache only within that class.
        blank_key = (proxy_hash, source["kind"])
        if blank_key not in blank_facts:
            blank_facts[blank_key] = proxy_blank(archive.read(source["source_member"]), source["source_member"], source["kind"] == "sprite")
        native = original_assets.get(path)
        if native is not None:
            require(native["canvas"] == logical, path, "stored supplied-original canvas differs from bundled RESOURCE")
        status = {"status": "pending", "acceptance": None, "recipe": None, "png_sha256": None}
        if path in packed:
            item, approval = packed[path], approved[path]
            recipe_path = item["recipe"]
            row = recipe_rows[recipe_path].get(path)
            require(row is not None, path, "asset is absent from referenced recipe")
            require(row.get("footprint") == item.get("footprint"), path, "recipe footprint differs from ledger")
            require(row.get("runtime_canvas") == footprint["canvas"], path, "recipe canvas differs from runtime")
            require(item.get("review") == approval_paths[path] and approval.get("recipe") == recipe_path,
                    path, "active recipe or acceptance pointer differs")
            require(item.get("source_sha256") == proxy_hash, path, "accepted HD proxy hash differs")
            require(item.get("sha256") == approval.get("sha256") == row.get("candidate_png_sha256"), path, "accepted PNG hashes differ")
            data = archive.read(PREFIX + path)
            require(digest(data) == item["sha256"], PREFIX + path, "production PNG hash differs")
            info = inspect_png(data, PREFIX + path, expected=tuple(footprint["canvas"]))
            if source["kind"] == "sprite":
                require(info["color_type"] in (4, 6), path, "accepted sprite has no alpha channel")
            else:
                require(info["alpha_opaque"] == info["width"] * info["height"], path, "accepted screen is not opaque")
            total = info["width"] * info["height"]
            alpha = "blank" if info["alpha_zero"] == total else "opaque" if info["alpha_opaque"] == total else "transparent"
            require(item.get("alpha") == alpha, path, "accepted alpha declaration differs")
            status = {"status": "accepted", "acceptance": approval_paths[path], "recipe": recipe_path, "png_sha256": item["sha256"]}
        assets.append({"path": path, "kind": source["kind"], "resource": source["resource"], "frame": source.get("index"),
                       "family": "resource:" + source["resource"], "bundled_logical_canvas": logical,
                       "runtime_canvas": footprint["canvas"],
                       "hd_proxy": {"member": source["source_member"], "sha256": proxy_hash,
                                    "canvas": [source["source_width"], source["source_height"]],
                                    "blank_under_hd_runtime_rule": blank_facts[blank_key],
                                    "exact_duplicate_of": groups[proxy_hash][0] if len(groups[proxy_hash]) > 1 else None},
                       "supplied_original_evidence": {"status": "available" if native is not None else "not_cataloged",
                           "record": native["record"] if native is not None else None,
                           "record_format": native["record_format"] if native is not None else None,
                           "asset_key": path if native is not None else None,
                           "independently_reread": False}, "production": status})
        if "id" in footprint:
            assets[-1]["footprint"] = footprint
    families = []
    for resource in sorted(resources, key=lambda name: (priorities.index(name) if name in priorities else len(priorities), name)):
        rows = [row for row in assets if row["resource"] == resource]
        families.append({"id": "resource:" + resource, "resource": resource,
                         "priority": priorities.index(resource) + 1 if resource in priorities else None,
                         "slots": len(rows), "accepted": sum(row["production"]["status"] == "accepted" for row in rows),
                         "hd_proxy_blank_slots": sum(row["hd_proxy"]["blank_under_hd_runtime_rule"] for row in rows)})
    kinds = Counter(row["kind"] for row in assets)
    accepted_count = sum(row["production"]["status"] == "accepted" for row in assets)
    return {"schema_version": 1, "purpose": "production-planning-only", "style": "cartoon",
            "scope": plan["scope"], "review_policy": plan["review_policy"],
            "evidence_policy": {"geometry": "Bundled RESOURCE dimensions cross-checked with the HD manifest. Supplied-original canvas comparison only where the stored original record has that slot.",
                "hd_proxy": "Exact encoded HD PNG bytes. Blank means no visible pixels under nonzero alpha and, for sprites only, the opaque A8-00-A8 compatibility key. No threshold, trimming, source-original blankness or artistic judgment is inferred.",
                "duplicates": "Exact encoded HD PNG hashes only. Identical proxies may be reuse candidates; every runtime slot needs its own acceptance.",
                "families": "Resource identity and explicit priority ordering only. No inferred action, limb identity, motion cadence or runtime reachability.",
                "original_reference": "Canonical asset_key identifies a slot in an asset-map or a resource/frame in a bmp-frame-list. Stored pixel/canvas overlaps and distribution hashes are checked; external originals are not reread. Linked reference records retain their palette/compositing and landmark limits.",
                "acceptance": "Current ledger, accepted review, recipe and production PNG hashes agree. The referenced human review's scope and known differences remain authoritative; this is not original parity.",
                "text_hashes": "Maintained plan/pack text uses UTF-8 with CRLF/CR normalized to LF; immutable art records and archive members use exact bytes."},
            "summary": {"slots": len(assets), "sprites": kinds["sprite"], "screens": kinds["screen"],
                "accepted": accepted_count, "pending": len(assets) - accepted_count,
                "hd_proxy_blank_slots": sum(row["hd_proxy"]["blank_under_hd_runtime_rule"] for row in assets),
                "distinct_hd_png_bytes": len(groups), "exact_duplicate_slots": len(assets) - len(groups),
                "supplied_original_evidence_slots": sum(row["supplied_original_evidence"]["status"] == "available" for row in assets)},
            "families": families, "duplicate_groups": [{"sha256": checksum, "paths": paths} for checksum, paths in sorted(groups.items()) if len(paths) > 1],
            "assets": assets}


def build(root):
    inputs, raw_hashes = {}, {}

    def record(path):
        safe_member(path)
        data = (root / path).read_bytes()
        raw_hashes[path] = digest(data)
        immutable = path not in (PLAN, PACK, ORIGINAL)
        inputs[path] = {"sha256": digest(data) if immutable else text_hash(data),
                        "basis": "file-bytes" if immutable else "utf8-normalized-newlines"}
        return read_json(data, path)

    plan, pack, original = record(PLAN), record(PACK), record(ORIGINAL)
    with zipfile.ZipFile(root / ARCHIVE) as archive:
        result = assemble(archive, plan, pack, original, record, bundled_canvases(archive),
                          lambda path: raw_hashes[path])
        for name in ("data/hd/manifest.json", "data/RESOURCE.MAP", "data/RESOURCE.001", PREFIX + "manifest.json"):
            inputs[ARCHIVE + "!" + name] = {"sha256": digest(archive.read(name)), "basis": "zip-member-bytes"}
    result["inputs"] = inputs
    return result


def markdown(report):
    s = report["summary"]
    lines = ["# Cartoon production catalog", "", "Generated by `python -B tools/art_production_catalog.py`; verify with `--check`.", "",
             f"The catalog tracks {s['slots']:,} shipped slots: {s['sprites']:,} sprites and {s['screens']} screens. "
             f"{s['accepted']} are accepted in production; {s['pending']:,} remain pending.", "",
             "[All slot records](cartoon-production-catalog.json) use resource identities, not inferred animation families. "
             "Walking and background resources are first in the explicit production plan. Human review of remaining walking directions precedes further expansion.", "",
             f"There are {s['distinct_hd_png_bytes']:,} distinct encoded HD PNGs, {s['exact_duplicate_slots']} duplicate slots and "
             f"{s['hd_proxy_blank_slots']} blank HD proxies under the legacy runtime transparency rule. These are proxy facts, not original-pixel or artistic truths. "
             "Duplicates and blank slots do not inherit acceptance automatically.", "",
             f"Stored supplied-original evidence is linked for {s['supplied_original_evidence_slots']} slots. Other slots are explicitly not cataloged against that evidence. "
             "This generator does not reread the external original distribution or establish motion/anatomical parity.", "",
             "## Resource worklist", "", "| Priority | Resource | Slots | Accepted | Pending | Blank HD proxies |", "|---|---|---:|---:|---:|---:|"]
    for family in report["families"]:
        lines.append(f"| {family['priority'] or ''} | `{family['resource']}` | {family['slots']} | {family['accepted']} | {family['slots'] - family['accepted']} | {family['hd_proxy_blank_slots']} |")
    lines += ["", "## Completion boundary", "", "Slot coverage is separate from visual approval. Validate every candidate PNG, preserve original canvases and script placement, "
              "review each motion/interaction family in the engine, and retain approval scope and known differences. Palette-driven primitives, scene transitions and application UI are outside the BMP/SCR replacement count.", "",
              "The existing [original-first pilot catalog](cartoon-art-metadata.md) and historical review records remain unchanged. "
              "This production catalog adds a worklist; it does not replace their evidence.", "",
              "Run `python -B tests/test_art_production_catalog.py --phase smoke`, then `--phase regression`. "
              "Use `--mutation-check` on the regression command for per-change guard verification.", ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = build(args.root)
        outputs = {OUTPUT + ".json": json.dumps(report, indent=2) + "\n", OUTPUT + ".md": markdown(report)}
        if args.check:
            for name, text in outputs.items():
                require((args.root / name).read_text(encoding="utf-8") == text, name, "generated production catalog differs")
        else:
            for name, text in outputs.items():
                path = args.root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8", newline="\n")
        print("REFERENCE HD proxies; stored supplied-original evidence only where linked; no external originals reread")
        print("PASS art-production-catalog " + json.dumps(report["summary"], sort_keys=True))
        return 0
    except (ArtError, OSError, ValueError, KeyError, TypeError, struct.error, zipfile.BadZipFile) as exc:
        print("ERROR " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
