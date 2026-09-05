#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Read the actually loaded WCD build ID and current boot ID."""
from pathlib import Path
import struct
import json
n = Path('/sys/module/snd_soc_wcd938x/notes/.note.gnu.build-id').read_bytes()
ns, ds, kind = struct.unpack_from('<III', n)
off = 12 + (ns + 3) // 4 * 4
if kind != 3 or n[12:12+ns].rstrip(b'\0') != b'GNU' or off + ds > len(n):
    raise SystemExit('Unexpected GNU build-id note format')
print(json.dumps({'loaded_build_id': n[off:off+ds].hex(),
                  'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip()}, indent=2))
