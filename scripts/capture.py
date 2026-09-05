#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""User-started local capture. No driver, mixer, service or debugfs changes."""
import argparse
import array
import json
import math
from pathlib import Path
import signal
import subprocess
import sys
import time
import wave

SOURCE = 'alsa_input.platform-sound.HiFi__Mic__source'
SINK = 'alsa_output.platform-sound.HiFi__Speaker__sink'

def stimulus(path):
    pcm = array.array('h', (int(3500*math.sin(2*math.pi*1000*i/48000))
                           if 4 <= i/48000 < 7 or 10 <= i/48000 < 13 else 0
                           for i in range(24*48000)))
    if sys.byteorder != 'little':
        pcm.byteswap()
    with wave.open(str(path), 'wb') as w:
        w.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
        w.writeframes(pcm.tobytes())

def journal(*args):
    return subprocess.check_output(['sudo', '-n', 'journalctl', '-k', '-b',
                                    '--no-pager', *args], stderr=subprocess.STDOUT, timeout=15)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['tones', 'voice'])
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--source', default=SOURCE)
    p.add_argument('--sink', default=SINK)
    a = p.parse_args()
    if a.out.exists():
        p.error('Output directory already exists; choose a fresh directory.')
    # Prove log access before starting audio, never prompt sudo inside capture.
    initial = journal('--show-cursor')
    if b'-- cursor: ' not in initial:
        raise SystemExit('Kernel journal cursor unavailable; no recording started.')
    a.out.mkdir(parents=True)
    seconds = 24 if a.mode == 'tones' else 15
    if a.mode == 'tones':
        stimulus(a.out/'stimulus.wav')
        print('24 seconds: remain quiet. Two 1 kHz tones at 4–7 and 10–13 seconds.')
    else:
        print('15 seconds: speak, pause for several seconds, then speak again.')
    input('Press Enter when ready / Нажмите Enter для начала записи: ')
    initial = journal('--show-cursor')
    cursor = initial.decode().rsplit('-- cursor: ', 1)[1].strip()
    # Full initial journal intentionally not persisted; only new messages below.
    info = {'mode': a.mode, 'source': a.source, 'sink': a.sink,
            'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip()}
    processes = []
    files = []
    try:
        log = (a.out/'record.log').open('w'); files.append(log)
        info['record_start_monotonic'] = time.monotonic()
        rec = subprocess.Popen(['pw-record', '--target', a.source, '--rate', '48000',
                                '--channels', '1', '--format', 's16', '--sample-count',
                                str(seconds*48000), str(a.out/'capture.wav')],
                               stdout=log, stderr=subprocess.STDOUT)
        processes.append(rec)
        if a.mode == 'tones':
            log = (a.out/'play.log').open('w'); files.append(log)
            info['play_start_monotonic'] = time.monotonic()
            play = subprocess.Popen(['pw-play', '--target', a.sink, str(a.out/'stimulus.wav')],
                                    stdout=log, stderr=subprocess.STDOUT)
            processes.append(play)
        print('RECORDING NOW / ЗАПИСЬ НАЧАЛАСЬ', flush=True)
        info['record_returncode'] = rec.wait(timeout=seconds+12)
        if a.mode == 'tones':
            info['play_returncode'] = play.wait(timeout=12)
    finally:
        for process in processes:
            if process.poll() is None:
                process.send_signal(signal.SIGINT)
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait()
        for f in files:
            f.close()
        (a.out/'timing.json').write_text(json.dumps(info, indent=2)+'\n')
        (a.out/'kernel-after.txt').write_bytes(journal('--after-cursor', cursor, '-o', 'short-monotonic'))
        for name, cmd in [('services', ['systemctl', '--user', 'is-active', 'pipewire', 'wireplumber', 'pipewire-pulse']),
                          ('audio-status', ['wpctl', 'status'])]:
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            (a.out/(name+'.txt')).write_bytes(result.stdout+result.stderr)
    with wave.open(str(a.out/'capture.wav'), 'rb') as w:
        valid = (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (1,2,48000,seconds*48000)
    if not valid:
        raise SystemExit('Unexpected WAV format/length; inspect logs.')
    if a.mode == 'tones':
        info['user_heard_both_tones'] = input('Did you hear both tones from the speakers? / Слышали оба тона? ').strip()
    else:
        info['user_spoke_with_pauses'] = input('Did you speak with pauses during recording? / Говорили с паузами? ').strip()
    (a.out/'timing.json').write_text(json.dumps(info, indent=2)+'\n')
    print(f'Full-length WAV saved in {a.out}. Return codes: {info.get("record_returncode")}, {info.get("play_returncode")}.')
    print('Inspect logs and analyze PCM. This script does not declare acoustic success.')

if __name__ == '__main__':
    main()
