# Patch licensing and order

Linux-derived patches here are GPL-2.0-only (see ../LICENSES/GPL-2.0-only.txt),
with upstream copyright retained as documented in ../NOTICE. The root MIT
license applies to original helper scripts/docs/config examples, not these
Linux patches.

0001 and 0002 were tested together; 0002 was the final acoustic fix.
0003 is optional and represents the mono prerequisite already present before
0002; apply only when TX_3 is still stereo. Its exported diff was checked against
a reconstructed stereo preimage and its result matches the tested logic.

Do not blindly apply the series on a newer driver. In particular, do not replace
an existing actual-ch_mask implementation with 0001. See ../docs/INSTALL.md.
