# Final native package validation

This adapter compares the final standard package with the prior production ZIP
whose SHA256 is `4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be`.
It permits exactly ten shoreline replacements and four holiday additions. All
14 PNG identities and canvases are independently bound to the reviewed sources.
The final banner is the approved inset V2 reproduction, byte-identical to the
shown V1 PNG. The old ZIP may be recovered with binary Git output from commit
`1aad361fe78dde2c956e05dc451b8d5bab100af0`; never replace the live ZIP for replay.

The frozen native observer and driver execute the real renderer and public walk
calls. Source must match that runtime commit. Docker has no network, the source
mount is read-only, and Xvfb provides the display. No workstation window opens.

The 14 case pairs cover five day holiday states, high and low wave cycles with
and without clovers, shifted night clovers, both Johnny arrival routes, and night
and shifted banner cycles. All 28 initial captures must pass before the 28 fresh
process repeats. The comparison checks actual surface offsets, logical draws,
every high or low wave phase, public call timing and Johnny positions. Pixel
changes are limited to the union of the old and new ground, enabled wave
canvases and active holiday. Low tide retains its existing fallback artwork;
night retains the existing NIGHT.SCR. State is selected explicitly, so calendar
triggers and story cargo suppression are outside this validation.

Run `check_inputs.py --baseline <prior.zip> --candidate <final.zip>
--candidate-sha256 <hash> --output <fresh-input-checks> --phase smoke`, followed
by the same arguments with `--phase regression`. The regression retains damaged
input results and a fresh process that executes a copy with the payload guard
removed, then checks the restored original again. These checks do not write ZIPs.

Run `run.py --baseline <prior.zip> --candidate <final.zip> --output
build/shoreline-repair-v1/<fresh-run> --phase full`. The pinned existing Linux
image compiles a fresh observer, then performs smoke before repeat regression.
The launcher records the actual command, image, source commit, input hashes,
exit status and container cleanup. Eight focused native controls alter copied
logs or pixels in memory; the actual capture files stay unchanged.

`preserve.py --run <completed-run> --checks <completed-input-checks>` is a one-time
checkpoint writer. Skip it during replay because the retained evidence folder
is immutable. Replay into fresh scratch directories and compare the reports.
Bulk PPMs, ZIP copies and executable remain ignored; the compact binder retains
reports, logs, source snapshots, controls and excluded PNG identities. Technical
success does not extend the scope of the separately recorded human approvals.
