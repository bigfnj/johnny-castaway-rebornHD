"""Run one authorized local FLUX.2 klein reference edit and retain its raw result."""
from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import time
import traceback

from PIL import Image, ImageStat

HERE = Path(__file__).resolve().parent
FAMILY = HERE.parent


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pin(path: Path) -> dict:
    return {"path": path.resolve().as_posix(), "sha256": digest(path)}


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def gpu_snapshot() -> str:
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,memory.free", "--format=csv"],
            capture_output=True, text=True, timeout=15, check=False,
        )
        return result.stdout.strip() if result.returncode == 0 else "unavailable"
    except (OSError, subprocess.TimeoutExpired):
        return "unavailable"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--model-path", type=Path)
    parser.add_argument("--prompt-file", type=Path)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--max-edge", type=int, default=1024)
    parser.add_argument("--steps", type=int, default=4)
    parser.add_argument("--run", action="store_true", help="Load model and perform the authorized GPU edit.")
    args = parser.parse_args()
    if not args.run_id or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for c in args.run_id):
        parser.error("run-id must contain only lowercase letters, digits, hyphens or underscores")
    if not 256 <= args.max_edge <= 2048:
        parser.error("max-edge must be between256 and2048")

    outdir = HERE / args.run_id
    outdir.mkdir(parents=True, exist_ok=False)
    original_request = json.loads(args.request.read_text(encoding="utf-8-sig"))
    arguments = original_request["arguments"]
    prompt = (args.prompt_file.read_text(encoding="utf-8") if args.prompt_file
              else arguments["prompt"])
    (outdir / "prompt.txt").write_text(prompt, encoding="utf-8")
    refs, images = [], []
    for index, name in enumerate(arguments["referenced_image_paths"], 1):
        source = Path(name)
        with Image.open(source) as original:
            rgba = original.convert("RGBA")
            # The local VAE accepts RGB. Preserve source bytes and make this adapter explicit.
            canvas = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
            rgb = Image.alpha_composite(canvas, rgba).convert("RGB")
            scale = min(1.0, args.max_edge / max(rgb.size))
            size = tuple(max(16, round(v * scale / 16) * 16) for v in rgb.size)
            rgb = rgb.resize(size, Image.Resampling.LANCZOS)
            prepared = outdir / f"reference-{index:02d}-rgb.png"
            rgb.save(prepared)
            refs.append({"source": pin(source), "source_mode": original.mode,
                         "source_size": list(original.size), "input": pin(prepared),
                         "input_size": list(rgb.size)})
            images.append(rgb)
    width, height = images[0].size
    record = {
        "schema_version": 1, "status": "prepared", "model": "black-forest-labs/FLUX.2-klein-4B",
        "source_request": pin(args.request), "prompt": pin(outdir / "prompt.txt"),
        "source_request_tool": original_request.get("tool"),
        "prompt_matches_source_request": prompt == arguments["prompt"], "references": refs,
        "input_preprocessing": "Alpha composited on white, then resized to max-edge and multiples of16. Original PNGs unchanged.",
        "settings": {"width": width, "height": height, "steps": args.steps,
                     "seed": args.seed, "guidance_scale": 1.0, "max_sequence_length": 512,
                     "dtype": "bfloat16", "model_cpu_offload": True},
        "output_policy": "Raw local RGB result. No alpha extraction or production replacement.",
        "user_authorized": "User explicitly requested building the .venv and running tests on2026-09-21.",
        "appearance_approval": None, "production_integrated": False,
    }
    save(outdir / "record.json", record)
    if not args.run:
        print(json.dumps({"status": "prepared_without_model_load", "folder": str(outdir), "size": [width, height]}), flush=True)
        return 0
    if args.model_path is None or not (args.model_path / "model_index.json").is_file():
        raise ValueError("--model-path must identify a complete downloaded local snapshot")
    # No credential lookup or network access is needed in the inference process.
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    import torch
    from diffusers import Flux2KleinPipeline

    record["packages"] = {name: importlib.metadata.version(name) for name in
                          ["torch", "diffusers", "transformers", "accelerate", "Pillow"]}
    record["model_snapshot"] = args.model_path.resolve().as_posix()
    record["model_index"] = pin(args.model_path / "model_index.json")
    record["gpu_before"] = gpu_snapshot()
    pipe = None
    generated = None
    start = time.perf_counter()
    success = False
    try:
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is unavailable in the isolated environment")
        record["gpu"] = torch.cuda.get_device_name(0)
        torch.cuda.reset_peak_memory_stats()
        print("Loading local FLUX.2-klein-4B snapshot with CPU offload.", flush=True)
        pipe = Flux2KleinPipeline.from_pretrained(
            str(args.model_path), torch_dtype=torch.bfloat16,
            local_files_only=True, use_safetensors=True,
        )
        pipe.enable_model_cpu_offload()
        record["model_load_seconds"] = round(time.perf_counter() - start, 3)
        record["status"] = "running"
        save(outdir / "record.json", record)
        infer_start = time.perf_counter()
        print(f"Editing {width}x{height}, {args.steps} steps, seed{args.seed}.", flush=True)
        with torch.inference_mode():
            result = pipe(
                image=images, prompt=prompt, width=width, height=height,
                num_inference_steps=args.steps, guidance_scale=1.0,
                max_sequence_length=512,
                generator=torch.Generator(device="cpu").manual_seed(args.seed),
            )
        torch.cuda.synchronize()
        record["inference_seconds"] = round(time.perf_counter() - infer_start, 3)
        generated = result.images[0]
        path = outdir / "output-raw.png"
        generated.save(path)
        with Image.open(path) as check:
            check.load()
            if check.size != (width, height) or max(ImageStat.Stat(check.convert("RGB")).stddev) < 1:
                raise RuntimeError("Generated PNG failed dimensions/nonconstant-content smoke check")
            record["output"] = {**pin(path), "mode": check.mode, "size": list(check.size),
                                "has_alpha": "A" in check.getbands()}
        record["peak_allocated_gib"] = round(torch.cuda.max_memory_allocated() / 2**30, 3)
        record["peak_reserved_gib"] = round(torch.cuda.max_memory_reserved() / 2**30, 3)
        record["status"] = "image_returned_needs_visual_review"
        success = True
    except Exception:
        record["status"] = "failed"
        record["error"] = traceback.format_exc()
        print(record["error"], flush=True)
    finally:
        pipe = None
        generated = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        record["process_seconds"] = round(time.perf_counter() - start, 3)
        record["gpu_after_cleanup_before_process_exit"] = gpu_snapshot()
        save(outdir / "record.json", record)
        print(json.dumps({"status": record["status"], "folder": str(outdir),
                          "seconds": record["process_seconds"]}), flush=True)
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
