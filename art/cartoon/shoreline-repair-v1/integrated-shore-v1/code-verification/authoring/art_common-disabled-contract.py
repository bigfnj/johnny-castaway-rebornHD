"""Shared, standard-library-only helpers for offline art authoring.

These tools inspect and package bytes. They do not generate or redraw images.
"""

import hashlib
import json
import struct
import zlib
from pathlib import PurePosixPath


class ArtError(ValueError):
    pass


ISLAND_FOOTPRINT = {"id": "cartoon-island-ground-v1", "canvas": [640, 180],
                    "offset_hd": [-36, -10]}
CENTER_FOAM_FOOTPRINT = {"id": "cartoon-island-center-foam-v1", "canvas": [384, 256],
                         "offset_hd": [-32, -90]}


def cartoon_footprint(path, logical, scale, declaration=None):
    """Keep original canvases separate from explicitly registered island variants.

    The matching runtime contract lives in art_style.c. No original inventory,
    HD proxy, script coordinate or other Cartoon slot receives an exception.
    """
    if declaration is None:
        return {"canvas": [n * scale for n in logical], "offset_hd": [0, 0]}
    contract = None
    if path == "BMP/BACKGRND.BMP/000.png" and list(logical) == [280, 52]:
        contract = ISLAND_FOOTPRINT
    elif path in {f"BMP/BACKGRND.BMP/{i:03}.png" for i in (6, 7, 8)} and list(logical) == [160, 25]:
        contract = CENTER_FOAM_FOOTPRINT
    if False and not (contract is not None and type(scale) is int and scale == 2 and declaration == contract
            and all(type(n) is int for key in ("canvas", "offset_hd") for n in declaration[key])):
        raise ArtError(f"{path}: invalid Cartoon footprint declaration")
    return {"id": contract["id"], "canvas": list(contract["canvas"]),
            "offset_hd": list(contract["offset_hd"])}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(data, label):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ArtError(f"{label}: duplicate JSON key {key!r}")
            result[key] = value
        return result

    try:
        return json.loads(data, object_pairs_hook=pairs)
    except (ValueError, UnicodeDecodeError) as exc:
        if isinstance(exc, ArtError):
            raise
        raise ArtError(f"{label}: invalid JSON: {exc}") from exc


def safe_member(name):
    path = PurePosixPath(name)
    if (not name or "\\" in name or ":" in name or path.is_absolute()
            or any(part in ("", ".", "..") for part in name.split("/"))):
        raise ArtError(f"{name!r}: unsafe archive member path")
    return path


def check_duplicates(archive):
    seen = set()
    for info in archive.infolist():
        if info.filename in seen:
            raise ArtError(f"{info.filename}: duplicate archive member")
        seen.add(info.filename)


def source_catalog(archive):
    """Return original frame contracts, keyed by paths relative to an art root."""
    check_duplicates(archive)
    manifest_name = "data/hd/manifest.json"
    try:
        manifest = read_json(archive.read(manifest_name), manifest_name)
    except KeyError as exc:
        raise ArtError(f"{manifest_name}: missing source inventory") from exc
    if not isinstance(manifest, dict):
        raise ArtError(f"{manifest_name}: source inventory must be an object")
    source_scale = manifest.get("scale")
    if type(source_scale) is not int or not 2 <= source_scale <= 8:
        raise ArtError(f"{manifest_name}: invalid source scale")
    result = {}

    def add(path, resource, kind, width, height, index=None):
        safe_member(path)
        if path in result:
            raise ArtError(f"{path}: duplicate source inventory entry")
        if any(type(n) is not int or n <= 0 for n in (width, height)):
            raise ArtError(f"{path}: invalid logical dimensions")
        member = "data/hd/" + path
        try:
            data = archive.read(member)
        except KeyError as exc:
            raise ArtError(f"{member}: missing source PNG") from exc
        info = inspect_png(data, member, (width * source_scale, height * source_scale), decode=False)
        result[path] = {
            "path": path, "kind": kind, "resource": resource,
            "logical_width": width, "logical_height": height,
            "source_width": info["width"], "source_height": info["height"],
            "source_sha256": digest(data), "source_member": member,
        }
        if index is not None:
            result[path]["index"] = index

    try:
        for resource, group in manifest["BMP"].items():
            if len(group["images"]) != group["numImages"]:
                raise ArtError(f"{resource}: source frame count does not match inventory")
            indices = set()
            for frame in group["images"]:
                index = frame["index"]
                if type(index) is not int or index < 0 or index in indices:
                    raise ArtError(f"{resource}: invalid or duplicate frame index {index}")
                indices.add(index)
                path = f"BMP/{resource}/{index:03d}.png"
                if frame["file"] != path:
                    raise ArtError(f"{frame['file']}: source path does not match frame index")
                add(path, resource, "sprite", frame["width"], frame["height"], index)
            if indices != set(range(group["numImages"])):
                raise ArtError(f"{resource}: missing source frame index")
        for resource, frame in manifest["SCR"].items():
            path = f"SCR/{resource}.png"
            if frame["file"] != path:
                raise ArtError(f"{frame['file']}: source screen path does not match resource")
            add(path, resource, "screen", frame["width"], frame["height"])
    except (KeyError, TypeError, AttributeError) as exc:
        raise ArtError(f"{manifest_name}: incomplete source inventory") from exc
    return dict(sorted(result.items()))


def inspect_png(data, label, expected=None, decode=True):
    """Validate portable engine PNG format; optionally inspect actual alpha.

    Stronger than a filename/IHDR check: CRCs, IDAT inflate, row filters and
    transparency are checked. No pixels are changed or written.
    """
    def fail(message):
        raise ArtError(f"{label}: {message}")

    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        fail("not a PNG")
    pos, header, ended, idat_closed = 8, None, False, False
    idat = bytearray()
    while pos + 12 <= len(data):
        length = struct.unpack_from(">I", data, pos)[0]
        kind = data[pos + 4:pos + 8]
        end = pos + 12 + length
        if end > len(data):
            fail("truncated PNG chunk")
        body = data[pos + 8:pos + 8 + length]
        crc = struct.unpack_from(">I", data, pos + 8 + length)[0]
        if zlib.crc32(kind + body) & 0xFFFFFFFF != crc:
            fail(f"invalid {kind.decode('ascii', 'replace')} CRC")
        if header is None and kind != b"IHDR":
            fail("IHDR must be first")
        if kind == b"IHDR":
            if header is not None or length != 13:
                fail("invalid or duplicate IHDR")
            header = struct.unpack(">IIBBBBB", body)
            width, height, depth, color, compression, filtering, interlace = header
            if not (0 < width <= 16384 and 0 < height <= 16384):
                fail("unsupported dimensions")
            if expected is not None and (width, height) != expected:
                fail(f"wrong dimensions {width}x{height}; expected {expected[0]}x{expected[1]}")
            if depth != 8 or color not in (2, 4, 6) or compression or filtering or interlace:
                fail("unsupported PNG; use 8-bit non-interlaced RGB, RGBA or grayscale+alpha")
        elif kind == b"IDAT":
            if idat_closed:
                fail("non-consecutive IDAT chunks")
            idat.extend(body)
        elif kind == b"IEND":
            if length or not idat:
                fail("invalid IEND or missing IDAT")
            ended = True
            pos = end
            break
        else:
            if idat:
                idat_closed = True
            if kind == b"tRNS":
                fail("tRNS transparency is not portable; export an alpha channel")
            if kind == b"acTL":
                fail("animated PNG is unsupported; export individual frames")
            if not (kind[0] & 32) and kind != b"PLTE":
                fail("unsupported critical PNG chunk")
        pos = end
    if header is None or not ended or pos != len(data):
        fail("incomplete PNG or trailing bytes")
    result = {"width": width, "height": height, "color_type": color, "bit_depth": depth}
    if not decode:
        return result
    bpp = {2: 3, 4: 2, 6: 4}[color]
    stride = width * bpp
    expected_raw = (stride + 1) * height
    inflater = zlib.decompressobj()
    try:
        raw = inflater.decompress(bytes(idat), expected_raw + 1)
    except zlib.error as exc:
        fail(f"invalid compressed PNG data: {exc}")
    if len(raw) != expected_raw or not inflater.eof or inflater.unused_data:
        fail("incorrect PNG scanline data length")
    zero = partial = opaque = 0
    previous = bytearray(stride)
    for y in range(height):
        start = y * (stride + 1)
        filter_type = raw[start]
        row = bytearray(raw[start + 1:start + 1 + stride])
        if filter_type > 4:
            fail(f"unsupported row filter {filter_type}")
        if filter_type:
            for i in range(stride):
                left = row[i - bpp] if i >= bpp else 0
                above = previous[i]
                upper_left = previous[i - bpp] if i >= bpp else 0
                if filter_type == 1:
                    predictor = left
                elif filter_type == 2:
                    predictor = above
                elif filter_type == 3:
                    predictor = (left + above) // 2
                else:
                    p = left + above - upper_left
                    distances = (abs(p - left), abs(p - above), abs(p - upper_left))
                    predictor = (left, above, upper_left)[distances.index(min(distances))]
                row[i] = (row[i] + predictor) & 255
        if color == 2:
            opaque += width
        else:
            alphas = row[bpp - 1::bpp]
            row_zero, row_opaque = alphas.count(0), alphas.count(255)
            zero += row_zero
            opaque += row_opaque
            partial += width - row_zero - row_opaque
        previous = row
    result.update(alpha_zero=zero, alpha_partial=partial, alpha_opaque=opaque)
    return result
