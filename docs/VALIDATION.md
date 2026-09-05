# Acoustic validation

## Verify the running driver

`modinfo` describes the file on disk, not necessarily the loaded module. After
reboot compare the loaded build ID with `readelf -n` from the module you built:

```sh
python3 scripts/loaded-id.py
```

Keep the boot ID locally to prove that the second pass is a different boot.
Do not assume other builds must have the reference build ID in evidence/.

If an older driver saved unwanted channels, complete the
[ALSA state migration](ALSA-STATE.md) before counting acceptance boots.

## Record with an explicit start

Prerequisites: Python 3 standard library, pw-record/pw-play, journalctl, and local
sudo access for kernel logs. The script uses `sudo -n`; run `sudo -v` yourself
first if needed. It never changes mixer state, restarts services, reads debugfs,
installs modules, masks IRQs or reboots. Run as your normal desktop user.

```sh
sudo -v
python3 scripts/capture.py tones --out results/boot1-tones
python3 scripts/analyze.py results/boot1-tones/capture.wav
python3 scripts/capture.py voice --out results/boot1-voice
python3 scripts/analyze.py results/boot1-voice/capture.wav
```

Each capture prompts for Enter. Tones: 24 seconds, silence 0–4 s, 1 kHz 4–7 s,
silence 7–10 s, 1 kHz 10–13 s, then silence. Be quiet and confirm both tones came
from the real speakers. Voice: 15 seconds, speak for a few seconds, pause, then
speak again. Playback defaults to the system Speaker node, not headphone PCM0.
Override `--source`/`--sink` only after confirming the actual hardware nodes.

The two processes start slightly apart, and PipeWire adds latency. `timing.json`
records process launch times, not an exact ADC acoustic onset. Inspect central
seconds (5,6,11,12 for on; 2,3,8,9,14,15 for off) and account for actual shifts.

Check `kernel-after.txt`: no new Bus clash/MAX_RETRY/FIFO during normal capture.
No kernel-log access means that requirement is unverified. The tested pw-record
returned 1 at its sample-count limit despite full valid WAVs and no error text;
the script preserves return codes and checks exact WAV length/format. It does not
silently convert a nonzero exit into evidence that capture succeeded.

## Acceptance

All of these are required:

- Correct driver loaded, route and mono 48 kHz format.
- Confirmed audible stimulus; no reliance on pw-play exit code alone.
- 1 kHz appears only during both on intervals and disappears during off intervals;
  compare neighboring frequencies too, not merely a persistent spectral peak.
- Voice changes over time with speech and pauses.
- No fresh bus errors without suppressing IRQs.
- Speakers work through the normal system output; services remain active.
- Repeat after a second separate boot, saving results under new directories.

Full master `qualcomm-registers` reads can themselves drain/read FIFO and trigger
underflow. Do not perform them during this test. Nonzero digital noise, a startup
impulse and a visible input are not acoustic evidence.

## Reference result

One Flip2, two boots, same tested WCD module; no new messages in normal voice and
tone test windows. First boot also established regmap view 0x345d=0x89 and DP3
mask 0x04; both speakers were Attached during stimulus. The second-boot 1 kHz
amplitude was 1062–1098 PCM counts during on windows versus 0.023–0.228 in off
windows; neighboring 900/1100 Hz were below 0.27. Absolute levels depend on volume,
placement and ambient sound; these are observations, not universal thresholds.

The first voice pass included user-confirmed speech/pauses. In the second, the
user confirmed speaking but was unsure of the exact start; the full recording
contained a changing speech-like signal. Both tone runs were audibly confirmed.
Only aggregate measurements are published in evidence/; raw personal audio stays
private. The helper scripts here were cleaned up for publication; the measured
runs used their local predecessors. Offline helper tests are separate from the
two on-device acceptance passes.
