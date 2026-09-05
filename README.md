# Retroid Pocket Flip2 microphone recovery on PockNix

[Русская инструкция](README.ru.md) · [Install](docs/INSTALL.md) · [Evidence](docs/VALIDATION.md)

A reproducible repair for a built-in microphone that appears in PipeWire but
records zeros after a startup transient on the **Retroid Pocket Flip2 with
SM8250 / WCD9385**. Validated on one device running PockNix kernel **7.2.0**, with
speech and switched 1 kHz tones after **two separate boots**. Speakers remained
functional and normal test captures produced no new kernel messages.

The decisive fix enables **bit 7 of WCD938x register 0x345d** for physical DMIC3
and clears it at shutdown. The factory driver calls this `dmic2_left_en`.
Physical **DMIC3**, SoundWire **DMIC2**, and the **DMIC2_CTL register** use different
numbering; they refer to the same tested path, not three interchangeable inputs.

```text
WCD938x DMIC3 → SWR_DMIC2 → TX DEC0 → TX_CODEC_DMA_TX_3 → MultiMedia3
```

## Start here

1. Read [scope and prerequisites](docs/INSTALL.md#scope-and-prerequisites).
2. Check which [patches and routing prerequisites](docs/INSTALL.md#choose-the-changes)
   your build already contains. Do not blindly apply a whole series.
3. Back up, build for your exact kernel, verify ABI, install and reboot.
   Check [stale ALSA state](docs/ALSA-STATE.md); it can require a migration boot.
4. Follow [acoustic validation](docs/VALIDATION.md), then repeat after a second boot.
5. Keep a [rollback path](docs/ROLLBACK.md).

If mono TX_3, the UCM/DT route and correct SoundWire channel state already exist,
the decisive change is only [patch 0002](patches/0002-wcd938x-enable-dmic3-left-input.patch).
A PipeWire source, non-zero noise or a successful playback exit code is not enough
to establish microphone recovery.

## Contents

- `patches/`: two tested WCD changes and a conditional mono TX_3 change.
- `config/`: microphone-only UCM, WirePlumber and DT integration examples.
- `scripts/`: module staging, explicit user-started recording and PCM analysis.
- `evidence/`: aggregate measurements and source hashes, without recordings.
- `docs/`: root cause, build/install, validation, rollback and publication notes.

No universal `.ko` is supplied: release strings alone do not guarantee kernel ABI
compatibility. Other Retroid models, kernels and simultaneous headset capture
were not validated. The local channel-index workaround has an alias limitation;
see [root cause](docs/ROOT-CAUSE.md).

Licensing: [MIT](LICENSE) for original docs/scripts/config examples;
[GPL-2.0-only](LICENSES/GPL-2.0-only.txt) for Linux-derived patches. See [NOTICE](NOTICE).
