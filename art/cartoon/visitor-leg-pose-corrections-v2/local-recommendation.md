# Proposed local editing trial

Recommendation on 2026-09-21: start with Black Forest Labs FLUX.2 [klein] 4B for a single SSUZY1 003 edit. This is a proposed workflow, not an installed or tested local result.

The official model card lists single- and multiple-reference editing, Diffusers and ComfyUI support, and approximately 13 GB VRAM. That makes it a practical first trial on the user's 24 GB RTX 4090. Actual peak usage depends on resolution, references and offloading. No runtime or memory measurements have been taken on this machine for this model.

Source: https://huggingface.co/black-forest-labs/FLUX.2-klein-4B

Use the byte-identical 001 PNG and exact 003 prompt preserved in `local-generation-handoff/`. First assess whether the bottle and cap are removed, the empty forearm moves slightly inward, and the character's face, swimwear, torso and two-leg pose remain consistent. The model's suitability for this artwork is a hypothesis until that visual test passes.

Use an isolated editing environment or standalone job. The existing SDXL-Turbo / FLUX.1-schnell broker endpoint is text-only and does not accept these reference inputs. Do not change the Wallpaper Engine environment to add unrelated generation dependencies.

No native transparent-output capability has been verified for this local workflow. Inspect returned image mode and background rather than assuming the prompt creates an alpha channel. Do not silently change the established transparent-asset workflow or call an opaque PNG production-ready.

The current Wallpaper Engine environment and cached tools are documented in `local-tool-discovery.md`. The user subsequently authorized creation of the isolated environment and running local tests. See `session-status.md` for the exact authorization and `local-generation-test/` for execution records.
