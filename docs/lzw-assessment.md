# Remaining LZW validation work

This assessment records existing behavior; it does not alter the decoder.
The prior cleanup rejects short output, but an output-length check alone does
not establish valid input codes. The maintenance plan intentionally separated
this investigation from the platform and tooling fixes.

The actual `jc_uncompress_test` probe uses method 2 and the production decoder.
The following bounded inputs completed with exit code zero at the inspected
maintenance baseline. Hex values describe the entire packed input.

| Input hex | Requested output bytes | Actual output hex | Interpretation |
| --- | ---: | --- | --- |
| Empty | 1 | `00` | EOF is replaced by a zero byte rather than refused. |
| `41` | 1 | `41` | An incomplete initial 9-bit code is accepted. |
| `0001` | 1 | `00` | First code 256 is treated as an initial byte. |
| `415802` | 3 | `414141` | Undefined code 300 after literal 65 is accepted as though it were the next dictionary code. |
| `410202` | 3 | `414141` | Valid next-code special case 257; this is an essential positive control. |
| `41020a01` | 2 | `4141` | Valid full-output return consumes three of four input bytes; requiring complete input consumption would break this contract. |

The probe output includes the production-method witness, resulting bytes and
consumed input count. These cases reproduce acceptance defects, not an observed
corruption of the shipped scenes. The existing golden comparison remains 2,452
decoded files; the broader original executable and resource comparison is in the
[knowledge base](knowledge-base/README.md).

A corrective pass should validate initial-code rules, input exhaustion, code
range, dictionary construction and reset/width transitions together. Controls
must vary those axes and preserve valid next-code handling and full-buffer
termination. Rebuild and execute the decoder for each deliberate guard removal,
then compare both shipped and supplied-original resource output. This work is
recorded in BACKLOG.md and is not claimed as completed by the short-output fix.
