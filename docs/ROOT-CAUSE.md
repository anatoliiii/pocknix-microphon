# Root cause and provenance

## Missing DMIC3 input enable

Retroid factory `audio_wcd938x.ko` was extracted read-only from the device's saved
vendor image. Factory model: Retroid Pocket Flip2; Android vendor build
`RPFlip205011233`, Android 11, dated 2025-05-01. A previously collected “downstream”
directory contained Pixel modules and was not accepted as a Retroid reference.

The actual Retroid function `wcd938x_codec_enable_dmic` selects a special register
only for widget shift 2 (physical DMIC3). Its PRE_PMU sets `(0x345d, 0x80, 0x80)`;
POST_PMD clears that bit. The corresponding Qualcomm source names it
`dmic2_left_en`: [pinned Qualcomm source](https://android.googlesource.com/kernel/msm-extra/+/9d4f46987e6c8082b91ec4aff8487be077a31571/asoc/codecs/wcd938x/wcd938x.c).
This matches the inspected operation in Retroid machine code; it does not imply
that this entire public tree is the exact Retroid build source.

| Physical DMIC3 PRE_PMU operation | Register / mask | Factory | Linux before 0002 |
|---|---|---|---|
| Select digital input | 0x345a / 0x02 | clear | clear |
| Existing hardware delay | — | 250–260 µs | 250–260 µs |
| Left input enable | 0x345d / 0x80 | set | omitted |
| DMIC clock rate | 0x3462 / 0xf0 | 0x30 | 0x30 |
| Clock enable | 0x345d / 0x08 | set | set |
| Clock scaling | 0x345b / 0x06 | set | set |

Patch 0002 restores only the paired enable/disable. It does not alter delays,
IRQ masks, bus frequency, packing, channel routing or speaker code. Active
regmap view after the fix was 0x345d=0x89; regmap may return cached values, so this
was not claimed as independent hardware readback.

## SoundWire channel state

The tested baseline also fixed `port_enable[portidx]` to `[ch_idx]`. Several
channels share one port, so port-indexed switch bookkeeping can report a channel
already enabled when it is not. Patch 0001 reproduces this local tested workaround.

It is **not a complete alias fix**: MBHC and DMIC2 alias one hardware bit but can
retain separate software states. The tested route enables DMIC2 and leaves MBHC
off. Do not claim simultaneous headset/DMIC handling is solved.
[Jonathan Marek's proposal](https://www.spinics.net/lists/kernel/msg5941486.html)
uses actual `port_config[].ch_mask` instead. If your source already has that or
an equivalent fix, skip 0001; do not reintroduce the array or replace a newer fix
with this workaround. That alternative was not installed in this experiment.

## Other prerequisites and rejected experiments

Mono TX_3 and the DMIC3 DT/UCM route were already present before 0002. They alone
did not prove acoustic recovery. Patch 0003 preserves all other backend channel
counts, but it targets TX_3 across this machine driver, not a board-specific quirk;
review other boards if packaging it in a shared kernel.

VA/GPIO probing, DMIC enumeration, block-pack=1 and alternate row48 framing had
not produced a valid acoustic result and were left out. No delay tuning was used.

A full Qualcomm SoundWire master debugfs dump coincided with four FIFO underflows
per read. `swrm_reg_show` walks all register addresses including the read FIFO data
register (0x318 on this controller). Errors fell inside each master-dump window.
The same installed driver recorded speech and tones without new kernel messages
when those dumps were omitted. Do not read `qualcomm-registers` during acceptance
capture; do not mask IRQs to produce a clean log.
