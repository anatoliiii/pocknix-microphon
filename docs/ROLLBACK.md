# Rollback

Do not reload or unbind a live SoundWire master. Save your work before reboot.
Use the backup path recorded during installation, not a path from another device.
For the uncompressed-module procedure in INSTALL.md:

```sh
BACKUP=/absolute/path/to/your/saved/backup-directory
sha256sum -c "$BACKUP/SHA256SUMS"
TARGET=$(cat "$BACKUP/installed-path.txt")
sudo install -m 644 "$BACKUP/snd-soc-wcd938x.ko" "$TARGET"
sudo depmod -a "$(uname -r)"
sync
```

If your module is included in initramfs, regenerate that image using your
distribution's procedure too. Then reboot manually. If the device cannot boot,
restore the old files using the SD card from another machine or the distribution's
recovery environment. Keep that route available before installation.

Restore only the DTB/UCM/WirePlumber files you changed, using your saved backups.
Do not blindly restore someone else's full ALSA state. Check system Speaker and
PipeWire/WirePlumber afterward. A module rollback does not revert the source
patch; use `git apply --check -R` followed by `git apply -R` for that separately.
