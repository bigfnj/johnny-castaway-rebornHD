#!/usr/bin/env python3
"""Validate accepted art or build a separate, reproducible candidate archive."""

import argparse
import copy
import json
import re
import sys
import zipfile
from pathlib import Path

from art_common import ArtError, check_duplicates, digest, inspect_png, read_json, safe_member, source_catalog


def accepted_pack(archive, ledger, accepted_dir, label="pack.json"):
    catalog = source_catalog(archive)
    if (not isinstance(ledger, dict) or type(ledger.get("schema_version")) is not int
            or ledger["schema_version"] != 1):
        raise ArtError(f"{label}: expected schema_version 1")
    runtime = ledger.get("runtime", {})
    if not isinstance(runtime, dict) or runtime.get("id") != "cartoon":
        raise ArtError(f"{label}: runtime.id must be cartoon")
    if type(runtime.get("scale")) is not int or runtime["scale"] != 2:
        raise ArtError(f"{label}: cartoon runtime.scale must be 2")
    if runtime.get("alpha") != "straight" or runtime.get("coverage") not in ("partial", "complete"):
        raise ArtError(f"{label}: runtime requires alpha straight and coverage partial or complete")
    # The runtime contract stays small. Provenance lives in the author ledger.
    runtime = {key: runtime[key] for key in ("id", "scale", "alpha", "coverage")}
    required = set()
    resources = ledger.get("required_resources", [])
    paths = ledger.get("required_assets", [])
    assets = ledger.get("assets", [])
    if not all(isinstance(value, list) for value in (resources, paths, assets)):
        raise ArtError(f"{label}: required_resources, required_assets and assets must be arrays")
    known_resources = {item["resource"] for item in catalog.values()}
    for resource in resources:
        if not isinstance(resource, str) or resource not in known_resources:
            raise ArtError(f"{resource}: unknown required resource")
        required.update(path for path, item in catalog.items() if item["resource"] == resource)
    for path in paths:
        if not isinstance(path, str) or path not in catalog:
            raise ArtError(f"{path}: unknown required asset")
        required.add(path)
    if runtime["coverage"] == "complete":
        required = set(catalog)
    elif not required:
        raise ArtError(f"{label}: partial pack must declare a nonempty required scope")
    base_dir = Path(accepted_dir).resolve()
    packed, alpha_summary = {}, {"opaque": 0, "transparent": 0, "blank": 0}
    for item in assets:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise ArtError(f"{label}: each accepted asset needs a path")
        path = item["path"]
        safe_member(path)
        if path in packed:
            raise ArtError(f"{path}: duplicate accepted asset")
        if path not in catalog:
            raise ArtError(f"{path}: unknown asset")
        source = catalog[path]
        if item.get("source_sha256") != source["source_sha256"]:
            raise ArtError(f"{path}: source_sha256 does not match the original reference")
        claimed_hash = item.get("sha256")
        if not isinstance(claimed_hash, str) or re.fullmatch(r"[0-9a-f]{64}", claimed_hash) is None:
            raise ArtError(f"{path}: missing or invalid accepted sha256")
        alpha = item.get("alpha")
        if not isinstance(alpha, str) or alpha not in alpha_summary:
            raise ArtError(f"{path}: alpha must explicitly be opaque, transparent or blank")
        filename = (base_dir / path).resolve()
        if not filename.is_relative_to(base_dir):
            raise ArtError(f"{path}: accepted file resolves outside its input directory")
        if not filename.is_file():
            raise ArtError(f"{path}: missing accepted PNG")
        data = filename.read_bytes()
        if digest(data) != claimed_hash:
            raise ArtError(f"{path}: accepted sha256 does not match PNG")
        expected = (source["logical_width"] * runtime["scale"], source["logical_height"] * runtime["scale"])
        info = inspect_png(data, path, expected)
        if source["kind"] == "sprite" and info["color_type"] not in (4, 6):
            raise ArtError(f"{path}: sprites require an explicit alpha channel")
        total = info["width"] * info["height"]
        actual = ("blank" if info["alpha_zero"] == total else
                  "opaque" if info["alpha_opaque"] == total else "transparent")
        if actual != alpha:
            raise ArtError(f"{path}: declared alpha {alpha} differs from actual {actual}")
        if source["kind"] == "screen" and actual != "opaque":
            raise ArtError(f"{path}: screen backgrounds must be opaque")
        packed[path] = data
        alpha_summary[actual] += 1
    missing = required - packed.keys()
    if missing:
        raise ArtError(f"{sorted(missing)[0]}: missing required accepted asset")
    if not packed:
        raise ArtError(f"{label}: empty style pack")
    present = {path.relative_to(base_dir).as_posix() for path in base_dir.rglob("*")
               if path.is_file() and path.suffix.lower() == ".png"}
    extra = present - packed.keys()
    if extra:
        raise ArtError(f"{sorted(extra)[0]}: PNG is not recorded in the acceptance ledger")
    return runtime, packed, alpha_summary


def build_archive(base, output, runtime, packed):
    base, output = Path(base).resolve(), Path(output).resolve()
    if base == output:
        raise ArtError(f"{output}: output must differ from the source archive")
    if output.exists():
        raise ArtError(f"{output}: refusing to overwrite an existing candidate")
    prefix = "data/styles/" + runtime["id"] + "/"
    style = {prefix + path: data for path, data in packed.items()}
    style[prefix + "manifest.json"] = (json.dumps(runtime, sort_keys=True, separators=(",", ":")) + "\n").encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    original_hashes = {}
    created = False
    try:
        with zipfile.ZipFile(base) as source, zipfile.ZipFile(output, "x") as target:
            created = True
            check_duplicates(source)
            target.comment = source.comment
            for info in source.infolist():
                if info.filename.startswith(prefix):
                    continue
                data = source.read(info.filename)
                original_hashes[info.filename] = digest(data)
                target.writestr(copy.copy(info), data)
            for name, data in sorted(style.items()):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                target.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        with zipfile.ZipFile(output) as candidate:
            check_duplicates(candidate)
            for name, expected_hash in original_hashes.items():
                if digest(candidate.read(name)) != expected_hash:
                    raise ArtError(f"{name}: original archive member changed during packing")
            for name, expected_data in style.items():
                if candidate.read(name) != expected_data:
                    raise ArtError(f"{name}: accepted bytes changed during packing")
    except Exception:
        # This candidate was created by this function; never remove the base.
        if created and output.is_file():
            output.unlink()
        raise
    return {"original_members_preserved": len(original_hashes), "archive_sha256": digest(output.read_bytes())}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("validate", "build"))
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--accepted", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if (args.mode == "build") != (args.output is not None):
        parser.error("--output is required for build and must be omitted for validate")
    try:
        ledger = read_json(args.ledger.read_bytes(), str(args.ledger))
        with zipfile.ZipFile(args.archive) as archive:
            runtime, packed, alpha = accepted_pack(archive, ledger, args.accepted, str(args.ledger))
        report = {"style": runtime["id"], "coverage": runtime["coverage"], "assets": len(packed), "alpha": alpha}
        if args.mode == "build":
            report.update(build_archive(args.archive, args.output, runtime, packed))
        print(json.dumps(report, sort_keys=True))
        return 0
    except (ArtError, OSError, zipfile.BadZipFile) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
