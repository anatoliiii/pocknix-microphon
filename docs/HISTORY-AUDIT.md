# Retained changes and earlier experiments

A read-only audit compared the earlier repair records, both available kernel
source trees, installed module hashes and the tested boot DTB. No additional
retained kernel patch was found beyond patches 0001–0003 in this repository.
The imported baseline versions of WCD938x, LPASS VA, SM8250 and Qualcomm
SoundWire matched the available Linux source archive byte-for-byte. This is a
comparison against the locally available archive, not independent verification
of that archive's provenance or a claim about every PockNix release.

## Required repair components

- WCD channel switch bookkeeping and physical DMIC3 left-input enable.
- Mono TX3 machine backend, DT DMIC3 endpoint/MIC BIAS3/SWR route, and Mic UCM.
- The supplied WirePlumber format restriction was present during acceptance.
- [Saved ALSA state migration](ALSA-STATE.md), when an old driver saved extra
  channels. This step was omitted from the first public instructions.

## Power configuration already present in PockNix

The tested installation also retains the distribution rule
`/usr/lib/udev/rules.d/99-wcd938x-nosleep.rules`, setting SoundWire WCD938x
`power/control` to `on` on bind. The installed rule matches the SM8250 BSP source;
its comment describes a jack-detection workaround. Preserve the distribution's
power policy. It was not introduced by the final microphone repair, and we did
not test microphone acceptance with that rule removed. Do not interpret the
absence of a new power patch as proof that baseline power configuration is
irrelevant. Use the matching PockNix BSP rather than copying this fix onto an
otherwise unspecified generic Arch installation.

## Earlier diagnostic helpers

The old `pocknix-internal-mic.service` (pins/VA-clock helpers) and user
`pocknix-internal-mic-verify.service` are disabled and inactive in the tested
state. No custom `pocknix_*` helper module is loaded. If you participated in
those earlier experiments, inspect and disable their automatic startup before
following this recovery; they are not installation prerequisites. Do not disable
the normal PipeWire, PipeWire Pulse or WirePlumber services.

The old `pocknix-internal-mic` command uses numeric mixer IDs that no longer match
the tested controls. Do not run it as a setup step. Use the named UCM controls
and current instructions instead.

Temporary bias/DAPM forcing, direct VA clock/pin register experiments and IRQ
reset helpers are not part of the accepted repair. The MIC BIAS3 supply route
is represented in the DT example. Block packing and alternate row48 framing
were unsuccessful experiments, not additional fixes to install.

## DT limits of the evidence

The tested DTB still contains historical VA DMIC routes and pin configurations
alongside the working WCD route. They were not removed for the successful tests.
There is no evidence that they caused the WCD repair, but a clean DT with those
entries removed has not been acoustically validated. The public DT fragment
therefore documents the WCD additions, not a byte-for-byte reconstruction of the
entire tested board tree. Preserve the existing board configuration; do not
blindly add or remove historical VA routes. A minimal-DT validation remains
separate work. No live audio settings were changed during this audit.
