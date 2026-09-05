#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Report PCM levels and on/off tone evidence; never automatically declares repair."""
import argparse
import array
import json
import math
import sys
import wave

def inspect(path):
    with wave.open(str(path), 'rb') as w:
        if (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getcomptype()) != (1, 2, 48000, 'NONE'):
            raise ValueError('Expected uncompressed mono S16_LE 48000 Hz WAV')
        count = w.getnframes()
        raw = w.readframes(count)
    if len(raw) != count * 2:
        raise ValueError('Truncated PCM')
    samples = array.array('h', raw)
    if sys.byteorder != 'little':
        samples.byteswap()
    result = []
    for start in range(0, len(samples), 48000):
        x = samples[start:start+48000]
        mean = sum(x)/len(x)
        amplitudes = {}
        for hz in (900, 1000, 1100):
            c = 2 * math.cos(2*math.pi*hz/48000)
            q1 = q2 = 0.0
            for value in x:
                q0 = value + c*q1-q2
                q2, q1 = q1, q0
            amplitudes[hz] = 2*math.sqrt(max(0, q1*q1+q2*q2-c*q1*q2))/len(x)
        result.append({'second': start/48000, 'sample_count': len(x),
                       'min': min(x), 'max': max(x), 'nonzero': sum(v != 0 for v in x),
                       'rms': math.sqrt(sum(v*v for v in x)/len(x)),
                       'rms_ac': math.sqrt(sum((v-mean)**2 for v in x)/len(x)),
                       'amplitude': amplitudes})
    return {'sample_count': count, 'seconds': count/48000, 'windows': result}

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('wav')
    a = p.parse_args()
    print(json.dumps(inspect(a.wav), indent=2))
