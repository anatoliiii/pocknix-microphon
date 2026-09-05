# Clear stale WCD microphone switch state

This is a conditional migration step, not a reset of the sound card. It matters
when an earlier driver or experiment saved extra DMIC switches as enabled.

## Why the driver patch alone may not be enough

The old port-indexed getter could report all switches sharing a port as enabled
when only one channel was selected. `alsactl store` then saved those values.
A later restore could actually enable the extra channels, including a DP3 mask
of 0x0f instead of the intended 0x04. Installing a corrected driver does not edit
that old state file. The successful recovery included correcting saved state;
this migration was missing from the initial public instructions.

The reference saved state for this **built-in-microphone-only** route is:

| Switch | Value |
|---|---|
| DMIC2 Switch | true |
| DMIC0, DMIC1, DMIC3 through DMIC7 Switch | false |
| MBHC Switch | false |

MBHC and DMIC2 alias a hardware bit. With the tested per-channel workaround,
clear MBHC and unwanted channels first, then set DMIC2 last. Do not run this
procedure during headset capture. An idle UCM session may legitimately switch
DMIC2 off; while capturing, the intended route must be selected. The table is the
reference saved migration state, not a requirement to keep the mic powered on.

## 1. Check the corrected driver is running

Complete the module build/install and verify the **loaded** build ID after boot
as described in INSTALL.md and VALIDATION.md. Do not trust getter readback or
resave state while still running the old port-indexed driver. Neither its
readback nor a newly installed file proves that the new module is executing.

The first boot with the corrected driver can still restore stale settings. If
so, perform this migration before acoustic acceptance and use one additional
controlled boot to test the corrected saved state. Do not hot-reload SoundWire
or mask errors to avoid that boot.

## 2. Back up and inspect

Close recording/voice applications, leave PipeWire/WirePlumber running, and
confirm your normal speakers work. Choose the actual ALSA card ID:

```sh
cat /proc/asound/cards
CARD=RetroidPocket
STATE=/var/lib/alsa/asound.state
STATE_BACKUP="$PWD/results/alsa-state-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$STATE_BACKUP"
# If your distribution uses another state path, change STATE first.
if sudo test -f "$STATE"; then
    sudo cp -a "$STATE" "$STATE_BACKUP/asound.state.before"
fi
amixer -c "$CARD" contents > "$STATE_BACKUP/mixer-before.txt"
for control in 'MBHC Switch' 'DMIC0 Switch' 'DMIC1 Switch' 'DMIC2 Switch' \
               'DMIC3 Switch' 'DMIC4 Switch' 'DMIC5 Switch' 'DMIC6 Switch' 'DMIC7 Switch'; do
    amixer -c "$CARD" cget "name='$control'" || break
done
```

Read the selected card's block in the saved state as well. If the controls or
card ID differ, stop and inspect your UCM/driver; do not substitute numeric numids.
If unwanted switches are already off, there is no need for a blanket reset.

## 3. Correct only the relevant switches and save

Run this only after the inspection above, with the corrected driver loaded and
no capture active. The subshell stops at the first failed control operation.
It leaves speaker gains, headphone routes and other mixer controls alone.

```sh
(
    set -e
    amixer -q -c "$CARD" cset "name='MBHC Switch'" 0
    for channel in 0 1 2 3 4 5 6 7; do
        amixer -q -c "$CARD" cset "name='DMIC${channel} Switch'" 0
    done
    amixer -q -c "$CARD" cset "name='DMIC2 Switch'" 1
    for control in 'MBHC Switch' 'DMIC0 Switch' 'DMIC1 Switch' 'DMIC2 Switch' \
                   'DMIC3 Switch' 'DMIC4 Switch' 'DMIC5 Switch' 'DMIC6 Switch' 'DMIC7 Switch'; do
        amixer -c "$CARD" cget "name='$control'"
    done
)
```

Verify the printed values match the table. If they do not, stop; do not save a
known-bad state. UCM or a recording application may be changing them, or a newer
alias-aware implementation may report MBHC differently. This exact procedure
is for the tested channel-index workaround; do not force its software readback
expectations onto a different driver.

Then save the current state using your distribution's ALSA state mechanism.
For the tested alsactl-based installation:

```sh
sudo alsactl -f "$STATE" store
sudo cat "$STATE" > "$STATE_BACKUP/asound.state.after"
sync
```

Inspect the relevant saved card block again. Do not copy a full state file from
another device, delete all ALSA state, or run `alsactl init` as a substitute.
If the distribution uses a different restore service/path, update the file it
actually reads. Keep an independent copy of the original state outside the repo.

## 4. Controlled boot and acceptance

Reboot manually after saving your work. Verify loaded driver identity and the
restored switches, then use the normal UCM Mic route and the tone/voice tests.
Check only fresh kernel messages for each capture window. If the previous boot
was already in a bus-error state, do not count it as a clean acceptance pass.
Do not read the complete Qualcomm master register dump during acceptance.

Verify normal system Speaker and active audio services afterward. This step
repairs persisted microphone-channel selection; it does not replace the DMIC3
left-input patch, the mono backend or the DT/UCM route.

## Rollback

If necessary, restore your own saved state file to the original STATE path and
apply it only with no active recording/playback, using the distribution's restore
procedure. Restoring the old file can reintroduce the original bad channel mask;
it is a rollback artifact, not a recommended working configuration. Restore
modules/DT separately as documented in ROLLBACK.md. No reboot is performed by
these instructions automatically.
