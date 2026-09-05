# SPDX-License-Identifier: MIT
import importlib.util
from pathlib import Path
import tempfile
import unittest
import wave

ROOT = Path(__file__).resolve().parents[1]
def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT/'scripts'/(name+'.py'))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

class Analysis(unittest.TestCase):
    def test_switched_tone_and_silence(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'test.wav'
            load('capture').stimulus(p)
            result = load('analyze').inspect(p)
            self.assertEqual(result['sample_count'], 24*48000)
            for sec in [2, 3, 8, 9, 14, 15]:
                self.assertEqual(result['windows'][sec]['nonzero'], 0)
            for sec in [5, 6, 11, 12]:
                amps = result['windows'][sec]['amplitude']
                self.assertGreater(amps[1000], 3490)
                self.assertLess(amps[900], 1)
                self.assertLess(amps[1100], 1)

    def test_wrong_format_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'wrong.wav'
            with wave.open(str(p), 'wb') as w:
                w.setparams((2,2,48000,0,'NONE','not compressed')); w.writeframes(b'\0'*16)
            with self.assertRaises(ValueError):
                load('analyze').inspect(p)

if __name__ == '__main__': unittest.main()
