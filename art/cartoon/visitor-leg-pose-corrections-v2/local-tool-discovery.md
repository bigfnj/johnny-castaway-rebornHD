# Local image tooling discovery

Read-only inspection on 2026-09-21. No torch import, model load, prompt, GPU inference, installation, configuration change or remote image generation was performed. Discovery is sufficient for choosing a next step, not an operational generation test.

## Result

Local image-generation code and SDXL-Turbo weights are installed. The existing broker image route supports text-to-image generation, not reference-image editing. A Diffusers image-to-image class is installed, but a task adapter would still be needed and has not been created or executed. There is also a callable LaMa image-and-mask inpainting CLI; it has no text instruction or pose-reference input.

| Option | Evidence and entrypoint | Editing limits |
| --- | --- | --- |
| SDXL-Turbo through the platform broker | `D:/.ai-work/venvs/media-venv/Scripts/python.exe`. Source: `D:/.ai-work/projects/ai-platform/services/broker/app/media_worker.py`, `do_image` at line85. API: `POST /v1/image`; OpenAI-compatible generation route also documented. Worker CLI shape: `python media_worker.py <in.json> <out.json>`. | Worker accepts prompts, model, negative_prompt, steps and square size. Its actual pipeline call has no image, mask or reference argument. It cannot perform the requested reference edit through its present API. Broker host/port and authentication were not inspected. |
| SDXL image-to-image library | `D:/.ai-work/venvs/media-venv/Lib/site-packages/diffusers/pipelines/stable_diffusion_xl/pipeline_stable_diffusion_xl_img2img.py`: `StableDiffusionXLImg2ImgPipeline` at line188, call method at line975. | Installed library implementation only. A source-image/strength/prompt adapter could use it, but no working project CLI or multi-reference instruction-editing endpoint was verified. Identity, exact pose fidelity and transparent output are not established. |
| LaMa masked inpainting | `D:/.ai-work/venvs/media-venv/Lib/site-packages/simple_lama_inpainting/cli.py`. CLI shape, not executed: `D:/.ai-work/venvs/media-venv/Scripts/python.exe -m simple_lama_inpainting.cli <image> <mask> <output>`. | Image plus mask only; fills masked pixels without a text prompt or pose reference. The CLI converts input to RGB and mask to L. It is not a drop-in tool for instructed leg reconstruction and does not preserve source alpha through that path. |
| FLUX.1-schnell | Declared by the platform's `packages/edu-media-core/src/edu_media_core/images.py`, `get_flux`, and selected by broker model `flux-schnell`. Source uses nf4 transformer and T5 quantization. A cache directory exists at `D:/.ai-work/cache/hf-cache/hub/models--black-forest-labs--FLUX.1-schnell`. | Existing code path is text-to-image only. Cached FLUX model weight completeness was not verified in this bounded discovery, so readiness is not claimed. |

The media interpreter's exact path is `D:/.ai-work/venvs/media-venv/Scripts/python.exe`. Package metadata directories show Diffusers0.37.0, Torch2.13.0+cu130, Transformers5.5.4, Accelerate1.14.0, bitsandbytes0.50.0 and simple_lama_inpainting0.1.2. These are filesystem observations, not successful imports or compatibility tests.

## Confirmed model files

SDXL-Turbo snapshot:

`C:/Users/Admin/.cache/huggingface/hub/models--stabilityai--sdxl-turbo/snapshots/71153311d3dbb46851df1931d3ca6e939de83304/`

The snapshot contains model_index.json, scheduler/tokenizer/config files and these nonempty fp16 weight files:

| Relative path | Bytes |
| --- | ---: |
| text_encoder/model.fp16.safetensors | 246144152 |
| text_encoder_2/model.fp16.safetensors | 1389382176 |
| unet/diffusion_pytorch_model.fp16.safetensors | 5135149760 |
| vae/diffusion_pytorch_model.fp16.safetensors | 167335342 |

LaMa checkpoint is present at `C:/Users/Admin/.cache/torch/hub/checkpoints/big-lama.pt`. Its contents were not loaded or hashed. The installed model implementation reads `LAMA_MODEL` if set, otherwise resolves/downloads its standard checkpoint.

ProPainter source and three weight files are also under `C:/Users/Admin/AppData/Local/DevToolbox/models/propainter/`, with entrypoint `inference_propainter.py`. This is video inpainting/object removal, not a verified instruction-based still-sprite editor, so it is not the proposed route.

## Scope and resource limits

### Wallpaper Engine follow-up

The current `D:/.ai-work/projects/wallpaperengine/.venv` contains only lz4 4.4.5, NumPy 2.4.6 and Pillow 12.2.0, matching that project's pyproject.toml. It has no installed Torch, Diffusers or generative editor. Its ARCHITECTURE.md line266 explicitly remembers separate `myai`/SDXL and `wallpaper-imagegen`/FLUX outpaint pipelines, so the user's recollection has documentary support. Those repositories were not present in the current projects directory or matching worktree names inspected; their previous files or environments may be elsewhere. This was a bounded project inspection, not a whole-machine absence claim.

The D-drive Hugging Face cache lists both SDXL-Turbo and FLUX.1-schnell. No FLUX.2-klein or Qwen image-edit cache directory was seen in the two inspected Hugging Face cache roots. No models were downloaded or activated.

Checked DevToolbox's current manifest and scripts-utilities manifest/docs first. They did not expose an installed image-generation service; the separate ai-platform media environment supplied the concrete paths above. A bounded process listing showed Ollama and Python processes, mostly existing local review servers. Two Python command lines were unavailable, so this is not proof that no other service is running. No HTTP generation or service-state-changing call was made.

The platform source describes few-step SDXL/FLUX generation and a 24GB-card design, but no current edit-job VRAM or elapsed-time measurement was found. Runtime and peak VRAM for these sprite edits are therefore unknown. The broker documentation says media work can evict heavy models and uses short-lived subprocesses. Any inference needs the user's explicit GPU authorization under the standing local-model gate. No adapter or model activation is part of this report.
