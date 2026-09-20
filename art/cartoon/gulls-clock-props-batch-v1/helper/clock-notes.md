# Clock and sleep-symbol draft notes

Twenty requested source slots are complete: MEANWHIL.BMP 000 through 016 and ZZZZS.BMP 000 through 002. Every call used built-in ImageGen after its exact request was saved. The recorder copied each raw PNG byte-for-byte and retained the request, reference and output hashes. There are 22 raw outputs including two retained first attempts.

Recommended selection for the family review is MEANWHIL 002 v2 and 006 v2, with all other clock and sleep slots at v1. This is an author selection for human appearance review, not user approval or runtime acceptance.

Watch 000 keeps the gold rim and crown, white numbered dial, central green face with two visible eyes and smile, source-colored head details and small checker shoes. The sixteen separate arms preserve their major source bends, attachment-side locations and pointing directions. They contain no complete watch bodies. Native pivot alignment and common-scale fitting have not been performed; the raw drawings must not be independently stretched to simulate that result.

The 002 v1 gray shadow was real under alpha composition. A focused built-in edit removed it while retaining the arm geometry. Two sampled haze pixels changed from alpha 58 and 47 to alpha 1 and 0 in v2; the light-background composite is visibly clear. Selected 002 SHA256 is d278456af07f81fd5072d4f6d591bf7b584246d3d6592e827f9383f221be64e7.

The 006 v1 added a round ball at the attachment end. A focused built-in edit replaced it with a plain narrow end while retaining the J-shaped arm and upward-pointing finger. Selected 006 SHA256 is f2e50c98bf4ff86ee8df7e16412fa24d9392bf09177e5f47a4a2800697857880.

The green halos visible in the raw tool previews for 007, 009, 013 and 015 disappear when composited using alpha. Those four outputs have maximum alpha 254 and were preserved as returned. All other selected outputs reach alpha 255. No selected output has meaningful edge clipping; 010 has a maximum edge alpha of 1 and the others have 0. The sleep symbols are single white Z letters with transparent negative spaces, not multiple-letter clouds. Their raw-preview speckles disappear in actual-alpha composition.

Source-versus-output contact sheets and transparency diagnostics were inspected under ignored build/gulls-clock-worker. No generated pixels were repainted, thresholded, keyed, cropped or otherwise modified. No runtime files, production package, gallery, central selector or Git state was changed by this worker. Full tests and native motion review remain deferred by the batch workflow.
