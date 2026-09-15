# Original-engine reference

The user supplied an installed DOSBox package. On 2026-09-14, its bundled
DOSBox 0.74 launched Windows and `SCRANTIC.EXE /s` successfully. Direct window
inspection showed the original 640 by 480 island scene, Johnny in the water,
and a later fishing state. This establishes successful launch and progression
between observed states, not complete animation or audio parity.

The test reference is the supplied 16-bit executable identified below. A more
specific product revision has not been established. The separately installed
DOSBox-X is not the emulator used for this observation. No additional download
was needed. No original binaries were added to the repository.

| Local reference member | Bytes | SHA-256 |
| --- | ---: | --- |
| `DOSBox.exe` | 3727360 | `e09f78e60b5be25a6af0381b71a90b8aa625f2ea42ecd427638edf2abb7130f0` |
| `WINDOWS/SCRANTIC.EXE` | 295952 | `7811b526b36bba2f08326d7a680f2f063190b4278e5a36393fde5a02080b0262` |
| `SIERRA/SCRANTIC/RESOURCE.MAP` | 1461 | `3d9ec330aab96bbe5a44ce34f5945703862e82b195088590b7adfef5d7345da7` |
| `SIERRA/SCRANTIC/RESOURCE.001` | 1175645 | `df9c2213f7c0abacf4e302cb53a476f9f220579c07ba350b167e351eed548eae` |

## Repeatable windowed launch

The local installation is `C:\JohnCast`. Run its executable with an explicit
configuration and working directory; launching only the executable from another
directory started an unconfigured DOS prompt during this investigation.

```powershell
Start-Process -FilePath 'C:\JohnCast\DOSBox.exe' -ArgumentList '-conf C:\JohnCast\dosbox.conf' -WorkingDirectory 'C:\JohnCast'
```

The configuration's autoexec mounts the installation as guest C:, enters
`WINDOWS`, and runs `win runexit c:\windows\scrantic.exe /s`. The screensaver
INI points to guest `C:\SIERRA\SCRANTIC` and enables background, clouds,
waves and sounds. The observed profile started with `NumDays=1` and
`Introduction=1`; the program may update its profile as it runs.

The user explicitly requested windowed operation to keep the workstation
usable. `fullscreen=false` is now stored in the installed `dosbox.conf` and
was verified by a fresh launch with a visible window border. Its post-change
SHA-256 is `bd6bcc2e530fd24797735228cb89f08948fb862bc785bdc8d4413174b39425d4`.
The executable and resource hashes are unchanged. Future observation must keep
this windowed preference and avoid taking over the desktop.

## Scope of the reference

The site's [research notes](https://johnnycastawayscreensaver.com/research.html)
describe a 4:3 presentation, 11 story days, 63 tracked routines and 23 preserved
sound cues. They also discuss day/introduction eligibility, tides, fades and
sound continuing during visual stalls. Those are research claims to compare
against the executable and code, not measurements made by this launch check.

Its [download catalog](https://johnnycastawayscreensaver.com/download.html)
distinguishes original 16-bit files, compatibility packages and native community
editions. We selected the already supplied original-in-Windows environment;
a modern remake would not independently establish original-engine behavior.

No physical audio measurement, complete eleven-day playthrough, exact original
timing calibration, or comprehensive branch capture has been completed here.
The [extractor comparison](original-extractor-reference.md) records the separate
byte-level findings. Script presence and scheduler coverage belong in the
[port inventory](port-inventory.md).

## Complete embedded-audio comparison

A separate read-only inspection parsed the executable's NE resource table,
using its alignment shift to locate each resource rather than relying on the
legacy helper's offset list. It contains 23 RIFF/WAVE resources under type
`0xF005`. All 23 declared RIFF byte sequences exactly match unique bundled WAV
prefixes, including the size fields and complete audio data. The
[resource-by-resource report](original-ne-audio.json) records identifiers,
offsets, declared and allocated lengths, hashes and matched archive names.

For 22 sounds, the whole aligned original allocation also equals the entire
bundled WAV file. `sound0.wav` contains the 10,752-byte final allocation plus
the executable's last 16 bytes at `0x48400`. Those bytes begin with `NB02` and
are followed by twelve `FF` bytes. They fall outside the 10,306-byte declared
RIFF content. They are not missing PCM or zero padding. No audio file was
changed during this comparison.

To repeat the method, read the little-endian NE header pointer at DOS offset
`0x3C`, then the resource-table offset at NE offset `0x24`. Read the alignment
shift, each type/count record and its 12-byte resource entries. Shift each
offset and allocation length, identify RIFF/WAVE headers, and compare
`uint32_le(offset + 4) + 8` bytes with the same-length bundled WAV prefix.
Compare the aligned allocation separately; do not conflate it with RIFF length.

This establishes audio-payload coverage for this executable. It does not prove
the original translation from PLAY_SAMPLE IDs to NE resource IDs. In particular,
the missing filenames `sound11.wav` and `sound13.wav` cannot by themselves prove
that the port lost two original sounds. Cue selection and timing remain a
separate original-engine investigation.
