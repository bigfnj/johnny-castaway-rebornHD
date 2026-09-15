# Johnny Castaway knowledge base

This is the working reference for checking the port against the original and
planning later art packs. It combines a public scene guide, an inventory derived
from our code and resources, and observations of the supplied original program.
Presence in a catalog is not proof that every branch runs correctly.

| Record | Purpose |
| --- | --- |
| [Scene catalog](scene-catalog.md) and [event data](scene-catalog.json) | Activities, story chapters, visitors, rare events, holidays and reported faults described by the public guide. |
| [Port inventory](port-inventory.md) and [inventory data](port-inventory.json) | Script/resource membership, scheduler entries and implemented or partial commands, generated from local evidence. |
| [Original reference](original-reference.md) | Exact executable/resource identity, windowed launch and what has actually been observed. |
| [External tools](external-tools.md) | Pinned xesf engine/viewer source, useful art-inspection patterns and limits of their playback implementations. |
| [Extractor comparison](original-extractor-reference.md) | Proven walking-data equality and the historical sound extraction length/numbering defect. |
| [Original image comparison](original-image-comparison.md) | Executed decoding comparisons, original-versus-bundled pixel differences and limits of palette/runtime evidence. |
| [Cartoon review metadata](cartoon-art-metadata.md) and [asset data](cartoon-art-metadata.json) | All 21 approved replacements mapped to original identities, native dimensions, HD proxies, recipes, motion records and human acceptance. |
| [Calm focus image lessons](../art-style-learnings-calm-focus.md) | Expression selection, rejected leg/shorts edits, accepted motion differences and runtime toe-clearance work. |
| [Pose capture observations](pose-review-capture-notes.md) | Windows completion-log uncertainty, successful Linux scene review and platform-specific scene selection. |
| [Source manifest](sources.json) | Retrieval date, page URLs, response hashes and rendered-text hashes for the public research. |

## Evidence levels

Use `guide-reported` for a fact from the fan site, `resource-present` when an
original script/asset has a counterpart, `statically-reachable` when code links
it into an eligible execution path, and `observed` for an actual reference run.
Reserve `parity-verified` for a stated comparison with recorded inputs and
matching outputs. Record the scope: a matching resource name, decoded script,
single frame, sound buffer and complete animation establish different things.

The [public scene index](https://johnnycastawayscreensaver.com/list.html) is a
secondary source. It does not define an exhaustive test oracle. Its modern
restoration counts may share upstream research with this port, so matching
counts are not independent confirmation. The catalog captures the enumerated
facts, uses short original descriptions, and links back to the relevant pages.
It does not mirror the site's prose, screenshots or downloads.

## Comparing a scene

1. Pick an event ID and its candidate ADS scene or TTM tag from the inventory.
2. Record the original executable/resource hashes and settings before the run.
   Use a separate local reference profile for forced days or introduction values.
   Keep the workstation clock unchanged and DOSBox windowed.
3. Record the complete sequence, including entry state, tide, lighting, direction,
   object persistence, sound, transition and ending. Preserve ordinary pauses.
4. Run the port with isolated settings and fixed inputs. Compare original pixels
   and timing before judging alternate artwork. A partial art pack may correctly
   fall back to HD/original assets.
5. Add the result and any uncertainty to the inventory or a linked observation.
   Put confirmed gaps and unresolved implementation questions in BACKLOG.md.

An original display defect is reference behavior to document. Reproducing it
in the port is a separate decision. This research does not authorize silently
changing scene semantics or replacing approved artwork.

For artwork review, begin with the supplied-original reference layer. The bundled
resource pixels and upscaled HD PNGs have their own provenance; they are not
interchangeable with the supplied installation. Record pose, facing, limb order
and foot contact against original evidence, then compare each variant. Matching
dimensions or registration arithmetic does not establish artistic fidelity.

The current accepted Cartoon pilot contains six walking poses and 15 island
assets. Some earlier motion notes describe work as pending because they predate
the final acceptance. Their historical wording and image-generation lessons are
preserved; the final acceptance ledgers and current metadata describe coverage.

## Maintaining these records

Keep binary payloads, extracted audio, browser caches and long capture sessions
out of this documentation folder. The installed original is the local test
reference; hashes make it identifiable without copying it into Git. Preserve
the [art direction lessons](../art-style-learnings.md) alongside this knowledge
base when starting the next style pack.
