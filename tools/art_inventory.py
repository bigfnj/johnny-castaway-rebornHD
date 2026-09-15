#!/usr/bin/env python3
"""Inventory/extract unchanged HD PNGs for offline art production."""

import argparse
import json
import sys
import zipfile
from pathlib import Path

from art_common import ArtError, digest, source_catalog


def inventory(archive_path, resources=(), export=None):
    with zipfile.ZipFile(archive_path) as archive:
        catalog = source_catalog(archive)
        known = {item["resource"] for item in catalog.values()}
        unknown = set(resources) - known
        if unknown:
            raise ArtError(f"{sorted(unknown)[0]}: unknown resource")
        selected = [item for item in catalog.values()
                    if not resources or item["resource"] in resources]
        aliases = {}
        for item in selected:
            source_hash = item["source_sha256"]
            if source_hash in aliases:
                item["identical_to"] = aliases[source_hash]
            else:
                aliases[source_hash] = item["path"]
            if export:
                destination = Path(export).resolve() / item["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                data = archive.read(item["source_member"])
                if destination.exists() and destination.read_bytes() != data:
                    raise ArtError(f"{destination}: refusing to overwrite a changed reference")
                destination.write_bytes(data)
                if digest(destination.read_bytes()) != source_hash:
                    raise ArtError(f"{destination}: exported reference hash differs")
        return {
            "schema_version": 1,
            "archive_sha256": digest(Path(archive_path).read_bytes()),
            "assets": selected,
            "summary": {
                "assets": len(selected),
                "sprites": sum(item["kind"] == "sprite" for item in selected),
                "screens": sum(item["kind"] == "screen" for item in selected),
                "unique_png_bytes": len(aliases),
            },
        }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, help="write the complete JSON catalog")
    parser.add_argument("--export", type=Path, help="extract selected PNGs without changing pixels")
    parser.add_argument("--resource", action="append", default=[], help="exact resource name; repeatable")
    args = parser.parse_args(argv)
    try:
        if args.output:
            source, output = args.archive.resolve(), args.output.resolve()
            if source == output or (output.exists() and source.samefile(output)):
                raise ArtError(f"{args.output}: output must differ from the source archive {args.archive}")
        report = inventory(args.archive, args.resource, args.export)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report["summary"], sort_keys=True))
        return 0
    except (ArtError, OSError, zipfile.BadZipFile) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
