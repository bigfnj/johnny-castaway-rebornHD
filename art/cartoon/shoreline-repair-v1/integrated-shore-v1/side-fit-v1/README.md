# Side-wave placement and clean center review

The enlarged approved island hid substantial portions of the existing side
waves. The V1 exporter uses the original unmasked side drawings, moves each
family consistently and recomputes the same ground visibility mask. It retains
the complete artwork at its existing scale. Left frames move 6 HD pixels left
and 8 down; right frames move 10 right and 10 down. The runtime accepts their
registered larger canvases while retaining the original logical positions.

The side-only V1 recipe and candidates remain historical inputs. The combined
native V2 comparison adds the single center 007 correction from
`../foam-shading-v1/`, removing the dark gray band the user identified. It
changes exactly seven ZIP payloads and retains the remaining 2,591, including
the approved ground, center phases 006/008, decorations and Johnny.

The full native comparison passed ten smoke captures before ten fresh exact
repeats. It covers high-tide clovers, shifted night clovers, low tide and both
Johnny routes. Timelines and positions match, low tide is pixel-identical and
all other differences stay inside the selected wave areas. Six negative
controls and an executed package-guard mutation passed. The complete compact
record is `native/evidence-v2/evidence.json`.

The captured selection report initially inherited an old raw-source annotation
and byte-identity flag for 007. Its package checks already bound the correct new
runtime PNG. The separate `native/verification-v2/corrected-selection-v2.json`
and `metadata-clarification.json` fix that ancestry for eventual integration,
without changing any captured input or pixel. Keep both records.

The synchronized browser review defaults to the corrected 007 phase and loops
the actual high-tide wave cycle. Human review of this combined motion is still
pending. Production has not been changed.

For replay after production changes, recover `assets/scrantic_data.zip` from
Git commit `1aad361fe78dde2c956e05dc451b8d5bab100af0` into a separate build file
using binary subprocess output. Its SHA256 is
`4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be`.
The side exporter accepts that preserved archive through `--archive`. Earlier
ancestor exporters that hardcode the production path must run in an isolated
scratch tree containing that recovered archive. Never replace the live archive
temporarily to reproduce historical art.
