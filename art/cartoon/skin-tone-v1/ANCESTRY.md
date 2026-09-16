# Skin-tone input ancestry

This record describes the 28 uncorrected runtime inputs. It does not approve
corrected colors or introduce new generated artwork. `ancestry.json` binds each
input to its exact raw drawing, prior recipe, exporter identity, original affine
registration, and historical review scope. All paths in that JSON are repository
relative.

The 25 inputs marked Main came from production ZIP
`1649218b32a4d11595806f8680e351a4f47950fcefbafdf8de758c2d225913db`
at commit `3af0242a74f234aab231d9203b48f78ca8e5c1b4`.
The other three are selected connecting drafts 009-v1, 010-v5 and 012-v1.
Private candidate `21194cf35e5b60eebfa9ba48520509ae8f86a72f26313b945f019671d1f345c5`
preserves all 2,591 production payloads and adds those three members.
The frozen inputs are sufficient for subsequent color-only correction; that
private ZIP need not remain on disk.

## Canonical lighter reference and human scope

Frame 029 is the second screenshot's lighter reference. Its actual raw source is
[029-heel-fit-v2.png](../walk-pilot/front-refresh-v1/029-heel-fit-v2.png),
SHA256 `e8efc7e91972fc7dca1bb3080a3cddc38b4e7519cb4fb7aaf98c31a1acbb922a`.
Its existing runtime PNG is
`8a33597aaba9206ff8ff98bad24bd12a52142eac0bdd56c92cbf4b7de798017a`.
This selection changes the palette reference; it does not select a new pose.

The user said, "while you work on that, the actual poses are accurate and well done."
[The immutable feedback](../walk-pilot/connecting-poses-v1/human-motion-feedback-v1.json)
also explicitly disputes color consistency. Static 009 and Face-v1 approvals
remain separately scoped. The six earlier production acceptance records preserve
what was reviewed previously, including the original colors, rather than approving
this new correction. Some ancestor technical recipes still say that human review
was pending at their creation; later acceptance records resolve that historical state.

## Executed source validation

Python 3.11.15, Pillow 12.3.0 and NumPy 2.4.6 were used. All 28 frozen PNG, RGBA,
alpha and canvas identities matched the input index. All 28 raw-source hashes
matched their recipe rows. Every input reproduced exactly as decoded RGBA pixels.
The 25 existing production rows also matched their historical accepted hashes
and recipe pointers. The full private/production member comparison preserved
all 2,591 existing payloads.

The preserved replay below then passed its frame029 smoke case, followed by the
full 28-frame replay. Both completed with exit code0 and wrote no files.

The reconstruction uses each original 0.1-scale affine transform: premultiply
to `RGBa`, BICUBIC affine sampling at 8x, LANCZOS reduction, then `RGBA`.
Historical 024-027 filter directly to their runtime canvas without padding.
The other frames use the recorded 64 HD padding and crop. The audit replays
those differences rather than normalizing them. This comparison is of decoded
pixels, not a claim that a newly encoded PNG has an identical envelope.

Raw 024-027 are bound through their immutable `source-images.zip` members.
Other rows use exact source files. The recorded pre-correction pack is a pinned
Git blob because the active pack will change at promotion; its Git LF hash differs
from the Windows checkout CRLF hash. No old artwork or record was rewritten.

## Source color observations

These are channel-wise median RGB values from near-opaque lower-leg/foot warm-color
samples. Counts describe runtime samples. They are a measurement proxy, not a
semantic material mask or an algorithm for correcting the artwork.

| Frame | Input status | Raw source RGB | Runtime RGB | Runtime samples |
|---|---|---|---|---|
| 000 | Main | 254, 152, 100 | 252, 151, 99 | 396 |
| 001 | Main | 253, 161, 104 | 252, 160, 103 | 709 |
| 002 | Main | 254, 163, 104 | 252, 161, 104 | 642 |
| 003 | Main | 254, 160, 105 | 252, 159, 104 | 440 |
| 004 | Main | 254, 165, 106 | 252, 164, 106 | 721 |
| 005 | Main | 254, 165, 109 | 252, 164, 109 | 772 |
| 006 | Main | 254, 164, 105 | 252, 162, 104 | 688 |
| 007 | Main | 254, 165, 108 | 252, 164, 107 | 461 |
| 008 | Main | 253, 165, 101 | 252, 164, 100 | 673 |
| 009 | Draft | 254, 155, 105 | 252, 154, 104 | 687 |
| 010 | Draft | 254, 157, 105 | 252, 156, 104 | 583 |
| 011 | Main | 253, 142, 91 | 252, 140, 90 | 394 |
| 012 | Draft | 253, 157, 102 | 252, 156, 101 | 689 |
| 015 | Main | 254, 148, 92 | 252, 147, 90 | 691 |
| 016 | Main | 254, 148, 94 | 252, 146, 93 | 628 |
| 017 | Main | 253, 144, 94 | 252, 142, 93 | 589 |
| 018 | Main | 254, 143, 88 | 252, 143, 87 | 487 |
| 019 | Main | 253, 135, 89 | 252, 134, 88 | 490 |
| 020 | Main | 254, 160, 104 | 252, 158, 103 | 521 |
| 021 | Main | 254, 144, 91 | 252, 143, 90 | 549 |
| 022 | Main | 254, 152, 99 | 252, 151, 97 | 563 |
| 023 | Main | 253, 138, 87 | 252, 137, 86 | 465 |
| 024 | Main | 254, 134, 85 | 252, 132, 84 | 443 |
| 025 | Main | 253, 132, 84 | 252, 130, 83 | 543 |
| 026 | Main | 253, 131, 87 | 251, 130, 86 | 530 |
| 027 | Main | 253, 134, 88 | 252, 133, 87 | 518 |
| 028 | Main | 254, 146, 90 | 252, 144.5, 89 | 560 |
| 029 | Main | 254, 149, 89 | 252, 147, 88 | 493 |

The older front 024-027 source drawings are redder than the newer profile 001-008
sources. Front 028-029 also differ from 024-027 before export. The same source
differences survive the documented filter. This is evidence of source palette
drift across drawings, not a wrong-source package substitution. These observations
do not establish that one family has the correct color; the user's 029 selection
supplies that artistic decision.

The exact measurement expression is:

```python
a = np.asarray(im.convert("RGBA")).astype(int)
mask = (
    (a[:, :, 3] >= 250)
    & (a[:, :, 0] >= 200)
    & (a[:, :, 1] > 65) & (a[:, :, 1] < 205)
    & (a[:, :, 2] > 40) & (a[:, :, 2] < 155)
    & ((a[:, :, 0] - a[:, :, 1]) > 45)
    & ((a[:, :, 1] - a[:, :, 2]) > 15)
)
mask[:int(y_min), :] = False
samples = a[:, :, :3][mask]
median = np.median(samples, axis=0)
mode = Counter(map(tuple, samples)).most_common(1)
```

For runtime images, `y_min = height * .65`. For raw images,
`y_min = (runtime_height * .65 - affine_ty) / affine_scale`.
Exact alpha255 alone is unsuitable for these statistics because many source
interiors have alpha254; it selects a much smaller, differently shaded sample.
The JSON preserves counts, modes and medians for both source and runtime.

## Read-only pixel replay

The following Python can run from the repository root with Pillow 12.3.0.
Passing `29` as its sole argument checks the canonical-reference smoke case;
running without frame arguments checks all 28. It uses the frozen inputs and
ancestors, so later production promotion does not invalidate this replay.
It writes no files. Source/approval identities and pixel equality are checked;
the separate color-correction tests own correction behavior.

```python
from pathlib import Path
import hashlib, io, json, sys, zipfile
from PIL import Image
import PIL

root = Path.cwd()
sha = lambda data: hashlib.sha256(data).hexdigest()
def read_bound(record):
    data = (root / record["path"]).read_bytes()
    assert sha(data) == record["sha256"], record["path"]
    return data

doc = json.loads((root / "art/cartoon/skin-tone-v1/ancestry.json").read_bytes())
index = json.loads(read_bound(doc["input_index"]))
index_rows = {row["frame"]: row for row in index["frames"]}
for path, record in doc["prior_acceptance_records"].items():
    read_bound({"path": path, "sha256": record["sha256"]})
for record in doc["pose_reviews"].values():
    read_bound(record["record"])
read_bound(doc["technical_selection"])
assert PIL.__version__ == "12.3.0"
requested = {int(value) for value in sys.argv[1:]}
rows = [row for row in doc["frames"] if not requested or row["frame"] in requested]
assert len(rows) == (len(requested) if requested else 28)
for row in rows:
    frame = row["frame"]
    recipe = json.loads(read_bound(row["ancestor_recipe"]))
    read_bound(row["ancestor_exporter"])
    source = row["raw_source"]
    if source["kind"] == "zip_member":
        with zipfile.ZipFile(io.BytesIO(read_bound(source["archive"]))) as bundle:
            raw = bundle.read(source["member"])
        assert sha(raw) == source["sha256"]
    else:
        raw = read_bound(source)
    spec = next(item for item in recipe["frames"] if item["frame"] == frame)
    assert source["sha256"] == spec["source_sha256"], frame
    runtime = Image.open(io.BytesIO(read_bound(row["runtime_input"]))).convert("RGBA")
    assert list(runtime.size) == row["runtime_input"]["canvas"] == spec["runtime_canvas"]
    assert sha(runtime.tobytes()) == index_rows[frame]["rgba_sha256"]
    assert sha(runtime.getchannel("A").tobytes()) == index_rows[frame]["alpha_sha256"]
    scale, _, tx, _, _, ty = spec["affine_forward"]
    pad = row["render_registration"]["padding_hd"]
    width, height = runtime.size
    size = (width + 2 * pad, height + 2 * pad)
    source_image = Image.open(io.BytesIO(raw)).convert("RGBA")
    high = source_image.convert("RGBa").transform(
        (size[0] * 8, size[1] * 8), Image.Transform.AFFINE,
        (1 / (scale * 8), 0, -(tx + pad) / scale,
         0, 1 / (scale * 8), -(ty + pad) / scale),
        resample=Image.Resampling.BICUBIC, fillcolor=(0, 0, 0, 0))
    replayed = high.resize(size, Image.Resampling.LANCZOS).convert("RGBA")
    replayed = replayed.crop((pad, pad, pad + width, pad + height))
    assert replayed.tobytes() == runtime.tobytes(), f"{frame:03}: RGBA replay mismatch"
print(f"PASS {len(rows)} frozen inputs reproduced pixel-exactly; no files written")
```
