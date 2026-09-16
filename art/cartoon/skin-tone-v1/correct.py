"""Reproduce a skin-only, post-export color pass without moving any pixel.

Run from any directory: python correct.py --output <new build directory>.
The original exported PNGs, fixed calibration patches and output masks are
explicit artifacts. This tool does not modify the production archive.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

BUNDLE = Path(__file__).resolve().parent


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def smooth(value: np.ndarray) -> np.ndarray:
    value = np.clip(value, 0.0, 1.0)
    return value * value * (3.0 - 2.0 * value)


def skin_confidence(rgba: np.ndarray) -> np.ndarray:
    """Conservative chromatic mask; semantic limits are independently reviewed.

    The red floor excludes dark ink and brown hair. Opponent-color ramps
    exclude near-white cloth/eyes and yellow-gold trim. Soft ramps retain
    antialiased skin mixtures rather than introducing a new hard contour.
    This is a confidence mask, not a claim of perfect semantic segmentation.
    """
    red, green, blue = rgba[:, :, :3].astype(np.float64).transpose(2, 0, 1)
    ratio = blue / np.maximum(green, 1.0)
    confidence = (
        smooth((red - 185.0) / 55.0)
        * smooth((red - green - 25.0) / 25.0)
        * smooth((green - blue - 10.0) / 15.0)
        * smooth((ratio - 0.32) / 0.15)
        * (1.0 - smooth((ratio - 0.79) / 0.08))
        * (rgba[:, :, 3] > 0)
    )
    return np.rint(confidence * 255.0).astype(np.uint8)


def recolor(rgba: np.ndarray, mask: np.ndarray, source_base: list,
            target_base: list) -> np.ndarray:
    """Apply fixed channel gains through mask; keep alpha and geometry exact."""
    if rgba.dtype != np.uint8 or rgba.ndim != 3 or rgba.shape[2] != 4:
        raise ValueError('Expected uint8 RGBA image')
    if mask.dtype != np.uint8 or mask.shape != rgba.shape[:2]:
        raise ValueError('Expected same-canvas uint8 mask')
    source = np.asarray(source_base, dtype=np.float64)
    target = np.asarray(target_base, dtype=np.float64)
    if source.shape != (3,) or target.shape != (3,) or np.any(source <= 0):
        raise ValueError('Expected positive three-channel base colors')
    result = rgba.copy()
    gain = target / source
    amount = mask.astype(np.float64)[:, :, None] / 255.0
    result[:, :, :3] = np.rint(np.clip(
        rgba[:, :, :3].astype(np.float64) * (1.0 + amount * (gain - 1.0)),
        0.0, 255.0)).astype(np.uint8)
    return result


def cap_exclusion(annotation: dict) -> np.ndarray:
    """Rasterize reviewed pixel-edge boundary with center-based membership."""
    width, height = annotation['canvas']
    boundary = np.asarray(annotation['lower_boundary_pixel_edges'], dtype=float)
    if np.any(np.diff(boundary[:, 0]) <= 0) or boundary[0, 0] != 0 or boundary[-1, 0] != width:
        raise ValueError('Cap boundary must span canvas with strictly increasing x')
    lower = np.interp(np.arange(width) + 0.5, boundary[:, 0], boundary[:, 1])
    protected = ((np.arange(height)[:, None] + 0.5) < lower[None, :]).astype(np.uint8) * 255
    if digest(protected.tobytes()) != annotation['mask_l_sha256']:
        raise ValueError(f"{annotation['frame']:03}: cap raster identity mismatch")
    return protected


def export(output: Path, frames: list[int] | None = None) -> dict:
    index_path = BUNDLE / 'input-index.json'
    calibration_path = BUNDLE / 'calibration-v1.json'
    cap_path = BUNDLE / 'protected-cap-polygons-v1.json'
    index = json.loads(index_path.read_bytes())
    calibration = json.loads(calibration_path.read_bytes())
    patches = {row['frame']: row for row in calibration['frames']}
    inputs = {row['frame']: row for row in index['frames']}
    cap_doc = json.loads(cap_path.read_bytes())
    caps = {row['frame']: row for row in cap_doc['frames']}
    if set(caps) != set(inputs) or cap_doc['input_index_sha256'] != digest(index_path.read_bytes()):
        raise ValueError('Cap exclusions must bind all frozen inputs')
    if set(patches) != set(inputs):
        raise ValueError('Calibration must cover exactly the frozen input frames')
    reference = calibration['reference_frame']
    if reference != 29 or reference != index['canonical_reference_frame']:
        raise ValueError('Reference must be user-selected frame 029')
    target = patches[reference]['base_rgb']
    if target != calibration['target_base_rgb']:
        raise ValueError('Target color must match reference patch')
    if frames is not None and not set(frames) <= set(inputs):
        raise ValueError('Unknown requested frame')
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for frame, row in inputs.items():
        if frames is not None and frame not in frames:
            continue
        source_path = BUNDLE / row['input']
        source_bytes = source_path.read_bytes()
        if digest(source_bytes) != row['sha256']:
            raise ValueError(f'{source_path.name}: frozen input hash mismatch')
        with Image.open(source_path) as image:
            if image.mode != 'RGBA' or list(image.size) != row['canvas']:
                raise ValueError(f'{source_path.name}: unexpected mode/canvas')
            rgba = np.asarray(image).copy()
        patch = patches[frame]
        if patch['input_sha256'] != row['sha256']:
            raise ValueError(f'{frame:03}: calibration input identity mismatch')
        x, y = patch['sample_xy']
        region = rgba[y-1:y+2, x-1:x+2]
        measured = np.median(region[:, :, :3].reshape(-1, 3), axis=0).tolist()
        if region.shape != (3, 3, 4) or np.min(region[:, :, 3]) < 250 or measured != patch['base_rgb']:
            raise ValueError(f'{frame:03}: fixed calibration patch changed')
        mask = skin_confidence(rgba)
        if caps[frame]['input_sha256'] != row['sha256'] or caps[frame]['canvas'] != row['canvas']:
            raise ValueError(f'{frame:03}: cap annotation input identity mismatch')
        protection = cap_exclusion(caps[frame])
        mask[protection > 0] = 0
        corrected = recolor(rgba, mask, patch['base_rgb'], target)
        if not np.array_equal(corrected[:, :, 3], rgba[:, :, 3]):
            raise ValueError(f'{frame:03}: alpha changed')
        changed = np.any(corrected[:, :, :3] != rgba[:, :, :3], axis=2)
        if np.any(changed & (mask == 0)):
            raise ValueError(f'{frame:03}: color changed outside skin mask')
        destination = output / 'sprites' / f'{frame:03}.png'
        mask_path = output / 'masks' / f'{frame:03}.png'
        destination.parent.mkdir(parents=True, exist_ok=True)
        mask_path.parent.mkdir(parents=True, exist_ok=True)
        if frame == reference:
            if not np.array_equal(corrected, rgba):
                raise ValueError('029: canonical reference must remain unchanged')
            destination.write_bytes(source_bytes)
        else:
            Image.fromarray(corrected).save(destination)
        Image.fromarray(mask).save(mask_path)
        records.append({
            'frame': frame, 'path': row['member'].removeprefix('data/styles/cartoon/'),
            'member': row['member'], 'runtime_canvas': row['canvas'],
            'input': row['input'], 'input_sha256': row['sha256'],
            'candidate_png': destination.relative_to(output).as_posix(),
            'candidate_png_sha256': digest(destination.read_bytes()),
            'rgba_sha256': digest(corrected.tobytes()),
            'alpha_sha256': digest(corrected[:, :, 3].tobytes()),
            'mask': mask_path.relative_to(output).as_posix(),
            'mask_sha256': digest(mask_path.read_bytes()),
            'protected_cap_mask_l_sha256': caps[frame]['mask_l_sha256'],
            'base_before_rgb': patch['base_rgb'], 'base_target_rgb': target,
            'base_after_rgb': np.median(corrected[y-1:y+2, x-1:x+2, :3].reshape(-1, 3), axis=0).astype(int).tolist(),
            'channel_gain': (np.asarray(target) / np.asarray(patch['base_rgb'])).tolist(),
            'changed_pixels': int(changed.sum()),
        })
    report = {
        'schema_version': 1, 'operation': 'post-export-color-correction',
        'scope': 'Draft color review; no production approval',
        'reference_frame': reference, 'target_base_rgb': target,
        'algorithm_sha256': digest(Path(__file__).read_bytes()),
        'input_index_sha256': digest(index_path.read_bytes()),
        'calibration_sha256': digest(calibration_path.read_bytes()),
        'cap_exclusions_sha256': digest(cap_path.read_bytes()),
        'frames': records,
    }
    (output / 'recipe.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--frames', type=int, nargs='+')
    options = parser.parse_args()
    result = export(options.output, options.frames)
    print(json.dumps({'status': 'PASS', 'frames': len(result['frames']),
                      'changed_frames': sum(r['changed_pixels'] > 0 for r in result['frames']),
                      'reference_frame': result['reference_frame']}))
