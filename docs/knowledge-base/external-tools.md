# External resource tools

Use these projects as additional resource readers and sources of implementation
ideas. Neither pinned revision is a reference implementation of the original
screensaver's complete behavior. This assessment inspected source on 2026-09-14;
it did not install dependencies or launch either application.

| Project | Reviewed commit | Appropriate use |
| --- | --- | --- |
| [xesf/castaway](https://github.com/xesf/castaway/tree/dea9bde8f0421bce6697bd1d2efcc813803c79b8) | `dea9bde8f0421bce6697bd1d2efcc813803c79b8` | Compare resource parsing, indexed-image exports and script text |
| [xesf/dgds-viewer](https://github.com/xesf/dgds-viewer/tree/4b98c8794fa9f6e000b6c4b2a1d4f7e623c88f49) | `4b98c8794fa9f6e000b6c4b2a1d4f7e623c88f49` | Design a visual asset browser and inspect resource relationships |

## Castaway

The [README](https://github.com/xesf/castaway/blob/dea9bde8f0421bce6697bd1d2efcc813803c79b8/README.md)
describes a JavaScript remake and resource-dumping tools. It also lists planned
behavior, which must not be treated as implemented coverage.

The [dump routines](https://github.com/xesf/castaway/blob/dea9bde8f0421bce6697bd1d2efcc813803c79b8/src/dgds/utils/dump.mjs#L62)
write each BMP image's dimensions, pixel data and indexed buffer under its original
zero-based image number. They also write TTM/ADS resource, tag and command text.
Those outputs can help cross-check a frame manifest or find the script referring
to a pose. The image export here is JSON/raw data, not a ready-made PNG authoring
pipeline.

The [scene table](https://github.com/xesf/castaway/blob/dea9bde8f0421bce6697bd1d2efcc813803c79b8/src/scrantic/metadata/scenes.mjs#L16)
contains ten entries, all from `ACTIVITY.ADS`. The
[story driver](https://github.com/xesf/castaway/blob/dea9bde8f0421bce6697bd1d2efcc813803c79b8/src/scrantic/story.mjs#L12)
chooses an entry but passes the loaded ADS to `startProcess` without the selected
tag. It does not establish eleven-day story or individual-outcome coverage.
The [interpreter](https://github.com/xesf/castaway/blob/dea9bde8f0421bce6697bd1d2efcc813803c79b8/src/dgds/scripting/process.mjs#L106)
has empty handlers for background saving, fades and other operations; its `GOTO`
ignores the requested tag. These are concrete reasons to avoid using playback as
an original-behavior oracle.

For audio, the [loader](https://github.com/xesf/castaway/blob/dea9bde8f0421bce6697bd1d2efcc813803c79b8/src/dgds/audio.mjs#L78)
and [sample dumper](https://github.com/xesf/castaway/blob/dea9bde8f0421bce6697bd1d2efcc813803c79b8/src/dgds/utils/dump.mjs#L9)
read a little-endian 32-bit RIFF size at byte offset 4 and add 8. The actual accessor
is signed `getInt32`, so this is useful evidence for the small supplied RIFFs, not
complete unsigned-length or container validation. Its hardcoded sample-index
offset table does not independently prove the original `PLAY_SAMPLE` mapping.

## DGDS Viewer

The [README](https://github.com/xesf/dgds-viewer/blob/4b98c8794fa9f6e000b6c4b2a1d4f7e623c88f49/README.md)
positions this project as a browser and dumper for several DGDS games. Its broader
game list does not establish correct playback of every Johnny Castaway command.

The [resource view](https://github.com/xesf/dgds-viewer/blob/4b98c8794fa9f6e000b6c4b2a1d4f7e623c88f49/src/ui/components/ResourceView.jsx#L16)
dispatches BMP images, palettes and SCR screens to canvas renderers and displays
TTM/ADS script listings. The
[BMP reader](https://github.com/xesf/dgds-viewer/blob/4b98c8794fa9f6e000b6c4b2a1d4f7e623c88f49/src/resources/bmp.js#L21)
retains image order and each image's own dimensions. Its
[sheet renderer](https://github.com/xesf/dgds-viewer/blob/4b98c8794fa9f6e000b6c4b2a1d4f7e623c88f49/src/graphics/index.js#L28)
places the images left-to-right, top-aligned, without scaling. That is useful for
comparing silhouettes, but the packed strip is not a scene coordinate system and
has no frame-number labels or semantic registration markers.

The [script component](https://github.com/xesf/dgds-viewer/blob/4b98c8794fa9f6e000b6c4b2a1d4f7e623c88f49/src/ui/components/ScriptCode.jsx#L52)
can highlight a current line, and `ResourceView` passes an update callback. However,
the pinned [process implementation](https://github.com/xesf/dgds-viewer/blob/4b98c8794fa9f6e000b6c4b2a1d4f7e623c88f49/src/scripting/process.js#L807)
never calls that supplied callback. A working live-line tracer should not be
claimed from this UI wiring alone. The interpreter also contains no-op handlers;
its shared opcode object defines some keys twice across ADS and TTM, including
`0xF010`, so the ADS fade handler replaces the TTM screen loader. Script listings
remain useful even when execution is incomplete.

The [package manifest](https://github.com/xesf/dgds-viewer/blob/4b98c8794fa9f6e000b6c4b2a1d4f7e623c88f49/package.json)
declares React 16, Electron 8, Webpack 4 and Node Sass 4, alongside its development
server and desktop wrapper. Launch compatibility with the current toolbox has not
been tested. Installing this historical frontend is unnecessary for the source
inspection and byte comparisons recorded here.

## Applying the useful parts

| Task | What to use | What still needs our evidence |
| --- | --- | --- |
| Frame numbering | Original BMP order, dimensions and raw-index exports | Match selected resource bytes and image numbers against our manifest |
| Contact sheets | Original-size, unscaled sprite presentation | Add explicit frame IDs, individual canvas boundaries and phase order |
| Art registration | Sprite dimensions plus script draw coordinates | Keep original canvas/landmark anchors; a packed strip cannot establish foot contact |
| Scene dependencies | ADS resource references and TTM tag/command listings | Trace the port's real interpreter and scheduler, including fallback and clipping |
| Audio extraction | RIFF length-field convention | Parse original NE allocations and separately establish script sample-ID mapping |

For acceptance, retain original-resource hashes, exact exported canvases and real
port captures. Compare pose registration, layering and time progression in the
engine rather than treating a second incomplete player as the expected image.
The [scene catalog](scene-catalog.md) and port crosswalk keep fan observations,
resource evidence and observed execution distinct.

## PNG artwork with JSON metadata

For future style packs, retain PNG pixels and pair them with structured metadata.
The existing art pipeline already checks JSON frame contracts and acceptance
records. Useful extensions are motion-family order, direction, front/back limb
ordering, measured registration landmarks, native timing and links to approved
reference images. Mark inferred landmarks separately from exact script coordinates.
These fields make alignment and coverage testable; they do not establish likeness
or replace a complete animated visual review.

The xesf raw-index JSON exports can help software compare decoded pixels and
palette indices. Converting every PNG into text pixel arrays would duplicate
large payloads without preserving any new facts. A textual description is also
incomplete: it cannot preserve all pixels needed to judge facial expression,
silhouette or gait. Base64 inside JSON is an image transport representation, as
shown in the [official image-input guide](https://developers.openai.com/api/docs/guides/images-vision),
not an additional source of visual semantics. Prefer labeled contact sheets and
real engine previews beside the metadata.

## Original audio comparison clarification

An independent read-only comparison of the supplied original executable and the
bundled ZIP confirms that all 23 declared RIFF/WAVE byte sequences match unique
bundled WAV prefixes. This is container-byte equality, not a claim about sample
selection or audible timing. The original executable hash and mapping evidence
belong in the [original extractor reference](original-extractor-reference.md).

The one full-allocation mismatch is `data/sound0.wav`: its declared RIFF occupies
10,306 bytes, the original NE allocation occupies 10,752 bytes, and the bundled
member occupies 10,768 bytes. Its first 10,752 bytes exactly match that allocation.
The extra 16 bytes match the executable immediately afterward at `0x48400`, through
EOF: an `NB02` marker followed by twelve `0xFF` bytes. They are outside both the RIFF
and NE allocation and are not zero padding. Their format meaning is not inferred
here. No production archive or extraction policy was changed by this review.
