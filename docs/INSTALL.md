# Build and install

## Scope and prerequisites

Validated: one Retroid Pocket Flip2 (SM8250 / WCD9385), PockNix kernel 7.2.0,
PipeWire 1.6.8. No claim of other hardware/kernel support. This guide presumes a
working PockNix installation with functional speakers and its distribution's
kernel source/build configuration. The experiment used a locally modified
kernel tree; its local commit is not a downloadable upstream release identifier.
Source preimage SHA256 values are in `evidence/tested-state.json`.

You need Git, Python 3, binutils, make and the kernel's matching toolchain/config,
generated headers and full `Module.symvers`. `modules_prepare` alone does not
provide symbol versions. Obtain the build recipe/source for your installed
PockNix version from its maintainer/distribution; do not substitute random
upstream headers. The repository contains patches, not a complete PockNix image.

```sh
uname -r
modinfo snd_soc_wcd938x
wpctl status
```

Keep an externally accessible backup of the SD/boot files before modifying the
kernel. Confirm which DTB and root filesystem your boot entry actually uses.

## Choose the changes

| Existing state | Action |
|---|---|
| DMIC3 PRE_PMU/POST_PMD already handle 0x345d BIT(7) | Skip 0002; this specific omission is already fixed |
| Missing DMIC3 left enable | Apply 0002 |
| Switches use port_enable[portidx] | Review/apply 0001 |
| Actual channel mask or equivalent bookkeeping already used | Skip 0001 |
| TX_3 still forced stereo | Review optional 0003 and rebuild machine module |
| DMIC3 power/endpoint or SWR route absent | Merge DT example, preserving all other routes |
| Correct Mic UCM/format already present | Preserve it; no configuration replacement needed |

For a tree matching the tested WCD preimage:

```sh
REPO=$(pwd)
KERNEL_SRC=/absolute/path/to/matching/kernel/source
KERNEL_BUILD=/absolute/path/to/matching/kernel/build
# These paths are examples: replace them with your distribution build paths.
git -C "$KERNEL_SRC" apply --check "$REPO/patches/0001-wcd938x-track-switches-per-channel.patch"
git -C "$KERNEL_SRC" apply "$REPO/patches/0001-wcd938x-track-switches-per-channel.patch"
git -C "$KERNEL_SRC" apply --check "$REPO/patches/0002-wcd938x-enable-dmic3-left-input.patch"
git -C "$KERNEL_SRC" apply "$REPO/patches/0002-wcd938x-enable-dmic3-left-input.patch"
```

Stop on a failed check; inspect the source instead of forcing offsets. Apply
0003 similarly only if needed. It expects the existing `cpu_dai` variable in
`sm8250_be_hw_params_fixup`; adapt with review if the function differs.

## Saved ALSA state migration

Before acoustic acceptance, inspect [saved WCD switch state](ALSA-STATE.md).
The old driver may have persisted extra channels as enabled. Correcting the
driver alone does not clean that file. Perform the migration only with the
corrected driver loaded; preserve speakers and avoid a whole-card reset.

## Build

For a WCD-only repair with unchanged driver headers/ABI:

```sh
python3 scripts/stage-module.py "$KERNEL_SRC" "$REPO/build/wcd"
make -C "$KERNEL_SRC" O="$KERNEL_BUILD" M="$REPO/build/wcd" -j2 modules
NEW_MODULE="$REPO/build/wcd/snd-soc-wcd938x.ko"
```

Keep build logs. If you need machine-driver/DT changes, use the distribution's
normal full kernel/module/DT build recipe for your board. Do not try to compile
only `sm8250.c` as a standalone module: its Kbuild dependencies also matter.
The tested external-module recipe used GCC 16.1.1 and binutils 2.46.0. BTF was
skipped because that build tree lacked vmlinux. This does not prescribe a compiler
for other kernel builds.

## ABI and installation

```sh
OLD_MODULE=$(modinfo -n snd_soc_wcd938x)
modinfo -F vermagic "$OLD_MODULE"
modinfo -F vermagic "$NEW_MODULE"
readelf -n "$NEW_MODULE"
nm -u "$NEW_MODULE"
```

Require successful MODPOST with the matching full Module.symvers, matching
vermagic, target architecture, kernel config and symbol versions. Check imports
against the build's Module.symvers; compare with the existing module. With 0002
alone the tested imports did not change. Equal vermagic is necessary, not
sufficient. Use your distribution's signing flow if signing is enforced; the
tested system had CONFIG_MODVERSIONS and CONFIG_MODULE_SIG disabled.

The following commands are **only for an existing uncompressed `.ko` target**,
as on the tested device. For `.ko.zst`/`.ko.xz` or packaged/signed modules use the
distribution tooling; do not write an uncompressed ELF over a compressed file.

```sh
case "$OLD_MODULE" in *.ko) ;; *) echo 'Use distribution module packaging'; exit 1;; esac
BACKUP="$REPO/build/backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP"
cp -a "$OLD_MODULE" "$BACKUP/snd-soc-wcd938x.ko"
sha256sum "$BACKUP/snd-soc-wcd938x.ko" > "$BACKUP/SHA256SUMS"
printf '%s\n' "$OLD_MODULE" > "$BACKUP/installed-path.txt"
sudo install -m 644 "$NEW_MODULE" "$OLD_MODULE"
sudo depmod -a "$(uname -r)"
sha256sum "$OLD_MODULE"
sync
```

Record the new file's build ID, backup path and running boot ID before reboot.
The running module is still the old instance until reboot. If your distribution
includes this module in initramfs, rebuild it using its supported procedure.
The tested boot entries did not use initramfs. Reboot manually once after all
required changes; do not use SoundWire unbind/rebind or hot reload as a shortcut.
After boot, [validate the loaded build ID](VALIDATION.md) and test acoustically.

## UCM / DT / WirePlumber when missing

Back up the existing DTB, UCM file and relevant WirePlumber config before editing.
`config/Mic.conf.fragment` replaces only `SectionDevice."Mic"` in the existing
Retroid `HiFi-RP.conf`; the existing HiFi verb must enable
`MultiMedia3 Mixer TX_CODEC_DMA_TX_3`. Preserve speaker/headphone sections and
existing includes. Use control names, not numerical numids. Do not enable MBHC
and DMIC2 together with the tested channel-index workaround.

Merge `config/flip2-dmic3-routing.dtsi.example` into the board's real DTS source.
An `audio-routing` assignment replaces the whole list: retain every existing
speaker/headphone route. Build the DTB through the board's existing recipe.
On the tested device both `/boot/dtbs/sm8250-retroidpocket-flip2.dtb` and
`/flash/boot/grub/sm8250-retroidpocket-flip2.dtb` were kept consistent; verify your
actual bootloader path rather than assuming these paths apply universally.

The WirePlumber example restricts only the named Mic source to the validated
format. Merge into `/etc/wireplumber/wireplumber.conf.d/` only if equivalent
settings are absent. These examples need the distribution's existing codec UCM
includes; they are not a replacement sound-card configuration.

Group necessary configuration/module changes before the same planned reboot.
Keep PipeWire/WirePlumber enabled. There is no need to stop or mask them for the
provided capture tests. A distribution update can replace custom modules;
carry the patches in your kernel packaging and rebuild for the new ABI.

## Historical configuration audit

See [retained changes and earlier experiments](HISTORY-AUDIT.md) before reusing
old helper scripts or changing the distribution power policy.
