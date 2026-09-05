#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Copy only WCD module sources to a new directory. Does not build or install."""
import argparse
from pathlib import Path
import shutil
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('kernel_source', type=Path)
p.add_argument('output', type=Path)
a = p.parse_args()
source = a.kernel_source / 'sound/soc/codecs'
names = ['wcd938x.c', 'wcd938x.h', 'wcd-common.h', 'wcd-mbhc-v2.h', 'wcd-clsh-v2.h']
for name in names:
    if not (source / name).is_file():
        p.error(f'Missing {source / name}; use the matching full kernel source.')
a.output.mkdir(parents=True, exist_ok=False)
for name in names:
    shutil.copy2(source / name, a.output / name)
(a.output / 'Makefile').write_text('obj-m += snd-soc-wcd938x.o\nsnd-soc-wcd938x-y := wcd938x.o\n')
print(a.output.resolve())
